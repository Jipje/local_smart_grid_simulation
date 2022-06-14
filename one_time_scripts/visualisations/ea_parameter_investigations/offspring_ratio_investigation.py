from one_time_scripts.visualisations.baselines_visualisation import make_bar_graph, statistic_tests
from one_time_scripts.visualisations.run_length_analysis import make_length_bar_graphs, length_statistical_test
from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_march = ['../../../data/new_ea_runs/offspring_ratio/march_40_over_100.csv',
                       '../../../data/new_ea_runs/offspring_ratio/march_80_over_100.csv',
                       '../../../data/new_ea_runs/offspring_ratio/march_160_over_100.csv']
    filenames_april = ['../../../data/new_ea_runs/offspring_ratio/april_40_over_100.csv',
                       '../../../data/new_ea_runs/offspring_ratio/april_80_over_100.csv',
                       '../../../data/new_ea_runs/offspring_ratio/april_160_over_100.csv']
    filenames_november = ['../../../data/new_ea_runs/offspring_ratio/november_40_over_100.csv',
                          '../../../data/new_ea_runs/offspring_ratio/november_80_over_100.csv',
                          '../../../data/new_ea_runs/offspring_ratio/november_160_over_100.csv']
    filenames_all = [filenames_march, filenames_april, filenames_november]
    base_title = 'Offspring ratio comparison '
    titles = [base_title + 'March', base_title + 'April', base_title + 'November']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)

    label_indexes = [13]
    source_folder = '../../../data/new_ea_runs/offspring_ratio/'
    source_folders = [source_folder, source_folder, source_folder]
    all_suffix = ['_40_over_100', '_80_over_100', '_160_over_100']
    few_months = [2, 3, 10]
    make_bar_graph(label_indexes, source_folders=source_folders, suffixes=all_suffix, few_months=few_months,
                   title='Comparing performance of EA offspring ratio')

    statistic_tests([], [source_folder, source_folder], few_months=few_months,
                    suffixes=['_80_over_100', '_40_over_100'])

    statistic_tests([], [source_folder, source_folder], few_months=few_months,
                    suffixes=['_80_over_100', '_160_over_100'])

    make_length_bar_graphs(source_folders, few_months=few_months, suffixes=all_suffix,
                           title='Comparing length of EA optimization for EA offspring ratio')
    all_suffix = ['_80_over_100', '_40_over_100', '_160_over_100']
    length_statistical_test(source_folders, few_months, all_suffix)
