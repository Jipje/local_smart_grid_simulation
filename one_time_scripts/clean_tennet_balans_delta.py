import pandas as pd

if __name__ == '__main__':
    tennet_delta_df = pd.read_csv('../data/tennet_balans_delta/tennet_balans_delta_2021.csv')
    tennet_delta_df.index = pd.to_datetime(tennet_delta_df['time'], errors='coerce')
    tennet_delta_df = tennet_delta_df.drop('time', axis=1)
    tennet_delta_df = tennet_delta_df.resample('1T').fillna(None)

    print(tennet_delta_df[tennet_delta_df['tennet_balansdelta.mean_mid_price'].isna()].to_string())
    print('5 known instances of outages. 27-10-2020 22:00, 09-12-2020 17:30, 21-03-2021 18:00, 14-06-2021 18:00, 18-06-2021 14:00')
