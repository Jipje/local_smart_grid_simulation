from network_objects.Battery import Battery
from network_objects.control_strategies.NaiveControlTower import NaiveControlTower


class StrategyControlTower(NaiveControlTower):
    def __init__(self, name, network_object: Battery, verbose_lvl=3, strategy=None):
        super().__init__(name, network_object, verbose_lvl)
        self.strategy = strategy

    def determine_step(self, environment_step, action_parameters):
        charge_price = environment_step[action_parameters[0]]
        discharge_price = environment_step[action_parameters[1]]

        soc_perc = int(self.battery.state_of_charge_kwh / self.battery.max_kwh * 100)
        if self.strategy is None:
            raise NotImplementedError('You did not specify a strategy.')

        action = self.strategy.make_decision(charge_price, discharge_price, soc_perc)

        if self.verbose_lvl > 3:
            print(f'\t\t{self.strategy.name} tells the battery to {action}')

        return action, self.battery.max_kw
