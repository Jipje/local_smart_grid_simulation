import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def date_parser(string):
    return dt.datetime.strptime(string, '%Y-%m-%d %H:%M:%S%z').replace(tzinfo=utc)


def load_solarvation_data(solarvation_filename='../../data/environments/lelystad_1_2021.csv'):
    solarvation_df = pd.read_csv(solarvation_filename, parse_dates=[0], date_parser=date_parser)
    try:
        solarvation_df.index = pd.to_datetime(solarvation_df['time_utc'], errors='coerce', utc=True)
        solarvation_df = solarvation_df.drop('time_utc', axis=1)
    except KeyError:
        solarvation_df.index = pd.to_datetime(solarvation_df['time_ams'], errors='coerce', utc=True)
        solarvation_df = solarvation_df.drop('time_ams', axis=1)

    solarvation_df['hour_of_production'] = solarvation_df.index.hour

    return solarvation_df


def do_basic_analysis(solarvation_df):
    # ['tennet_balansdelta.mean_max_price', 'tennet_balansdelta.mean_mid_price', 'tennet_balansdelta.mean_min_price',
    #  'power', 'irradiance', 'expected_power', 'lower_range', 'upper_range', 'losses']
    plt.hist(solarvation_df['power'], bins=100)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Power generation (kW)')
    plt.title('Histogram of power generation by solar field Lelystad 1')
    plt.show()

    plt.hist(solarvation_df['power'], bins=100)
    plt.ylim(0, 4000)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Power generation (kW)')
    plt.title('Histogram of power generation by solar field Lelystad 1')
    plt.show()

    plt.scatter(solarvation_df['hour_of_production'], solarvation_df['power'])
    plt.ylabel('Generated power 1m (kW)')
    plt.xlabel('Hour in which power was generated (UTC)')
    plt.title('Scatterplot of power generation by solar field Lelystad 1')
    plt.ylim(0, 20000)
    plt.show()


def do_monthly_analysis(solarvation_df):
    fig, axs = plt.subplots(4, 3, figsize=(12, 9))
    for i in range(1, 13):
        month = i
        start_of_month = dt.datetime(2021, month, 1, tzinfo=utc)
        temp_day = start_of_month.replace(day=28) + dt.timedelta(days=4)
        end_of_month = temp_day - dt.timedelta(days=temp_day.day)

        if month in [1, 4, 7, 10]:
            axes_y = 0
        elif month in [2, 5, 8, 11]:
            axes_y = 1
        else:
            axes_y = 2

        axes_x = None
        for j in range(1, 5):
            if month <= (j * 3):
                axes_x = j - 1
                break

        month_df = solarvation_df[start_of_month:end_of_month]
        axs[axes_x, axes_y].scatter(month_df['hour_of_production'], month_df['power'])
        fig.suptitle('Scatterplot of generated power per month')
        axs[axes_x, axes_y].set_title('{}'.format(start_of_month.strftime('%B')))
        axs[axes_x, axes_y].set_ylim((0, 20000))
    for ax in axs.flat:
        ax.set(xlabel='Hour (UTC)', ylabel='Generated power (kW)')
        ax.label_outer()
    plt.show()


if __name__ == '__main__':
    # solarvation_df = load_solarvation_data(solarvation_filename='../../data/solar_data/solarvation/solarvation_lelystad_1.csv')
    solarvation_df = load_solarvation_data()

    # start_filter = dt.datetime(2021, 3, 3, 7, 0, 0, tzinfo=utc)
    # end_filter = dt.datetime(2021, 3, 3, 17, 0, 0, tzinfo=utc)
    # solarvation_df = solarvation_df[start_filter:end_filter]

    # do_basic_analysis(solarvation_df)

    # do_monthly_analysis(solarvation_df)

    do_monthly_analysis(solarvation_df)
