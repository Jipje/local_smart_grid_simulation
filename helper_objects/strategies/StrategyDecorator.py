from helper_objects.strategies.Strategy import Strategy


class StrategyDecorator(Strategy):
    def __init__(self, base_strategy: Strategy, name):
        super().__init__(name)
        self.base_strategy = base_strategy

    def price_index(self, price):
        return self.base_strategy.price_index(price)

    def clean_price(self, price, discharge_price=True):
        return self.base_strategy.clean_price(price, discharge_price)

    def initialize_strategy_matrix(self):
        return self.base_strategy.initialize_strategy_matrix()

    def upload_strategy(self, args):
        pass

    def make_decision(self, charge_price, discharge_price, state_of_charge_perc: int):
        return self.base_strategy.make_decision(charge_price, discharge_price, state_of_charge_perc)
