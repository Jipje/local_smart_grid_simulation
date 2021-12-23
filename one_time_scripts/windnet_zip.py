import pandas as pd
from csv import writer

if __name__ == '__main__':
    tennet_delta_df = pd.read_csv('../data/tennet_balans_delta/tennet_balans_delta_okt_2020_nov_2021.csv')
    tennet_delta_df.index = pd.to_datetime(tennet_delta_df['time'], errors='coerce')
    tennet_delta_df = tennet_delta_df.drop('time', axis=1)
    # tennet_delta_df = tennet_delta_df.dropna()
    # print(tennet_delta_df)

    windnet_df = pd.read_csv('../data/windnet/pandas_interpolation_windnet.csv')
    windnet_df.index = pd.to_datetime(windnet_df['date'], errors='coerce')
    windnet_df = windnet_df.drop('date', axis=1)
    # print(windnet_df)

    res_df = pd.merge(tennet_delta_df, windnet_df, left_index=True, right_index=True, how='inner')

    res_df = res_df.drop(['nht_usage_kwh', 'nht_production_kwh', 'mmt_usage_kwh', 'mmt_production_kwh'], axis=1)
    print(res_df)
    res_df.to_csv('../data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv')
