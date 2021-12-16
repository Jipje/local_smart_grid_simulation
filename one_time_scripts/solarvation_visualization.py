import matplotlib.pyplot as plt
import pandas as pd
import datetime as dt
import dateutil.tz

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


def date_parser(string):
    return dt.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S.000Z').replace(tzinfo=utc)


if __name__ == '__main__':
    solarvation_filename = '../data/solarvation/cleaned_solarvation_1h.csv'
    solarvation_df = pd.read_csv(solarvation_filename, parse_dates=[0], date_parser=date_parser)
    solarvation_df.index = pd.to_datetime(solarvation_df['time'], errors='coerce', utc=True)
    solarvation_df = solarvation_df.drop('time', axis=1)
    # print(solarvation_df)

    plt.hist(solarvation_df['power_generation'], bins=100)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Expected power generation (calculated hourly) (kW)')
    plt.title('Histogram of modelled power generation by solar field Solarvation')
    plt.axvline(24000, color='red')
    plt.show()

    plt.hist(solarvation_df['power_generation'], bins=100)
    plt.ylim(0, 150)
    plt.ylabel('Number of occurrences')
    plt.xlabel('Expected power generation (calculated hourly) (kW)')
    plt.title('Histogram of modelled power generation by solar field Solarvation')
    plt.axvline(24000, color='red')
    plt.show()

    solarvation_df['hour_of_production'] = solarvation_df.index.hour

    plt.scatter(solarvation_df['hour_of_production'], solarvation_df['power_generation'])
    plt.ylabel('Generated power 1h (kW)')
    plt.xlabel('Hour in which power was generated (UTC)')
    plt.title('Scatterplot of generated power by solar field Solarvation')
    plt.axhline(24000, color='red')
    plt.show()
