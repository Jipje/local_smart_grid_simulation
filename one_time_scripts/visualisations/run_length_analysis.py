import random
import matplotlib.pyplot as plt
import numpy as np

from one_time_scripts.visualisations.baselines_visualisation import analyse_length_of_run_per_month_from_folder

pretty_colours = [(0.15, 0.81, 0.82), (1, 0.24, 0.22), (0.52, 0.86, 0.39),
                  (0.87, 0.34, 0.74), (0.11, 0.47, 0.76), (1, 0.69, 0),
                  (0.29, 0.21, 0.28)]


def make_grouped_bar_graph(y_values, y_errors, x_ticks, y_labels):
    for _ in range(len(y_values)):
        pretty_colours.append('#%06X' % random.randint(0, 0xFFFFFF))

    max_x = 10 + len(y_values[0]) * 10
    x_axis = np.array(list(range(10, max_x, 10)))
    num_of_items = len(y_values)

    offsets = []
    if num_of_items == 2:
        offsets = [-2, 2]
    elif num_of_items == 3:
        offsets = [-2, 0, 2]
    elif num_of_items == 4:
        offsets = [-3, -1, 1, 3]
    elif num_of_items == 5:
        offsets = [-3, -1.5, 0, 1.5, 3]
    elif num_of_items == 6:
        offsets = [-3.125, -1.875, -0.625, 0.625, 1.875, 3.125]
    width = offsets[-1] - offsets[-2]

    for bar_index in range(len(y_values)):
        y_value = y_values[bar_index]
        y_err = y_errors[bar_index]
        plt.bar(x_axis + offsets[bar_index], y_value, width,
                label=y_labels[bar_index], color=pretty_colours[bar_index])
        if y_err != 0:
            plt.errorbar(x_axis + offsets[bar_index], y_value, yerr=y_err,
                         fmt='o', markersize=width, elinewidth=width*0.5)

    plt.xticks(x_axis, x_ticks)
    plt.xlabel('Month (2021)')
    plt.ylabel('Number of fitness function calls')
    plt.title('Comparing monthly performance')
    plt.legend(fontsize=6)
    plt.show()


if __name__ == '__main__':
    source_folder = '../../data/new_ea_runs/sorting/'
    source_folders = [source_folder, source_folder, source_folder]
    suffixes = ['_no_sort', '_sort_1', '_sort_3']
    labels = ['No sort', 'Sort 1', 'Sort 3']

    super_y_values = []
    super_y_errors = []
    for i in range(len(source_folders)):
        source_folder = source_folders[i]
        suffix = suffixes[i]
        y_values, y_errors = analyse_length_of_run_per_month_from_folder(source_folder=source_folder, few_months=[2, 3, 10], suffix=suffix)
        super_y_values.append(y_values)
        super_y_errors.append(y_errors)
    make_grouped_bar_graph(super_y_values, super_y_errors, ['March', 'April', 'November'], labels)
