import pandas as pd
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.UTC


class ImbalancePriceReader(object):
    def __init__(self, market_data='../data/tennet_balans_delta/tennet_balans_delta_15m.csv'):
        market_df = pd.read_csv(market_data, parse_dates=True)
        market_df.index = pd.to_datetime(market_df['time'], utc=True)
        print(market_df)

        market_df = market_df.drop('time', axis=1)
        self.market_df = market_df

    def get_day(self, day=None):
        if day is None:
            day = dt.datetime(2020, 12, 27, tzinfo=utc)
        else:
            day = day.replace(hour=0, minute=0, second=0, microsecond=0)

        start_of_day = day
        end_of_day = day + dt.timedelta(days=1)

        filtered_df = self.market_df[(self.market_df.index > start_of_day) & (self.market_df.index <= end_of_day)]
        return filtered_df


if __name__ == '__main__':
    imbalance_price_reader = ImbalancePriceReader()
    print(imbalance_price_reader.get_day())
