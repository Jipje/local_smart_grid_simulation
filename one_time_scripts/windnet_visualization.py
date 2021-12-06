import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import datetime as dt
import dateutil.tz
import random

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def date_parser(string):
    return dt.datetime.strptime(string, '%d/%m/%Y %H:%M').replace(tzinfo=ams)


def round_to_ptu(dt_object, round='UP'):
    num_of_minutes = dt_object.minute
    corrected_hour = dt_object.hour

    if num_of_minutes % 15 != 0:
        leftovers = num_of_minutes % 15
        if round == 'UP':
            num_of_minutes += (15 - leftovers)
            if num_of_minutes == 60:
                corrected_hour += 1
                num_of_minutes = 0
        else:
            num_of_minutes -= leftovers
    dt_object = dt_object.replace(hour=corrected_hour, minute=num_of_minutes)
    return dt_object


def situation_sketch(df, moment=None, chosen_date=None):
    if moment is None and chosen_date is None:
        moment = random.randint(0, len(df))
        print(moment)

    if moment is not None:
        single_row = df.iloc[moment]
        middle_of_set = single_row.name

    if chosen_date is not None:
        middle_of_set = chosen_date

    window_size = 180
    start_of_set = round_to_ptu(middle_of_set - dt.timedelta(minutes=window_size), 'DOWN')
    end_of_set = round_to_ptu(middle_of_set + dt.timedelta(minutes=window_size), 'UP')
    return start_of_set, end_of_set
    # print('Start scenario {}. End scenario {}.'.format(start_of_set, end_of_set))


def make_base_graphs(windnet_df):
    plt.hist(windnet_df['nht_production_kwh'], bins=100)
    plt.ylabel('Number of occurences')
    plt.xlabel('Generated power in 5m (kWh)')
    plt.title('Histogram of generated power by wind farm Neushoorntocht')
    plt.show()

    plt.hist(windnet_df['nht_production_kwh'], bins=100)
    plt.ylim(0, 200)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Generated power in 5m (kWh)')
    plt.title('Histogram of generated power by wind farm Neushoorntocht')
    plt.show()

    plt.hist(windnet_df['nht_production_kw'], bins=100)
    plt.ylim(0, 200)
    plt.axvline(x=22630, color='red')
    plt.ylabel('Number of occurrences')
    plt.xlabel('Average Generated power per 5m (kW)')
    plt.title('Histogram of generated power by wind farm Neushoorntocht')
    plt.show()

    congestion_windnet_df = windnet_df.nlargest(n=100, columns='nht_production_kw')

    plt.scatter(congestion_windnet_df['hour_of_production'], congestion_windnet_df['nht_production_kw'])
    plt.ylabel('Average Generated power per 5m (kW)')
    plt.xlabel('Hour in which power was generated')
    plt.title('Scatterplot of generated power by wind farm Neushoorntocht')
    plt.show()

    plt.scatter(congestion_windnet_df['minute_of_production'], congestion_windnet_df['nht_production_kw'])
    plt.ylabel('Average Generated power per 5m (kW)')
    plt.xlabel('Minute in which power was generated')
    plt.title('Scatterplot of generated power by wind farm Neushoorntocht')
    plt.show()


if __name__ == '__main__':
    # headers = ['time', 'neushoorntocht_consumed_kw', 'neushoorntocht_produced_kw', 'mammoettocht_consumed_kw', 'mammoettocht_produced_kw']
    base_windnet_filename = '../data/windnet/base_windnet_data_sep_2020_sep_2021.csv'
    windnet_df = pd.read_csv(base_windnet_filename, parse_dates=[0], date_parser=date_parser)
    windnet_df.index = pd.to_datetime(windnet_df['date'], errors='coerce', utc=True)

    windnet_df['nht_production_kw'] = windnet_df['nht_production_kwh'] / 5 * 60
    windnet_df['hour_of_production'] = windnet_df.index.hour
    windnet_df['minute_of_production'] = windnet_df.index.minute

    congestion_windnet_df = windnet_df.nlargest(n=100, columns='nht_production_kw')
    print(congestion_windnet_df.sort_index())

    # make_base_graphs(windnet_df)

    dates_of_interest = [dt.datetime(2020, 12, 27, 3, tzinfo=utc), dt.datetime(2020, 12, 27, 7, tzinfo=utc),
                         dt.datetime(2020, 12, 27, 11, tzinfo=utc), dt.datetime(2021, 2, 6, 21, 30, tzinfo=utc),
                         dt.datetime(2021, 4, 5, 10, tzinfo=utc), dt.datetime(2021, 4, 5, 20, tzinfo=utc),
                         dt.datetime(2021, 4, 7, 8, 45, tzinfo=utc)]
    random_index = random.randint(0, len(dates_of_interest) - 1)
    chosen_date = dates_of_interest[random_index]
    start_of_set, end_of_set = situation_sketch(congestion_windnet_df, chosen_date=chosen_date)
    situation_df = windnet_df[start_of_set :end_of_set]
    # print(situation_df.to_string())

    plt.plot(situation_df.index, situation_df['nht_production_kw'])
    ax = plt.gca()
    formatter = mdates.DateFormatter('%H:%M')
    ax.xaxis.set_major_formatter(formatter)
    plt.ylim(16000, 26000)
    plt.ylabel('Average Generated power per 5m (kW)')
    plt.xlabel('Hour in which power was generated (UTC)')
    plt.title('Generated power by wind farm Neushoorntocht on {}'.format(chosen_date.strftime('%a %d %b %Y')))
    plt.show()

#     56
