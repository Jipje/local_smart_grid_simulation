from one_time_scripts.visualisations.baselines_visualisation import make_bar_graph
from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_march = ['../../../data/ea_runs/sorting_investigation/march_sort_none.csv',
                       '../../../data/ea_runs/sorting_investigation/march_sort_1.csv',
                       '../../../data/ea_runs/sorting_investigation/march_sort_2.csv',
                       '../../../data/ea_runs/sorting_investigation/march_sort_3.csv']
    filenames_april = ['../../../data/ea_runs/sorting_investigation/april_sort_none.csv',
                       '../../../data/ea_runs/sorting_investigation/april_sort_1.csv',
                       '../../../data/ea_runs/sorting_investigation/april_sort_2.csv',
                       '../../../data/ea_runs/sorting_investigation/april_sort_3.csv']
    filenames_nov = ['../../../data/ea_runs/sorting_investigation/november_sort_none.csv',
                     '../../../data/ea_runs/sorting_investigation/november_sort_1.csv',
                     '../../../data/ea_runs/sorting_investigation/november_sort_2.csv',
                     '../../../data/ea_runs/sorting_investigation/november_sort_3.csv']
    filenames_all = [filenames_march, filenames_april, filenames_nov]
    base_title = 'Sorting investigation '
    titles = [base_title + 'March', base_title + 'April', base_title + 'November']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)

    label_indexes = [13]
    source_folder_3 = '../../../data/ea_runs/sorting_investigation/'
    source_folders = [source_folder_3, source_folder_3, source_folder_3, source_folder_3]
    all_suffix = ['_sort_none', '_sort_1', '_sort_2', '_sort_3']
    few_months = [2, 3, 10]
    make_bar_graph(label_indexes, source_folders=source_folders, suffixes=all_suffix, few_months=few_months)
