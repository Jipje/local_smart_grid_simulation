import datetime as dt
import dateutil.tz
import pandas as pd

utc = dateutil.tz.tzutc()


def time_and_size_multiple_congestion_events(solarvation_df, starting_times, ending_times, labels=None, verbose_lvl=1):
    res_arr = []
    for i in range(len(starting_times)):
        period_df = solarvation_df[starting_times[i]:ending_times[i]]

        if labels is not None and verbose_lvl > 3:
            print(labels[i] + ' - Time investigation')
        res_dict = time_congestion_events(period_df, verbose_lvl)
        if labels is not None and verbose_lvl > 3:
            print(labels[i] + ' - Size investigation')
        size_dict = size_congestion_events(period_df, verbose_lvl)

        res_dict.update(size_dict)
        res_dict = time_and_size_congestion_dict(res_dict)

        res_arr.append(res_dict)
    res_df = pd.DataFrame(res_arr)
    res_df = res_df.transpose()
    if labels is not None:
        res_df.columns = labels
    return res_df


# This method will time and size congestion slightly smarter
#  for timing that is, the earliest start time rounded down, and the latest end time rounded up
#  for sizing that is the battery should be empty enough to handle the worst case capacity * 20%
#  and there is enough hours to prepare the battery for that case
def time_and_size_leip(res_dict, max_kwh=28500, safety_margin=1.2, min_kwh=1500, max_congestion_kw=5000, max_kw=14000):
    # This simply copies the timing from the conservative system
    res_dict = time_and_size_conservative(res_dict)

    # The max capacity is multiplied with the safety margin
    max_capacity_in_congestion = abs(res_dict['max_capacity'] * safety_margin)
    # However the worst case is limited by the size of the battery
    worst_case_capacity = min(max_kwh-min_kwh, max_capacity_in_congestion)
    worst_case_capacity = round(worst_case_capacity, 0)
    # Save how much room there has to be in the battery
    res_dict['prep_max_soc'] = max_kwh - worst_case_capacity

    # So if the battery is full, how much needs to be discharged in the preparation period?
    worst_case_to_discharge_capacity = (max_kwh + min_kwh) - res_dict['prep_max_soc']
    prep_hours = round(worst_case_to_discharge_capacity / max_kw, 1)
    res_dict['prep_start'] = res_dict['congestion_start'] - dt.timedelta(hours=prep_hours)
    # And round the preparation period down to a PTU
    res_dict['prep_start'] = res_dict['prep_start'] - dt.timedelta(minutes=res_dict['prep_start'].minute % 15)
    return res_dict


# This method will time and size congestion spot on the worst case values
#  for timing that is, the earliest start time, and the latest end time
#  for sizing that is the battery should be fully empty
#  and there is 2 hours to prepare the battery for that case
def time_and_size_spot_on(res_dict):
    res_dict['congestion_start'] = res_dict['earliest_start']
    res_dict['congestion_end'] = res_dict['latest_ending']
    res_dict['prep_max_soc'] = 1500
    res_dict['prep_start'] = res_dict['congestion_start'] - dt.timedelta(hours=2)
    return res_dict


# This method will time and size congestion slightly conservatively
#  for timing that is, the earliest start time rounded down, and the latest end time rounded up
#  for sizing that is the battery should be fully empty
#  and there is 2 hours to prepare the battery for that case
def time_and_size_conservative(res_dict):
    res_dict = time_and_size_spot_on(res_dict)
    res_dict['congestion_start'] = res_dict['congestion_start'] - dt.timedelta(minutes=res_dict['congestion_start'].minute % 15)
    res_dict['congestion_end'] = res_dict['congestion_end'] + dt.timedelta(minutes=(15 - res_dict['congestion_end'].minute % 15))
    res_dict['prep_max_soc'] = 1500
    res_dict['prep_start'] = res_dict['congestion_start'] - dt.timedelta(hours=2.5)
    return res_dict


def time_and_size_congestion_dict(dict, strategy=1):
    if len(dict) == 0:
        res_dict = {'congestion_start': None,
                    'congestion_end': None,
                    'prep_max_soc': None,
                    'prep_start': None
                    }
    else:
        res_dict = time_and_size_conservative(dict)

        res_dict['congestion_start'] = res_dict['congestion_start'].time().replace(tzinfo=utc)
        res_dict['congestion_end'] = res_dict['congestion_end'].time().replace(tzinfo=utc)
        res_dict['prep_start'] = res_dict['prep_start'].time().replace(tzinfo=utc)

    return res_dict


