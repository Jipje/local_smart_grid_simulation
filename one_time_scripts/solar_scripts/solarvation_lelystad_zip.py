import pandas as pd
import dateutil.tz

utc = dateutil.tz.tzutc()

if __name__ == '__main__':
    choose_a_number_1_or_2_or_3 = 3

    if choose_a_number_1_or_2_or_3 == 3:
        solar_df_1 = pd.read_csv(f'../../data/solar_data/solarvation/solarvation_lelystad_1.csv')
        solar_df_1.index = pd.to_datetime(solar_df_1['time_ams'], utc=True)
        solar_df_1 = solar_df_1.drop(['time_ams'], axis=1)

        solar_df_2 = pd.read_csv(f'../../data/solar_data/solarvation/solarvation_lelystad_2.csv')
        solar_df_2.index = pd.to_datetime(solar_df_2['time_ams'], utc=True)
        solar_df_2 = solar_df_2.drop(['time_ams'], axis=1)

        joined_solar_df = solar_df_1.join(solar_df_2, how='inner', lsuffix='_1', rsuffix='_2')
        joined_solar_df['power'] = joined_solar_df['power_1'] + joined_solar_df['power_2']
        joined_solar_df['irradiance'] = joined_solar_df['irradiance_1'] + joined_solar_df['irradiance_2'] / 2
        joined_solar_df['expected_power'] = joined_solar_df['expected_power_1'] + joined_solar_df['expected_power_2']
        joined_solar_df['lower_range'] = joined_solar_df['lower_range_1'] + joined_solar_df['lower_range_2']
        joined_solar_df['upper_range'] = joined_solar_df['upper_range_1'] + joined_solar_df['upper_range_2']
        joined_solar_df['losses'] = joined_solar_df['losses_1'] + joined_solar_df['losses_2']

        joined_solar_df = joined_solar_df.drop(['power_1', 'power_2', 'irradiance_1', 'irradiance_2',
                                                'expected_power_1', 'expected_power_2', 'lower_range_1', 'lower_range_2',
                                                'upper_range_1', 'upper_range_2', 'losses_1', 'losses_2'], axis=1)
        solar_df = joined_solar_df.resample('1T').interpolate(method='linear', limit=4)

    else:
        solar_df = pd.read_csv(f'../../data/solar_data/solarvation/solarvation_lelystad_{choose_a_number_1_or_2_or_3}.csv')
        solar_df.index = pd.to_datetime(solar_df['time_ams'], utc=True)
        solar_df = solar_df.drop(['time_ams'], axis=1)

        solar_df = solar_df.resample('1T').interpolate(method='linear', limit=4)
    print(solar_df)

    balans_delta_df = pd.read_csv('../../data/tennet_balans_delta/tennet_balans_delta_2021.csv')
    balans_delta_df.index = pd.to_datetime(balans_delta_df['time'], format='%Y-%m-%dT%H:%M:%S.000Z', utc=True, errors='coerce')
    balans_delta_df = balans_delta_df.drop(['time'], axis=1)
    print(balans_delta_df)

    res_df = pd.merge(balans_delta_df, solar_df, left_index=True, right_index=True)
    res_df['power'] = res_df['power'].astype('float64')
    res_df['irradiance'] = res_df['irradiance'].astype('float64')
    res_df['expected_power'] = res_df['expected_power'].astype('float64')
    res_df['losses'] = res_df['losses'].astype('float64')
    # TODO automatically add time_utc label to the columns
    res_df.to_csv(f'../../data/environments/lelystad_{choose_a_number_1_or_2_or_3}_2021.csv')
    print(res_df)
