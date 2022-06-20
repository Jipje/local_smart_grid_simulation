import random

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats

from one_time_scripts.visualisations.visualise_ea_runs import convert_file_into_dict

month_shorts = ['jan', 'feb', 'mar', 'apr',
                'may', 'june', 'july', 'aug',
                'sep', 'oct', 'nov', 'dec']
month_long = ['january', 'february', 'march', 'april',
                'may', 'june', 'july', 'august',
                'september', 'october', 'november', 'december']

pretty_colours = [(0.15, 0.81, 0.82), (1, 0.24, 0.22), (0.52, 0.86, 0.39),
                  (0.87, 0.34, 0.74), (0.11, 0.47, 0.76), (1, 0.69, 0),
                  (0.29, 0.21, 0.28)]

try:
    baseline_df = pd.read_csv('../../data/baseline_earnings/overview.csv', delimiter=';')
except FileNotFoundError:
    baseline_df = pd.read_csv('../../../data/baseline_earnings/overview.csv', delimiter=';')


# 0                          Solarvation only discharging
# 1     Wombat disregard congestion (with base money s...
# 2             Wombat disregard congestion GIGA Baseline
# 3                          Wombat only solve congestion
# 4          Wombat yearly timing (with base money strat)
# 5                    Wombat yearly timing GIGA Baseline
# 6     Wombat conservative monthly timed (with base m...
# 7       Wombat conservative monthly timed GIGA Baseline
# 8     Wombat smart monthly timed (with base money st...
# 9              Wombat smart monthly timed GIGA Baseline
# 10    Wombat max smart monthly timed (with base mone...
# 11         Wombat max smart monthly timed GIGA Baseline
# 12    Wombat avg smart monthly timed (with base mone...
# 13         Wombat avg smart monthly timed GIGA Baseline
def make_list_of_monthly_earnings(single_run, few_months=None):
    if few_months is None:
        few_months = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    res = []
    for i in few_months:
        month_label = month_shorts[i] + '_earning'
        res.append(single_run[month_label])
    return res


def make_mean_and_std_per_month_from_folder(source_folder='../../data/ea_runs/giga_baseline/',
                                            suffix='', few_months=None):
    if few_months is None:
        few_months = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    res_mean = []
    res_error = []
    for i in few_months:
        month_filename = source_folder + month_long[i] + suffix + '.csv'
        dict_of_runs, num_of_runs = convert_file_into_dict(month_filename)
        arr_of_best_individuals = []
        for run_num in range(num_of_runs):
            run_label = f'run_{run_num}_best_individual'
            arr_of_best_individuals.append(dict_of_runs[run_label][-1])
        arr_of_best_individuals = np.array(arr_of_best_individuals)
        res_mean.append(np.mean(arr_of_best_individuals))
        res_error.append(np.std(arr_of_best_individuals))
    return res_mean, res_error


def analyse_length_of_run_per_month_from_folder(source_folder='../../data/ea_runs/giga_baseline/',
                                                suffix='', few_months=None,
                                                mutation_prob=50, population=100, offspring=80):
    if few_months is None:
        few_months = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    res_mean = []
    res_error = []
    res_run_lengths = []
    for i in few_months:
        month_filename = source_folder + month_long[i] + suffix + '.csv'
        dict_of_runs, num_of_runs = convert_file_into_dict(month_filename)
        arr_of_fit_calcs = []
        for run_num in range(num_of_runs):
            run_label = f'run_{run_num}_best_individual'
            number_of_generations = len(dict_of_runs[run_label])
            num_of_fit_calcs = num_of_gens_to_fitness_calcs(number_of_generations, mutation_prob,
                                                            population, offspring)
            arr_of_fit_calcs.append(num_of_fit_calcs)
        arr_of_fit_calcs = np.array(arr_of_fit_calcs)
        res_mean.append(np.mean(arr_of_fit_calcs))
        res_error.append(np.std(arr_of_fit_calcs))
        res_run_lengths.append(arr_of_fit_calcs)
    return res_mean, res_error, res_run_lengths


