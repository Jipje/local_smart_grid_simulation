import os
import pandas as pd
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')

if __name__ == '__main__':
    directory_str = '../data/solar_data/solarvation/raw_solarvation_lelystad_1'
    directory = os.fsencode(directory_str)

    month_tracker = None
    month_array = []
    res_df = None
    for file in os.listdir(directory):
        filename = str(os.fsdecode(file))
        filename_route = directory_str + '/' + filename
        read_file = open(filename_route, 'r', encoding='utf-16')

        counter = 0
        for row in read_file.readlines():
            row = row.replace('"', '')
            row = row.replace(',', '')
            row = row.split('\t')
            if len(row) <= 1:
                continue
            counter += 1
            if counter < 2:
                continue

            row_dict = {}
            time_ams = dt.datetime.strptime(row[0], '%a %d/%m %H:%M').replace(year=2021, tzinfo=ams)
            if month_tracker != time_ams.month and len(month_array) != 0:
                month_df = pd.DataFrame(month_array)
                month_df.index = month_df['time_ams']
                month_df = month_df.drop('time_ams', axis=1)
                if res_df is None:
                    res_df = month_df
                else:
                    res_df = res_df.append(month_df)
                print(res_df)
                month_array = []
            if month_tracker is None or month_tracker != time_ams.month:
                month_tracker = time_ams.month

            if row[1] == 'x':
                power = None
            else:
                power = float(row[1])
            if row[2] == 'x':
                irradiance = None
            else:
                irradiance = float(row[2])
            if row[3] == 'x' or row[3] == '':
                expected_power = None
            else:
                expected_power = float(row[3])

            if row[4] == '':
                lower_range = None
                upper_range = None
            else:
                range = row[4].split(' - ')
                lower_range = float(range[0])
                upper_range = float(range[1])

            if row[5].__contains__('x'):
                losses = None
            else:
                losses = float(row[5][:-2])
            row_dict = {
                'time_ams': time_ams,
                'power': power,
                'irradiance': irradiance,
                'expected_power': expected_power,
                'lower_range': lower_range,
                'upper_range': upper_range,
                'losses': losses
            }
            month_array.append(row_dict)
    res_df.to_csv('../data/solar_data/solarvation/solarvation_lelystad_1.csv')
