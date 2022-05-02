from one_time_scripts.visualisations.baselines_visualisation import make_bar_graph
from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_march = ['../../../data/ea_runs/num_of_points_investigation/march_num_of_points_4.csv',
                       '../../../data/ea_runs/num_of_points_investigation/march_num_of_points_6.csv',
                       '../../../data/ea_runs/num_of_points_investigation/march_num_of_points_8.csv']
    filenames_april = ['../../../data/ea_runs/num_of_points_investigation/april_num_of_points_4.csv',
                       '../../../data/ea_runs/num_of_points_investigation/april_num_of_points_6.csv',
                       '../../../data/ea_runs/num_of_points_investigation/april_num_of_points_8.csv']
    filenames_november = ['../../../data/ea_runs/num_of_points_investigation/november_num_of_points_4.csv',
                          '../../../data/ea_runs/num_of_points_investigation/november_num_of_points_6.csv',
                          '../../../data/ea_runs/num_of_points_investigation/november_num_of_points_8.csv']
    filenames_all = [filenames_march, filenames_april, filenames_november]
    base_title = 'Number of Points investigation '
    titles = [base_title + 'March', base_title + 'April', base_title + 'November']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)

    label_indexes = [13]
    source_folder = '../../../data/ea_runs/num_of_points_investigation/'
    source_folders = [source_folder, source_folder, source_folder]
    all_suffix = ['_num_of_points_4', '_num_of_points_6', '_num_of_points_8']
    few_months = [2, 3, 10]
    make_bar_graph(label_indexes, source_folders=source_folders, suffixes=all_suffix, few_months=few_months)