def num_of_gens_to_fitness_calcs(num_of_gens, mutation_prob=50, population=100, offspring=80):
    offspring_fitness_calcs = num_of_gens * offspring
    mutation_fitness_calcs = num_of_gens * (population * mutation_prob / 100)
    initial_pop = population
    return initial_pop + offspring_fitness_calcs + mutation_fitness_calcs


def make_arr_of_best_individuals_per_month_from_folder(source_folder='../../data/ea_runs/giga_baseline/',
                                                       suffix='', few_months=None):
    if few_months is None:
        few_months = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    res = []
    for i in few_months:
        month_filename = source_folder + month_long[i] + suffix + '.csv'
        dict_of_runs, num_of_runs = convert_file_into_dict(month_filename)
        arr_of_best_individuals = []
        for run_num in range(num_of_runs):
            run_label = f'run_{run_num}_best_individual'
            arr_of_best_individuals.append(dict_of_runs[run_label][-1])
        arr_of_best_individuals = np.array(arr_of_best_individuals)
        res.append(arr_of_best_individuals)
    return res


def statistic_tests(baseline_indices, source_folders, few_months=None, suffixes=None):
    res_dict = {}
    for source_folder_index in range(len(source_folders)):
        source_folder = source_folders[source_folder_index]
        if suffixes is not None:
            assert len(suffixes) == len(source_folders), 'Please supply as many suffixes as folders'
            suffix = suffixes[source_folder_index]
        else:
            suffix = ''

        arr_of_arr_of_best_individuals = make_arr_of_best_individuals_per_month_from_folder(source_folder,
                                                                                            suffix=suffix,
                                                                                            few_months=few_months)
        res_dict[source_folder_index] = arr_of_arr_of_best_individuals

    for source_folder_index in range(len(source_folders) - 1):
        suffix_one = suffixes[source_folder_index]
        suffix_other = suffixes[source_folder_index + 1]
        print(f'Comparing performance of {suffix_one} with {suffix_other} with T-Test')
        for month in range(len(few_months)):
            one = res_dict[source_folder_index][month]
            other = res_dict[source_folder_index + 1][month]
            print(f'Running test for month {few_months[month] + 1}')
            two_sided_t_test(one, other)


def two_sided_t_test(one, other):
    t_value, p_value = stats.ttest_ind(one, other)
    print('\tTest statistic is %f' % float("{:.6f}".format(t_value)))
    print('\tp-value for two tailed test is %f' % p_value)
    alpha = 0.05
    if p_value <= alpha:
        print('\tConclusion', 'n', 'Since p-value(=%f)' % p_value, '<', 'alpha(=%.2f)' % alpha,
              '''We reject the null hypothesis H0.\n\t\tSo we conclude that the effect of the tested parameter are not equal i.e., μ1 = μ2 at %.2f level of significance.''' % alpha)
    else:
        print('\tConclusion', 'n', 'Since p-value(=%f)' % p_value, '>', 'alpha(=%.2f)' % alpha,
              '''We do not reject the null hypothesis H0.''')


