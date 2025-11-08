from behave_bo.behave_django_bo.plugins.base import (
    Plugin,
)
from behave_bo.loggers import (
    tests_logger,
)


class OverrideSettingsPlugin(Plugin):
    """Указание значений параметров django settings для последующего переопределения при выполнении автотестов.

    $ behave --all --plugins override_settings --plugin_vars override_settings_PRODUCTION_REQUEST_LOG_SERVER=False
    """

    def __init__(self, *args, **kwargs):
        self.override_settings_dict = {}

        for key, value in kwargs.items():
            if value.isdigit():
                value = int(value)
            elif value.upper() in ('TRUE', "FALSE"):
                value = value.upper() == 'TRUE'

            self.override_settings_dict[key] = value

        tests_logger.info(f'Будут переопределены django settings: {self.override_settings_dict}')

    def before_all(self, context):
        context._runner.override_settings_dict = self.override_settings_dict


plugin_class = OverrideSettingsPlugin
