import datetime
import json
import os
import shutil
import tempfile
import traceback
import uuid
from collections import (
    defaultdict,
)
from contextlib import (
    contextmanager,
)
from itertools import (
    zip_longest,
)

import time_machine
from django.apps import (
    apps,
)
from django.conf import (
    settings,
)
from django.db.models.signals import (
    post_delete,
    post_init,
    post_save,
)
from django.test.utils import (
    override_settings,
)

from behave_bo.loggers import (
    tests_logger,
)


def get_features_paths():
    """Возвращает список путей до директорий features в app'ах, если существуют."""

    paths = []
    for app in apps.get_app_configs():
        features_dir = os.path.join(app.path, 'features')
        if os.path.isdir(features_dir):
            paths.append(features_dir)

    return paths


@contextmanager
def override_dirs(scenario):
    """Контекстный менеджер для создания уникальных директорий под временные файлы и downloads для выполняемого сценария

    Args:
        scenario: объект класса Scenario

    """
    prefix = scenario.main_tag if scenario.tags else uuid.uuid4().hex[:6]

    old_tempdir = settings.TEMPDIR
    old_downloads_dir = settings.DOWNLOADS_DIR

    new_tempdir = f"{old_tempdir}/{prefix}__{scenario.line}"
    new_downloads_dir = f"{old_downloads_dir}/{prefix}__{scenario.line}"

    if os.path.isdir(new_tempdir):
        shutil.rmtree(new_tempdir, ignore_errors=True)

    tempfile.tempdir = new_tempdir

    if not os.path.isdir(tempfile.gettempdir()):
        os.makedirs(tempfile.gettempdir())

    if os.path.isdir(new_downloads_dir):
        shutil.rmtree(new_downloads_dir, ignore_errors=True)

    if not os.path.isdir(new_downloads_dir):
        os.makedirs(new_downloads_dir)

    try:
        with override_settings(TEMPDIR=new_tempdir, DOWNLOADS_DIR=new_downloads_dir):
            yield
    finally:
        tempfile.tempdir = old_tempdir


@contextmanager
def override_current_date(selected_date):
    """Контекстный менеджер для подмены текущей даты

    Args:
        selected_date: дата на которую требуется подменить текущую дату
    """
    try:
        if selected_date:
            with time_machine.travel(selected_date):
                yield
        else:
            yield
    finally:
        pass


