from csv import reader, writer
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()

if __name__ == '__main__':
    with open('../../data/solar_data/solar_power/cleaned_solar_forecast.csv', 'w+', newline='') as new_file:
        csv_writer = writer(new_file)
        csv_writer.writerow(['time', 'solar_mw'])
        with open('../../data/solar_data/solar_power/solar_forecast_okt_2021.csv', 'r') as read_obj:
            csv_reader = reader(read_obj)
            header = False
            for solar_forecast in csv_reader:
                if not header:
                    header = True
                    continue
                time_dt = dt.datetime.strptime(solar_forecast[0], '%Y-%m-%dT%H:%M:%S.000Z')
                time_dt = time_dt.astimezone(utc)
                time_str = time_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
                csv_row = [time_str, solar_forecast[1]]
                csv_writer.writerow(csv_row)
