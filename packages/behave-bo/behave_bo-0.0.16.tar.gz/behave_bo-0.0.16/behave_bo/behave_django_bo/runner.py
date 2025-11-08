import datetime
import os
import traceback
import uuid
from collections import (
    defaultdict,
)
from typing import (
    List,
    Tuple,
)

from django.conf import (
    settings,
)
from django.db import (
    connections,
)
from django.db.models.query_utils import (
    DeferredAttribute,
)
from django.db.utils import (
    load_backend,
)
from django.test.utils import (
    override_settings,
)

from behave_bo.behave_django_bo.base_runner import (
    BaseBehaveTestRunner,
)
from behave_bo.behave_django_bo.consts import (
    override_settings_prefix,
    replace_current_date_prefix,
)
from behave_bo.behave_django_bo.loggers import (
    FixChecksLogger,
)
from behave_bo.behave_django_bo.plugins.base import (
    RunnerPluginsMixin,
)
from behave_bo.behave_django_bo.testcase import (
    BehaveTestCase,
    BehaveTransactionTestCase,
)
from behave_bo.behave_django_bo.utils import (
    override_current_date,
    override_dirs,
)
from behave_bo.behave_django_bo.wrapper_with_queries_log import (
    changed_tables,
)
from behave_bo.configuration import (
    Configuration,
)
from behave_bo.loggers import (
    tests_logger,
)
from behave_bo.model import (
    Scenario,
)


behave_run_scenario = Scenario.run


class PatchedScenario(Scenario):

    @property
    def override_settings_tag(self):
        override_settings_tag = None

        for tag in self.tags:
            if tag.startswith(override_settings_prefix):
                override_settings_tag = tag
                break

        return override_settings_tag

    def make_override_settings_dict(self, runner) -> dict:
        """Формирует словарь настроек для переопределения в override_settings.

        Настройки, задаваемые в runner.override_settings_dict, будут переопределены
        или дополнены для конкретного сценария.

        Args:
            runner: объект класса Runner, исполнителя behave-автотестов.

        Returns:
            Словарь вида {Наименование настройки: значение}.

        """
        override_settings_dict = getattr(runner, 'override_settings_dict', {})

        if self.override_settings_tag:
            settings_string = self.override_settings_tag.removeprefix(override_settings_prefix)
            for key, value in map(lambda s: s.split('=', 1), settings_string.split(',')):
                if value.isdigit():
                    value = int(value)
                elif value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                elif value.lower() == 'none':
                    value = None

                override_settings_dict[key] = value

            tests_logger.info(
                f'Для сценария {self.main_tag} будут переопределены django settings: {override_settings_dict}'
            )

        return override_settings_dict

    @property
    def replace_current_date_tag(self):
        """Определение тега замены текущей даты у сценария."""
        replace_current_date_tag = None

        for tag in self.tags:
            if tag.startswith(replace_current_date_prefix):
                replace_current_date_tag = tag
                break

        return replace_current_date_tag

    def get_scenario_current_date(self) -> datetime.date:
        """Получение даты из тега замены текущей даты сценария.

        Returns:
            Объект даты
        """
        replace_current_date = None

        if self.replace_current_date_tag:
            replace_current_date = datetime.datetime.strptime(
                self.replace_current_date_tag.removeprefix(replace_current_date_prefix).split('=')[1],
                '%d.%m.%Y',
            ).date()

            tests_logger.info(
                f'Для сценария {self.main_tag} будут переопределена текущая дата: {replace_current_date:%d.%m.%Y}'
            )

        return replace_current_date

    def run_scenario(self, runner):
        """Пропатченный метод запуска behave-сценария.

        Сразу проверяется необходимость выполнения сценария, и если не нужно выполнять, помечается пропущенным.
        Если нужно выполнять, на время выполнения конкретного сценария создаёт уникальную временную директорию.

        Args:
            self: объект класса Scenario
            runner: объект класса Runner, исполнителя behave-автотестов.
        """
        failed = False
        should_run_scenario = self.should_run(runner.config)

        if should_run_scenario:
            for number, step in enumerate(self.steps, 1):
                step.number = number
            settings_dict = self.make_override_settings_dict(runner)
            scenario_current_date = self.get_scenario_current_date()

            with override_dirs(self), override_settings(**settings_dict), override_current_date(scenario_current_date):
                failed = behave_run_scenario(self, runner)
        else:
            self.mark_skipped()

        return failed


