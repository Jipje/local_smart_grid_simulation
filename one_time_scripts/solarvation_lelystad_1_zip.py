import pandas as pd
import datetime as dt
import dateutil.tz

utc = dateutil.tz.tzutc()

if __name__ == '__main__':
    solar_df = pd.read_csv('../data/solar_data/solarvation/solarvation_lelystad_1.csv')
    solar_df['time_utc'] = pd.to_datetime(solar_df['time_ams'], utc=True, errors='coerce')
    solar_df.index = solar_df['time_utc']
    solar_df = solar_df.drop(['time_ams', 'time_utc'], axis=1)
    solar_df = solar_df.resample('1T').interpolate(method='linear', limit=4)
    print(solar_df)

    balans_delta_df = pd.read_csv('../data/tennet_balans_delta/tennet_balans_delta_2021.csv')
    balans_delta_df.index = pd.to_datetime(balans_delta_df['time'], format='%Y-%m-%dT%H:%M:%S.000Z', utc=True, errors='coerce')
    balans_delta_df = balans_delta_df.drop(['time'], axis=1)
    print(balans_delta_df)

    res_df = pd.merge(balans_delta_df, solar_df, left_index=True, right_index=True)
    res_df['power'] = res_df['power'].astype('float64')
    res_df['irradiance'] = res_df['irradiance'].astype('float64')
    res_df['expected_power'] = res_df['expected_power'].astype('float64')
    res_df['losses'] = res_df['losses'].astype('float64')
    # res_df.to_csv('../data/environments/lelystad_1_2021.csv')
    print(res_df)
