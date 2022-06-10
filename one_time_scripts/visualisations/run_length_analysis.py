import random
import matplotlib.pyplot as plt
import numpy as np

from one_time_scripts.visualisations.baselines_visualisation import analyse_length_of_run_per_month_from_folder, \
    two_sided_t_test, month_shorts, month_long

pretty_colours = [(0.15, 0.81, 0.82), (1, 0.24, 0.22), (0.52, 0.86, 0.39),
                  (0.87, 0.34, 0.74), (0.11, 0.47, 0.76), (1, 0.69, 0),
                  (0.29, 0.21, 0.28)]


def make_grouped_bar_graph(y_values, y_errors, x_ticks, y_labels, title=None):
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
    plt.title(title)
    plt.legend(fontsize=6)
    plt.show()


def length_statistical_test(source_folders, few_months, suffixes):
    res_dict = {}

    for source_folder_index in range(len(source_folders)):
        source_folder = source_folders[source_folder_index]
        if suffixes is not None:
            assert len(suffixes) == len(source_folders), 'Please supply as many suffixes as folders'
            suffix = suffixes[source_folder_index]
        else:
            suffix = ''

        _, _, run_lengths = analyse_length_of_run_per_month_from_folder(source_folder=source_folder,
                                                                        few_months=few_months,
                                                                        suffix=suffix)
        res_dict[source_folder_index] = run_lengths

    for source_folder_index in range(len(source_folders) - 1):
        suffix_org = suffixes[0]
        suffix_other = suffixes[source_folder_index + 1]
        print(f'Comparing run length of {suffix_org} with {suffix_other} with T-Test')
        for month in range(len(few_months)):
            one = res_dict[source_folder_index][month]
            other = res_dict[source_folder_index + 1][month]
            print(f'Running test for month {few_months[month] + 1}')
            two_sided_t_test(one, other)


def make_length_bar_graphs(source_folders, few_months, suffixes, labels=None,
                           title=None):
    if title is None:
        title = 'Comparing monthly performance'

    month_labels = []
    if few_months is None:
        for month in month_shorts:
            month_labels.append(month.capitalize())
    else:
        for month_index in few_months:
            month = month_long[month_index]
            month_labels.append(month.capitalize())

    if labels is None:
        labels = []
        for i in range(len(source_folders)):
            label = source_folders[i] + suffixes[i]
            labels.append(label)

    super_y_values = []
    super_y_errors = []
    for i in range(len(source_folders)):
        source_folder = source_folders[i]
        suffix = suffixes[i]
        y_values, y_errors, _ = analyse_length_of_run_per_month_from_folder(source_folder=source_folder,
                                                                            few_months=few_months, suffix=suffix)
        super_y_values.append(y_values)
        super_y_errors.append(y_errors)
    make_grouped_bar_graph(super_y_values, super_y_errors, month_labels, labels, title)


if __name__ == '__main__':
    sf = '../../data/new_ea_runs/sorting/'
    temp_source_folders = [sf, sf, sf, sf]
    temp_suffixes = ['_no_sort', '_sort_1', '_sort_2', '_sort_3']
    labels = ['No sort', 'Sort 1', 'Sort 2', 'Sort 3']

    make_length_bar_graphs(temp_source_folders, few_months=[2, 3, 10], suffixes=temp_suffixes)

    length_statistical_test(temp_source_folders, suffixes=temp_suffixes, few_months=[2, 3, 10])