Scenario.base_skip_tags = list(Scenario.base_skip_tags) + [override_settings_prefix]
Scenario.override_settings_tag = PatchedScenario.override_settings_tag
Scenario.replace_current_date_tag = PatchedScenario.replace_current_date_tag
Scenario.make_override_settings_dict = PatchedScenario.make_override_settings_dict
Scenario.get_scenario_current_date = PatchedScenario.get_scenario_current_date
Scenario.run = PatchedScenario.run_scenario


class BehaveTestRunner(BaseBehaveTestRunner, RunnerPluginsMixin):

    reset_sequences_sql = {}
    default_db_name = None
    test_db_name = None
    behave_config: Configuration = None
    max_identifier_length: int = None

    def get_tempdir_path(self):
        return settings.TEMPDIR

    def get_template_data_types(self):
        return dict()

    def get_environment_filepath(self):
        return os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            'environment.py'
        )

    def define_testcase_class(self, config):
        if config.save_changes_to_db:
            testcase_class = BehaveTransactionTestCase
        else:
            testcase_class = BehaveTestCase

        return testcase_class

    def run_behave_tests(self, behave_args, options):
        with FixChecksLogger(options.get('fix_checks', False) or options.get('fix_excluded_keys', False)):
            run_result = super().run_behave_tests(behave_args, options)

        self._remove_readonly_requests_files()

        return run_result

    def _add_extra_parameters_to_behave_config(self, options):
        """Добавляет дополнительные параметры в конфиг в соответствии с options.

        Args:
            options: Аргументы команды запуска.

        """
        config = super()._add_extra_parameters_to_behave_config(options)

        config.bgjob_wait_time = options.get('bgjob_wait_time')
        config.bgjob_wait_iteration_freeze = options.get('bgjob_wait_iteration_freeze')
        config.remove_readonly_requests = options.get('remove_readonly_requests')
        config.remove_readonly_requests_data = {
            'not_used_request_files': set(),
            'not_used_steps_lines': defaultdict(list),
            'used_request_files': set(),
            'used_steps_funcs': defaultdict(set),
        }
        config.skip_readonly_requests = options.get('skip_readonly_requests')
        config.skip_readonly_requests_url_endings = options.get('skip_readonly_requests_url_endings')
        config.skip_production_request_checks = options.get('skip_production_request_checks')
        config.fix_checks = options.get('fix_checks')
        config.fix_excluded_keys = options.get('fix_excluded_keys')
        config.analyze_model_records = options.get('analyze_model_records', '').split(',')
        config.log_non_200_requests = options.get('log_non_200_requests')

        config.test_case_type = self.define_testcase_class(config)
        config.test_case_type.runner = self

        if config.save_changes_to_db and not options.get('tags'):
            raise Exception(
                'Сохранение БД возможно только при запуске индивидуальных тестов!'
            )
        if config.save_changes_to_db and config.parallel:
            raise Exception(
                'Нельзя одновременно использовать параметры --parallel и --save-db'
            )
        if config.fix_excluded_keys and config.fix_checks:
            raise Exception(
                'Нельзя одновременно использовать параметры --fix-checks и --fix-excluded-keys'
            )

        return config

    def setup_databases(self, **kwargs):
        """
        Создание БД перед тестированием - средствами SQL и частично Django
        """
        connections['default'].close()
        db_postfix = kwargs.get('db_postfix') or uuid.uuid4().hex
        self.test_db_name = f'_{db_postfix}'

        self.default_db_name = settings.DATABASES['default']['NAME']
        temp_settings = connections['default'].settings_dict.copy()

        backend = load_backend(temp_settings['ENGINE'])
        temp_settings['NAME'] = 'postgres'
        temp_connection = backend.DatabaseWrapper(
            temp_settings,
            alias='temp_connection',
        )

        cursor = temp_connection.cursor()

        try:
            cursor.connection.set_isolation_level(0)
            cursor.execute(f'DROP DATABASE IF EXISTS "{self.test_db_name}"')
        except Exception as e:
            tests_logger.critical(f"Database deletion error: {e}\n")

        try:
            cursor.execute(f'CREATE DATABASE "{self.test_db_name}" '
                           f'TEMPLATE {self.default_db_name}')
        except Exception as e:
            tests_logger.critical(f'Database creation error: {e}\n')
            exit(-1)

        tests_logger.info(f'Database "{self.test_db_name}" created')
        temp_settings['NAME'] = self.test_db_name
        connections['default'] = backend.DatabaseWrapper(
            temp_settings,
            alias='default',
        )
        temp_connection.close()
        connections['default'].connect()

    def teardown_database(self):
        """
        Снос копии БД созданной для запуска автотестов
        """
        if not self.keepdb and self.test_db_name:
            connections['default'].close()
            db_settings = connections['default'].settings_dict.copy()
            backend = load_backend(db_settings['ENGINE'])
            db_settings['NAME'] = self.default_db_name
            default_connection = connections['default'] = backend.DatabaseWrapper(
                db_settings,
                alias='default',
            )
            default_connection.connect()

            cursor = default_connection.cursor()
            try:
                cursor.execute(f'DROP DATABASE IF EXISTS "{self.test_db_name}"')
                tests_logger.info(f'Database "{self.test_db_name}" destroyed!')
            except Exception as e:
                tests_logger.critical(f"Database deletion error: {e}\n")
            else:
                self.test_db_name = None

    def get_sequences(self, connection) -> List[Tuple[str, str]]:
        """Получает список последовательностей таблиц бд.

        Args:
            connection: Конект к бд.

        Returns:
            Список наименований таблиц и их последовательностей.
        """
        with connection.cursor() as cursor:
            cursor.execute(
                """SELECT tbl.relname, s.relname as sequence_name 
                FROM pg_class s
                    JOIN pg_depend d ON d.refobjid = s.oid AND d.refclassid = 'pg_class'::regclass
                    JOIN pg_attrdef ad ON ad.oid = d.objid AND d.classid = 'pg_attrdef'::regclass
                    JOIN pg_class tbl ON tbl.oid = ad.adrelid
                    JOIN pg_namespace n ON n.oid = tbl.relnamespace
                WHERE s.relkind = 'S'
                    AND d.deptype in ('a', 'n')
                    AND n.nspname = 'public';"""
            )
            return cursor.fetchall()

    def define_max_identifier_length(self, connection):
        """Определяет и сохраняет максимальную длину идентификатора бд max_identifier_length.

        Args:
            connection: Конект к бд.
        """
        with connection.cursor() as cursor:
            cursor.execute('SHOW max_identifier_length;')
            self.max_identifier_length = int(cursor.fetchone()[0])

    def collect_reset_sequences_sql(self) -> None:
        """Собирает данные по последовательностям бд.

        Заносит в self.reset_sequences_sql наименование таблицы и sql-код для сброса последовательности.
        """
        connection = connections['default']
        self.define_max_identifier_length(connection)
        for table, sequence in self.get_sequences(connection):
            with connection.cursor() as cursor:
                cursor.execute(
                    f'SELECT last_value, is_called from "{sequence}";'
                )
                last_value, is_called = cursor.fetchone()
                setval_sql = (
                    f"SELECT setval('\"{sequence}\"', {last_value}, {is_called});"
                )
                self.reset_sequences_sql[table] = setval_sql

    def reset_sequences(self) -> None:
        """Сбрасывает последовательности таблиц."""
        connection = connections['default']
        with connection.cursor() as cursor:
            for table in changed_tables.copy():
                pg_table_name = table[:self.max_identifier_length]
                if pg_table_name in self.reset_sequences_sql:
                    cursor.execute(self.reset_sequences_sql[pg_table_name])
                changed_tables.remove(table)

    def collect_requests_data(self, is_used) -> None:
        """
        Найдем из стека вызовов данные о используемых/неиспользуемых файлах отправки запросов.
        Берём последние 4 фрейма т.к. стандартно вызов отправки запроса происходит из функции шага,
        далее в функции запроса, далее в методе execute, и далее в текущем методе.

        Args:
            is_used: Признак использования файла запроса
        """
        last_frames_index = -4
        request_file_prefix = 'request_'
        steps_file_prefix = 'steps_'
        data = self.behave_config.remove_readonly_requests_data

        for frame in traceback.extract_stack()[last_frames_index:]:
            filename = os.path.basename(frame.filename)

            if is_used:
                if filename.startswith(steps_file_prefix):
                    data['used_steps_funcs'][frame.filename].add(
                        frame.line.split('(')[0],  # название функции отправки запроса
                    )
                elif filename.startswith(request_file_prefix):
                    data['used_request_files'].add(frame.filename)
            else:
                if filename.startswith(steps_file_prefix):
                    data['not_used_steps_lines'][frame.filename].append((
                        frame.lineno,  # номер линии в файле, где вызывается функция
                        frame.line.split('(')[0],  # название функции отправки запроса
                    ))
                elif filename.startswith(request_file_prefix):
                    data['not_used_request_files'].add(frame.filename)

    def _remove_readonly_requests_files(self):
        """
        Удаляет файлы readonly-запросов шагов предыстории из автотестов на основе данных remove_readonly_requests_data.
        """
        data = self.behave_config.remove_readonly_requests_data
        remove_key = 'remove'

        for step_file, lines_list in data['not_used_steps_lines'].items():
            tests_logger.info(f'Удаляем вызов функции отправки readonly-запроса из файла реализации шагов {step_file}')
            used_steps_funcs = data['used_steps_funcs'][step_file]

            with open(step_file) as f:
                lines = f.readlines()

            remove_indexes, remove_func_names = zip(*lines_list)

            for idx, line in enumerate(lines):
                file_line_num = idx + 1

                if file_line_num in remove_indexes:
                    # Удаление из функции реализации шага
                    lines[idx] = remove_key
                elif any(f'{remove_func_name},' in line and remove_func_name not in used_steps_funcs
                         for remove_func_name in remove_func_names):
                    # Удаление из секции импортов
                    for remove_idx in (
                        idx - 1,
                        idx,
                        idx + 1,
                    ):
                        lines[remove_idx] = remove_key

            new_lines = []
            step_def = False

            for line in lines:
                if line != remove_key:
                    if step_def:
                        if not line.strip():
                            new_lines.append('    pass\n')
                        step_def = False

                    new_lines.append(line)

                if 'def ' in line:
                    step_def = True

            with open(step_file, 'w') as f:
                f.writelines(new_lines)

        for request_file in (data['not_used_request_files'] - data['used_request_files']):
            tests_logger.info(f'Удаляем файл readonly-запроса {request_file}')
            try:
                os.remove(request_file)
            except Exception as e:
                tests_logger.info(f'Ошибка при удалении файла: {e}')


