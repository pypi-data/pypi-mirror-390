import datetime

import time_machine

from django.conf import (
    settings,
)
from django.test.runner import (
    DiscoverRunner,
)

from behave_bo.__main__ import (
    run_behave,
)
from behave_bo.configuration import (
    Configuration,
)
from behave_bo.loggers import (
    tests_logger,
)
from behave_bo.reporter.failed_tags import (
    FailedTagsParallelReporter,
    FailedTagsReporter,
)
from behave_bo.reporter.junit import (
    JUnitReporter,
)
from behave_bo.runner import (
    BehaveRunner,
    BehaveTagsCachedRunner,
    ParallelBehaveRunner,
)
from behave_bo.tag_expression import (
    TagExpression,
)


class BaseBehaveTestRunner(DiscoverRunner):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.return_code_success = 0
        self.behave_config = None

        if kwargs.get('save_db'):
            # В случае если нужно сохранить результат в БД / отдельную БД,
            # атрибут keepdb должен быть True
            self.keepdb = True

    def get_tempdir_path(self):
        raise NotImplementedError

    def get_template_data_types(self):
        raise NotImplementedError

    def get_environment_filepath(self):
        raise NotImplementedError

    def run_behave_tests(self, behave_args, options):
        """Выполняет запуск behave тестов.

        Args:
            behave_args: Аргументы, относящиеся к behave_bo.
            options: Все аргументы команды запуска.

        Returns:
            Результат выполнения тестов.

        """
        self.behave_config = Configuration(behave_args)
        try:
            log_capture_exclude_template = settings.WEB_BB_BEHAVE__LOG_CAPTURE_EXCLUDE_TEMPLATE
        except AttributeError:
            log_capture_exclude_template = ''

        self.behave_config.log_capture_exclude_template = log_capture_exclude_template

        self._add_extra_parameters_to_behave_config(options)

        traveller = None

        if self.behave_config.replace_current_date:
            traveller = time_machine.travel(self.behave_config.replace_current_date)
            traveller.start()

        if self.parallel:
            behave_runner_class = ParallelBehaveRunner
            failed_tags_reporter_class = FailedTagsParallelReporter
        else:
            if self.behave_config.optimize_steps_loading:
                behave_runner_class = BehaveTagsCachedRunner
            else:
                behave_runner_class = BehaveRunner
            failed_tags_reporter_class = FailedTagsReporter

        failed_tags_reporter = failed_tags_reporter_class(self.behave_config)
        self.behave_config.reporters.append(failed_tags_reporter)

        try:
            junit_reporter = [r for r in self.behave_config.reporters if isinstance(r, JUnitReporter)][0]
        except IndexError:
            junit_reporter = None

        runner_kwargs = {
            'tempdir': self.get_tempdir_path(),
            'step_template_data_types': self.get_template_data_types(),
            'environment_filepath': self.get_environment_filepath(),
            'test_runner': self,
        }

        run_result = run_behave(
            self.behave_config,
            runner_class=behave_runner_class,
            runner_kwargs=runner_kwargs,
        )

        while failed_tags_reporter.rerun_required():
            failed_tags_reporter.rerun_up()
            tests_logger.info(
                f'Перезапуск упавших сценариев для выявления ложных падений '
                f'среди {len(failed_tags_reporter.main_run_failed_tags)} сценариев: '
                f'{", ".join(failed_tags_reporter.main_run_failed_tags)} '
                f'(попытка №{failed_tags_reporter.rerun_attempt})...\n'
            )

            if junit_reporter:
                junit_reporter.rerun = True
                self.behave_config.reporters.append(junit_reporter)

            run_behave(
                self.behave_config,
                runner_class=behave_runner_class,
                runner_kwargs=runner_kwargs,
            )

            if failed_tags_reporter.check_all_false_positive():
                run_result = self.return_code_success

        if traveller:
            traveller.stop()

        return run_result

    def _add_extra_parameters_to_behave_config(self, options):
        """Добавляет дополнительные параметры в конфиг в соответствии с options.

        Args:
            options: Аргументы команды запуска.

        """
        config = self.behave_config
        config.django_test_runner = self

        config.parallel = options.get('parallel')
        config.parallel_count = options.get('parallel_count')
        config.collect_top_scenarios = options.get('collect_top_scenarios')
        config.save_db = options.get('save_db')
        config.optimize_steps_loading = options.get('optimize_steps_loading')
        config.clear_cached_step_locations = options.get('clear_cached_step_locations')
        config.optimize_features_steps_loading = options.get('optimize_features_steps_loading')
        config.in_tags_order = options.get('in_tags_order')
        config.rerun_if_failed = options.get('rerun_if_failed')
        config.rerun_attempts = options.get('rerun_attempts')
        config.measure_requests_coverage = options.get('measure_requests_coverage')
        config.replace_current_date = None

        if options.get('replace_current_date'):
            try:
                config.replace_current_date = datetime.datetime.strptime(options['replace_current_date'], '%d.%m.%Y')
                tests_logger.info(
                    f'Запуск автотестов с заменой текущей даты на {config.replace_current_date:%d.%m.%Y}'
                )
            except ValueError as e:
                tests_logger.warning(f'Некорректное значение для параметра replace_current_date: {e}')

        config.save_changes_to_db = bool(config.save_db)

        if options.get('from_file_tags'):
            file_path = options.get('from_file_tags')
            try:
                with open(file_path) as f:
                    tags_from_file = f.readlines()[0]
                    config.tags = TagExpression([tags_from_file])
                    tests_logger.warning(
                        f'! Запуск автотестов по тегам перечисленным в файле {file_path}: {tags_from_file}'
                    )
            except Exception as e:
                tests_logger.warning(
                    f'Не удалось получить данные из файла с перечислением тегов для запуска автотестов {file_path}: {e}'
                )

        return config
