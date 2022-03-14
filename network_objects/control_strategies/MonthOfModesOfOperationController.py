from network_objects.Battery import Battery
from network_objects.control_strategies.NaiveControlTower import NaiveControlTower
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


class MonthOfModesOfOperationController(NaiveControlTower):
    def __init__(self, name, network_object: Battery, verbose_lvl=3):
        super().__init__(name, network_object)
        self.battery = network_object
        self.verbose_lvl = verbose_lvl

        self.controllers = []
        self.ready = False

    def add_controller(self, control_strategy: NaiveControlTower):
        self.controllers.append(control_strategy)
        if len(self.controllers) > 12:
            raise AttributeError('MonthOfModesOfOperationController can only take 12 controllers, one for each month')
        if len(self.controllers) == 12:
            self.ready = True

    def determine_step(self, environment_step, action_parameters) -> (str, int):
        if not self.ready:
            raise AttributeError('Please add 12 control strategies before calling this ControlTower')

        current_datetime = environment_step[action_parameters[3]]
        current_month = current_datetime.month
        chosen_controller = self.controllers[current_month - 1]

        return chosen_controller.determine_step(environment_step, action_parameters)
