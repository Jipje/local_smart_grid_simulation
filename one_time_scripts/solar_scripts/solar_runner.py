import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import datetime as dt
import dateutil.tz

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

    # First design decision, pad or interpolate 1h radiation data?
    # radiation_df = radiation_df.resample('15T').pad()
    radiation_df = radiation_df.resample('15T').interpolate()
    res_df = solar_power_mw_df.merge(radiation_df, how='inner', left_index=True, right_index=True)
    # print(res_df)

    my_solar_farm_m2 = 45
    my_solar_farm_kwp = 36350

    # Second method
    res_df['solar_farms_m2'] = res_df['solar_mw'] * 1000 / res_df['radiation']
    # Third method and Fifth method
    res_df['cloud_coverage'] = res_df['solar_mw'] / res_df['solar_mw'].max()
    # Fourth method
    res_df['cloud_coverage_rolling'] = res_df['solar_mw'] / res_df['solar_mw'].rolling(180).max()

    # First method - Simply take radiation
    res_df['kw_my_solar_farm'] = my_solar_farm_m2 * res_df['radiation']

    # However that does not take into account the efficiency of our solar panels.
    #  It assumes all power that reaches them is translated into energy, that is not the case.
    #  The total solar production offers us data on how efficient the solar panels are running

    # Second method - Based on m2 of windfarms
    res_df['kw_my_solar_farm_2'] = my_solar_farm_m2 / res_df['solar_farms_m2'] * res_df['solar_mw'] * 1000
    res_df['kw_my_solar_farm_2'].replace(np.NaN, 0, inplace=True)

    # Third method
    res_df['kw_my_solar_farm_3'] = res_df['cloud_coverage'] * my_solar_farm_m2 * res_df['radiation']

    # Fourth method
    res_df['kw_my_solar_farm_4'] = res_df['cloud_coverage_rolling'] * my_solar_farm_m2 * res_df['radiation']

    # Fifth method
    res_df['kw_my_solar_farm_5'] = res_df['cloud_coverage'] * my_solar_farm_kwp

    res_df['hour_of_production'] = res_df.index.hour

    plt.scatter(res_df['hour_of_production'], res_df['kw_my_solar_farm_5'])
    plt.ylabel('Generated power 15m (kW)')
    plt.xlabel('Hour in which power was generated (UTC)')
    plt.title('Scatterplot of generated power by generic solar farm')
    plt.show()

    start_of_set = dt.datetime(2021, 7, 15, tzinfo=utc)
    end_of_set = dt.datetime(2021, 7, 19, tzinfo=utc)
    res_df = res_df[start_of_set:end_of_set]
    # print(res_df.to_string())
    plt.plot(res_df.index, res_df['kw_my_solar_farm'], label='Radiation method')
    plt.plot(res_df.index, res_df['kw_my_solar_farm_2'], label='m2 of solar farms')
    plt.plot(res_df.index, res_df['kw_my_solar_farm_3'], label='Cloud coverage large max')
    plt.plot(res_df.index, res_df['kw_my_solar_farm_4'], label='Cloud coverage rolling window')
    plt.plot(res_df.index, res_df['kw_my_solar_farm_5'], label='Power cloud coverage on max kW')
    ax = plt.gca()
    max_formatter = mdates.DateFormatter('%d-%m')
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(max_formatter)
    plt.ylabel('Genrated power (kW)')
    plt.xlabel('Time (UTC)')
    plt.title('Generated power for {}m2 solar farm.'.format(my_solar_farm_m2))
    plt.legend(loc='lower right')
    plt.show()