def _DeferredAttributeWithCheck__get__(self, instance, cls=None):
    """
    Добавление проверки/логирования в метод отложенного получения значения атрибута.

    Args:
        self: экземпляр класса DeferredAttribute
        instance: экземпляр класса модели для которого выполняется получение значения атрибута.
        cls: класс модели

    Returns:
        Значение атрибута.

    Raises:
        Исключение в случае если включена настройка CHECK_DEFERRED_ATTR_GET
         и значение атрибута не найдено в кэше, а значит его планируется получить из БД выполнив дополнительный запрос.
    """
    if instance is None:
        return self
    data = instance.__dict__
    field_name = self.field.attname

    if field_name in data:
        return data[field_name]

    attr = f"{instance.__class__.__name__}.{field_name}"
    message = f"Lazy fetching of {attr} may cause 1+N issue"

    if settings.WEB_BB_BEHAVE__CHECK_DEFERRED_ATTR_GET:
        raise AssertionError(message)
    elif settings.WEB_BB_BEHAVE__LOG_DEFERRED_ATTR_GET:
        tests_logger.warning(message)

    return DeferredAttribute__get(self, instance, cls)


DeferredAttribute__get, DeferredAttribute.__get__ = DeferredAttribute.__get__, _DeferredAttributeWithCheck__get__
