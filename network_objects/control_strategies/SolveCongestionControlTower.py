from network_objects.Battery import Battery
from network_objects.control_strategies.StrategyControlTower import StrategyControlTower


class SolveCongestionControlTower(StrategyControlTower):
    def __init__(self, name, network_object: Battery, congestion_kw, congestion_safety_margin=0.95, verbose_lvl=3, strategy=None):
        super().__init__(name, network_object, verbose_lvl, strategy)

        self.congestion_kw = abs(congestion_kw)
        self.congestion_safety_margin = congestion_safety_margin

    def determine_step(self, environment_step, action_parameters):
        strategy_action, strategy_action_kw = StrategyControlTower.determine_step(self, environment_step, action_parameters)

        excess_power = self.congestion_safety_margin * self.congestion_kw - environment_step[action_parameters[2]]

        adjusted_action = strategy_action
        adjusted_action_kw = strategy_action_kw

        # Check if there is congestion
        if excess_power < 0:
            # We cannot discharge or wait as there is excess power causing congestion.
            if strategy_action == 'DISCHARGE' or strategy_action == 'WAIT':
                # This control tower will solve that congestion by charging the excess power
                adjusted_action = 'CHARGE'
                adjusted_action_kw = abs(excess_power)
        # If there is no excess power and the battery wants to discharge, we need to make sure we don't cause congestion
        elif adjusted_action == 'DISCHARGE':
            adjusted_action_kw = abs(excess_power)

        return adjusted_action, adjusted_action_kw
