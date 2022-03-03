from network_objects.Battery import Battery


class ControlStrategy(object):
    def __init__(self, network_object: Battery, strategy=None, verbose_lvl=3):
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
