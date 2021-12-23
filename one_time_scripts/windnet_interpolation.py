import datetime as dt
import dateutil.tz
import pandas as pd
import matplotlib.pyplot as plt

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()

start_graph = dt.datetime(2021, 3, 20, 18, tzinfo=utc)
end_graph = start_graph + dt.timedelta(minutes=240)


def trivial_interpolation_windnet():
    base_windnet_df = pd.read_csv('../data/windnet/cleaned_windnet_data_aug_2020_sep_2021.csv')
    base_windnet_df.index = pd.to_datetime(base_windnet_df['date'], utc=True, errors='coerce')
    base_windnet_df.index = base_windnet_df.index - dt.timedelta(minutes=5)
    base_windnet_df = base_windnet_df.drop(['date'], axis=1)

    base_windnet_df['nht_usage_kwh'] = base_windnet_df['nht_usage_kwh'] / 5
    base_windnet_df['nht_production_kwh'] = base_windnet_df['nht_production_kwh'] / 5
    base_windnet_df['mmt_usage_kwh'] = base_windnet_df['mmt_usage_kwh'] / 5
    base_windnet_df['mmt_production_kwh'] = base_windnet_df['mmt_production_kwh'] / 5

    base_windnet_df = base_windnet_df.resample('1T').pad()
    return base_windnet_df


def pandas_linear_interpolation_windnet():
    base_windnet_df = pd.read_csv('../data/windnet/cleaned_windnet_data_aug_2020_sep_2021.csv')
    base_windnet_df.index = pd.to_datetime(base_windnet_df['date'], utc=True, errors='coerce')
    base_windnet_df.index = base_windnet_df.index - dt.timedelta(minutes=5)
    base_windnet_df = base_windnet_df.drop(['date', 'nht_usage_kwh', 'nht_production_kwh', 'mmt_usage_kwh', 'mmt_production_kwh'], axis=1)

    base_windnet_df = base_windnet_df.resample('1T').interpolate()

    base_windnet_df['nht_usage_kwh'] = base_windnet_df['nht_usage_kw'] / 60
    base_windnet_df['nht_production_kwh'] = base_windnet_df['nht_production_kw'] / 60
    base_windnet_df['mmt_usage_kwh'] = base_windnet_df['mmt_usage_kw'] / 60
    base_windnet_df['mmt_production_kwh'] = base_windnet_df['mmt_production_kw'] / 60

    return base_windnet_df


def csv_maker():
    trivial_df = trivial_interpolation_windnet()
    pandas_df = pandas_linear_interpolation_windnet()

    print(trivial_df)
    print(pandas_df)

    trivial_df.to_csv('../data/windnet/trivial_cleaned_windnet_data_sep_2020_sep_2021.csv')
    trivial_df.to_csv('../data/windnet/trivial_interpolation_windnet.csv')
    pandas_df.to_csv('../data/windnet/pandas_interpolation_windnet.csv')


def make_simple_graph(filtered_df, title):
    plt.plot(filtered_df.index, filtered_df['nht_production_kw'], marker='o')
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel('Produced power (kW)')
    plt.show()


if __name__ == '__main__':
    # csv_maker()

    original_df = pd.read_csv('../data/windnet/cleaned_windnet_data_aug_2020_sep_2021.csv')
    original_df.index = pd.to_datetime(original_df['date'], utc=True, errors='coerce')
    original_df.index = original_df.index - dt.timedelta(minutes=5)
    original_df = original_df.drop(['date'], axis=1)

    trivial_df = pd.read_csv('../data/windnet/trivial_interpolation_windnet.csv')
    trivial_df.index = pd.to_datetime(trivial_df['date'])

    pandas_df = pd.read_csv('../data/windnet/pandas_interpolation_windnet.csv')
    pandas_df.index = pd.to_datetime(pandas_df['date'])

    original_df = original_df[original_df.index.to_series().between(start_graph, end_graph)]
    trivial_df = trivial_df[trivial_df.index.to_series().between(start_graph, end_graph)]
    pandas_df = pandas_df[pandas_df.index.to_series().between(start_graph, end_graph)]

    make_simple_graph(original_df, title='Original data')
    make_simple_graph(trivial_df, title='Trivial interpolation.')
    make_simple_graph(pandas_df, title='Pandas interpolation.')
