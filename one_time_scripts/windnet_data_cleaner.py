import dateutil.tz
import pandas as pd

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def correct_dates_windnet_csv():
    base_windnet_df = pd.read_csv('../data/windnet/base_windnet_data_sep_2020_sep_2021.csv')
    base_windnet_df.index = pd.to_datetime(base_windnet_df['date'], utc=False, errors='coerce', dayfirst=True)
    base_windnet_df.index = base_windnet_df.index.tz_localize(ams, ambiguous='infer')
    base_windnet_df.index = base_windnet_df.index.tz_convert(utc)
    base_windnet_df = base_windnet_df.drop('date', axis=1)
    print(base_windnet_df)
    base_windnet_df.to_csv('../data/windnet/corrected_dates_windnet_data_sep_2020_sep_2021.csv')


def add_power_to_base_windnet():
    base_windnet_df = pd.read_csv('../data/windnet/corrected_dates_windnet_data_sep_2020_sep_2021.csv')
    base_windnet_df.index = pd.to_datetime(base_windnet_df['date'], utc=True)
    base_windnet_df = base_windnet_df.drop('date', axis=1)

    base_windnet_df['nht_usage_kw'] = base_windnet_df['nht_usage_kwh'] * 12
    base_windnet_df['nht_production_kw'] = base_windnet_df['nht_production_kwh'] * 12
    base_windnet_df['mmt_usage_kw'] = base_windnet_df['mmt_usage_kwh'] * 12
    base_windnet_df['mmt_production_kw'] = base_windnet_df['mmt_production_kwh'] * 12
    print(base_windnet_df)
    base_windnet_df.to_csv('../data/windnet/cleaned_windnet_data_aug_2020_sep_2021.csv')


if __name__ == '__main__':
    correct_dates_windnet_csv()
    add_power_to_base_windnet()
