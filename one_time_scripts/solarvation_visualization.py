import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def date_parser(string):
    return dt.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=utc)


if __name__ == '__main__':
    solarvation_filename = '../data/solar_data/solarvation/cleaned_solarvation_1h.csv'
    solarvation_df = pd.read_csv(solarvation_filename, parse_dates=[0], date_parser=date_parser)
    solarvation_df.index = pd.to_datetime(solarvation_df['time'], errors='coerce', utc=True)
    solarvation_df = solarvation_df.drop('time', axis=1)
    # print(solarvation_df)

    plt.hist(solarvation_df['power_generation'], bins=100)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Expected power generation (calculated hourly) (kW)')
    plt.title('Histogram of modelled power generation by solar field Solarvation')
    plt.axvline(24000, color='red')
    plt.show()

    plt.hist(solarvation_df['power_generation'], bins=100)
    plt.ylim(0, 150)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Expected power generation (calculated hourly) (kW)')
    plt.title('Histogram of modelled power generation by solar field Solarvation')
    plt.axvline(24000, color='red')
    plt.show()

    solarvation_df['hour_of_production'] = solarvation_df.index.hour

    plt.scatter(solarvation_df['hour_of_production'], solarvation_df['power_generation'])
    plt.ylabel('Generated power 1h (kW)')
    plt.xlabel('Hour in which power was generated (UTC)')
    plt.title('Scatterplot of generated power by solar field Solarvation')
    plt.show()

    my_solar_farm_kwp = solarvation_df['power_generation'].max()
    solar_power_mw_df = pd.read_csv('../data/solar_data/solar_power/cleaned_solar_production.csv', parse_dates=[0], date_parser=date_parser)
    solar_power_mw_df.index = pd.to_datetime(solar_power_mw_df['time'], errors='coerce', utc=True)
    solar_power_mw_df = solar_power_mw_df.drop('time', axis=1)

    solar_power_mw_df['hour_of_production'] = solar_power_mw_df.index.hour
    solar_power_mw_df['cloud_coverage'] = solar_power_mw_df['solar_mw'] / solar_power_mw_df['solar_mw'].max()
    solar_power_mw_df['kw_my_solar_farm'] = solar_power_mw_df['cloud_coverage'] * my_solar_farm_kwp

    plt.scatter(solar_power_mw_df['hour_of_production'], solar_power_mw_df['kw_my_solar_farm'])
    plt.ylabel('Generated power 15m (kW)')
    plt.xlabel('Hour in which power was generated (UTC)')
    plt.title('Scatterplot of generated power by own model solar field')
    plt.show()
