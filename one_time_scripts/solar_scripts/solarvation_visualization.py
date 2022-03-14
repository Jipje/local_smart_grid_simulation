import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import dateutil.tz

from helper_objects.congestion_helper.time_and_size_congestion_helper import time_and_size_multiple_congestion_events, \
    time_congestion_events, size_congestion_events, identify_congestion
from one_time_scripts.helper_objects.date_helper import retrieve_months

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def date_parser(string):
    return dt.datetime.strptime(string, '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=utc)


def load_solarvation_data(solarvation_filename='../../data/environments/lelystad_1_2021.csv'):
    solarvation_df = pd.read_csv(solarvation_filename, parse_dates=[0], date_parser=date_parser)
    try:
        solarvation_df.index = pd.to_datetime(solarvation_df['time_utc'], errors='coerce', utc=True)
    except KeyError:
        solarvation_df.index = pd.to_datetime(solarvation_df['time_ams'], errors='coerce', utc=True)
        solarvation_df = solarvation_df.drop('time_ams', axis=1)
        solarvation_df['time_utc'] = solarvation_df.index

    solarvation_df['hour_of_production'] = solarvation_df.index.hour
    solarvation_df['time'] = solarvation_df['time_utc'].apply(lambda x: x.replace(year=1970, month=1, day=1))

    return solarvation_df


def do_basic_analysis(solarvation_df, max_kw=None, congestion_kw=None, solar_farm_name=''):
    # ['tennet_balansdelta.mean_max_price', 'tennet_balansdelta.mean_mid_price', 'tennet_balansdelta.mean_min_price',
    #  'power', 'irradiance', 'expected_power', 'lower_range', 'upper_range', 'losses']
    plt.hist(solarvation_df['power'], bins=100)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Power generation (kW)')
    plt.title(f'Histogram of power generation by solar farm {solar_farm_name}')
    if congestion_kw is not None:
        plt.vlines(congestion_kw, 0, 100000, ls='--', colors='red')
    plt.show()

    plt.hist(solarvation_df['power'], bins=100)
    plt.ylim(0, 4000)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Power generation (kW)')
    plt.title(f'Histogram of power generation by solar farm {solar_farm_name}')
    if congestion_kw is not None:
        plt.vlines(congestion_kw, 0, 4000, ls='--', colors='red')
    plt.show()

    plt.scatter(solarvation_df['hour_of_production'], solarvation_df['power'])
    plt.ylabel('Generated power 1m (kW)')
    plt.xlabel('Hour in which power was generated (UTC)')
    plt.title(f'Scatterplot of power generation by solar farm {solar_farm_name}')
    if max_kw is not None:
        plt.ylim(0, max_kw)
    if congestion_kw is not None:
        plt.hlines(congestion_kw, 0, 23, ls='--', colors='red')
    plt.show()


def do_monthly_analysis(solarvation_df, max_kw, congestion_kw=None, solar_farm_name=''):
    fig, axs = plt.subplots(4, 3, figsize=(12, 9))
    for i in range(1, 13):
        month = i
        start_of_month = dt.datetime(2021, month, 1, tzinfo=utc)
        temp_day = start_of_month.replace(day=28) + dt.timedelta(days=4)
        end_of_month = temp_day.replace(day=1) - dt.timedelta(minutes=1)

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
        axs[axes_x, axes_y].scatter(month_df['hour_of_production'], month_df['power'])
        axs[axes_x, axes_y].set_title('{}'.format(start_of_month.strftime('%B')))
        axs[axes_x, axes_y].set_ylim((0, max_kw))
        axs[axes_x, axes_y].set_xlim((0, 23))
        if congestion_kw is not None:
            axs[axes_x, axes_y].axhline(congestion_kw, 0, 23, ls='--', c='red')

    fig.suptitle(f'Scatterplot of generated power per month of the {solar_farm_name} solar farm')
    for ax in axs.flat:
        ax.set(xlabel='Hour (UTC)', ylabel='Generated power (kW)')
        ax.label_outer()
    plt.show()


def do_range_investigation(solarvation_df):
    print('Is the measured power between the expected range?')
    solarvation_df['within_range'] = (solarvation_df['upper_range'] >= solarvation_df['power']) & (solarvation_df['power'] >= solarvation_df['lower_range'])
    within_range_values = solarvation_df['within_range'].value_counts()
    range_value_counts_msg(within_range_values)

    print('Add 20 percent safety margin to the expected range, how does that improve it?')
    solarvation_df['20_perc_upper_range'] = solarvation_df['upper_range'] * 1.2
    solarvation_df['20_perc_lower_range'] = solarvation_df['lower_range'] * 0.8
    solarvation_df['20_perc_within_range'] = (solarvation_df['20_perc_upper_range'] >= solarvation_df['power']) & (solarvation_df['power'] >= solarvation_df['20_perc_lower_range'])
    within_range_values = solarvation_df['20_perc_within_range'].value_counts()
    range_value_counts_msg(within_range_values)

    print('Is the measured power lower than the upper range?')
    solarvation_df['upper_range_correct'] = solarvation_df['upper_range'] >= solarvation_df['power']
    within_range_values = solarvation_df['upper_range_correct'].value_counts()
    range_value_counts_msg(within_range_values)

    print('If we take an upper range with 20% safety margin?')
    solarvation_df['20_perc_upper_range_correct'] = solarvation_df['20_perc_upper_range'] >= solarvation_df['power']
    within_range_values = solarvation_df['20_perc_upper_range_correct'].value_counts()
    range_value_counts_msg(within_range_values)

    print('If we take an upper range with 50% safety margin?')
    solarvation_df['50_perc_upper_range'] = solarvation_df['upper_range'] * 1.5
    solarvation_df['50_perc_upper_range_correct'] = solarvation_df['50_perc_upper_range'] >= solarvation_df['power']
    within_range_values = solarvation_df['50_perc_upper_range_correct'].value_counts()
    range_value_counts_msg(within_range_values)

    print('If we take an upper range with 100% safety margin?')
    solarvation_df['100_perc_upper_range'] = solarvation_df['upper_range'] * 2
    solarvation_df['100_perc_upper_range_correct'] = solarvation_df['100_perc_upper_range'] >= solarvation_df['power']
    within_range_values = solarvation_df['100_perc_upper_range_correct'].value_counts()
    range_value_counts_msg(within_range_values)

    print('\nAha, issue is a prediction of 0 and small measured values.')
    print('Lets filter out issues where measured power is below 1000 kW\n')

    filtered_df = solarvation_df[solarvation_df['power'] > 1000]

    print('Filtered DataFrame with 100% safety margin')
    within_range_values = filtered_df['100_perc_upper_range_correct'].value_counts()
    range_value_counts_msg(within_range_values)

    print('Filtered DataFrame with 20% safety margin')
    within_range_values = filtered_df['20_perc_upper_range_correct'].value_counts()
    range_value_counts_msg(within_range_values)


def range_value_counts_msg(within_range_values):
    correct = within_range_values[True]
    try:
        incorrect = within_range_values[False]
    except KeyError:
        incorrect = 0
    total_number_of_points = correct + incorrect
    perc_correct = round(correct / total_number_of_points * 100, 2)
    msg = '\t{} data points analyzed.\n' \
          '\tThe range estimation was correct {} of times.\n' \
          '\tThe range estimation was incorrect {} number of times.\n' \
          '\tThe range was correct {}% of the time.'.format(total_number_of_points, correct, incorrect, perc_correct)
    print(msg)


def daily_vis(solarvation_df, day_dt=None):
    counter = 0
    if day_dt is not None:
        end_of_day = day_dt + dt.timedelta(days=1) - dt.timedelta(minutes=1)
        solarvation_df = solarvation_df[day_dt:end_of_day]

    start_day = solarvation_df.iloc[0].time_utc.to_pydatetime().replace(hour=0)

    for day_index in range(int(len(solarvation_df) / 1440)):
        current_day_start = (start_day + dt.timedelta(days=day_index)).replace(hour=0, minute=0)
        current_day_end = current_day_start + dt.timedelta(days=1) - dt.timedelta(minutes=1)

        current_day_str = current_day_start.strftime('%b %d')
        current_day_df = solarvation_df[current_day_start:current_day_end]
        counter += 1

        plt.plot(current_day_df['time'], current_day_df['power'], label=current_day_str)
        if counter == 4:
            break
    plt.legend()
    plt.ylabel('Generated power 1m (kW)')
    plt.xlabel('Time (UTC)')
    plt.ylim(0, 20000)
    plt.title('Solar generation profile for multiple days.')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    plt.show()


def make_congestion_series(solarvation_df, start_date, end_date, start_hours, end_hours):
    res_arr = []
    columns = []
    current_date = start_date.replace(hour=0, minute=0)

    while current_date < end_date:
        start_of_period = current_date.replace(hour=start_hours.hour, minute=start_hours.minute)
        end_of_period = current_date.replace(hour=end_hours.hour, minute=end_hours.minute)

        day_df = solarvation_df[start_of_period:end_of_period]
        if day_df['congestion'].max():
            day_df.index = day_df['time']
            res_arr.append(day_df['power'])
            day_str = current_date.strftime('%d-%m-%Y')
            columns.append(day_str)

        current_date = current_date + dt.timedelta(days=1)
    res_df = pd.DataFrame(res_arr).transpose()
    res_df.columns = columns
    print(res_df)
    return res_df


if __name__ == '__main__':
    solarvation_filename = '../../data/environments/lelystad_1_2021.csv'
    max_kw = 20000
    solar_field_name = "Lelystad 1"

    # solarvation_filename = '../../data/environments/lelystad_2_2021.csv'
    # max_kw = 10000
    # solar_field_name = "Lelystad 2"

    # solarvation_filename = '../../data/environments/lelystad_3_2021.csv'
    # max_kw = 30000
    # solar_field_name = "Wissentweg"

    congestion_kw = 14000

    solarvation_df = load_solarvation_data(solarvation_filename)
    solarvation_df['congestion'], solarvation_df['excess_power'] = identify_congestion(solarvation_df, congestion_kw)

    # daily_vis(solarvation_df, dt.datetime(2021, 8, 7, tzinfo=utc))

    # start_filter = dt.datetime(2021, 6, 16, 0, 0, 0, tzinfo=utc)
    # end_filter = dt.datetime(2021, 6, 22, 0, 0, 0, tzinfo=utc)
    # solarvation_df = solarvation_df[start_filter:end_filter]

    # congestion_kw = None
    # do_basic_analysis(solarvation_df, max_kw=max_kw, congestion_kw=congestion_kw, solar_farm_name=solar_field_name)
    # do_range_investigation(solarvation_df)
    # do_monthly_analysis(solarvation_df, max_kw=max_kw, congestion_kw=congestion_kw, solar_farm_name=solar_field_name)

    starting_times, ending_times = retrieve_months(2021)
    labels = ['January', 'February', 'March', 'April', 'May', 'June',
              'July', 'August', 'September', 'October', 'November', 'December']
    res_df = time_and_size_multiple_congestion_events(solarvation_df, starting_times, ending_times, labels)
    print(res_df.to_string())

    print('2021 - Time investigation')
    print(time_congestion_events(solarvation_df))
    print('2021 - Size investigation')
    print(size_congestion_events(solarvation_df))

    # start_date = dt.datetime(2021, 1, 1, tzinfo=utc)
    # end_date = dt.datetime(2022, 1, 1, tzinfo=utc)
    # start_hours = dt.time(6, 24, tzinfo=utc)
    # end_hours = dt.time(17, 15, tzinfo=utc)
    #
    # make_congestion_series(solarvation_df, start_date, end_date, start_hours, end_hours)
