import pandas as pd

if __name__ == '__main__':
    tennet_delta_df = pd.read_csv('data/tennet_balans_delta_nov_2020_nov_2021.csv')
    tennet_delta_df.index = pd.to_datetime(tennet_delta_df['time'], errors='coerce')
    tennet_delta_df = tennet_delta_df.drop('time', axis=1)
    # print(tennet_delta_df)

    windnet_df = pd.read_csv('data/trivial_cleaned_windnet_data_sep_2020_sep_2021.csv')
    windnet_df.index = pd.to_datetime(windnet_df['time'], errors='coerce')
    windnet_df = windnet_df.drop('time', axis=1)
    # print(windnet_df)

    res_df = pd.merge(tennet_delta_df, windnet_df, left_index=True, right_index=True, how='inner')
    # print(res_df)

    res_df.to_csv('data/tennet_balans_delta_and_trivial_windnet.csv')
