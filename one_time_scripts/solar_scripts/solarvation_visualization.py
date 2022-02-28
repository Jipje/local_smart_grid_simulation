import matplotlib.dates as mdates
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
    solarvation_df['time'] = solarvation_df['time_utc'].apply(lambda x: x.replace(year=1970, month=1, day=1))

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

    temp_df = pd.DataFrame()
    temp_df['congestion_start'] = solarvation_df[solarvation_df['congestion']]['time']
    temp_df['congestion_end'] = temp_df['congestion_start']
    if len(temp_df) == 0:
        print('\tNo congestion events found.')
        return 0
    temp_df = temp_df.resample('1D').agg({'congestion_start': min, 'congestion_end': max})
    temp_df['congestion_length'] = temp_df['congestion_end'] - temp_df['congestion_start']

    time_congestion_df = pd.merge(solarvation_df, temp_df, left_index=True, right_index=True, how='left')

    min_start = time_congestion_df['congestion_start'].min().strftime('%X')
    max_end = time_congestion_df['congestion_end'].max().strftime('%X')
    mean_start = time_congestion_df['congestion_start'].mean().strftime('%X')
    mean_end = time_congestion_df['congestion_end'].mean().strftime('%X')
    median_start = time_congestion_df['congestion_start'].median().strftime('%X')
    median_end = time_congestion_df['congestion_end'].median().strftime('%X')

    mean_length = time_congestion_df['congestion_length'].mean()
    median_length = time_congestion_df['congestion_length'].median()
    max_length = time_congestion_df['congestion_length'].max()
    min_length = time_congestion_df[time_congestion_df['congestion_length'] > dt.timedelta(minutes=0)]['congestion_length'].min()

    # print(solarvation_df[solarvation_df['congestion_length'] == min_length])

    msg = f"\tEarliest starting time of congestion is {min_start}\n" \
          f"\tLatest ending time of congestion is {max_end}\n" \
          f"\tMean start time of congestion is {mean_start}\n" \
          f"\tMean end time of congestion is {mean_end}\n" \
          f"\tMedian start time of congestion is {median_start}\n" \
          f"\tMedian end time of congestion is {median_end}\n" \
          "-----------------------------------\n" \
          f"\tMean congestion length is {mean_length}\n" \
          f"\tMedian congestion length is {median_length}\n" \
          f"\tMax congestion length is {max_length}\n" \
          f"\tMin congestion length is {min_length}"
    print(msg)


def size_congestion_events(solarvation_df, congestion_size=10000):
    try:
        assert 'congestion' in solarvation_df.columns
    except AssertionError:
        raise KeyError('Please offer an index DataFrame with a boolean column called congestion')

    temp_df = pd.DataFrame()
    temp_df['excess_power'] = solarvation_df[solarvation_df['congestion']]['power'] - congestion_size
    temp_df['congestion_day_counter'] = 1
    temp_df['excess_capacity'] = temp_df['excess_power'] * 1/60
    if len(temp_df) == 0:
        print('\tNo congestion events found.')
        return 0
    temp_df = temp_df.resample('1D').agg({'excess_power': sum, 'congestion_day_counter': sum, 'excess_capacity': sum})
    temp_df['excess_power'] = temp_df['excess_power'] / temp_df['congestion_day_counter']
    temp_df = temp_df.drop('congestion_day_counter', axis=1)

    print(temp_df)
    time_congestion_df = pd.merge(solarvation_df, temp_df, left_index=True, right_index=True, how='left')

    min_power = time_congestion_df['excess_power'].min()
    max_power = time_congestion_df['excess_power'].max()
    mean_power = time_congestion_df['excess_power'].mean()
    median_power = time_congestion_df['excess_power'].median()

    min_capacity = time_congestion_df['excess_capacity'].min()
    max_capacity = time_congestion_df['excess_capacity'].max()
    mean_capacity = time_congestion_df['excess_capacity'].mean()
    median_capacity = time_congestion_df['excess_capacity'].median()

    msg = f"\tMinimum measured power during congestion is {min_power} kW\n" \
          f"\tMaximum measured power during congestion is {max_power} kW\n" \
          f"\tMean measured power during congestion is {mean_power} kW\n" \
          f"\tMedian measured power during congestion is {median_power} kW\n" \
          "-----------------------------------\n" \
          f"\tMinimum capacity generated during congestion length is {min_capacity} kWh\n" \
          f"\tMaximum capacity generated during congestion is {max_capacity} kWh\n" \
          f"\tMean capacity generated during congestion is {mean_capacity} kWh\n" \
          f"\tMedian capacity generated during congestion is {median_capacity} kWh"
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


def main():
    # solarvation_df = load_solarvation_data(solarvation_filename='../../data/solar_data/solarvation/solarvation_lelystad_1.csv')
    solarvation_df = load_solarvation_data()

    # start_filter = dt.datetime(2021, 6, 16, 0, 0, 0, tzinfo=utc)
    # end_filter = dt.datetime(2021, 6, 22, 0, 0, 0, tzinfo=utc)
    # solarvation_df = solarvation_df[start_filter:end_filter]

    do_basic_analysis(solarvation_df)

    do_range_investigation(solarvation_df)

    solarvation_df['congestion'] = identify_congestion(solarvation_df, 10000)
    print()
    do_monthly_analysis(solarvation_df)

    # temp_solarvation_df = solarvation_df[solarvation_df['congestion']]
    # do_monthly_analysis(temp_solarvation_df)

    print("CONGESTION TIME INVESTIGATION OF 2021")
    time_congestion_events(solarvation_df)

    # daily_vis(solarvation_df, dt.datetime(2021, 2, 24, tzinfo=utc))


def retrieve_quarters(year=2021):
    starting_times = []
    ending_times = []
    for i in range(4):
        start_month = i * 3 + 1
        end_month = start_month + 3

        if end_month == 13:
            end_q = dt.datetime(year + 1, 1, 1, tzinfo=utc)
        else:
            end_q = dt.datetime(year, end_month, 1, tzinfo=utc)
        start_q = dt.datetime(year, start_month, 1, tzinfo=utc)

        starting_times.append(start_q)
        ending_times.append(end_q)
    return starting_times, ending_times


def time_multiple_congestion_events(solarvation_df, starting_times, ending_times, labels=None):
    for i in range(len(starting_times)):
        period_df = solarvation_df[starting_times[i]:ending_times[i]]

        if labels is not None:
            print(labels[i])
        time_congestion_events(period_df)
        size_congestion_events(period_df)


if __name__ == '__main__':
    # main()
    solarvation_df = load_solarvation_data()
    solarvation_df['congestion'] = identify_congestion(solarvation_df, 10000)

    starting_times, ending_times = retrieve_quarters()
    labels = ['Analyzing Q1', 'Analyzing Q2', 'Analyzing Q3', 'Analyzing Q4']
    time_multiple_congestion_events(solarvation_df, starting_times, ending_times, labels)

    # start_date = dt.datetime(2021, 1, 1, tzinfo=utc)
    # end_date = dt.datetime(2022, 1, 1, tzinfo=utc)
    # start_hours = dt.time(6, 24, tzinfo=utc)
    # end_hours = dt.time(17, 15, tzinfo=utc)
    #
    # make_congestion_series(solarvation_df, start_date, end_date, start_hours, end_hours)

    # size_congestion_events(solarvation_df)
