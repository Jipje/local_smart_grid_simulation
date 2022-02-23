import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import dateutil.tz

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

    return solarvation_df


def do_basic_analysis(solarvation_df):
    # ['tennet_balansdelta.mean_max_price', 'tennet_balansdelta.mean_mid_price', 'tennet_balansdelta.mean_min_price',
    #  'power', 'irradiance', 'expected_power', 'lower_range', 'upper_range', 'losses']
    plt.hist(solarvation_df['power'], bins=100)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Power generation (kW)')
    plt.title('Histogram of power generation by solar field Lelystad 1')
    plt.show()

    plt.hist(solarvation_df['power'], bins=100)
    plt.ylim(0, 4000)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Power generation (kW)')
    plt.title('Histogram of power generation by solar field Lelystad 1')
    plt.show()

    plt.scatter(solarvation_df['hour_of_production'], solarvation_df['power'])
    plt.ylabel('Generated power 1m (kW)')
    plt.xlabel('Hour in which power was generated (UTC)')
    plt.title('Scatterplot of power generation by solar field Lelystad 1')
    plt.ylim(0, 20000)
    plt.show()


def do_monthly_analysis(solarvation_df):
    fig, axs = plt.subplots(4, 3, figsize=(12, 9))
    for i in range(1, 13):
        month = i
        start_of_month = dt.datetime(2021, month, 1, tzinfo=utc)
        temp_day = start_of_month.replace(day=28) + dt.timedelta(days=4)
        end_of_month = temp_day - dt.timedelta(days=temp_day.day)

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
        axs[axes_x, axes_y].scatter(month_df['hour_of_production'], month_df['power'])
        axs[axes_x, axes_y].set_title('{}'.format(start_of_month.strftime('%B')))
        axs[axes_x, axes_y].set_ylim((0, 20000))
        axs[axes_x, axes_y].set_xlim((0, 23))
    fig.suptitle('Scatterplot of generated power per month')
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

    faulty_df = filtered_df[~filtered_df['20_perc_upper_range_correct']]
    print(faulty_df[['power', 'upper_range', '20_perc_upper_range']])


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


def identify_congestion(solarvation_df, congestion_kw):
    congestion_margin = 0.95
    congestion_margin_kw = congestion_margin * congestion_kw
    solarvation_df['cable_usage'] = solarvation_df['power'] / congestion_margin_kw
    solarvation_df['congestion_probability'] = solarvation_df['cable_usage'].rolling(60, min_periods=0, center=True).mean()
    solarvation_df['congestion'] = solarvation_df[['cable_usage', 'congestion_probability']].max(axis=1)
    solarvation_df['congestion'] = solarvation_df['congestion'] > 1
    return solarvation_df['congestion']


def time_congestion_events(solarvation_df):
    try:
        assert 'congestion' in solarvation_df.columns
    except AssertionError:
        raise KeyError('Please offer an index DataFrame with a boolean column called congestion')

    solarvation_df['time'] = solarvation_df['time_utc'].apply(lambda x: x.replace(year=1970, month=1, day=1))

    temp_df = pd.DataFrame()
    temp_df['congestion_time'] = solarvation_df[solarvation_df['congestion']]['time']

    solarvation_df = pd.merge(solarvation_df, temp_df, left_index=True, right_index=True, how='left')

    min_start = solarvation_df['congestion_time'].min().strftime('%X')
    max_end = solarvation_df['congestion_time'].max().strftime('%X')
    msg = "Earliest starting time of congestion is {}\n" \
          "Latest ending time of congestion is {}".format(min_start, max_end)
    print(msg)


if __name__ == '__main__':
    # solarvation_df = load_solarvation_data(solarvation_filename='../../data/solar_data/solarvation/solarvation_lelystad_1.csv')
    solarvation_df = load_solarvation_data()

    # start_filter = dt.datetime(2021, 4, 30, 0, 0, 0, tzinfo=utc)
    # end_filter = dt.datetime(2021, 9, 1, 0, 0, 0, tzinfo=utc)
    # solarvation_df = solarvation_df[start_filter:end_filter]

    # do_basic_analysis(solarvation_df)

    # do_monthly_analysis(solarvation_df)

    # do_range_investigation(solarvation_df)

    solarvation_df['congestion'] = identify_congestion(solarvation_df, 10000)

    # temp_solarvation_df = solarvation_df[solarvation_df['congestion']]
    # do_monthly_analysis(temp_solarvation_df)

    time_congestion_events(solarvation_df)


def weird_vis():
    solarvation_df['time'] = solarvation_df['timestamp'].apply(lambda x: x.replace(year=2021, month=1, day=1))
    counter = 0
    start_day = solarvation_df.iloc[0].timestamp.to_pydatetime().replace(hour=0)

    solarvation_df = solarvation_df.resample('1H').max()
    print(solarvation_df)
    for day_index in range(int(len(solarvation_df) / 1440)):
        current_day_start = (start_day + dt.timedelta(days=day_index)).replace(hour=0, minute=0)
        current_day_end = current_day_start + dt.timedelta(days=1) - dt.timedelta(minutes=1)

        current_day_str = current_day_start.strftime('%b %d')
        current_day_df = solarvation_df[current_day_start:current_day_end]
        congestion_current_day = current_day_df[current_day_df['congestion']]
        counter += 1

        plt.scatter(congestion_current_day['time'], congestion_current_day['power'], label=current_day_str)
        if counter == 7:
            break
    # plt.legend()
    plt.show()
