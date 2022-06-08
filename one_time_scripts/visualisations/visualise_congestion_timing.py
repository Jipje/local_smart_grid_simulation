import pandas as pd
from matplotlib.lines import Line2D
from numpy import mean
from pandas import NaT

from helper_objects.congestion_helper.month_congestion_size_and_timer import get_month_congestion_timings, \
    get_month_congestion_timings_with_df
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime as dt
import dateutil.tz
from random import randint

from one_time_scripts.helper_objects.solarvation_loader import load_solarvation_data

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()

standard_month_colors = [(0.0, 0.486, 0.737), (0.0, 0.6, 0.824), (0.0, 0.616, 0.314),
                         (0.455, 0.682, 0.212), (0.675, 0.776, 0.102), (0.922, 0.667, 0.071),
                         (0.91, 0.533, 0.063), (0.914, 0.208, 0.063), (0.882, 0.169, 0.318),
                         (0.702, 0.208, 0.49), (0.427, 0.247, 0.592), (0.275, 0.251, 0.596)]


def visualise_congestion_time_and_sizes(res_df, title=None):
    prep_starts = res_df.loc['prep_start'].array
    congestion_starts = res_df.loc['congestion_start'].array
    preparing_max_kwh = res_df.loc['prep_max_soc'].array
    solving_congestion_until = res_df.loc['congestion_end'].array

    prep_starts_y_min = []
    prep_starts_y_max = []
    y_ticks = []
    colors = standard_month_colors
    largest_prep_kwh = -1
    for i in range(len(prep_starts)):
        prep_starts_y_min.append((i * 20) + 5)
        prep_starts_y_max.append((i * 20) + 20)

        if prep_starts[i] is NaT:
            prep_starts[i] = dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc)
            congestion_starts[i] = dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc)
            solving_congestion_until[i] = dt.datetime(1970, 1, 1, 0, 0, tzinfo=utc)
            preparing_max_kwh[i] = 0
        else:
            prep_starts[i] = dt.datetime(1970, 1, 1, prep_starts[i].hour, prep_starts[i].minute, tzinfo=utc)
            congestion_starts[i] = dt.datetime(1970, 1, 1, congestion_starts[i].hour, congestion_starts[i].minute, tzinfo=utc)
            solving_congestion_until[i] = dt.datetime(1970, 1, 1, solving_congestion_until[i].hour, solving_congestion_until[i].minute, tzinfo=utc)
            if preparing_max_kwh[i] > largest_prep_kwh:
                largest_prep_kwh = preparing_max_kwh[i]
        colors.append('#%06X' % randint(0, 0xFFFFFF))
        y_ticks.append((i * 20) + 12.5)

    plt.hlines(prep_starts_y_min + prep_starts_y_max, xmin=dt.datetime(1970, 1, 1, 0, 1),
               xmax=dt.datetime(1970, 1, 1, 23, 58), colors=(0.9, 0.9, 0.9, 0.5))

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


def visualise_daily_profile_per_month(solarvation_df, max_kw, congestion_kw=None, solar_farm_name=''):
    fig, axs = plt.subplots(4, 3, figsize=(12, 9))
    congestion_df = get_month_congestion_timings_with_df(solarvation_df, verbose_lvl=1, strategy=3)
    print(congestion_df.to_string())
    early_start_color = (0.64, 0.26, 0.75, 0.85)
    late_end_color = (0.75, 0.26, 0.62, 0.85)
    max_cap_color = (0.75, 0.26, 0.37, 0.85)
    base_color = (0.26, 0.62, 0.75, 0.2)

    for month in range(1, 13):
        start_of_month = dt.datetime(2021, month, 1, tzinfo=utc)
        temp_day = start_of_month.replace(day=28) + dt.timedelta(days=4)
        end_of_month = temp_day.replace(day=1) - dt.timedelta(minutes=1)

        month_congestion_series = congestion_df[month-1]
        highlighted_days = [
            month_congestion_series.earliest_start_day.day,
            month_congestion_series.latest_end_day.day,
            month_congestion_series.max_capacity_day.day
        ]

        if month in [1, 4, 7, 10]:
            axes_y = 0
        elif month in [2, 5, 8, 11]:
            axes_y = 1
        else:
            axes_y = 2

        axes_x = None
        for j in range(1, 5):
            if month <= (j * 3):
                axes_x = j - 1
                break

        month_df = solarvation_df[start_of_month:end_of_month]
        month_df.index = pd.to_datetime(month_df['time_utc'], errors='coerce', utc=True)
        start_day = month_df.iloc[0].time_utc.to_pydatetime().replace(hour=0)
        month_df = month_df.resample('15T').agg({
            'power': mean,
            'time': min
        })

        for day_index in range(int((end_of_month - start_of_month).days)):
            current_day_start = (start_day + dt.timedelta(days=day_index)).replace(hour=0, minute=0)
            current_day_end = current_day_start + dt.timedelta(days=1) - dt.timedelta(minutes=1)

            current_day_str = current_day_start.strftime('%b %d')
            current_day_df = month_df[current_day_start:current_day_end]
            current_day_df = current_day_df.dropna()

            if current_day_start.day == highlighted_days[0]:
                color = early_start_color
            elif current_day_start.day == highlighted_days[1]:
                color = late_end_color
            elif current_day_start.day == highlighted_days[2]:
                color = max_cap_color
            else:
                color = base_color
            axs[axes_x, axes_y].plot(current_day_df['time'], current_day_df['power'], label=current_day_str, color=color)
        axs[axes_x, axes_y].set_title('{}'.format(start_of_month.strftime('%B')))
        axs[axes_x, axes_y].set_ylim((0, max_kw))
        axs[axes_x, axes_y].xaxis.set_major_formatter(mdates.DateFormatter('%H'))
        if congestion_kw is not None:
            axs[axes_x, axes_y].axhline(congestion_kw, 0, 23, ls='--', c='red')

    fig.suptitle(f'Daily load profile per month of the {solar_farm_name} solar farm')
    for ax in axs.flat:
        ax.set(xlabel='Hour (UTC)', ylabel='Generated power (kW)')
        ax.label_outer()
    own_lines = [
        Line2D([0], [0], color=(0.26, 0.62, 0.75, 1), lw=2),
        Line2D([0], [0], color=(0.64, 0.26, 0.75, 1), lw=2),
        Line2D([0], [0], color=(0.75, 0.26, 0.62, 1), lw=2),
        Line2D([0], [0], color=(0.75, 0.26, 0.37, 1), lw=2)
    ]
    plt.legend(own_lines, ['Daily profile', 'Earliest congestion start',
                           'Latest congestion end', 'Highest capacity during congestion'])
    plt.show()


if __name__ == '__main__':
    solarvation_identifier = '../../data/environments/lelystad_1_2021.csv'
    solarvation_df = load_solarvation_data(solarvation_identifier)

    strategy_titles = ['', 'Smart sizing and monthly times', 'Monthly times rounded', 'Monthly times', 'Yearly times',
                       'Preparation timed on MAX profile', 'Preparation timed on AVG profile']
    # for strategy_num in range(1, 7):
    #     congestion_df = get_month_congestion_timings_with_df(solarvation_df, verbose_lvl=1, strategy=strategy_num)
    #     visualise_congestion_time_and_sizes(congestion_df, title=strategy_titles[strategy_num])

    for strategy_num in [4, 3, 1, 6]:
        congestion_df = get_month_congestion_timings_with_df(solarvation_df, verbose_lvl=1, strategy=strategy_num)
        visualise_congestion_time_and_sizes(congestion_df, title=strategy_titles[strategy_num])
