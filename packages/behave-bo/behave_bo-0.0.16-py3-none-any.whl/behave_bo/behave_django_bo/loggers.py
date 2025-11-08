import logging
import os
import uuid

from behave_bo.loggers import (
    tests_logger,
)
from django.conf import (
    settings,
)


class FixChecksLogger:
    """Контекстный менеджер, выполняющий настройку логирования в файл при исправлении данных в проверках.

    Attributes:
        enable: Булевый флаг. Если True - будет выполнена настройка логгера и вывод в консоль при выходе.
        log_file_path: Путь к лог-файлу.
    """
    logger_name = 'fix_checks_logger'

    def __init__(self, enable: bool):
        """Инициализация FixChecksLogger."""
        self.enable = enable
        self.log_file_path = (
            os.path.join(settings.DOWNLOADS_DIR, f'fix_checks_{str(uuid.uuid4())[:8]}.txt')
        )

    def __enter__(self):
        if self.enable:
            self._setup_logger()
            tests_logger.info(f'Исправления по тегу --fix-checks будут сохранены в {self.log_file_path}.\n')

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.enable:
            if os.path.exists(self.log_file_path):
                message = (
                    f'Файл с изменениями по тегу --fix-checks сохранён в {self.log_file_path}\n'
                    f'Данный файл необходимо приложить в PR задачи!!!\n'
                )
            else:
                message = 'Исправлений по тегу --fix-checks не внесено. Файл не создан.\n'

            tests_logger.info(message)

    def _setup_logger(self):
        """Выполняет настройку логгера."""
        log_setup = logging.getLogger(self.logger_name)
        formatter = logging.Formatter(
            fmt='%(levelname)s: %(asctime)s %(message)s',
            datefmt='%m/%d/%Y %I:%M:%S %p',
        )
        filehandler = logging.FileHandler(
            self.log_file_path,
            mode='a',
            delay=True,
        )
        filehandler.setFormatter(formatter)
        log_setup.setLevel(logging.ERROR)
        log_setup.addHandler(filehandler)


fix_checks_logger = logging.getLogger(FixChecksLogger.logger_name)
