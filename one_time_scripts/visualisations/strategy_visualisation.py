import os
from helper_objects.StrategyBattery import StrategyBattery
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

if __name__ == '__main__':
    strategy_one_path = '..{0}..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
    strategy_one = StrategyBattery(name='TESTING', strategy_csv=strategy_one_path, price_step_size=1)
    print(strategy_one)
    strategy_matrix = strategy_one.strategy_matrix
    red = (0.934, 0.277, 0.434)
    blue = (0.129, 0.535, 0.492)
    white = (1, 1, 1)

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

    strategy_matrix = [*zip(*strategy_matrix)]
    plt.title('Strategy One')
    plt.ylabel('Imbalance price')
    plt.xlabel('State of charge (SoC %)')

    legend_elements = [Patch(facecolor=red, edgecolor='black', label='CHARGE'),
                       Patch(facecolor=white, edgecolor='black', label='WAIT'),
                       Patch(facecolor=blue, edgecolor='black', label='DISCHARGE')]
    plt.legend(handles=legend_elements, loc='lower left')
    plt.imshow(strategy_matrix, interpolation='none', origin='lower')

    plt.show()
