import re

from django.db.backends import (
    utils,
)
from django.db.backends.postgresql import (
    base,
)


changed_tables = set()


class CursorWrapper(utils.CursorWrapper):
    """
    Враппер курсора БД для получения информации об операция вставки в таблицы
    """
    sql_insert_operator = "INSERT INTO"
    re_pattern = re.compile(f'{sql_insert_operator} "?(.*?)"? .+', re.U | re.I)

    def execute(self, sql, params=None):
        if self.sql_insert_operator in sql.upper():
            result = self.re_pattern.search(sql)
            if result:
                changed_tables.add(result[1])

        return super().execute(sql, params)


class DatabaseWrapper(base.DatabaseWrapper):

    def cursor(self):
        self.validate_thread_sharing()
        cursor = CursorWrapper(self._cursor(), self)

        return cursor