def make_bar_graph(baseline_indices, source_folders, few_months=None, suffixes=None,
                   num_of_source_folder_baselines=0, title=None, folder_label=None):
    if title is None:
        title = 'Comparing monthly performance'

    for _ in range(len(baseline_indices) + num_of_source_folder_baselines):
        pretty_colours.append('#%06X' % random.randint(0, 0xFFFFFF))

    month_labels = []
    if few_months is None:
        max_x = 130
        for month in month_shorts:
            month_labels.append(month.capitalize())
    else:
        max_x = 10 + len(few_months) * 10
        for month_index in few_months:
            month = month_long[month_index]
            month_labels.append(month.capitalize())

    x_axis = np.array(list(range(10, max_x, 10)))
    num_of_items = len(baseline_indices) + len(source_folders)
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

    offset_tracker = -1
    colour_index = len(source_folders) - num_of_source_folder_baselines + 1
    for i in range(len(baseline_indices)):
        single_run = baseline_df.loc[baseline_indices[i]]
        single_run_y = make_list_of_monthly_earnings(single_run, few_months)

        hatch = ''
        alpha = 1
        if single_run['time_steps_with_congestion'] > 1:
            alpha = 0.75
            hatch = '//'

        plt.bar(x_axis + offsets[i], single_run_y, width, label=single_run['name'],
                hatch=hatch, alpha=alpha, color=pretty_colours[colour_index + i])
        offset_tracker = i

    colour_index = colour_index + num_of_source_folder_baselines
    flag_colour_index_reset = False
    for source_folder_index in range(len(source_folders)):
        if num_of_source_folder_baselines == 0 and not flag_colour_index_reset:
            colour_index = 0
            flag_colour_index_reset = True

        source_folder = source_folders[source_folder_index]
        if suffixes is not None:
            assert len(suffixes) == len(source_folders), 'Please supply as many suffixes as folders'
            suffix = suffixes[source_folder_index]
        else:
            suffix = ''

        offset_tracker = offset_tracker + 1
        y_values, y_errors = make_mean_and_std_per_month_from_folder(source_folder, suffix=suffix,
                                                                     few_months=few_months)
        if folder_label is None:
            folder_label = source_folder.split('/')[-2].replace('_', ' ').title()
        suffix_label = suffix.replace('_', ' ').title()
        if suffix_label != '':
            label = folder_label + ' - ' + suffix_label
        else:
            label = folder_label
        plt.bar(x_axis + offsets[offset_tracker], y_values, width, label=label,
                color=pretty_colours[colour_index],
                # alpha=0.75, hatch='//'
                )
        plt.errorbar(x_axis + offsets[offset_tracker], y_values, yerr=y_errors,
                     fmt='o', markersize=width, elinewidth=width*0.5)
        num_of_source_folder_baselines = num_of_source_folder_baselines - 1
        colour_index = colour_index + 1

    plt.xticks(x_axis, month_labels)
    plt.xlabel('Month (2021)')
    plt.ylabel('Total EUR', fontsize=8)
    plt.title(title)
    plt.ylim(0, 275000)
    plt.legend(fontsize=6, loc="upper left")
    plt.show()


if __name__ == '__main__':
    label_indexes = [8, 13]
    source_folder_1 = '../../data/new_ea_runs/giga_baseline_with_congestion/'
    source_folder_2 = '../../data/ea_runs/random_init_first_runs/'
    make_bar_graph(label_indexes, source_folders=[source_folder_1, source_folder_2])

    label_indexes = [3, 5, 7, 9, 13]
    make_bar_graph(label_indexes, source_folders=[], suffixes=[],
                   title='GIGA Baseline performance with different congestion heuristics')

    label_indexes = [2]
    make_bar_graph(label_indexes, source_folders=['../../data/new_ea_runs/default_runs_disregard_congestion/'],
                   num_of_source_folder_baselines=1, title='Disregard congestion evolutionary algorithm optimization')

    label_indexes = [13]
    make_bar_graph(label_indexes, source_folders=['../../data/new_ea_runs/default_runs/'],
                   num_of_source_folder_baselines=1)

    label_indexes = []
    source_folder_3 = '../../data/ea_runs/sorting_investigation/'
    source_folders = [source_folder_1, source_folder_3, source_folder_3, source_folder_3, source_folder_3]
    all_suffix = ['', '_sort_none', '_sort_1', '_sort_2', '_sort_3']
    few_months = [2, 3, 10]

    make_bar_graph(label_indexes, source_folders=source_folders, suffixes=all_suffix, few_months=few_months,
                   num_of_source_folder_baselines=1)
  
    statistic_tests([], [source_folder_3, source_folder_3], few_months=[2, 3, 10],
                    suffixes=['_sort_none', '_sort_1'])

    print(make_mean_and_std_per_month_from_folder(source_folder='../../data/new_ea_runs/sorting/', few_months=[2, 3, 10], suffix='_sort_3'))
    print(analyse_length_of_run_per_month_from_folder(source_folder='../../data/new_ea_runs/sorting/', few_months=[2, 3, 10], suffix='_sort_3'))
