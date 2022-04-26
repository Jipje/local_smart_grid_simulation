from one_time_scripts.visualisations.baselines_visualisation import make_bar_graph
from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_march = ['../../../data/ea_runs/mutation_investigation/march_big_mutation.csv',
                       '../../../data/ea_runs/mutation_investigation/march_big_mutation_with_overshoot.csv',
                       '../../../data/ea_runs/mutation_investigation/march_random_mutation.csv']
    filenames_april = ['../../../data/ea_runs/mutation_investigation/april_big_mutation.csv',
                       '../../../data/ea_runs/mutation_investigation/april_big_mutation_with_overshoot.csv',
                       '../../../data/ea_runs/mutation_investigation/april_random_mutation.csv']
    filenames_november = ['../../../data/ea_runs/mutation_investigation/november_big_mutation.csv',
                          '../../../data/ea_runs/mutation_investigation/november_big_mutation_with_overshoot.csv',
                          '../../../data/ea_runs/mutation_investigation/november_random_mutation.csv']
    filenames_all = [filenames_march, filenames_april, filenames_november]
    base_title = 'Mutation investigation '
    titles = [base_title + 'March', base_title + 'April', base_title + 'November']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)

    label_indexes = [13]
    source_folder = '../../../data/ea_runs/mutation_investigation/'
    source_folders = [source_folder, source_folder, source_folder]
    all_suffix = ['_random_mutation', '_big_mutation', '_big_mutation_with_overshoot']
    few_months = [2, 3, 10]
    make_bar_graph(label_indexes, source_folders=source_folders, suffixes=all_suffix, few_months=few_months)
