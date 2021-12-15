import datetime as dt
import dateutil.tz
import pandas as pd
import matplotlib.pyplot as plt
from one_time_scripts.helper_objects.SmartWindnetInterpolater import SmartWindnetInterpolater

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()

start_graph = dt.datetime(2021, 3, 14, 16, tzinfo=utc)
end_graph = start_graph + dt.timedelta(minutes=500)


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


def smarter_interpolation_windnet():
    smarter_interpolater = SmartWindnetInterpolater()

    base_windnet_df = pd.read_csv('../data/windnet/cleaned_windnet_data_aug_2020_sep_2021.csv')
    base_windnet_df = base_windnet_df.drop(['nht_usage_kwh', 'nht_production_kwh', 'mmt_usage_kwh', 'mmt_production_kwh'], axis=1)

    df2 = pd.DataFrame([['23/02/1997 20:20', None, None, None, None], ['23/02/1997 20:22', None, None, None, None]],
                       columns=['date', 'nht_usage_kw', 'nht_production_kw', 'mmt_usage_kw', 'mmt_production_kw'],
                       index=[-1, len(base_windnet_df)])
    shuffled_kw_windnet = base_windnet_df.append(df2)

    res_list = []

    for index, current_wind_net_data in shuffled_kw_windnet.iterrows():
        if index == -1 or index == len(base_windnet_df):
            continue
        previous_wind_net_data = shuffled_kw_windnet.iloc[index - 1]
        next_wind_net_data = shuffled_kw_windnet.iloc[index + 1]

        end_of_5m_interval = dt.datetime.strptime(current_wind_net_data[0], '%Y-%m-%d %H:%M:%S%z')
        start_of_5m_interval = end_of_5m_interval - dt.timedelta(minutes=5)

        neushoorntocht_consumed_kw = smarter_interpolater.kw_per_minute(float(current_wind_net_data[1]),
                                                                        float(previous_wind_net_data[1]),
                                                                        float(next_wind_net_data[1]))
        neushoorntocht_produced_kw = smarter_interpolater.kw_per_minute(float(current_wind_net_data[2]),
                                                                        float(previous_wind_net_data[2]),
                                                                        float(next_wind_net_data[2]))
        mammoettocht_consumed_kw = smarter_interpolater.kw_per_minute(float(current_wind_net_data[3]),
                                                                      float(previous_wind_net_data[3]),
                                                                      float(next_wind_net_data[3]))
        mammoettocht_produced_kw = smarter_interpolater.kw_per_minute(float(current_wind_net_data[4]),
                                                                      float(previous_wind_net_data[4]),
                                                                      float(next_wind_net_data[4]))

        for i in range(5):
            time_tracker = start_of_5m_interval + dt.timedelta(minutes=i)
            time_tracker_str = time_tracker.strftime('%Y-%m-%dT%H:%M:%S%z')
            new_row = {
                'time': time_tracker_str,
                'nht_usage_kw': neushoorntocht_consumed_kw[i],
                'nht_production_kw': neushoorntocht_produced_kw[i],
                'mmt_usage_kw': mammoettocht_consumed_kw[i],
                'mmt_production_kw': mammoettocht_produced_kw[i]
            }
            res_list.append(new_row)

    res_df = pd.DataFrame(res_list)
    res_df.index = pd.to_datetime(res_df['time'], utc=True, errors='coerce')
    res_df = res_df.drop(['time'], axis=1)

    res_df['nht_usage_kwh'] = res_df['nht_usage_kw'] / 60
    res_df['nht_production_kwh'] = res_df['nht_production_kw'] / 60
    res_df['mmt_usage_kwh'] = res_df['mmt_usage_kw'] / 60
    res_df['mmt_production_kwh'] = res_df['mmt_production_kw'] / 60

    return res_df


def make_simple_graph(filtered_df, title):
    plt.plot(filtered_df.index, filtered_df['nht_production_kw'])
    plt.title(title)
    plt.xlabel('Time')
    plt.ylabel('Produced power (kW)')
    plt.show()


if __name__ == '__main__':
    trivial_df = trivial_interpolation_windnet()
    pandas_df = pandas_linear_interpolation_windnet()
    own_df = smarter_interpolation_windnet()

    trivial_df = trivial_df[trivial_df.index.to_series().between(start_graph, end_graph)]
    pandas_df = pandas_df[pandas_df.index.to_series().between(start_graph, end_graph)]
    own_df = own_df[own_df.index.to_series().between(start_graph, end_graph)]

    make_simple_graph(trivial_df, title='Trivial interpolation.')
    make_simple_graph(pandas_df, title='Pandas interpolation.')
    make_simple_graph(own_df, title='Own interpolation.')
