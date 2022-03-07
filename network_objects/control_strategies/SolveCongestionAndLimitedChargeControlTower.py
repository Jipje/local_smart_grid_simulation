from network_objects.Battery import Battery
from network_objects.control_strategies.StrategyControlTower import StrategyControlTower
from network_objects.control_strategies.SolveCongestionControlTower import SolveCongestionControlTower
from network_objects.control_strategies.StrategyWithLimitedChargeCapacityControlTower import StrategyWithLimitedChargeCapacityControlTower


class SolveCongestionAndLimitedChargeControlTower(StrategyControlTower):
    def __init__(self, name, network_object: Battery, congestion_kw, congestion_safety_margin=0.95, charging_limitation_kw=0, verbose_lvl=3, strategy=None):
        super().__init__(name, network_object, verbose_lvl, strategy)

        self.congestion_kw = abs(congestion_kw)
        self.congestion_safety_margin = congestion_safety_margin
        self.charging_limitation_kw = abs(charging_limitation_kw)

        self.limited_charge = StrategyWithLimitedChargeCapacityControlTower(name, network_object, verbose_lvl=verbose_lvl, strategy=strategy)
        self.solve_congestion = SolveCongestionControlTower(name, network_object, verbose_lvl=verbose_lvl, strategy=strategy, congestion_kw=congestion_kw, congestion_safety_margin=congestion_safety_margin)

    def determine_step(self, environment_step, action_parameters):
        # Limited charge returns the original strategy action but adjusts the charge action the limited amount
        limited_charge_action, limited_charge_action_kw = self.limited_charge.determine_step(environment_step, action_parameters)

        # Solve congestion changes the original strategy action to handle congestion
        # in cases where there is congestion there is always enough power to charge.
        solve_congestion_action, solve_congestion_action_kw = self.solve_congestion.determine_step(environment_step, action_parameters)

        adjusted_action = solve_congestion_action
        adjusted_action_kw = solve_congestion_action_kw

        if solve_congestion_action == 'CHARGE' and limited_charge_action == 'CHARGE':
            adjusted_action = solve_congestion_action
            adjusted_action_kw = min(limited_charge_action_kw, solve_congestion_action_kw)

        return adjusted_action, adjusted_action_kw
