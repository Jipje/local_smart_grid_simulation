from network_objects.Battery import Battery
from network_objects.control_strategies.StrategyControlTower import StrategyControlTower
from network_objects.control_strategies.SolveCongestionControlTower import SolveCongestionControlTower
from network_objects.control_strategies.StrategyWithLimitedChargeCapacityControlTower import StrategyWithLimitedChargeCapacityControlTower


class SolveCongestionAndLimitedChargeControlTower(StrategyControlTower):
    def __init__(self, name, network_object: Battery, congestion_kw, congestion_safety_margin=0.95,
                 verbose_lvl=3, strategy=None, transportation_kw=0):
        super().__init__(name, network_object, verbose_lvl, strategy)

        self.congestion_kw = abs(congestion_kw)
        self.congestion_safety_margin = congestion_safety_margin

        if transportation_kw > congestion_kw:
            raise AttributeError('transportation_kw must be smaller than or equal to congestion_kw'
                                 f'However {transportation_kw}kW is larger than {congestion_kw}')

        self.limited_charge = StrategyWithLimitedChargeCapacityControlTower(name, network_object, verbose_lvl=verbose_lvl, strategy=strategy, transportation_kw=transportation_kw)
        self.solve_congestion = SolveCongestionControlTower(name, network_object, verbose_lvl=verbose_lvl, strategy=strategy, congestion_kw=congestion_kw, congestion_safety_margin=congestion_safety_margin)

    def determine_step(self, environment_step, action_parameters):
        # Limited charge returns the original strategy action but adjusts the charge action the limited amount
        limited_charge_action, limited_charge_action_kw = self.limited_charge.determine_step(environment_step, action_parameters)

        # Solve congestion changes the original strategy action to handle congestion
        # in cases where there is congestion there is always enough power to charge.
        solve_congestion_action, solve_congestion_action_kw = self.solve_congestion.determine_step(environment_step, action_parameters)

        adjusted_action = solve_congestion_action
        adjusted_action_kw = solve_congestion_action_kw

        # When they both say charge, we overwrite the action with the adjusted amount from limited charge
        if solve_congestion_action == 'CHARGE' and limited_charge_action == 'CHARGE':
            adjusted_action = solve_congestion_action
            adjusted_action_kw = min(limited_charge_action_kw, solve_congestion_action_kw)

        return adjusted_action, adjusted_action_kw
