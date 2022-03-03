from network_objects.Battery import Battery
from network_objects.NetworkObject import NetworkObject


class NaiveControlTower(NetworkObject):
    def __init__(self, name, network_object: Battery, verbose_lvl=3):
        super().__init__(name)
        self.battery = network_object
        self.verbose_lvl = verbose_lvl

    def take_step(self, environment_step, action_parameters) -> int:
        self.progress_battery(environment_step, action_parameters)

        action, action_kw = self.determine_action(environment_step, action_parameters)

        action_kw = self.battery.take_action(action, action_kw)
        return action_kw

    def determine_step(self, environment_step, action_parameters) -> (str, int):
        return 'WAIT', 0

    def progress_battery(self, environment_step, action_parameters):
        charge_price = environment_step[action_parameters[0]]
        discharge_price = environment_step[action_parameters[1]]
        self.battery.update_step(charge_price, discharge_price)

    def done_in_mean_time(self):
        return self.battery.done_in_mean_time()

    def end_of_environment_message(self, num_of_days=None):
        return self.battery.end_of_environment_message(num_of_days)
