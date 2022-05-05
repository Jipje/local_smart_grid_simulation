class Strategy(object):
    def __init__(self, name, price_step_size=5):
        self.name = name

        self.price_step_size = price_step_size
        self.max_price = -9999
        self.min_price = 9999

        self.strategy_matrix = []
        self.uploaded = False

        self.dayahead_tracker = False

    def price_index(self, price) -> int:
        price = self.clean_price(price)
        price = price - self.min_price
        price_index = price / self.price_step_size
        price_index = int(price_index)
        return price_index

    def clean_price(self, price, discharge_price=True) -> int:
        if price % self.price_step_size == 0:
            res = price
        else:
            if discharge_price:
                res = price - price % self.price_step_size
            else:
                res = price + self.price_step_size - (price % self.price_step_size)

        if price > self.max_price:
            res = self.max_price
        elif price < self.min_price:
            res = self.min_price
        res = int(round(res, 0))
        return res

    def initialize_strategy_matrix(self):
        num_of_price_buckets = int((self.max_price - self.min_price) / self.price_step_size)
        strategy_matrix = []
        for i in range(100 + 1):
            strategy_matrix.append([])
            for _ in range(num_of_price_buckets + 1):
                strategy_matrix[i].append('WAIT')
        self.strategy_matrix = strategy_matrix

    def upload_strategy(self, args):
        """The upload method of a strategy is determined by the strategy itself."""
        pass

    def make_decision(self, charge_price, discharge_price, state_of_charge_perc: int):
        if not self.uploaded:
            raise ValueError('Strategy has not yet been uploaded')

        charge_price = self.clean_price(charge_price, discharge_price=False)
        discharge_price = self.clean_price(discharge_price, discharge_price=True)
        charge_price_index = self.price_index(charge_price)
        discharge_price_index = self.price_index(discharge_price)

        if state_of_charge_perc > 100 or state_of_charge_perc < 0:
            raise ValueError("A SoC percentage was expected. Please offer a value between or equal to 0 and 100")
        soc_index = int(state_of_charge_perc)

        charge_check_decision = self.strategy_matrix[soc_index][charge_price_index]
        discharge_check_decision = self.strategy_matrix[soc_index][discharge_price_index]
        # In R2 situations the charge price could want the battery to discharge
        if charge_check_decision == 'DISCHARGE':
            charge_check_decision = 'WAIT'
        # And vice-versa
        if discharge_check_decision == 'CHARGE':
            discharge_check_decision = 'WAIT'

        decision = None
        if charge_check_decision == 'WAIT' and discharge_check_decision == 'WAIT':
            decision = 'WAIT'
        elif charge_check_decision == 'CHARGE' and discharge_check_decision == 'WAIT':
            decision = 'CHARGE'
        elif charge_check_decision == 'WAIT' and discharge_check_decision == 'DISCHARGE':
            decision = 'DISCHARGE'
        elif charge_check_decision == 'CHARGE' and discharge_check_decision == 'DISCHARGE':
            if state_of_charge_perc > 50:
                decision = 'DISCHARGE'
            else:
                decision = 'CHARGE'

        return decision
