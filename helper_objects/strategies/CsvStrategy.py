import pandas as pd
from helper_objects.strategies.Strategy import Strategy


class CsvStrategy(Strategy):
    def __init__(self, name, strategy_csv, price_step_size=5):
        super().__init__(name, price_step_size)
        self.upload_strategy(strategy_csv)

    def update_max_and_min_price(self, strategy_df):
        assert(strategy_df['state_from'].min() == 0)
        assert(strategy_df['state_until'].max() == 100)
        highest_price = strategy_df['price_from'].drop_duplicates(keep='last').nlargest(1).iloc[0] + self.price_step_size
        lowest_price = strategy_df['price_until'].drop_duplicates(keep='last').nsmallest(1).iloc[0] - self.price_step_size

        self.max_price = highest_price
        self.min_price = lowest_price

    def upload_strategy(self, strategy_csv):
        strategy_df = pd.read_csv(strategy_csv)
        self.update_max_and_min_price(strategy_df)
        self.initialize_strategy_matrix()
        strategy_matrix = self.strategy_matrix

        for _, strategy_line in strategy_df.iterrows():
            if strategy_line.command not in ['CHARGE', 'WAIT', 'DISCHARGE']:
                raise ValueError('Strategies should only contain the following commands: CHARGE, WAIT, DISCHARGE')

            if strategy_line.price_from != 9999 and strategy_line.price_from != -9999:
                if strategy_line.price_from % 5 != 0:
                    raise ValueError('Strategies should be defined in price steps of 5. Found price: {}'.format(strategy_line.price_from))
            if strategy_line.price_until != 9999 and strategy_line.price_until != -9999:
                if strategy_line.price_until % 5 != 0:
                    raise ValueError('Strategies should be defined in price steps of 5. Found price: {}'.format(strategy_line.price_until))

            current_soc = strategy_line.state_from
            if strategy_line.state_until == 100:
                strategy_line.state_until = 101
            while current_soc < strategy_line.state_until:
                current_soc_index = current_soc
                for current_price in range(self.min_price, self.max_price + self.price_step_size, self.price_step_size):
                    current_price_index = self.price_index(current_price)
                    if strategy_line.price_from <= current_price <= strategy_line.price_until:
                        strategy_matrix[current_soc_index][current_price_index] = strategy_line.command
                current_soc += 1

        self.uploaded = True
        self.strategy_matrix = strategy_matrix
