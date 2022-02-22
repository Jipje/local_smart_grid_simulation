import pandas as pd
import datetime as dt
import dateutil.tz

utc = dateutil.tz.tzutc()

if __name__ == '__main__':
    solar_df = pd.read_csv('../data/solar_data/solarvation/solarvation_lelystad_1.csv')
    solar_df['time_utc'] = pd.to_datetime(solar_df['time_ams'], utc=True, errors='coerce')
    solar_df.index = solar_df['time_utc']
    solar_df = solar_df.drop(['time_ams', 'time_utc'], axis=1)
    solar_df = solar_df.resample('1T').interpolate()
    print(solar_df)
