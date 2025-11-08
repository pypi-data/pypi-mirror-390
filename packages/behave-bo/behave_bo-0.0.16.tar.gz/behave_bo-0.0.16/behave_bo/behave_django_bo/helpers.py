import os
import zipfile
from difflib import (
    unified_diff,
)
from tempfile import (
    TemporaryDirectory,
)

from django.conf import (
    settings,
)

from behave_bo.model import (
    Table,
)


def get_context_extractor_class():
    # TODO BOBUH-23698 Вынести настройку CONTEXT_EXTRACTOR из web_bb_behave
    context_extractor_cls = (
        settings.WEB_BB_BEHAVE__CONTEXT_EXTRACTOR or
        'behave_bo.behave_django_bo.extractors.ContextExtractor'
    )
    context_extractor_cls_path = context_extractor_cls.split('.')
    # Allow for relative paths
    if len(context_extractor_cls_path) > 1:
        extractor_module_name = '.'.join(context_extractor_cls_path[:-1])
    else:
        extractor_module_name = '.'
    extractor_module = __import__(extractor_module_name, {}, {}, context_extractor_cls_path[-1])
    return getattr(extractor_module, context_extractor_cls_path[-1])


def filter_dict_keys(
    obj,
    excluded_keys,
):
    """Исключает ключи из словаря и его вложенных словарей.

    Args:
        obj: Словарь/список/любое значение.
        excluded_keys: Список строк ключей для исключения.
    Returns:
        Словарь/список/любое значение без исключённых ключей.
    """
    if isinstance(obj, dict):
        obj = {
            key: filter_dict_keys(
                value,
                excluded_keys,
            )
            for key, value in obj.items()
            if key not in excluded_keys
        }
    elif isinstance(obj, list):
        obj = [
            filter_dict_keys(
                item,
                excluded_keys,
            )
            for item in obj
        ]

    return obj


def sort_lists_in_dict(obj, sort_key=None):
    """Сортирует все списки в словаре.

    Args:
        data: Словарь/список/любое значение.
        sort_key: Ключ для сортировки списка.

    Returns:
        Словарь/список/любое значение с отсортированными списками.

    """
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = sort_lists_in_dict(value, sort_key)

    elif isinstance(obj, list):
        for item in obj:
            sort_lists_in_dict(item, sort_key)

        obj.sort(key=sort_key)

    return obj


