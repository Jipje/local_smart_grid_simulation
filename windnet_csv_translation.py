from csv import reader
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()

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
            neushoorntocht_produced_kwh = float(wind_net_data[2])
            print(neushoorntocht_produced_kwh)
            mammoettocht_produced_kwh = float(wind_net_data[4])
            print(mammoettocht_produced_kwh)
            break
