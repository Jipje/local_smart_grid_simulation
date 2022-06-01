from one_time_scripts.visualisations.baselines_visualisation import make_bar_graph, statistic_tests
from one_time_scripts.visualisations.run_length_analysis import make_length_bar_graphs, length_statistical_test
from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_march = ['../../../data/new_ea_runs/sorting/march_no_sort.csv',
                       '../../../data/new_ea_runs/sorting/march_sort_1.csv',
                       '../../../data/new_ea_runs/sorting/march_sort_2.csv',
                       '../../../data/new_ea_runs/sorting/march_sort_3.csv']
    filenames_april = ['../../../data/new_ea_runs/sorting/april_no_sort.csv',
                       '../../../data/new_ea_runs/sorting/april_sort_1.csv',
                       '../../../data/new_ea_runs/sorting/april_sort_2.csv',
                       '../../../data/new_ea_runs/sorting/april_sort_3.csv']
    filenames_nov = ['../../../data/new_ea_runs/sorting/november_no_sort.csv',
                     '../../../data/new_ea_runs/sorting/november_sort_1.csv',
                     '../../../data/new_ea_runs/sorting/november_sort_2.csv',
                     '../../../data/new_ea_runs/sorting/november_sort_3.csv']
    filenames_all = [filenames_march, filenames_april, filenames_nov]
    base_title = 'Sorting investigation '
    titles = [base_title + 'March', base_title + 'April', base_title + 'November']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)

    label_indexes = [13]
    source_folder = '../../../data/new_ea_runs/sorting/'
    source_folders = [source_folder, source_folder, source_folder, source_folder]
    all_suffix = ['_no_sort', '_sort_1', '_sort_2', '_sort_3']
    few_months = [2, 3, 10]
    make_bar_graph(label_indexes, source_folders=source_folders, suffixes=all_suffix, few_months=few_months,
                   num_of_source_folder_baselines=0)

    statistic_tests([], [source_folder, source_folder], few_months=few_months,
                    suffixes=['_sort_1', '_no_sort'])

    statistic_tests([], [source_folder, source_folder], few_months=few_months,
                    suffixes=['_sort_1', '_sort_2'])

    statistic_tests([], [source_folder, source_folder], few_months=few_months,
                    suffixes=['_sort_1', '_sort_3'])

    statistic_tests([], [source_folder, source_folder], few_months=few_months,
                    suffixes=['_no_sort', '_sort_1'])

    statistic_tests([], [source_folder, source_folder], few_months=few_months,
                    suffixes=['_no_sort', '_sort_2'])

    statistic_tests([], [source_folder, source_folder], few_months=few_months,
                    suffixes=['_no_sort', '_sort_3'])

    make_length_bar_graphs(source_folders, few_months=few_months, suffixes=all_suffix)
    all_suffix = ['_sort_1', '_no_sort', '_sort_2', '_sort_3']
    length_statistical_test(source_folders, few_months, all_suffix)
