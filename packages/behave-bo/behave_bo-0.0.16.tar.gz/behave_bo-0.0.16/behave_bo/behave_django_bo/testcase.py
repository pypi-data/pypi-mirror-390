import ast
import fileinput
import json
import os
import re
import shutil
import traceback
from datetime import (
    datetime,
)
from pprint import (
    pformat,
)

from django.conf import (
    settings,
)
from django.test.testcases import (
    TestCase,
    TransactionTestCase,
)

from behave_bo.behave_django_bo.helpers import (
    context_extractor,
    filter_dict_keys,
    sort_lists_in_dict,
)
from behave_bo.behave_django_bo.loggers import (
    fix_checks_logger,
)
from behave_bo.loggers import (
    tests_logger,
)

from behave_bo.behave_django_bo.helpers import (
    FilesCompare,
)


class ReplaceChecksDataMixin:
    """Миксин добавляющий в класс тесткейса метод перезаписи данных для проверок."""

    def replace_checks_data(self, prev_frame, raw):
        """
        Заменить данные в автоматически сгенерированных проверка.

        Args:
            prev_frame: объект класса traceback.StackSummary необходимый для доступа к файлу проверок
                и номеру строки на которой выполнялся вызов метода проверки.
            raw: Данные на которые требуется произвести замену.

        """
        line_no = prev_frame.lineno + 1  # Следующая строка т.к. сами данные для проверки указываются на новой строке.

        for idx, line in enumerate(
            fileinput.input([prev_frame.filename], inplace=True),
            start=1,
        ):
            if line_no == idx:
                if re.search(': (f\'|f"|context)', line):
                    params = re.findall("(\'[a-zA-Z0-9_]+\': .*?),", line)
                    params_from_context = [param for param in params if 'context' in param]
                    error_msg = (
                        f'Проверочные данные в строке {prev_frame.lineno + 1} '
                        f'содержат переменные {params_from_context} '
                        f'и не могут быть полностью заменены данными ответа на запрос в приложение.'
                    )
                    tests_logger.error(error_msg)
                    fix_checks_logger.error(error_msg)

                    print(line, end='')
                else:
                    msg_splitter = ", msg='"
                    line = line.strip()
                    if msg_splitter in line:
                        line, end_of_line = line.split(msg_splitter)
                        end_of_line = f'{msg_splitter}{end_of_line}'
                    else:
                        end_of_line = ','

                    actual_part = ast.get_source_segment(
                        line,
                        ast.parse(line).body[0].value.elts[0],
                    )
                    new_expected_part = pformat(json.loads(raw), width=1000000)

                    new_line = f'{" " * 8}{actual_part}, {new_expected_part}{end_of_line}'
                    print(f'{new_line}')
            else:
                print(line, end='')


class AddExcludedKeysMixin:
    """Миксин добавляющий в класс тесткейса метод добавления (или дополнения существующего) excluded_keys."""

    def __init__(self):
        self.counter = 0 # счетчик количества добавленных строк в файле проверок
        super().__init__()

    def add_excluded_keys(self, prev_frame, params_to_add_to_excluded_keys):
        """
        Добавить новый или дополнить старый excluded_keys.

        Args:
            prev_frame: объект класса traceback.StackSummary необходимый для доступа к файлу проверок
                и номеру строки на которой выполнялся вызов метода проверки.
            params_to_add_to_excluded_keys: Данные на которые требуется добавить в excluded_keys.

        """
        # Следующая строка с учётом ранее добавленных строк, т.к. исключения для проверки указываются на новой строке.
        line_no = prev_frame.lineno + self.counter + 2

        for idx, line in enumerate(
            fileinput.input([prev_frame.filename], inplace=True),
            start=1,
        ):
            if line_no == idx:
                if 'excluded_keys' in line:
                    old_excluded_keys = re.search(r'excluded_keys=[\(|\[](.*?),?[\)|\]]', line).group(1)
                    if old_excluded_keys == '':
                        new_excluded_keys = params_to_add_to_excluded_keys
                    else:
                        new_excluded_keys = (
                                tuple(old_excluded_keys.replace('\'', '').replace(' ', '').split(',')) +
                                params_to_add_to_excluded_keys
                        )
                    new_line = f'{" " * 8}excluded_keys={tuple(set(list(new_excluded_keys)))},'
                else:
                    line = line.replace('\n', '')
                    new_line = f'{" " * 8}excluded_keys={params_to_add_to_excluded_keys},\n{line}'
                    self.counter += 1
                print(f'{new_line}')
            else:
                print(line, end='')


