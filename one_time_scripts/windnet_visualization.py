import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def date_parser(string):
    return dt.datetime.strptime(string, '%d/%m/%Y %H:%M').replace(tzinfo=ams)


if __name__ == '__main__':
    # headers = ['time', 'neushoorntocht_consumed_kw', 'neushoorntocht_produced_kw', 'mammoettocht_consumed_kw', 'mammoettocht_produced_kw']
    base_windnet_filename = '../data/windnet/base_windnet_data_sep_2020_sep_2021.csv'
    windnet_df = pd.read_csv(base_windnet_filename, parse_dates=[0], date_parser=date_parser)
    windnet_df.index = pd.to_datetime(windnet_df['date'], errors='coerce', utc=True)

    windnet_df['nht_production_kw'] = windnet_df['nht_production_kwh'] / 5 * 60

    print(windnet_df)

    plt.hist(windnet_df['nht_production_kwh'], bins=100)
    plt.ylabel('Number of occurences')
    plt.xlabel('Generated power in 5m (kWh)')
    plt.title('Histogram of generated power by wind farm Neushoorntocht')
    plt.show()
