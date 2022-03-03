from network_objects.Battery import Battery
from network_objects.NetworkObject import NetworkObject


class BatteryControlStrategy(NetworkObject):
    def __init__(self, name, network_object: Battery, strategy=None, verbose_lvl=3):
        super(BatteryControlStrategy, self).__init__(name)
        self.battery = network_object
        self.verbose_lvl = verbose_lvl
        self.strategy = strategy

    def take_step(self, environment_step, action_parameters) -> int:
        self.battery.take_step(environment_step, action_parameters)
        charge_price = environment_step[action_parameters[0]]
        discharge_price = environment_step[action_parameters[1]]

        soc_perc = int(self.battery.state_of_charge_kwh / self.battery.max_kwh * 100)
        if self.strategy is None:
            raise NotImplementedError('You did not specify a strategy.')
        action = self.strategy.make_decision(charge_price, discharge_price, soc_perc)
        action_kw = self.battery.take_action(action)
        return action_kw

    def done_in_mean_time(self):
        return self.battery.done_in_mean_time()

    def end_of_environment_message(self, num_of_days=None):
        return self.battery.end_of_environment_message(num_of_days)
