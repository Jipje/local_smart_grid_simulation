from helper_objects.strategies.Strategy import Strategy
from helper_objects.strategies.StrategyDecorator import StrategyDecorator


class DischargeUntilStrategy(StrategyDecorator):
    def __init__(self, base_strategy: Strategy, name, discharge_until_soc_perc):
        super().__init__(base_strategy, name)
        self.discharge_until_soc_perc = discharge_until_soc_perc

    def make_decision(self, charge_price, discharge_price, state_of_charge_perc: int):
        base_decision = self.base_strategy.make_decision(charge_price, discharge_price, state_of_charge_perc)

        overwrite_decision = base_decision
        if state_of_charge_perc > self.discharge_until_soc_perc:
            overwrite_decision = 'DISCHARGE'

        return overwrite_decision
