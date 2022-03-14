from helper_objects.congestion_helper.time_and_size_congestion_helper import time_and_size_multiple_congestion_events, \
    identify_congestion
from one_time_scripts.solar_scripts.solarvation_visualization import load_solarvation_data
from one_time_scripts.helper_objects.date_helper import retrieve_months


def main(verbose_lvl=1):
    solarvation_filename = '../../data/environments/lelystad_1_2021.csv'
    congestion_kw = 14000

    solarvation_df = load_solarvation_data(solarvation_filename)
    solarvation_df['congestion'], solarvation_df['excess_power'] = identify_congestion(solarvation_df, congestion_kw)

    starting_times, ending_times = retrieve_months(2021)
    labels = ['January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December']
    return time_and_size_multiple_congestion_events(solarvation_df, starting_times, ending_times, labels, verbose_lvl)


if __name__ == '__main__':
    res_df = main(verbose_lvl=4)
    print(res_df.to_string())
