from csv import reader, writer
import datetime as dt
import dateutil.tz
import pandas as pd
import matplotlib.pyplot as plt
from one_time_scripts.helper_objects.SmartWindnetInterpolater import SmartWindnetInterpolater

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def trivial_kw_per_minute(total_kwh, previous_kwh, next_kwh, number_of_minutes=5):
    kwh_per_minute = total_kwh / number_of_minutes
    kw_per_minute = kwh_per_minute * 60
    kw_per_minute = round(kw_per_minute, 2)

    res = []
    for _ in range(number_of_minutes):
        res.append(kw_per_minute)
    return res


def make_trivial_windnet_csv():
    with open('../data/windnet/trivial_cleaned_windnet_data_sep_2020_sep_2021.csv', 'w+', newline='') as new_file:
        csv_writer = writer(new_file)
        csv_writer.writerow(['time', 'neushoorntocht_consumed_kw', 'neushoorntocht_produced_kw',
                             'mammoettocht_consumed_kw', 'mammoettocht_produced_kw'])
        with open('../data/windnet/base_windnet_data_sep_2020_sep_2021.csv', 'r') as read_obj:
            csv_reader = reader(read_obj)
            header = False
            for wind_net_data in csv_reader:
                if not header:
                    header = True
                    continue
                end_of_5m_interval = dt.datetime.strptime(wind_net_data[0], '%d/%m/%Y %H:%M').replace(tzinfo=ams)
                end_of_5m_interval = end_of_5m_interval.astimezone(utc)
                start_of_5m_interval = end_of_5m_interval - dt.timedelta(minutes=5)

                time_tracker = start_of_5m_interval
                neushoorntocht_consumed_kw = trivial_kw_per_minute(float(wind_net_data[1]))
                neushoorntocht_produced_kw = trivial_kw_per_minute(float(wind_net_data[2]))
                mammoettocht_consumed_kw = trivial_kw_per_minute(float(wind_net_data[3]))
                mammoettocht_produced_kw = trivial_kw_per_minute(float(wind_net_data[4]))
                while time_tracker < end_of_5m_interval:
                    time_tracker_str = time_tracker.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                    csv_row = [time_tracker_str, neushoorntocht_consumed_kw, neushoorntocht_produced_kw,
                               mammoettocht_consumed_kw, mammoettocht_produced_kw]
                    csv_writer.writerow(csv_row)
                    if time_tracker.hour == 20 and time_tracker.minute == 20:
                        print(csv_row)
                    time_tracker += dt.timedelta(minutes=1)


def viusalise_windnet_interpolation(interpolation_function=trivial_kw_per_minute, title='Trivially extrapolated 5m wind data'):
    base_windnet_df = pd.read_csv('../data/windnet/base_windnet_data_sep_2020_sep_2021.csv')

    df2 = pd.DataFrame([[None, None, None, None, None], [None, None, None, None, None]],
                       columns=['date', 'nht_usage_kwh', 'nht_production_kwh', 'mmt_usage_kwh', 'mmt_production_kwh'],
                       index=[-1, len(base_windnet_df) + 1])
    base_windnet_df = base_windnet_df.append(df2)

    res_list = []
    counter = 0
    for index, current_wind_net_data in base_windnet_df.iterrows():
        previous_wind_net_data = base_windnet_df.iloc[index - 1]
        next_wind_net_data = base_windnet_df.iloc[index + 1]

        end_of_5m_interval = dt.datetime.strptime(current_wind_net_data[0], '%d/%m/%Y %H:%M').replace(tzinfo=ams)
        end_of_5m_interval = end_of_5m_interval.astimezone(utc)
        start_of_5m_interval = end_of_5m_interval - dt.timedelta(minutes=5)

        neushoorntocht_consumed_kw = interpolation_function(float(current_wind_net_data[1]),
                                                                              float(previous_wind_net_data[1]),
                                                                              float(next_wind_net_data[1]))
        neushoorntocht_produced_kw = interpolation_function(float(current_wind_net_data[2]),
                                                                              float(previous_wind_net_data[2]),
                                                                              float(next_wind_net_data[2]))
        mammoettocht_consumed_kw = interpolation_function(float(current_wind_net_data[3]),
                                                                            float(previous_wind_net_data[3]),
                                                                            float(next_wind_net_data[3]))
        mammoettocht_produced_kw = interpolation_function(float(current_wind_net_data[4]),
                                                                            float(previous_wind_net_data[4]),
                                                                            float(next_wind_net_data[4]))

        for i in range(5):
            time_tracker = start_of_5m_interval + dt.timedelta(minutes=i)
            time_tracker_str = time_tracker.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            new_row = {
                'time': time_tracker_str,
                'neushoorntocht_consumed_kw': neushoorntocht_consumed_kw[i],
                'neushoorntocht_produced_kw': neushoorntocht_produced_kw[i],
                'mammoettocht_consumed_kw': mammoettocht_consumed_kw[i],
                'mammoettocht_produced_kw': mammoettocht_produced_kw[i]
            }
            if counter > 800:
                res_list.append(new_row)
            counter += 1
        if counter >= 1440:
            break
    res_df = pd.DataFrame(res_list)
    res_df.index = pd.to_datetime(res_df['time'], utc=False, errors='coerce')
    res_df = res_df.drop(['time'], axis=1)

    plt.plot(res_df.index, res_df['neushoorntocht_produced_kw'])
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel('Produced power (kW)')
    plt.ylim(0, 1100)
    plt.show()


def pandas_linear_interpolation():
    base_windnet_df = pd.read_csv('../data/windnet/base_windnet_data_sep_2020_sep_2021.csv')

    base_windnet_df.index = pd.to_datetime(base_windnet_df['date'], utc=False, errors='coerce')
    base_windnet_df.index = base_windnet_df.index.tz_localize(ams, ambiguous='infer')
    base_windnet_df = base_windnet_df.drop(['date'], axis=1)

    base_windnet_df['neushoorntocht_produced_kw'] = base_windnet_df['nht_production_kwh'] * 12

    base_windnet_df = base_windnet_df.resample('1T').interpolate()

    filtered_df = base_windnet_df.iloc[800:1440]

    plt.plot(filtered_df.index, filtered_df['neushoorntocht_produced_kw'])
    plt.title('Pandas linear interpolation 5m wind data')
    plt.xlabel('Time')
    plt.ylabel('Produced power (kW)')
    plt.ylim(0, 1100)
    plt.show()


if __name__ == '__main__':
    viusalise_windnet_interpolation()
    smart_windnet_interpolater = SmartWindnetInterpolater()
    viusalise_windnet_interpolation(smart_windnet_interpolater.kw_per_minute, title='Own faulty interpolation 5m wind data')
    pandas_linear_interpolation()
