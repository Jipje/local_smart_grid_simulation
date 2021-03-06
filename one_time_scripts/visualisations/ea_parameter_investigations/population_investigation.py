from one_time_scripts.visualisations.baselines_visualisation import make_bar_graph, statistic_tests
from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_march = ['../../../data/new_ea_runs/population/march_16_over_20.csv',
                       '../../../data/new_ea_runs/population/march_32_over_40.csv',
                       '../../../data/new_ea_runs/population/march_80_over_100.csv',
                       '../../../data/new_ea_runs/population/march_160_over_200.csv']
    filenames_april = ['../../../data/new_ea_runs/population/april_16_over_20.csv',
                       '../../../data/new_ea_runs/population/april_32_over_40.csv',
                       '../../../data/new_ea_runs/population/april_80_over_100.csv',
                       '../../../data/new_ea_runs/population/april_160_over_200.csv']
    filenames_november = ['../../../data/new_ea_runs/population/november_16_over_20.csv',
                          '../../../data/new_ea_runs/population/november_32_over_40.csv',
                          '../../../data/new_ea_runs/population/november_80_over_100.csv',
                          '../../../data/new_ea_runs/population/november_160_over_200.csv']
    filenames_all = [filenames_march, filenames_april, filenames_november]
    base_title = 'Population investigation '
    titles = [base_title + 'March', base_title + 'April', base_title + 'November']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)

    label_indexes = [13]
    giga_baseline = '../../../data/new_ea_runs/giga_baseline_with_congestion/'
    source_folder_1 = '../../../data/new_ea_runs/population/'
    source_folders = [giga_baseline, source_folder_1, source_folder_1, source_folder_1, source_folder_1]
    all_suffix = ['', '_16_over_20', '_32_over_40', '_80_over_100', '_160_over_200']
    few_months = [2, 3, 10]
    make_bar_graph(label_indexes, source_folders=source_folders, suffixes=all_suffix, few_months=few_months)

    statistic_tests([], [source_folder_1, source_folder_1], few_months=few_months,
                    suffixes=['_32_over_40', '_80_over_100'])