class ModelRecordAnalyzer:
    """Инструмент для анализа очередности создания, удаления и инициализации записей моделей."""

    class Aside:
        """Класс для хранения промежуточного состояния."""
        def __init__(self):
            self.prev_step_id = None
            self.step_id = None
            self.model_label = None
            self.pk_list = []
            self.action = None
            self.stack = None
            self.hash_on_stack = 0

    def __init__(self, context, *args, **kwargs):
        self.context = context

        row_id = ''

        if context.scenario._row:
            row_id = f'_{context.scenario._row.id}'

        self.scenario_id = f'{context.scenario.main_tag}{row_id}'

        self.step_log = {self._get_step_id(step): [] for step in context.scenario.all_steps}
        self.stack_log = defaultdict()
        self._connect()

        self._counter = 0
        self.aside = self.Aside()

    def _connect(self):
        """Подключение к сигналам django."""
        post_save.connect(self._save_post_save)
        post_delete.connect(self._save_post_delete)
        post_init.connect(self._save_post_init)

    def _save_post_save(self, sender, instance, created, **kwargs):
        """Обработчик post_save сигнала."""
        self._lazy_save(sender, instance.pk, 'created' if created else 'updated')

    def _save_post_delete(self, sender, instance, **kwargs):
        """Обработчик post_delete сигнала."""
        self._lazy_save(sender, instance.pk, 'deleted')

    def _save_post_init(self, sender, instance, **kwargs):
        """Обработчик post_init сигнала."""
        if instance.pk and not self._called_from_factory():
            self._lazy_save(sender, instance.pk, 'evaluated')

    def _called_from_factory(self):
        """Выполняется ли вызов через Factory."""
        # TODO BOBUH-25284 web_bb_behave/runner путь из проекта убрать
        return any('web_bb_behave/runner/factories/base.py' in p.filename for p in self._get_stack())

    @property
    def _dir_path_to_save(self):
        """Директория хранения логов по выполненным тестам."""
        dir_to_save = os.path.join(settings.FACTORY_BO__FIXTURES_DIR_PATH, 'testing_analyze_model_records')
        if not os.path.exists(dir_to_save):
            os.mkdir(dir_to_save)

        return dir_to_save

    @property
    def _file_path_to_save(self):
        """Путь к файлу для сохранения результата."""
        timestamp = f'{datetime.datetime.now():%d%m%y%H%M%S}'
        file_path_to_save = os.path.join(self._dir_path_to_save, f'{self.scenario_id}_{timestamp}')

        return file_path_to_save

    @property
    def _step_id(self):
        """Идентификатор шага."""
        if hasattr(self.context, 'current_step'):

            return self._get_step_id(self.context.current_step)

    @staticmethod
    def _get_step_id(step):
        """Поучает идентификатор шага."""

        number = getattr(step, 'number', 0)

        return f'{number}. {step.keyword} {step.name}'

    def _next_num(self):
        """Увеличивает счетчик на 1 и возвращает полученное значение."""
        self._counter += 1

        return self._counter

    @staticmethod
    def _in_projects_dirs(path):
        """Проверяет, относится ли путь к основным директориям проекта."""

        return any(repo in path for repo in settings.WEB_BB_BEHAVE__TESTING_PROJECTS)

    def _get_stack(self):
        """Получает стек по директориям проекта."""
        stack = [s for s in traceback.extract_stack() if self._in_projects_dirs(s.filename)]

        return stack

    def _get_hash_on_stack(self):
        """Получает хэш по стеку, без учета последних 3 строк, относящихся к вызовам внутри данного инструмента."""
        stack = [f'{s.filename}:{s.lineno}' for s in self._get_stack()][:-3]

        return hash(''.join(stack))

    def _put_aside(self, sender, pk, action, hash_on_stack, reset_pk=False):
        """Запоминает состояние вызова."""
        if reset_pk:
            self.aside.pk_list.clear()

        self.aside.step_id = self._step_id
        self.aside.model_label = sender._meta.label
        self.aside.action = action
        self.aside.pk_list.append(pk)
        self.aside.hash_on_stack = hash_on_stack
        self.aside.stack = self._get_stack()

    def _save(self):
        """Сохраняет состояние aside в основной лог выполнения."""
        if self.aside.prev_step_id != self.aside.step_id:
            self.aside.prev_step_id = self.aside.step_id
            self._counter = 0
        number = self._next_num()
        string_to_save = f'{number} {self.aside.model_label} {self.aside.pk_list} {self.aside.action}'

        self.step_log[f'{self.aside.step_id}'].append(string_to_save)
        self.stack_log[string_to_save] = self.aside.stack

    def _lazy_save(self, sender, pk, action):
        """Отложенное сохранение результата выполнения."""
        if self._step_id:
            hash_on_stack = self._get_hash_on_stack()
            # При первом вызове сохраняет состояние в aside.
            if not self.aside.hash_on_stack:
                self._put_aside(sender, pk, action, hash_on_stack)
            # При совпадении стека, модели и действия расширяет список aside.pk_list.
            # Таким образом выполняется отбор вызовов относящихся к одному queryset.
            elif (
                hash_on_stack == self.aside.hash_on_stack
                and self.aside.model_label == sender._meta.label
                and self.aside.action == action
            ):
                self._put_aside(sender, pk, action, hash_on_stack)
            # Иначе aside.pk_list сбрасывается.
            else:
                self._save()
                self._put_aside(sender, pk, action, hash_on_stack, reset_pk=True)

    def _parse_log_file(self, file_path):
        """Парсит лог файл."""
        with open(file_path) as f:
            json_log = json.loads(f.read())

        return json_log

    def _get_last_created_log_file_for_scenario(self):
        """Получает путь к последнему созданному файлу для сценария."""
        last_created_log_file = None

        for file_name in sorted(os.listdir(self._dir_path_to_save), reverse=True):
            if file_name.startswith(f'{self.scenario_id}'):
                last_created_log_file = os.path.join(self._dir_path_to_save, file_name)
                break

        return last_created_log_file

    def _get_previous_log_for_scenario(self):
        """Получает лог последнего запуска для сценария."""
        log = None

        last_created_log_file = self._get_last_created_log_file_for_scenario()
        if last_created_log_file:
            log = self._parse_log_file(last_created_log_file)

        return log

    def _compare_with_previous_log(self):
        """Выполняет сравнение с результатом предыдущего запуска, если такой был."""
        prev_log = self._get_previous_log_for_scenario()
        if not prev_log:
            tests_logger.info('Previous log file not found.')
        elif prev_log.keys() != self.step_log.keys():
            tests_logger.info('Steps don\'t match.')
        else:
            for step_name, prev_list, curr_list in zip(prev_log.keys(), prev_log.values(), self.step_log.values()):
                for prev, curr in zip_longest(prev_list, curr_list, fillvalue=None):
                    if prev != curr:
                        try:
                            stack = self.stack_log[curr]
                        except KeyError:
                            stack = 'Failed to get traceback.'
                        else:
                            stack = ''.join(traceback.format_list(stack))
                        tests_logger.warning(
                            f'First difference found in step {step_name}\n'
                            f'Previous: {prev}\n'
                            f'Current:  {curr}\n'
                            f'Traceback:\n'
                            f'{stack}'
                        )
                        break
                else:
                    continue
                break

    def write(self):
        """Запись результата в файл."""
        self._save()
        self._compare_with_previous_log()

        with open(self._file_path_to_save, 'w') as f:
            string_to_write = json.dumps(self.step_log, indent=2, ensure_ascii=False)
            f.write(string_to_write)
