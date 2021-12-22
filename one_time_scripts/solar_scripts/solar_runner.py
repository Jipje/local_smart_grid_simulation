import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import dateutil.tz
from sklearn.metrics import mean_squared_error

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def date_parser(string):
    return dt.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=utc)


if __name__ == '__main__':
    solar_power_mw_df = pd.read_csv('../../data/solar_data/solar_power/cleaned_solar_production.csv', parse_dates=[0], date_parser=date_parser)
    solar_power_mw_df.index = pd.to_datetime(solar_power_mw_df['time'], errors='coerce', utc=True)
    solar_power_mw_df = solar_power_mw_df.drop('time', axis=1)
    # print(solar_power_mw_df)

    radiation_df = pd.read_csv('../../data/solar_data/radiation_with_forecast/cleaned_radiation_forecast_and_values.csv', parse_dates=[0], date_parser=date_parser)
    radiation_df.index = pd.to_datetime(radiation_df['time'], errors='coerce', utc=True)
    radiation_df = radiation_df.drop('time', axis=1)
    # print(radiation_df)

    radiation_df = radiation_df.resample('15T').pad()
    res_df = solar_power_mw_df.merge(radiation_df, how='inner', left_index=True, right_index=True)
    # print(res_df)

    res_df['total_m2_solar'] = res_df['solar_mw'] * 1000 / res_df['radiation']
    my_solar_farm_m2 = 10
    res_df['cloud_coverage'] = res_df['solar_mw'] / res_df['solar_mw'].max()
    # res_df['kw_my_solar_farm'] = my_solar_farm_m2 / res_df['total_m2_solar'] * res_df['solar_mw'] * 1000
    res_df['kw_my_solar_farm'] = res_df['cloud_coverage'] * my_solar_farm_m2 * res_df['radiation']

    # start_of_set = dt.datetime(2021, 7, 10, tzinfo=utc)
    # end_of_set = dt.datetime(2021, 7, 12, tzinfo=utc)
    # res_df = res_df[start_of_set:end_of_set]

    print(res_df.to_string())

    res_df['hour_of_production'] = res_df.index.hour

    plt.scatter(res_df['hour_of_production'], res_df['kw_my_solar_farm'])
    plt.ylabel('Generated power 15m (kW)')
    plt.xlabel('Hour in which power was generated (UTC)')
    plt.title('Scatterplot of generated power by generic solar farm')
    plt.show()