class FilesCompare:
    """Предоставляет функционал сравнения файлов.

    Attributes:
        message: str. Сообщение с подробным результатом сравнения.
        compare_file_names: bool. Сравнивать наименования файлов.
            во временной директории

    """

    TABLE_MAP = {
        'Без проверки имен файлов': 'without_compare_file_names',
    }

    def __init__(self, **kwargs):
        self.message = ''
        self.compare_file_names = kwargs.get('compare_file_names', True)
        self._in_temporary_dir = False

        if kwargs.get('table'):
            params = self._processing_table(kwargs['table'])
            self._processing_params(params)
        else:
            self._processing_params(kwargs)

        self._compare_func_type_map = {
            'CSV': self.compare_csv_files,
            'TXT': self.compare_text_files,
            'HTML': self.compare_html_files,
        }

    def _processing_table(self, table: Table) -> dict:
        """Преобразует behave таблицу в словарь, при этом наименования столбцов
        заменяет в соответствии с таблицей TABLE_MAP.

        Args:
            table: объект Table полученный из *feature файла*.

        Returns:
            Словарь параметров.
        """

        return {self.TABLE_MAP[k]: v for k, v in table.rows[0].items() if k in self.TABLE_MAP.keys()}

    def _processing_params(self, params: dict) -> None:
        """Выполняет обработку параметров сравнения.

        Args:
            params: Словарь параметров.

        Returns:
            None.
        """
        if 'without_compare_file_names' in params:
            self.compare_file_names = False

    def compare_csv_files(self, left: str, right: str):
        """Сравнивает csv файлы.

        Args:
            left: Абсолютный путь до файла.
            right: Абсолютный путь до файла.

        Returns:
            Результат сравнения.
        """

        return self.compare_text_files(left, right, encoding='utf8')

    def compare_text_files(self, left: str, right: str, encoding: str = 'cp1251'):
        """Сравнивает текстовые файлы.

        Args:
            left: Абсолютный путь до файла.
            right: Абсолютный путь до файла.
            encoding: Кодировка файлов.

        Returns:
            Результат сравнения.
        """
        with open(left, encoding=encoding) as left_file:
            with open(right, encoding=encoding) as right_file:
                left_lines = left_file.readlines()
                right_lines = right_file.readlines()

                if len(left_lines) != len(right_lines):
                    result = False
                    self.message += 'Файлы содержат разное количество строк.\n'
                else:
                    diff = list(unified_diff(left_lines, right_lines, 'Left', 'Right'))
                    result = not diff
                    self.message += f'{"".join(diff)}'
        if result:
            self.message += 'OK\n'

        return result

    def compare_html_files(self, left: str, right: str):
        """Сравнивает html файлы.

        Args:
            left: Абсолютный путь до файла.
            right: Абсолютный путь до файла.

        Returns:
            Результат сравнения.
        """

        return self.compare_text_files(left, right, encoding='utf8')

    def compare_by_type(self, left: str, right: str, file_type: str = None) -> bool:
        """Вызывает функцию сравнения в соответствии с переданным типом.
        Если передан неизвестный тип, будет вызвано сравнение текстовых файлов.

        Args:
            left: Абсолютный путь до файла.
            right: Абсолютный путь до файла.
            file_type: Тип файла.

        Returns:
            Результат выполнения функции.
        """
        if not file_type:
            file_type = self.get_type(left)
        try:
            compare_func = self._compare_func_type_map[file_type]
        except KeyError:
            result = self.compare_text_files(left, right)
        else:
            result = compare_func(left, right)

        return result

    def compare_zip_archives(self, left: str, right: str) -> bool:
        """Сравнивает zip архивы.

        Args:
            left: Абсолютный путь до файла.
            right: Абсолютный путь до файла.

        Returns:
            Результат сравнения.
        """
        with TemporaryDirectory() as left_tmp_dir:
            with TemporaryDirectory() as right_tmp_dir:
                self._in_temporary_dir = True
                left_zip_archive = zipfile.ZipFile(left)
                left_zip_archive.extractall(left_tmp_dir)
                right_zip_archive = zipfile.ZipFile(right)
                right_zip_archive.extractall(right_tmp_dir)
                result = self.compare_dirs(left_tmp_dir, right_tmp_dir)

        return result

    def compare_dirs(self, left_dir: str, right_dir: str) -> bool:
        """Сравнивает директории по файлам без учета поддиректорий.

        Args:
            left_dir: Абсолютный путь.
            right_dir: Абсолютный путь.

        Returns:
            Результат сравнения.
        """
        left_files = sorted(os.listdir(left_dir))
        right_files = sorted(os.listdir(right_dir))

        if len(left_files) != len(right_files):
            result = False
            self.message = (
                f'Директории содержат разное количество файлов:\n'
                f'Left:  {left_files}\nRight: {right_files}\n'
            )
        elif self.compare_file_names and left_files != right_files:
            result = False
            self.message = (
                f'Директории отличаются содержанием:\n'
                f'Left:  {left_files}\nRight: {right_files}\n'
            )
        else:
            result = True
            for left, right in zip(left_files, right_files):
                self.message += f'Сравнение файлов {left} и {right}.\n'
                temp_result = self.compare_by_type(
                    os.path.join(left_dir, left),
                    os.path.join(right_dir, right),
                    self.get_type(left)
                )
                result = result and temp_result

        return result

    def get_type(self, path_name: str) -> str:
        """Получает тип файла по расширению файла.
        Если не указано расширение, возвращает TXT.

        Args:
            path_name: Путь или наименование файла

        Returns:
            Строковый тип файла.
        """
        _, extension = os.path.splitext(path_name)
        if extension:
            file_type = extension[1:].upper()
        else:
            file_type = 'TXT'

        return file_type


context_extractor_class = get_context_extractor_class()
context_extractor = context_extractor_class()
