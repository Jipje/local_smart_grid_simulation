from one_time_scripts.visualisations.baselines_visualisation import make_bar_graph, statistic_tests
from one_time_scripts.visualisations.run_length_analysis import make_length_bar_graphs, length_statistical_test
from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_march = ['../../../data/new_ea_runs/mutation/march_random_mutation.csv',
                       '../../../data/new_ea_runs/mutation/march_big_random_mutation.csv',
                       '../../../data/new_ea_runs/mutation/march_big_sided_mutation.csv']
    filenames_april = ['../../../data/new_ea_runs/mutation/april_random_mutation.csv',
                       '../../../data/new_ea_runs/mutation/april_big_random_mutation.csv',
                       '../../../data/new_ea_runs/mutation/april_big_sided_mutation.csv']
    filenames_november = ['../../../data/new_ea_runs/mutation/november_random_mutation.csv',
                          '../../../data/new_ea_runs/mutation/november_big_random_mutation.csv',
                          '../../../data/new_ea_runs/mutation/november_big_sided_mutation.csv']
    filenames_all = [filenames_march, filenames_april, filenames_november]
    base_title = 'Mutation investigation '
    titles = [base_title + 'March', base_title + 'April', base_title + 'November']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)

    label_indexes = [13]
    source_folder = '../../../data/new_ea_runs/mutation/'
    source_folders = [source_folder, source_folder, source_folder]
    all_suffix = ['_random_mutation', '_big_random_mutation', '_big_sided_mutation']
    few_months = [2, 3, 10]
    make_bar_graph(label_indexes, source_folders=source_folders, suffixes=all_suffix, few_months=few_months,
                   title='Comparing performance of EA mutation definitions')

    statistic_tests([], [source_folder, source_folder], few_months=few_months,
                    suffixes=['_random_mutation', '_big_random_mutation'])

    statistic_tests([], [source_folder, source_folder], few_months=few_months,
                    suffixes=['_random_mutation', '_big_sided_mutation'])

    make_length_bar_graphs(source_folders, few_months=few_months, suffixes=all_suffix,
                           title='Comparing length of EA optimization of EA mutation definitions')
    length_statistical_test(source_folders, few_months, all_suffix)
