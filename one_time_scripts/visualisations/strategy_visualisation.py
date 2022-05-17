import os

from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from helper_objects.strategies.CsvStrategy import CsvStrategy
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from helper_objects.strategies.Strategy import Strategy


def visualize_strategies(strategies):
    counter = 0

    for strategy in strategies:
        counter += 1
        if counter == len(strategies):
            opacity = 0.4
        else:
            opacity = 0.2
        strategy_matrix = [row[:] for row in strategy.strategy_matrix]
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
        plt.imshow(strategy_matrix, extent=[0, 100, strategy.min_price, strategy.max_price], interpolation='none',
                   origin='lower', aspect='auto', alpha=opacity)

    plt.title('{}'.format(strategy.name))
    plt.ylabel('Imbalance price')
    plt.xlabel('State of charge (SoC %)')

    legend_elements = [Patch(facecolor=red, edgecolor='black', label='CHARGE'),
                       Patch(facecolor=white, edgecolor='black', label='WAIT'),
                       Patch(facecolor=blue, edgecolor='black', label='DISCHARGE')]
    plt.legend(handles=legend_elements, loc='lower left')

    plt.show()


def visualize_strategy(strategy: Strategy):
    strategy_matrix = [row[:] for row in strategy.strategy_matrix]
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
    csv_strategy = CsvStrategy(name='Rhino Strategy 1', strategy_csv=csv_strategy_path, price_step_size=1)
    visualize_strategy(csv_strategy)

    csv_strategy_path = '..{0}..{0}data{0}strategies{0}always_discharge.csv'.format(os.path.sep)
    csv_strategy = CsvStrategy(name='Always discharge strategy', strategy_csv=csv_strategy_path, price_step_size=1)
    visualize_strategy(csv_strategy)

    point_based_strat = PointBasedStrategy('200k december strategy', price_step_size=2)

    point_based_strat.add_point((47, 280, 'CHARGE'))
    point_based_strat.add_point((70, 258, 'CHARGE'))
    point_based_strat.add_point((79, 46, 'CHARGE'))
    point_based_strat.add_point((84, 42, 'CHARGE'))

    point_based_strat.add_point((37, 512, 'DISCHARGE'))
    point_based_strat.add_point((52, 302, 'DISCHARGE'))
    point_based_strat.add_point((82, 222, 'DISCHARGE'))
    point_based_strat.add_point((95, -8, 'DISCHARGE'))

    point_based_strat.upload_strategy()

    visualize_strategy(point_based_strat)

    point_based_strat = PointBasedStrategy('Random strategy', price_step_size=11)

    point_based_strat.add_point((50, 55, 'CHARGE'))
    point_based_strat.add_point((60, 33, 'CHARGE'))
    point_based_strat.add_point((70, 44, 'CHARGE'))
    point_based_strat.add_point((95, 0, 'CHARGE'))

    point_based_strat.add_point((40, 99, 'DISCHARGE'))
    point_based_strat.add_point((60, 88, 'DISCHARGE'))
    point_based_strat.add_point((70, 77, 'DISCHARGE'))
    point_based_strat.add_point((95, 66, 'DISCHARGE'))

    point_based_strat.upload_strategy()

    visualize_strategy(point_based_strat)

    for i in range(1, 4):
        point_based_strat = PointBasedStrategy('Random strategy', price_step_size=11)

        point_based_strat.add_point((50, 55, 'CHARGE'))
        point_based_strat.add_point((60, 33, 'CHARGE'))
        point_based_strat.add_point((70, 44, 'CHARGE'))
        point_based_strat.add_point((95, 0, 'CHARGE'))

        point_based_strat.add_point((40, 99, 'DISCHARGE'))
        point_based_strat.add_point((60, 88, 'DISCHARGE'))
        point_based_strat.add_point((70, 77, 'DISCHARGE'))
        point_based_strat.add_point((95, 66, 'DISCHARGE'))

        point_based_strat.upload_strategy()

        point_based_strat.name = f'Sorted random strategy (Sort strategy {i})'
        point_based_strat.sort_and_fix_points(sort_strategy=i)
        point_based_strat.upload_strategy()
        visualize_strategy(point_based_strat)
