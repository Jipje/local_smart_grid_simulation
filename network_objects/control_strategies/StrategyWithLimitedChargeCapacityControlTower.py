from network_objects.Battery import Battery
from network_objects.control_strategies.StrategyControlTower import StrategyControlTower


class StrategyWithLimitedChargeCapacityControlTower(StrategyControlTower):
    def __init__(self, name, network_object: Battery, verbose_lvl=3, strategy=None, transportation_kw=0):
        super().__init__(name, network_object, verbose_lvl, strategy)
        if transportation_kw < 0:
            raise AttributeError('transportation_kw should be larger than 0')
        self.transportation_kw = transportation_kw

    def determine_step(self, environment_step, action_parameters):
        strategy_action, strategy_action_kw = StrategyControlTower.determine_step(self, environment_step, action_parameters)

        adjusted_action_kw = strategy_action_kw
        if strategy_action == 'CHARGE':
            max_charge_kw = environment_step[action_parameters[2]] + self.transportation_kw
            if strategy_action_kw > max_charge_kw:
                adjusted_action_kw = max_charge_kw

            if self.verbose_lvl > 3:
                if self.transportation_kw > 0:
                    print(f'\t\tLimited charge controller limits {strategy_action} to {adjusted_action_kw}kW. '
                          f'{self.transportation_kw}kW transportation authorized.')
                else:
                    print(f'\t\tLimited charge controller limits {strategy_action} to {adjusted_action_kw}kW')

        return strategy_action, adjusted_action_kw
