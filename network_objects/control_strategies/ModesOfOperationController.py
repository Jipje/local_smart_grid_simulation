from network_objects.Battery import Battery
from network_objects.NetworkObject import NetworkObject
from network_objects.control_strategies.NaiveControlTower import NaiveControlTower
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


class ModesOfOperationController(NaiveControlTower):
    def __init__(self, name, network_object: Battery, verbose_lvl=3):
        super().__init__(name, network_object)
        self.battery = network_object
        self.verbose_lvl = verbose_lvl

        self.controllers = []
        self.timings = [dt.time(0, 0, tzinfo=utc)]

    def add_mode_of_operation(self, start_time, control_strategy:NaiveControlTower):
        try:
            assert start_time > self.timings[len(self.timings) - 1]
        except AssertionError:
            raise AttributeError('Start times of modes of operation should be add incrementally')

        try:
            assert start_time < dt.time(23, 59, tzinfo=utc)
        except AssertionError:
            raise AttributeError('This modes of operation controller only handles a single day')

        self.controllers.append(control_strategy)
        self.timings.append(start_time)

    def determine_step(self, environment_step, action_parameters) -> (str, int):
        current_datetime = environment_step[action_parameters[3]]
        current_time = dt.time(current_datetime.hour, current_datetime.minute, tzinfo=utc)
        chosen_controller = self.controllers[len(self.controllers) - 1]

        for i in range(len(self.timings)):
            timing_counter = self.timings[i]
            if current_time < timing_counter:
                chosen_controller = self.controllers[i - 1]
                break

        return chosen_controller.determine_step(environment_step, action_parameters)
