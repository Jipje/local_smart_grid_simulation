import pandas as pd
import datetime as dt
from helper_objects.ImbalanceMessageInterpreter import ImbalanceMessageInterpreter

if __name__ == '__main__':
    tennet_delta_df = pd.read_csv('../data/tennet_balans_delta/tennet_balans_delta_sep_2020_sep_2021.csv')
    tennet_delta_df.index = pd.to_datetime(tennet_delta_df['time'], errors='coerce')
    tennet_delta_df = tennet_delta_df.drop('time', axis=1)
    print(tennet_delta_df)

    imbalance_msg_inter = ImbalanceMessageInterpreter()
    res = []

    for index, row in tennet_delta_df.iterrows():
        mid_price = row['tennet_balansdelta.mean_mid_price']
        max_price = row['tennet_balansdelta.mean_max_price']
        min_price = row['tennet_balansdelta.mean_min_price']

        if mid_price is None or max_price is None or min_price is None:
            print('A NONE VALUE AT {}'.format(index))

        try:
            imbalance_msg_inter.update(mid_price, max_price, min_price)
        except OverflowError:
            quarter_mid_price, quarter_max_price, quarter_min_price = imbalance_msg_inter.get_current_price()
            quarter_row = {
                'time': index,
                'mid_price': quarter_mid_price,
                'max_price': quarter_max_price,
                'min_price': quarter_min_price
            }
            res.append(quarter_row)

            imbalance_msg_inter.reset()
            imbalance_msg_inter.update(mid_price, max_price, min_price)

    res_df = pd.DataFrame(res)
    res_df.index = pd.to_datetime(res_df['time'], errors='coerce')
    res_df = res_df.drop('time', axis=1)
    print(res_df)
    res_df.to_csv('../data/tennet_balans_delta/tennet_balans_delta_15m.csv')
