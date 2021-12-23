from csv import reader, writer
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()

if __name__ == '__main__':
    with open('../../data/solar_data/radiation_with_forecast/cleaned_radiation_forecast_and_values.csv', 'w+', newline='') as new_file:
        csv_writer = writer(new_file)
        csv_writer.writerow(['time', 'radiation', 'radiation_d_1', 'radiation_d_3', 'radiation_d_5'])
        with open('../../data/solar_data/radiation_with_forecast/radiation_forecast_and_values.csv', 'r') as read_obj:
            csv_reader = reader(read_obj)
            header = False
            for radiation_data in csv_reader:
                if not header:
                    header = True
                    continue
                time_dt = dt.datetime.strptime(radiation_data[0], '%Y-%m-%dT%H:%M:%S.000Z')
                time_dt = time_dt.astimezone(utc)
                time_str = time_dt.strftime('%Y-%m-%dT%H:%M:%S%z')
                csv_row = [time_str, radiation_data[1], radiation_data[2], radiation_data[3], radiation_data[4]]
                csv_writer.writerow(csv_row)
