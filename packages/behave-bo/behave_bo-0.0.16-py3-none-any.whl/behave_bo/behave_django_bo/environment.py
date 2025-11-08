from datetime import (
    datetime,
)

try:
    from celery.signals import (
        task_failure,
    )
except ImportError:
    task_failure = None

from django.db import (
    transaction,
)
from django.dispatch import (
    receiver,
)
from factory.django import (
    mute_signals,
)

from behave_bo.behave_django_bo.cache import (
    django_cache_dump,
    django_cache_restore,
    setup_cache_server_db,
)
from behave_bo.behave_django_bo.client import (
    BehaveBOClient,
)
from behave_bo.behave_django_bo.enums import (
    SaveDbParameterEnum,
)
from behave_bo.behave_django_bo.plugins.base import use_plugins
from behave_bo.behave_django_bo.requests import (
    AppRequest,
)
from behave_bo.behave_django_bo.signals import (
    after_scenario_signal,
    after_step_plugins,
)
from behave_bo.behave_django_bo.utils import (
    ModelRecordAnalyzer,
)
from behave_bo.consts import (
    scenario_tag_cookie_key,
)
from behave_bo.loggers import (
    tests_logger,
)


failure_task_exceptions = []

if task_failure:
    @receiver(task_failure)
    def handle_task_failure(exception, **kwargs):
        """
        Обработка сигнала ошибочного завершения фоновой, для последующей
        обработки в process_after_step.
        """
        failure_task_exceptions.append(exception)


class Environment:

    def failure_task_possible_exception(self, exc, context):
        return f'ignore{exc.__class__.__name__}' in context.scenario.tags

    def process_after_step(self, context):
        """
        Некоторые таски celery запускаются через событие on_commit,
        которое не происходит когда нужно, потому что каждый тест
        оборачивается в atomic. Прогоним вручную
        """
        conn = transaction.get_connection()

        if conn.in_atomic_block:
            for _, _func in conn.run_on_commit:
                if signals_to_mute := context.signals_to_mute_in_tasks:
                    with mute_signals(*signals_to_mute):
                        _func()
                else:
                    _func()

                if failure_task_exceptions:
                    raise failure_task_exceptions.pop()

            conn.run_on_commit = []

        if failure_task_exceptions:
            raw_exceptions = []
            for exc in failure_task_exceptions:
                if self.failure_task_possible_exception(exc, context):
                    tests_logger.info(f'{exc.__class__}: {exc}')
                else:
                    raw_exceptions.append(exc)

            failure_task_exceptions.clear()

            if raw_exceptions:
                raw_exceptions_str = '\n'.join(f'{e.__class__.__name__}: {e}' for e in raw_exceptions)
                raise Exception(
                    f'Количество необработанных ошибок в фоновых задачах: {len(raw_exceptions)}\n{raw_exceptions_str}'
                )

    @use_plugins
    def before_all(self, context):
        context.session = BehaveBOClient()
        context.AppRequest = AppRequest

        if context.config.parallel:
            setup_cache_server_db(context.config.group_number)

    @use_plugins
    def before_feature(self, context, feature):
        pass

    @use_plugins
    def before_scenario(self, context, scenario):
        if f'{scenario.main_tag}' in context.config.analyze_model_records:
            context.model_record_analyzer = ModelRecordAnalyzer(context)

        context.today_date = datetime.today()

        # Сохраняем DjangoCache
        context.cache_dump = django_cache_dump()

        # Инициализируем объект теста
        context.test = context.config.test_case_type()

        # Отключаем лимит вывода информации от assert-методов сравнения,
        # в случае несоответствия сравниваемых данных.
        context.test.maxDiff = None

        # инициализируем тесткейс
        setup_result = context.test.setUpClass()
        if setup_result is False:
            scenario.skip("Can't setup class")

        test_tag = scenario.main_tag
        context.test_tag = test_tag

        if context.config.save_db == SaveDbParameterEnum.SEPARATE:
            if scenario._row:
                test_tag += scenario._row.id

            context.config.django_test_runner.setup_databases(
                db_postfix=test_tag,
            )

        self.set_session_cookies_scenario_tags(context, scenario)

    @use_plugins
    def before_step(self, context, step):
        setattr(context, 'current_step', step)
        context.signals_to_mute_in_tasks = None

    @use_plugins
    def after_step(self, context, step):
        after_step_plugins.send(sender=None, context=context, step=step)
        
        self.process_after_step(context)

        if hasattr(context, 'current_step'):
            delattr(context, 'current_step')

    @use_plugins
    def after_scenario(self, context, scenario):
        context.test.tearDownClass()

        if context.config.save_db == None:
            context.config.django_test_runner.reset_sequences()

        del context.test

        # Восстанавливаем DjangoCache
        django_cache_restore(context.cache_dump)
        after_scenario_signal.send(sender=None, context=context, scenario=scenario)

        if f'{scenario.main_tag}' in context.config.analyze_model_records:
            context.model_record_analyzer.write()

        if context.config.log_non_200_requests:
            context.session.print_non_200_requests()

    @use_plugins
    def after_feature(self, context, feature):
        """Объявление функции нужно для выполнения кода в соответствующем хуке плагинов."""
        pass

    @use_plugins
    def after_all(self, context):
        context.session = None
        context.config.django_test_runner.teardown_database()

    def set_session_cookies_scenario_tags(self, context, scenario):
        """
        Прокидывает в cookies сессии информацию о тегах сценария, -- указывает основной тег сценария.
        Для случая Структуры сценария дополняет тег сценария номером примера.

        Args:
            context: объект контекста тестирования behave_bo.runner.Context
            scenario: объект сценария behave_bo.model.Scenario
        """
        if scenario._row:
            cookie_test_tag = f'{scenario.main_tag}-{scenario._row.id}'
        else:
            cookie_test_tag = scenario.main_tag

        context.session.cookies[scenario_tag_cookie_key] = cookie_test_tag


environment_object = Environment()