class CheckJsonWithExclusionMixin(ReplaceChecksDataMixin, AddExcludedKeysMixin):
    """Миксин добавляющий в класс тесткейса метод проверки JSON с исключением ключей."""

    files_compare_class = FilesCompare
    assertJSONEqual: callable
    runner = None
    common_excluded_keys = {
        'id',
        'pk',
    }

    def _get_content_from_current_response(self):
        """Получает содержимое текущего ответа на запрос."""
        check_func_stack_level = -3  # уровень вызова функции сравнения данных, относительно текущего уровня
        response_name = re.search(
            r'\(context\.(.*)\.context',
            traceback.extract_stack()[check_func_stack_level].line
        ).group(1)
        response = getattr(self.runner.behave_runner.context, response_name)

        try:
            response_content = json.loads(response.content)
        except json.JSONDecodeError:
            response_content = response.content.decode()

        return response_content

    def get_context_json(self, context):
        """Извлекает из контекста объект компонента и преобразует его в json-строку.

        Args:
            context: Объект списка контекстов ContextList

        Returns:
            JSON-строка.
        """
        assert context is not None, (
            f'Не удалось получить данные окна из объекта контекста. Вместо этого получен ответ:\n'
            f'{self._get_content_from_current_response()}'
        )

        component = None

        if 'window' in context:
            component = context['window']
        elif 'component' in context:
            component = context['component']

        return context_extractor.prepare_component_json(component) if component else '{}'

    def get_content_file(self, content) -> str:
        """Формирует абсолютный путь до скаченного файла

        Args:
            content: Контент ответа на запрос

        Returns:
            Строка с абсолютным путем до файла.
        """

        file_name = context_extractor.parse_download_file_name(
            content.decode('utf-8'),
            settings.DOWNLOADS_URL,
        )

        return os.path.join(settings.DOWNLOADS_DIR, file_name)

    def get_content_data_with_regex(self, content) -> str:
        """Получает из js-ответа данные с помощью регулярных выражений.

        Args:
            content: Контент ответа на запрос.

        Returns:
            JSON-строка.
        """
        content_data = context_extractor.extract_data_with_regex(content)
        if content_data:
            result = json.dumps(content_data)
        else:
            raise Exception('Regex found nothing')

        return result

    def assertFileEqual(self, context, file_download, file_compare, compare_file_names=True,
                        file_name_mask=None, current_date_in_file_name=False):
        """Проверяет утверждение что файлы совпадают

        Args:
            context: Объект контекста выполнения автотеста behave_bo.runner.Context
            file_download: Абсолютный путь до файла.
            file_compare: Относительный путь до файла.
            compare_file_names: Проверять или нет названия файлов на совпадение
            file_name_mask: Маска названия загружаемого файла
            current_date_in_file_name: Присутствует ли текущая дата в названии выгружаемого файла

        Examples:
            file_name_mask: r'Реестр_Шаблоны_видов_оплат_и_удержаний_15.07.2024_[0-9a-f]{16}.xls'

        Raises:
            AssertionError: в случае выявления различий сравниваемых файлов
        """

        def check_and_replace_current_date(file_name_mask):
            """
            Метод проверки и замены текущей даты в названии файла

            Args:
                file_name_mask: Маска названия загружаемого файла

            Returns:
                 file_name_mask: Маска названия загружаемого файла с заменой найденной даты на текущую в том же формате
            """
            now = datetime.now()
            current_date_formats = [
                "%d\\.%m\\.%Y",
                "%Y%m%d",
                "%Y\\.%m\\.%d",
            ]
            current_date_strings = [now.strftime(el) for el in current_date_formats]

            date_patterns = [
                '_?(\\d{2}\\\\.\\d{2}\\\\.20\\d{2})_',
                r'_?(20\d{2}\d{2}\d{2})_',
                '_?(20\\d{2}\\\\.\\d{2}\\\\.\\d{2})_',
            ]

            for date_str, pattern in zip(current_date_strings, date_patterns):
                matches = re.findall(pattern, file_name_mask)
                if matches:
                    file_name_mask = file_name_mask.replace(matches[0], date_str)
                    break

            return file_name_mask

        if compare_file_names:
            file_compare_name = os.path.basename(file_compare)
            file_download_name = str(file_download).split(f'{settings.DOWNLOADS_DIR}/')[1].replace('/', '_')

            if file_name_mask:
                mask_type = 'Заданный шаблон'
                if current_date_in_file_name:
                    file_name_mask = check_and_replace_current_date(file_name_mask)
                file_names_match = bool(re.match(file_name_mask, file_download_name))
            else:
                mask_type = 'Созданный шаблон'
                file_names_match = file_compare_name == file_download_name

                if not file_names_match:
                    file_compare_name = file_compare_name.replace('[', r'\[').replace(']', r'\]')
                    # Формирование маски по имени эталонного файла.
                    for hex_uuid_len in range(32, 7, -4):
                        re_hex_uuid = f'[0-9a-f]{{{hex_uuid_len}}}'
                        uuid_match = re.match(f'(.*)?({re_hex_uuid})(.*)?', file_compare_name)

                        if uuid_match:
                            file_name_mask = ''.join((uuid_match.group(1), re_hex_uuid, uuid_match.group(3)))
                            file_name_mask = file_name_mask.replace(
                                '.', r'\.').replace('(', r'\(').replace(')', r'\)')
                            if current_date_in_file_name:
                                file_name_mask = check_and_replace_current_date(file_name_mask)

                            file_names_match = bool(re.match(file_name_mask, file_download_name))
                            break
                    else:
                        file_name_mask = 'Не удалось сформировать шаблон.'

            if not file_names_match:
                error_message = (
                    f'Название полученного файла не совпадает с эталонным или не соответствуют шаблону!\n'
                    f'Полученный файл:\t{file_download_name}\n'
                    f'Эталонный файл:\t{file_compare_name}\n'
                    f'{mask_type}:\t{file_name_mask}\n'
                )
                raise AssertionError(error_message)

        compare = self.files_compare_class(table=context.table)
        _, extension = os.path.splitext(file_download)
        file_compare_path = os.path.join(context.scenario.location.dirname(), file_compare)

        if extension[1:].upper() == 'ZIP':
            result_compare = compare.compare_zip_archives(
                file_download, file_compare_path
            )
        else:
            result_compare = compare.compare_by_type(
                file_download, file_compare_path
            )

        if not result_compare:
            format_frame = traceback.format_stack()[-2]
            error_message = (
                f'{format_frame.splitlines()[0]}\n'
                f'Файл:\n'
                f'\t{file_download}\n'
                f'не совпадает по содержанию c эталонным файлом:\n'
                f'\t{file_compare_path}!\n'
                f'{compare.message}'
            )

            if self.runner.behave_config.fix_checks:
                os.remove(file_compare_path)
                shutil.copy(file_download, file_compare_path)
                tests_logger.error(error_message)
                fix_checks_logger.error(error_message)
            else:
                raise AssertionError(error_message)

    def get_sort_key(self, item):
        """Получить значения ключа для сортировки."""
        if isinstance(item, dict):
            item_list = [(key, self.get_sort_key(value)) for key, value in item.items()]
            key = sorted(item_list, key=lambda x: (x[1] is None, x))
        elif isinstance(item, list):
            item.sort(key=self.get_sort_key)
            key = item
        else:
            key = str(item)

        return key

    def check_sorted_json_equal(
        self,
        fact_data,
        expected_data,
    ) -> bool:
        """Проверяет на равенство списки и словари с отсортированными списками.

        Args:
            fact_data: Проверяемые данные.
            expected_data: Ожидаемые данные.

        Returns:
            Результат сравнения.
        """
        sorted_fact_data = sort_lists_in_dict(fact_data, sort_key=self.get_sort_key)
        sorted_expected_data = sort_lists_in_dict(expected_data, sort_key=self.get_sort_key)

        result = True
        try:
            self.assertJSONEqual(
                json.dumps(sorted_fact_data),
                sorted_expected_data,
            )
        except AssertionError:
            result = False

        return result

    def assertJSONEqualWithExclusion(
        self,
        raw: str,
        expected_data: dict,
        excluded_keys=None,
        non_excluded_keys=None,
        excluded_grid_indexes=None,
        exclude_sorting=False,
        msg=None,
    ):
        """Проверяет утверждение что сырой JSON соответствует ожидаемому словарю.

        Только при условии исключения значений соответствующих ключам
        из self.common_excluded_keys и excluded_keys
        и включения значение соответствующих ключам из non_excluded_keys.

        Args:
            raw: JSON-строка.
            expected_data: Словарь который ожидаем получить.
            excluded_keys: Список ключей для исключения.
            non_excluded_keys: Список ключей для не исключения.
            excluded_grid_indexes: Список индексов для исключения из проверки по ключу grid.
            exclude_sorting: Исключить проверку соответствия сортировки записей.
            msg: Сообщение выводимое при не прохождении проверки.
        """
        if not excluded_keys:
            excluded_keys = set()
        if not non_excluded_keys:
            non_excluded_keys = set()

        all_excluded_keys = self.common_excluded_keys.copy()
        all_excluded_keys.update(set(excluded_keys))
        all_excluded_keys = all_excluded_keys.difference(set(non_excluded_keys))

        filtered_raw = filter_dict_keys(
            json.loads(raw),
            all_excluded_keys,
        )

        expected_data = filter_dict_keys(
            expected_data,
            all_excluded_keys,
        )

        if excluded_grid_indexes:
            for index in sorted(excluded_grid_indexes, reverse=True):
                [el.pop(index) for el in filtered_raw['grid']]
                [el.pop(index) for el in expected_data['grid']]

        if exclude_sorting and filtered_raw and expected_data:
            filtered_raw = sort_lists_in_dict(filtered_raw, sort_key=self.get_sort_key)
            expected_data = sort_lists_in_dict(expected_data, sort_key=self.get_sort_key)

        error_msg = 'Данные из response не соответствуют ожидаемым!'

        if msg:
            error_msg = f'{error_msg} {msg}'

        try:
            self.assertJSONEqual(
                json.dumps(filtered_raw),
                expected_data,
                error_msg,
            )
        except Exception as exc:
            if not exclude_sorting and filtered_raw and expected_data:
                sorted_json_are_equal = False

                try:
                    sorted_json_are_equal = self.check_sorted_json_equal(
                        filtered_raw,
                        expected_data,
                    )
                except Exception as e:
                    tests_logger.error(f'Невозможно отсортировать записи для проверки различия сортировки: {e}')

                if sorted_json_are_equal:
                    error_msg += ' ОТЛИЧАЕТСЯ СОРТИРОВКА!'

            format_frame = traceback.format_stack()[-2]
            tests_logger.error(f'{error_msg}\n{format_frame.splitlines()[0]}')

            if self.runner.behave_config.fix_checks:
                exc_lines = "\n".join(
                    line for line in str(exc).split('\n')
                    if any(line.strip().startswith(char) for char in ('?', '+', '-'))
                )

                tests_logger.error(f'\n{exc_lines}')
                fix_checks_logger.error(f'{error_msg}\n{format_frame.splitlines()[0]}\n{exc_lines}\n')

                prev_frame = traceback.extract_stack()[-2]
                self.replace_checks_data(prev_frame, raw)
            elif self.runner.behave_config.fix_excluded_keys:
                params_to_add_to_excluded_keys = tuple(
                    key for key in self.runner.behave_config.fix_excluded_keys.split(',')
                )
                tests_logger.error(f'\nКлючи для добавления в excluded_keys: {params_to_add_to_excluded_keys}')

                fix_checks_logger.error(f'fix_excluded_keys: {error_msg}\n{format_frame.splitlines()[0]}\n'
                                        f'Ключи для добавления в excluded_keys: {params_to_add_to_excluded_keys}\n')

                prev_frame = traceback.extract_stack()[-2]
                self.add_excluded_keys(prev_frame, params_to_add_to_excluded_keys)
            else:
                raise exc


class BehaveTestCase(CheckJsonWithExclusionMixin, TestCase):

    live_server_url = '127.0.0.0'
    runner = None


class BehaveTransactionTestCase(CheckJsonWithExclusionMixin, TransactionTestCase):

    live_server_url = '127.0.0.0'

    def _fixture_setup(self):
        pass

    def _fixture_teardown(self):
        pass
