import pandas as pd
from matplotlib import pyplot as plt

if __name__ == '__main__':
    settlement_df = pd.read_csv('../../data/tennet_balans_delta/tennet_settlement_2021.csv', parse_dates=True,
                                converters={'epex_price': float, 'tennet_short': float, 'tennet_long': float})
    settlement_df.index = pd.to_datetime(settlement_df['time_ams'], utc=False)
    settlement_df = settlement_df.drop(['time', 'time_ams'], axis=1)

    plt.hist(settlement_df['tennet_short'], bins=800)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Imbalance price (€/MWh)')
    plt.title('Histogram of imbalance charge prices')
    plt.show()

    plt.hist(settlement_df['tennet_long'], bins=800)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Imbalance price (€/MWh)')
    plt.title('Histogram of imbalance discharge prices')
    plt.show()
