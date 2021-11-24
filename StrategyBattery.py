import pandas as pd


class StrategyBattery(object):
    def __init__(self, strategy_csv='data/strategies/simplified_passive_imbalance_1.csv'):
        self.dayhead_tracker = False
        self.uploaded = False
        self.strategy_matrix = []
        self.upload_strategy(strategy_csv)
        self.max_price = -9999
        self.min_price = 9999

    def upload_strategy(self, strategy_csv):
        strategy_df = pd.read_csv(strategy_csv)
        print(strategy_df.to_string())
        assert(strategy_df['state_from'].min() == 0)
        assert(strategy_df['state_until'].max() == 100)
        highest_price = strategy_df['price_from'].drop_duplicates(keep='last').nlargest(2).iloc[1] + 5
        lowest_price = strategy_df['price_until'].drop_duplicates(keep='last').nsmallest(2).iloc[1]

        self.max_price = highest_price
        self.min_price = lowest_price

        num_of_price_buckets = int((highest_price - lowest_price) / 5)
        strategy_matrix = []
        for i in range(100):
            strategy_matrix.append([])
            for _ in range(num_of_price_buckets):
                strategy_matrix[i].append('WAIT')

        for _, strategy_line in strategy_df.iterrows():
            current_soc = strategy_line.state_from
            while current_soc < strategy_line.state_until:
                current_soc_index = current_soc
                for current_price in range(lowest_price, highest_price, 5):
                    if strategy_line.price_from <= current_price <= strategy_line.price_until:
                        current_price_index = int(current_price / 5)
                        strategy_matrix[current_soc_index][current_price_index] = strategy_line.command
                current_soc += 1

        self.uploaded = True
        self.strategy_matrix = strategy_matrix

    def clean_price(self, price):
        res = price
        if price > self.max_price:
            res = self.max_price
        elif price < self.min_price:
            res = self.min_price
        return res

    def make_decision(self, charge_price, discharge_price, state_of_charge):
        if not(self.uploaded):
            raise LookupError("A STRATEGY HAS NOT BEEN UPLOADED")

        charge_price = self.clean_price(charge_price)
        discharge_price = self.clean_price(discharge_price)

        soc_index = int(state_of_charge)
        charge_price_index = int(charge_price / 5)
        discharge_price_index = int(discharge_price / 5)

        charge_check_decision = self.strategy_matrix[soc_index][charge_price_index]
        if charge_check_decision == 'DISCHARGE':
            charge_check_decision = 'WAIT'
        discharge_check_decision = self.strategy_matrix[soc_index][discharge_price_index]
        if discharge_check_decision == 'CHARGE':
            discharge_check_decision = 'WAIT'

        decision = 'WAIT'
        if charge_check_decision == 'WAIT' and discharge_check_decision == 'WAIT':
            decision = 'WAIT'
        elif charge_check_decision == 'CHARGE' and discharge_check_decision == 'WAIT':
            decision = 'CHARGE'
        elif charge_check_decision == 'WAIT' and discharge_check_decision == 'DISCHARGE':
            decision = 'DISCHARGE'
        else:
            raise Exception('THIS SHOULD BE IMPOSSIBLE')

        return decision




