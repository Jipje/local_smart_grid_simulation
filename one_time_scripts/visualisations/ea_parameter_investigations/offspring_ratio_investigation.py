from one_time_scripts.visualisations.baselines_visualisation import make_bar_graph
from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_march = ['../../../data/new_ea_runs/offspring_ratio/march_80_over_100.csv',
                       '../../../data/new_ea_runs/offspring_ratio/march_160_over_100.csv']
    filenames_april = ['../../../data/new_ea_runs/offspring_ratio/april_80_over_100.csv',
                       '../../../data/new_ea_runs/offspring_ratio/april_160_over_100.csv']
    filenames_november = ['../../../data/new_ea_runs/offspring_ratio/november_80_over_100.csv',
                          '../../../data/new_ea_runs/offspring_ratio/november_160_over_100.csv']
    filenames_all = [filenames_march, filenames_april, filenames_november]
    base_title = 'Offspring investigation '
    titles = [base_title + 'March', base_title + 'April', base_title + 'November']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)

    label_indexes = [13]
    giga_baseline = '../../../data/new_ea_runs/giga_baseline_with_congestion/'
    source_folder_1 = '../../../data/new_ea_runs/offspring_ratio/'
    source_folders = [giga_baseline, source_folder_1, source_folder_1]
    all_suffix = ['', '_80_over_100', '_160_over_100']
    few_months = [2, 3, 10]
    make_bar_graph(label_indexes, source_folders=source_folders, suffixes=all_suffix, few_months=few_months)
