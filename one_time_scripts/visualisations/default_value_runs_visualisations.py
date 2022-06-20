import random
import matplotlib.pyplot as plt
import numpy as np

from one_time_scripts.visualisations.baselines_visualisation import baseline_df, make_list_of_monthly_earnings, \
    make_mean_and_std_per_month_from_folder

pretty_colours = [(0.15, 0.81, 0.82), (1, 0.24, 0.22), (0.52, 0.86, 0.39),
                  (0.87, 0.34, 0.74), (0.11, 0.47, 0.76), (1, 0.69, 0),
                  (0.29, 0.21, 0.28)]


def make_grouped_bar_graph(y_values, y_errors, x_ticks, y_labels, title=None):
    if title is None:
        title = 'Comparing monthly performance'

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
                # hatch='//', alpha=0.75,
                label=y_labels[bar_index], color=pretty_colours[bar_index])
        if sum(y_err) != 0:
            plt.errorbar(x_axis + offsets[bar_index], y_value, yerr=y_err,
                         fmt='o', markersize=width, elinewidth=width*0.5)

    plt.xticks(x_axis, x_ticks)
    plt.xlabel('Month (2021)')
    plt.ylabel('Total EUR', fontsize=8)
    plt.title(title)
    plt.legend(fontsize=6)
    plt.ylim((0, 275000))
    plt.show()


if __name__ == '__main__':
    month_shorts = ['jan', 'feb', 'mar', 'apr',
                    'may', 'june', 'july', 'aug',
                    'sep', 'oct', 'nov', 'dec']
    for i in range(len(month_shorts)):
        month = month_shorts[i]
        month_shorts[i] = month.capitalize()

    single_run = baseline_df.loc[13]
    single_run_y = make_list_of_monthly_earnings(single_run)

    source_folder = '../../data/new_ea_runs/default_runs/'
    default_y_values, default_y_errors = make_mean_and_std_per_month_from_folder(source_folder)

    filename_0 = '../../data/baseline_earnings/overview_default_runs_money_year_timings.csv'
    filename_1 = '../../data/baseline_earnings/overview_default_runs_money_month_timings.csv'
    filename_2 = '../../data/baseline_earnings/overview_default_runs_money_smart_timings.csv'
    filename_3 = '../../data/baseline_earnings/overview_default_runs_money_avg_timings.csv'
    filenames = [filename_0, filename_1, filename_2, filename_3]

    super_y_values = [single_run_y]
    super_y_errors = [[0]]

    for filename in filenames:
        y_values = []
        y_errors = []
        with open(filename) as random_file:
            header = True
            for row in random_file.readlines():
                if header:
                    header = False
                    continue
                month_earnings = np.array(row.split(',')).astype(float)
                if len(month_earnings) == 1:
                    y_values.append(month_earnings[0])
                    y_errors.append(0)
                else:
                    y_values.append(np.mean(month_earnings))
                    y_errors.append(np.std(month_earnings))
        super_y_values.append(y_values)
        super_y_errors.append(y_errors)

    make_grouped_bar_graph(super_y_values, super_y_errors, month_shorts,
                           ['AVG generation considered GIGA Baseline', 'Yearly times', 'Monthly times', 'Smart sizing', 'AVG generation considered'],
                           title='Disregard congestion evolutionary algorithm optimization\napplied to different congestion heuristics')

    super_y_values = [single_run_y, super_y_values[4], default_y_values]
    super_y_errors = [[0], super_y_errors[4], default_y_errors]
    make_grouped_bar_graph(super_y_values, super_y_errors, month_shorts,
                           ['AVG generation considered GIGA Baseline', 'AVG generation considered disregard congestion optimization', 'Evolutionary algorithm congestion optimization'],
                           title='Evolutionary algorithm optimizing with congestion compared to\nbest performing congestion heuristics')