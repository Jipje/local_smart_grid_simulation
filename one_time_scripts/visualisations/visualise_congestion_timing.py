from pandas import NaT

from helper_objects.congestion_helper.month_congestion_size_and_timer import get_month_congestion_timings, \
    get_month_congestion_timings_with_df
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import dateutil.tz
from random import randint

from one_time_scripts.solar_scripts.solarvation_visualization import load_solarvation_data

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def visualise_congestion_time_and_sizes(res_df, title=None):
    prep_starts = res_df.loc['prep_start'].array
    congestion_starts = res_df.loc['congestion_start'].array
    preparing_max_kwh = res_df.loc['prep_max_soc'].array
    solving_congestion_until = res_df.loc['congestion_end'].array

    prep_starts_y_min = []
    prep_starts_y_max = []
    y_ticks = []
    colors = []
    largest_prep_kwh = -1
    for i in range(len(prep_starts)):
        if prep_starts[i] is NaT:
            prep_starts[i] = dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc)
            congestion_starts[i] = dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc)
            solving_congestion_until[i] = dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc)
            preparing_max_kwh[i] = 0
            prep_starts_y_min.append(None)
            prep_starts_y_max.append(None)
        else:
            prep_starts[i] = dt.datetime(1970, 1, 1, prep_starts[i].hour, prep_starts[i].minute, tzinfo=utc)
            congestion_starts[i] = dt.datetime(1970, 1, 1, congestion_starts[i].hour, congestion_starts[i].minute, tzinfo=utc)
            solving_congestion_until[i] = dt.datetime(1970, 1, 1, solving_congestion_until[i].hour, solving_congestion_until[i].minute, tzinfo=utc)
            prep_starts_y_min.append((i * 20) + 5)
            prep_starts_y_max.append((i * 20) + 20)
            if preparing_max_kwh[i] > largest_prep_kwh:
                largest_prep_kwh = preparing_max_kwh[i]
        colors.append('#%06X' % randint(0, 0xFFFFFF))
        y_ticks.append((i * 20) + 12.5)

    for i in range(12):
        y_min = prep_starts_y_min[i]
        y_max = prep_starts_y_max[i]
        color = colors[i]
        opacity = 0.1
        if y_min is None:
            end_of_prep_y = None
        else:
            end_of_prep_y = preparing_max_kwh[i] / 30000 * 12 + 2 + y_min
        plt.plot([prep_starts[i], prep_starts[i]], [y_min, y_max], color=color)
        plt.fill([prep_starts[i], prep_starts[i], congestion_starts[i], congestion_starts[i]], [y_min, y_max, y_max, y_min], color=color, alpha=opacity)
        plt.fill([prep_starts[i], prep_starts[i], congestion_starts[i], congestion_starts[i]], [y_min, y_max, end_of_prep_y, y_min], color=color, alpha=0.4)
        plt.plot([congestion_starts[i], congestion_starts[i]], [y_min, y_max], color=color)
        plt.fill([congestion_starts[i], congestion_starts[i], solving_congestion_until[i], solving_congestion_until[i]], [y_min, y_max, y_max, y_min], color=color, alpha=opacity)
        plt.fill([congestion_starts[i], congestion_starts[i], solving_congestion_until[i], solving_congestion_until[i]], [y_min, end_of_prep_y, end_of_prep_y, y_min], color=color, alpha=0.4)
        plt.plot([solving_congestion_until[i], solving_congestion_until[i]], [y_min, y_max], color=color)

    my_fmt = mdates.DateFormatter('%H:%M')
    title_suffix = ''
    if title is not None:
        title_suffix = '\n' + title
    plt.title('Fixed schedule to prepare for and solve congestion' + title_suffix)
    plt.ylabel('Month')
    plt.xlabel('Time')
    plt.xlim(dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc), dt.datetime(1970, 1, 1, 23, 59))
    plt.ylim(0, 250)

    plt.gca().xaxis.set_major_formatter(my_fmt)

    plt.yticks(y_ticks, ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'])
    plt.show()


if __name__ == '__main__':
    solarvation_identifier = '../../data/environments/lelystad_1_2021.csv'
    solarvation_df = load_solarvation_data(solarvation_identifier)

    strategy_titles = ['', 'Smart sizing and monthly times', 'Monthly times rounded', 'Monthly times', 'Yearly times']
    for strategy_num in range(1, 5):
        congestion_df = get_month_congestion_timings_with_df(solarvation_df, verbose_lvl=1, strategy=strategy_num)
        visualise_congestion_time_and_sizes(congestion_df, title=strategy_titles[strategy_num])

    print(congestion_df.to_string())
