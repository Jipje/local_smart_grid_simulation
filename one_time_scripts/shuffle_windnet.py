import pandas as pd
import datetime as dt

if __name__ == '__main__':
    base_windnet_df = pd.read_csv('../data/windnet/base_windnet_data_sep_2020_sep_2021.csv')
    base_windnet_df['date'] = pd.to_datetime(base_windnet_df['date'], utc=True, errors='coerce')

    base_windnet_df['nht_usage_kw'] = base_windnet_df['nht_usage_kwh'] * 12
    base_windnet_df['nht_production_kw'] = base_windnet_df['nht_production_kwh'] * 12
    base_windnet_df['mmt_usage_kw'] = base_windnet_df['mmt_usage_kwh'] * 12
    base_windnet_df['mmt_production_kw'] = base_windnet_df['mmt_production_kwh'] * 12

    base_windnet_df.index = base_windnet_df['date'] - dt.timedelta(minutes=3)
    base_windnet_df = base_windnet_df.drop(['date', 'nht_usage_kwh', 'nht_production_kwh', 'mmt_usage_kwh', 'mmt_production_kwh'], axis=1)
    print(base_windnet_df)
    base_windnet_df.to_csv('../data/windnet/windnet_centered_mid_5m.csv')
