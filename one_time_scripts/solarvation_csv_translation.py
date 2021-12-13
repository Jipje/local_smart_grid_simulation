from csv import reader, writer
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()

if __name__ == '__main__':
    with open('../data/solarvation/cleaned_solarvation_1h.csv', 'w+', newline='') as new_file:
        csv_writer = writer(new_file)
        csv_writer.writerow(['time', 'irradation', 'temperature',
                             'wind_speed', 'power_generation'])
        with open('../data/solarvation/original_data.csv', 'r') as read_obj:
            csv_reader = reader(read_obj)
            header = False
            for solarvation_data in csv_reader:
                if not header:
                    header = True
                    continue
                time_dt = dt.datetime.strptime(solarvation_data[0], '%d/%m/%Y %H:%M')
                time_dt = time_dt.replace(year=2021, tzinfo=ams)
                time_dt = time_dt.astimezone(utc)
                time_str = time_dt.strftime('%Y-%m-%dT%H:%M:%S.000Z')
                csv_row = [time_str, solarvation_data[1], solarvation_data[2], solarvation_data[3], solarvation_data[4]]
                csv_writer.writerow(csv_row)
