import os

from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from helper_objects.strategies.CsvStrategy import CsvStrategy
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from helper_objects.strategies.Strategy import Strategy


def visualize_strategy(strategy: Strategy):
    strategy_matrix = strategy.strategy_matrix
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
    plt.title('{}'.format(strategy.name))
    plt.ylabel('Imbalance price')
    plt.xlabel('State of charge (SoC %)')

    legend_elements = [Patch(facecolor=red, edgecolor='black', label='CHARGE'),
                       Patch(facecolor=white, edgecolor='black', label='WAIT'),
                       Patch(facecolor=blue, edgecolor='black', label='DISCHARGE')]
    plt.legend(handles=legend_elements, loc='lower left')
    plt.imshow(strategy_matrix, extent=[0, 100, strategy.min_price, strategy.max_price], interpolation='none', origin='lower', aspect='auto')

    plt.show()

if __name__ == '__main__':
    csv_strategy_path = '..{0}..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
    csv_strategy = CsvStrategy(name='CSV Strategy', strategy_csv=csv_strategy_path, price_step_size=1)
    visualize_strategy(csv_strategy)

    point_based_strat = PointBasedStrategy('Point Based Strategy', price_step_size=1)

    point_based_strat.add_point((50, 50, 'CHARGE'))
    point_based_strat.add_point((70, 30, 'CHARGE'))
    point_based_strat.add_point((95, 0, 'CHARGE'))

    point_based_strat.add_point((40, 100, 'DISCHARGE'))
    point_based_strat.add_point((70, 80, 'DISCHARGE'))
    point_based_strat.add_point((95, 65, 'DISCHARGE'))

    point_based_strat.upload_strategy()

    visualize_strategy(point_based_strat)
