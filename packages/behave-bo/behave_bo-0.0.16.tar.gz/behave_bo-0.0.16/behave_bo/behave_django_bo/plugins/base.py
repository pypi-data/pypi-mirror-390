import functools
import importlib

from django.conf import (
    settings,
)

from behave_bo.loggers import (
    tests_logger,
)


class RunnerPluginsMixin:

    plugins = {}

    def get_plugins_packages(self):
        return [
            'behave_bo.behave_django_bo.plugins'
        ]

    def setup_plugins(self, behave_args, options):
        """Подключает плагины.

        Args:
            behave_args: Аргументы, относящиеся к behave_bo.
            options: Все аргументы команды запуска.

        """
        if options['plugins']:
            plugins_with_options = self._get_plugins_options(
                options['plugins'],
                options['plugin_vars'],
            )
            self._setup_plugins(
                plugins_with_options,
                options['disable_failed_plugin'],
            )

            for plugin_name, plugin_object in self.plugins.items():
                if hasattr(plugin_object, 'before_run'):
                    result = plugin_object.before_run()
                    behave_args.extend(result)

    def _setup_plugins(self, plugins_with_options, skip_if_failed=False):
        """Получает классы плагинов и инициализирует их с соответствующими параметрами.

        Args:
            plugins_options: dict. Словарь плагинов с параметрами.
            skip_if_failed: bool. Пропускать подключение при ошибке(не вызывать ошибку).

        """
        for plugin, options in plugins_with_options.items():
            import_errors = []
            plugin_class = None

            for package in self.get_plugins_packages():
                try:
                    plugin_module = importlib.import_module(f'{package}.{plugin}')
                    plugin_class = getattr(plugin_module, 'plugin_class')
                    break
                except ImportError as e:
                    import_errors.append(e)

            if plugin_class:
                try:
                    self.plugins[plugin] = plugin_class(**options)
                except Warning as w:
                    tests_logger.warning(w)
                except Exception as e:
                    if skip_if_failed:
                        tests_logger.warning(f"Can't import and setup plugin {plugin} due to {e}")
                    else:
                        tests_logger.fatal(f"Can't import and setup plugin {plugin} due to: {e}")
                        exit(-1)
            elif import_errors:
                if skip_if_failed:
                    tests_logger.warning(f"Can't import plugin '{plugin}':\n{import_errors}")
                else:
                    raise ImportError(f"Can't import plugin '{plugin}':\n{import_errors}")


    @staticmethod
    def _get_plugins_options(plugins, plugins_vars):
        """Получает опции плагинов из параметров командной строки.

        Args:
            plugins: str. Плагины.
            plugins_vars: Опции плагинов.

        Returns:
            dict. Словарь вида (наименование плагина: опции плагина).

        """
        plugin_list = plugins.split(',')
        plugins_dict = {name: {} for name in plugin_list}

        if plugins_vars:
            plugin_vars_list = plugins_vars.split(',')
            for plugin in plugin_list:
                for plugin_var in plugin_vars_list:
                    if plugin_var.startswith(f'{plugin}_'):
                        plugin_var = plugin_var.removeprefix(f'{plugin}_')
                        try:
                            key, value = plugin_var.split('=')
                        except ValueError:
                            key, value = plugin_var, True
                        plugins_dict[plugin][key] = value

        return plugins_dict


class PluginException(Exception):
    pass


class PluginWarning(Warning):
    pass


class Plugin:

    REQUIRED_SETTINGS = []

    def before_all(self, context):
        pass

    def before_feature(self, context, feature):
        pass

    def before_scenario(self, context, scenario):
        pass

    def before_step(self, context, step):
        pass

    def after_step(self, context, step):
        pass

    def after_scenario(self, context, scenario):
        pass

    def after_feature(self, context, feature):
        pass

    def after_all(self, context):
        pass

    def check_required_settings(self):
        """Проверяет необходимые настройки для плагина.

        Raises:
            PluginException: при отсутствии настроек self.REQUIRED_SETTINGS.

        """
        missing_settings = []

        for setting_name in self.REQUIRED_SETTINGS:
            if not hasattr(settings, setting_name):
                missing_settings.append(setting_name)

        if missing_settings:
            raise PluginException(
                f'{self.__class__.__name__} requires settings: {", ".join(missing_settings)}.'
            )


def apply_plugins(plugins_dict, hook_name, *args, **kwargs):
    for plugin_name, plugin_object in plugins_dict.items():
        try:
            plugin_action = getattr(plugin_object, hook_name)
            plugin_action(*args, **kwargs)
        except AssertionError as e:
            raise e
        except Exception as e:
            tests_logger.warning(f'Plugin action "{plugin_name}" failed due to {e}')


def use_plugins(hook):
    """Декоратор для запуска hook'ов в классе плагина.

    """
    @functools.wraps(hook)
    def wrapper(self, *args, **kwargs):
        context = args[0]
        plugins = context.config.django_test_runner.plugins

        if hook.__name__.startswith('before_'):
            # Если это before-хук, сначала выполняем код из плагинов, а после него код хука.
            apply_plugins(plugins, hook.__name__, *args, **kwargs)

        result = hook(self, *args, **kwargs)

        if hook.__name__.startswith('after_'):
            # Если это after-хук, сначала выполняем код хука, а после него код из плагинов.
            apply_plugins(plugins, hook.__name__, *args, **kwargs)

        return result

    return wrapper
