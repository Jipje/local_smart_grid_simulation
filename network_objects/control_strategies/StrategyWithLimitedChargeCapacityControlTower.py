from network_objects.Battery import Battery
from network_objects.control_strategies.StrategyControlTower import StrategyControlTower


class StrategyWithLimitedChargeCapacityControlTower(StrategyControlTower):
    def __init__(self, name, network_object: Battery, verbose_lvl=3, strategy=None):
        super().__init__(name, network_object, verbose_lvl, strategy)

    def take_step(self, environment_step, action_parameters) -> int:
        self.progress_battery(environment_step, action_parameters)

        action, action_kw = self.determine_step(environment_step, action_parameters)

        action_kw = self.battery.take_action(action, action_kw)
        return action_kw

    def determine_step(self, environment_step, action_parameters):
        strategy_action, strategy_action_kw = StrategyControlTower.determine_step(self, environment_step, action_parameters)

        adjusted_action_kw = strategy_action_kw
        if strategy_action == 'CHARGE':
            max_charge_kw = environment_step[action_parameters[2]]
            if strategy_action_kw > max_charge_kw:
                adjusted_action_kw = max_charge_kw

        return strategy_action, adjusted_action_kw
