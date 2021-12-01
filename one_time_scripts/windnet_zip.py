import pandas as pd
from csv import writer

if __name__ == '__main__':
    tennet_delta_df = pd.read_csv('../data/tennet_balans_delta/tennet_balans_delta_sep_2020_sep_2021.csv')
    tennet_delta_df.index = pd.to_datetime(tennet_delta_df['time'], errors='coerce')
    tennet_delta_df = tennet_delta_df.drop('time', axis=1)
    tennet_delta_df = tennet_delta_df.dropna()
    # print(tennet_delta_df)

    windnet_df = pd.read_csv('../data/windnet/trivial_cleaned_windnet_data_sep_2020_sep_2021.csv')
    windnet_df.index = pd.to_datetime(windnet_df['time'], errors='coerce')
    windnet_df = windnet_df.drop('time', axis=1)
    # print(windnet_df)

    res_df = pd.merge(tennet_delta_df, windnet_df, left_index=True, right_index=True, how='inner')
    # print(res_df)

    with open('../data/tennet_and_windnet/larger_tennet_balans_delta_and_trivial_windnet.csv', 'w+', newline='') as new_file:
        csv_writer = writer(new_file)
        header = ['time'] + list(res_df.columns)
        csv_writer.writerow(header)
        tracker = 0

        for index, row in res_df.iterrows():
            csv_row = []

            index_str = index.strftime('%Y-%m-%dT%H:%M:%S.000Z')

            csv_row = [index_str, row['tennet_balansdelta.mean_max_price'], row['tennet_balansdelta.mean_mid_price'],
                       row['tennet_balansdelta.mean_min_price'], row['neushoorntocht_consumed_kw'],
                       row['neushoorntocht_produced_kw'], row['mammoettocht_consumed_kw'], row['mammoettocht_produced_kw']]
            csv_writer.writerow(csv_row)

            if tracker % 202020 == 0:
                print(csv_row)
            tracker += 1
