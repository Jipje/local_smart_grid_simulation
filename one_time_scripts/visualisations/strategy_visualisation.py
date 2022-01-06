import os
from helper_objects.StrategyBattery import StrategyBattery
import matplotlib.pyplot as plt

if __name__ == '__main__':
    strategy_one_path = '..{0}..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
    strategy_one = StrategyBattery(strategy_csv=strategy_one_path)
    print(strategy_one)
    strategy_matrix = strategy_one.strategy_matrix
    red = (239, 71, 111)
    blue = (33, 137, 126)
    white = (250, 250, 250)

    for row_index in range(len(strategy_matrix)):
        row = strategy_matrix[row_index]
        for column_index in range(len(row)):
            item = row[column_index]

            new_item = white
            if item == 'CHARGE':
                new_item = red
            elif item == 'DISCHARGE':
                new_item = blue

            strategy_matrix[row_index][column_index] = new_item

    plt.xlabel('Imbalance price')
    plt.ylabel('State of charge (SoC %)')
    plt.imshow(strategy_matrix, interpolation='none')

    plt.show()
