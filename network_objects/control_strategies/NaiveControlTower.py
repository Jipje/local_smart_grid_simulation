from network_objects.Battery import Battery
from network_objects.NetworkObject import NetworkObject


class NaiveControlTower(NetworkObject):
    def __init__(self, name, network_object: Battery, verbose_lvl=3):
        super().__init__(name)
        self.battery = network_object
        self.verbose_lvl = verbose_lvl

    def take_step(self, environment_step, action_parameters) -> int:
        charge_price = environment_step[action_parameters[0]]
        discharge_price = environment_step[action_parameters[1]]
        self.battery.update_step(charge_price, discharge_price)
        return 0

    def done_in_mean_time(self):
        return self.battery.done_in_mean_time()

    def end_of_environment_message(self, num_of_days=None):
        return self.battery.end_of_environment_message(num_of_days)
