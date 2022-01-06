import os
from helper_objects.StrategyBattery import StrategyBattery

if __name__ == '__main__':
    strategy_one_path = '..{0}..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
    strategy_one = StrategyBattery(strategy_csv=strategy_one_path)
    print(strategy_one)
