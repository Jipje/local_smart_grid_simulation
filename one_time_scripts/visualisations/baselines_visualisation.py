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


if __name__ == '__main__':
    print(baseline_df.name)
    # label_indexes = [6, 8, 10, 12]
    # label_indexes = [7, 9, 11, 13]
    # label_indexes = [2, 7, 9, 11, 13]
    label_indexes = [13]

    source_folder='../../data/ea_runs/giga_baseline/'
    y_values, y_errors = make_list_of_monthly_earnings_from_ea_run_folder(source_folder)
    num_of_items = len(label_indexes) + 1

    x_axis = np.array(list(range(10, 130, 10)))
    offsets = []
    width = 0
    if num_of_items == 2:
        offsets = [-2, 2]
        width = 4
    elif num_of_items == 3:
        offsets = [-2, 0, 2]
        width = 2
    elif num_of_items == 4:
        offsets = [-3, -1, 1, 3]
        width = 2
    elif num_of_items == 5:
        offsets = [-3, -1.5, 0, 1.5, 3]
        width = 1.5

    for i in range(num_of_items - 1):
        single_run = baseline_df.loc[label_indexes[i]]
        single_run_y = make_list_of_monthly_earnings(single_run)

        hatch = ''
        alpha = 1
        if single_run['time_steps_with_congestion'] > 1:
            alpha = 0.75
            hatch = '///'

        plt.bar(x_axis + offsets[i], single_run_y, width, label=single_run['name'],
                hatch=hatch, alpha=alpha)

    plt.bar(x_axis + offsets[-1], y_values, width, label=source_folder)
    plt.errorbar(x_axis + offsets[-1], y_values, yerr=y_errors,
                 fmt='o', markersize=width, elinewidth=width*0.5)

    plt.xticks(x_axis, month_shorts)
    plt.xlabel('Month')
    plt.ylabel('Total EUR')
    plt.title('Comparing monthly performance')
    plt.legend()
    plt.show()
