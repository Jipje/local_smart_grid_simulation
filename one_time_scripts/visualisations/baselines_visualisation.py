import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from one_time_scripts.visualisations.visualise_ea_runs import convert_file_into_dict

month_shorts = ['jan', 'feb', 'mar', 'apr',
                'may', 'june', 'july', 'aug',
                'sep', 'oct', 'nov', 'dec']
month_long = ['january', 'february', 'march', 'april',
                'may', 'june', 'july', 'august',
                'september', 'october', 'november', 'december']
baseline_df = pd.read_csv('../../data/baseline_earnings/overview.csv', delimiter=';')

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
def make_list_of_monthly_earnings(single_run):
    res = []
    for i in range(12):
        month_label = month_shorts[i] + '_earning'
        res.append(single_run[month_label])
    return res


def make_list_of_monthly_earnings_from_ea_run_folder(source_folder='../../data/ea_runs/giga_baseline/'):
    res_mean = []
    res_error = []
    for i in range(12):
        month_filename = source_folder + month_long[i] + '.csv'
        dict_of_runs, num_of_runs = convert_file_into_dict(month_filename)
        arr_of_best_individuals = []
        for run_num in range(num_of_runs):
            run_label = f'run_{run_num}_best_individual'
            arr_of_best_individuals.append(dict_of_runs[run_label][-1])
        arr_of_best_individuals = np.array(arr_of_best_individuals)
        res_mean.append(np.mean(arr_of_best_individuals))
        res_error.append(np.std(arr_of_best_individuals))
    return res_mean, res_error


def make_bar_graph(baseline_indices, source_folders):
    num_of_items = len(baseline_indices) + len(source_folders)
    x_axis = np.array(list(range(10, 130, 10)))
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

    offset_tracker = 0
    for i in range(len(baseline_indices)):
        single_run = baseline_df.loc[baseline_indices[i]]
        single_run_y = make_list_of_monthly_earnings(single_run)

        hatch = ''
        alpha = 1
        if single_run['time_steps_with_congestion'] > 1:
            alpha = 0.75
            hatch = '///'

        plt.bar(x_axis + offsets[i], single_run_y, width, label=single_run['name'],
                hatch=hatch, alpha=alpha)
        offset_tracker = i

    for source_folder in source_folders:
        offset_tracker = offset_tracker + 1
        y_values, y_errors = make_list_of_monthly_earnings_from_ea_run_folder(source_folder)
        plt.bar(x_axis + offsets[offset_tracker], y_values, width, label=source_folder)
        plt.errorbar(x_axis + offsets[offset_tracker], y_values, yerr=y_errors,
                 fmt='o', markersize=width, elinewidth=width*0.5)

    plt.xticks(x_axis, month_shorts)
    plt.xlabel('Month (2021)')
    plt.ylabel('Total EUR')
    plt.title('Comparing monthly performance')
    plt.legend(fontsize=6)
    plt.show()


if __name__ == '__main__':
    label_indexes = [6, 7, 12, 13]
    source_folder = '../../data/ea_runs/random_init_first_runs/'
    make_bar_graph(label_indexes, source_folders=[source_folder])
