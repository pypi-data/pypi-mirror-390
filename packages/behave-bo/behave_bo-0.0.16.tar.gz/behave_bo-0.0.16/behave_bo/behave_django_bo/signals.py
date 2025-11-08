from django.dispatch import (
    Signal,
)


skip_request_check_signal = Signal()
after_step_plugins = Signal(providing_args=['context', 'step'])
after_scenario_signal = Signal(providing_args=['context', 'scenario'])
