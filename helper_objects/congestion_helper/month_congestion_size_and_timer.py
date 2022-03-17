from pandas import DataFrame

from helper_objects.congestion_helper.time_and_size_congestion_helper import time_and_size_multiple_congestion_events, \
    identify_congestion
from one_time_scripts.solar_scripts.solarvation_visualization import load_solarvation_data
from one_time_scripts.helper_objects.date_helper import retrieve_months


def get_month_congestion_timings(solarvation_identifier: str = '../../data/environments/lelystad_1_2021.csv', verbose_lvl=1, strategy=4):
    congestion_kw = 14000

    solarvation_df = load_solarvation_data(solarvation_identifier)
    solarvation_df['congestion'], solarvation_df['excess_power'] = identify_congestion(solarvation_df, congestion_kw)

    starting_times, ending_times = retrieve_months(2021)
    # labels = ['January', 'February', 'March', 'April', 'May', 'June',
    #             'July', 'August', 'September', 'October', 'November', 'December']
    return time_and_size_multiple_congestion_events(solarvation_df, starting_times, ending_times, verbose_lvl=verbose_lvl, strategy=strategy)


def get_month_congestion_timings_with_df(solarvation_identifier: DataFrame,  verbose_lvl=1, strategy=4):
    congestion_kw = 14000
    solarvation_identifier['congestion'], solarvation_identifier['excess_power'] = identify_congestion(solarvation_identifier, congestion_kw)

    starting_times, ending_times = retrieve_months(2021)
    # labels = ['January', 'February', 'March', 'April', 'May', 'June',
    #             'July', 'August', 'September', 'October', 'November', 'December']
    return time_and_size_multiple_congestion_events(solarvation_identifier, starting_times, ending_times, verbose_lvl=verbose_lvl, strategy=strategy)


if __name__ == '__main__':
    res_df = get_month_congestion_timings(verbose_lvl=4, strategy=4)
    print(res_df.to_string())
