import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

month_shorts = ['jan', 'feb', 'mar', 'apr',
                'may', 'june', 'july', 'aug',
                'sep', 'oct', 'nov', 'dec']
baseline_df = pd.read_csv('../../data/baseline_earnings/overview.csv', delimiter=';')


def make_list_of_monthly_earnings(single_run):
    res = []
    for i in range(12):
        month_label = month_shorts[i] + '_earning'
        res.append(single_run[month_label])
    return res


if __name__ == '__main__':
    print(baseline_df.name)
    # label_indexes = [6, 8, 10, 12]
    label_indexes = [7, 9, 11, 13]
    num_of_items = len(label_indexes)

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

    for i in range(num_of_items):
        single_run = baseline_df.loc[label_indexes[i]]
        single_run_y = make_list_of_monthly_earnings(single_run)
        plt.bar(x_axis + offsets[i], single_run_y, width, label=single_run['name'])

    plt.xticks(x_axis, month_shorts)
    plt.xlabel('Month')
    plt.ylabel('Total EUR')
    plt.title('Comparing monthly performance')
    plt.legend()
    plt.show()
