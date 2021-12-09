from csv import reader, writer
import datetime as dt
import dateutil.tz
import pandas as pd
import matplotlib.pyplot as plt

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def trivial_kw_per_minute(total_kwh, number_of_minutes=5):
    kwh_per_minute = total_kwh / number_of_minutes
    kw_per_minute = kwh_per_minute * 60
    kw_per_minute = round(kw_per_minute, 2)

    res = []
    for i in range(number_of_minutes):
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
                    csv_row = [time_tracker_str, neushoorntocht_consumed_kw, neushoorntocht_produced_kw, mammoettocht_consumed_kw, mammoettocht_produced_kw]
                    csv_writer.writerow(csv_row)
                    if time_tracker.hour == 20 and time_tracker.minute == 20:
                        print(csv_row)
                    time_tracker += dt.timedelta(minutes=1)


def viusalise_trivial_windnet_interpolation():
    with open('../data/windnet/base_windnet_data_sep_2020_sep_2021.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)

        res_list = []
        header = False
        counter = 0
        for wind_net_data in csv_reader:
            if not header:
                header = True
                continue
            end_of_5m_interval = dt.datetime.strptime(wind_net_data[0], '%d/%m/%Y %H:%M').replace(tzinfo=ams)
            end_of_5m_interval = end_of_5m_interval.astimezone(utc)
            start_of_5m_interval = end_of_5m_interval - dt.timedelta(minutes=5)

            neushoorntocht_consumed_kw = trivial_kw_per_minute(float(wind_net_data[1]))
            neushoorntocht_produced_kw = trivial_kw_per_minute(float(wind_net_data[2]))
            mammoettocht_consumed_kw = trivial_kw_per_minute(float(wind_net_data[3]))
            mammoettocht_produced_kw = trivial_kw_per_minute(float(wind_net_data[4]))

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
                res_list.append(new_row)
                counter += 1
            if counter >= 1440:
                break
    res_df = pd.DataFrame(res_list)
    res_df.index = pd.to_datetime(res_df['time'], utc=False, errors='coerce')
    res_df = res_df.drop(['time'], axis=1)

    plt.plot(res_df.index, res_df['neushoorntocht_produced_kw'])
    plt.title('Trivially extrapolated 5m wind data')
    plt.xlabel('Time')
    plt.ylabel('Produced power (kW)')
    plt.show()


if __name__ == '__main__':
    viusalise_trivial_windnet_interpolation()
