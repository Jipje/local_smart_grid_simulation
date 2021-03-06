import pandas as pd
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.UTC


class ImbalancePriceReader(object):
    def __init__(self, market_data='../data/tennet_balans_delta/tennet_balans_delta_15m.csv'):
        market_df = pd.read_csv(market_data, parse_dates=True)
        market_df.index = pd.to_datetime(market_df['time'], utc=True)

        market_df = market_df.drop('time', axis=1)
        self.market_df = market_df

    def get_day(self, day=None):
        if day is None:
            day = dt.datetime(2020, 12, 27, tzinfo=utc)
        else:
            day = day.replace(hour=0, minute=0, second=0, microsecond=0)

        start_of_day = day
        end_of_day = day + dt.timedelta(days=1)

        return self.get_specific_time(start_of_day, end_of_day)

    def get_specific_time(self, start_of_time=None, end_of_time=None):
        if start_of_time is None:
            start_of_time = dt.datetime(2020, 12, 27, tzinfo=utc)

        if end_of_time is None:
            end_of_time = start_of_time + dt.timedelta(days=1)

        filtered_df = self.market_df[(self.market_df.index > start_of_time) & (self.market_df.index <= end_of_time)]
        return filtered_df


if __name__ == '__main__':
    imbalance_price_reader = ImbalancePriceReader()
    print(imbalance_price_reader.get_day())
    print(imbalance_price_reader.get_specific_time())
