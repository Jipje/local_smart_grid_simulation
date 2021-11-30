from csv import reader
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def trivial_kw_per_minute(total_kwh, number_of_minutes=5):
    kwh_per_minute = total_kwh / number_of_minutes
    kw_per_minute = kwh_per_minute * 60

    return kw_per_minute


if __name__ == '__main__':
    with open('data/wind_net_csv.csv', 'r') as read_obj:
        csv_reader = reader(read_obj)
        header = False
        for wind_net_data in csv_reader:
            if not header:
                header = True
                continue
            end_of_5m_interval = dt.datetime.strptime(wind_net_data[0], '%d/%m/%Y %H:%M').replace(tzinfo=ams)
            end_of_5m_interval = end_of_5m_interval.astimezone(utc)
            start_of_5m_interval = end_of_5m_interval - dt.timedelta(minutes=5)
            print(start_of_5m_interval)
            print(end_of_5m_interval)

            time_tracker = start_of_5m_interval
            neushoorntocht_consumed_kw = trivial_kw_per_minute(float(wind_net_data[1]))
            neushoorntocht_produced_kw = trivial_kw_per_minute(float(wind_net_data[2]))
            mammoettocht_consumed_kw = trivial_kw_per_minute(float(wind_net_data[3]))
            mammoettocht_produced_kw = trivial_kw_per_minute(float(wind_net_data[4]))
            while time_tracker < end_of_5m_interval:
                print(time_tracker)
                print(neushoorntocht_consumed_kw)
                print(neushoorntocht_produced_kw)
                print(mammoettocht_consumed_kw)
                print(mammoettocht_produced_kw)
                time_tracker += dt.timedelta(minutes=1)
            break
