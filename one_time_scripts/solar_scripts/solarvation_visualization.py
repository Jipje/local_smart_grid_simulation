import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def date_parser(string):
    return dt.datetime.strptime(string, '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=utc)


if __name__ == '__main__':
    solarvation_filename = '../../data/environments/lelystad_1_2021.csv'
    solarvation_df = pd.read_csv(solarvation_filename, parse_dates=[0], date_parser=date_parser)
    solarvation_df.index = pd.to_datetime(solarvation_df['time_utc'], errors='coerce', utc=True)
    solarvation_df = solarvation_df.drop('time_utc', axis=1)
    print(solarvation_df)

    # ['tennet_balansdelta.mean_max_price', 'tennet_balansdelta.mean_mid_price', 'tennet_balansdelta.mean_min_price',
    #  'power', 'irradiance', 'expected_power', 'lower_range', 'upper_range', 'losses']
    plt.hist(solarvation_df['power'], bins=100)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Power generation (kW)')
    plt.title('Histogram of power generation by solar field Lelystad 1')
    plt.show()

    plt.hist(solarvation_df['power'], bins=100)
    plt.ylim(0, 4000)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Power generation (kW)')
    plt.title('Histogram of power generation by solar field Lelystad 1')
    plt.show()

    solarvation_df['hour_of_production'] = solarvation_df.index.hour

    plt.scatter(solarvation_df['hour_of_production'], solarvation_df['power'])
    plt.ylabel('Generated power 1m (kW)')
    plt.xlabel('Hour in which power was generated (UTC)')
    plt.title('Scatterplot of power generation by solar field Lelystad 1')
    plt.show()