def time_congestion_events(solarvation_df, verbose_lvl=1):
    try:
        assert 'congestion' in solarvation_df.columns
    except AssertionError:
        raise KeyError('Please offer an index DataFrame with a boolean column called congestion')

    temp_df = pd.DataFrame()
    temp_df['congestion_start'] = solarvation_df[solarvation_df['congestion']]['time']
    temp_df['congestion_end'] = temp_df['congestion_start']
    if len(temp_df) == 0:
        if verbose_lvl > 3:
            print('\tNo congestion events found.')
        return {}
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
    if verbose_lvl > 3:
        print(msg)
    res_dict = {
        'earliest_start': dt.datetime.strptime(min_start, '%H:%M:%S').replace(tzinfo=utc),
        'latest_ending': dt.datetime.strptime(max_end, '%H:%M:%S').replace(tzinfo=utc),
        'mean_start': mean_start,
        'mean_end': mean_end,
        'median_start': median_start,
        'median_end': median_end,
        'mean_length': mean_length,
        'median_length': median_length,
        'max_length': max_length,
        'min_length': min_length
    }
    return res_dict


def size_congestion_events(solarvation_df, verbose_lvl=1):
    try:
        assert 'excess_power' in solarvation_df.columns
    except AssertionError:
        raise KeyError('Please offer an index DataFrame with a column called excess_power')

    time_congestion_df = pd.DataFrame()
    time_congestion_df['max_power'] = solarvation_df[solarvation_df['congestion']]['excess_power']
    time_congestion_df['min_power'] = time_congestion_df['max_power']

    time_congestion_df['excess_capacity'] = time_congestion_df['max_power'] * 1/60

    if len(time_congestion_df) == 0:
        if verbose_lvl > 3:
            print('\tNo congestion events found.')
        return {}

    time_congestion_df = time_congestion_df.resample('1D').agg(
        {'max_power': max, 'min_power': min,  'excess_capacity': sum})

    max_power = round(time_congestion_df['max_power'].max(), 2)
    min_power = round(time_congestion_df['min_power'].min(), 2)

    max_capacity = round(time_congestion_df['excess_capacity'].max(), 2)
    min_capacity = round(time_congestion_df['excess_capacity'].min(), 2)
    median_capacity = round(time_congestion_df['excess_capacity'].median(), 2)
    mean_capacity = round(time_congestion_df['excess_capacity'].mean(), 2)

    msg = f"\tMinimum measured power during congestion is {min_power} kW\n" \
          f"\tMaximum measured power during congestion is {max_power} kW\n" \
          "-----------------------------------\n" \
          f"\tMinimum capacity generated during congestion is {min_capacity} kWh\n" \
          f"\tMaximum capacity generated during congestion is {max_capacity} kWh\n" \
          f"\tMean capacity generated during congestion is {mean_capacity} kWh\n" \
          f"\tMedian capacity generated during congestion is {median_capacity} kWh"
    if verbose_lvl > 3:
        print(msg)
    res_dict = {
        'min_power': min_power,
        'max_power': max_power,
        'min_capacity': min_capacity,
        'max_capacity': max_capacity,
        'mean_capacity': mean_capacity,
        'median_capacity': median_capacity
    }
    return res_dict


def identify_congestion(solarvation_df, congestion_kw):
    congestion_margin = 0.95
    congestion_margin_kw = congestion_margin * congestion_kw
    solarvation_df['cable_usage'] = solarvation_df['power'] / congestion_margin_kw
    solarvation_df['congestion_probability'] = solarvation_df['cable_usage'].rolling(60, min_periods=0, center=True).mean()
    solarvation_df['congestion'] = solarvation_df[['cable_usage', 'congestion_probability']].max(axis=1)
    solarvation_df['congestion'] = solarvation_df['congestion'] > 1

    solarvation_df['excess_power'] = solarvation_df['power'] - congestion_kw
    return solarvation_df['congestion'], solarvation_df['excess_power']
