from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_march = ['../../data/ea_runs/sorting_investigation/march_sort_none.csv',
                       '../../data/ea_runs/sorting_investigation/march_sort_1.csv',
                       '../../data/ea_runs/sorting_investigation/march_sort_2.csv',
                       '../../data/ea_runs/sorting_investigation/march_sort_3.csv']
    filenames_april = ['../../data/ea_runs/sorting_investigation/april_sort_none.csv',
                       '../../data/ea_runs/sorting_investigation/april_sort_1.csv',
                       '../../data/ea_runs/sorting_investigation/april_sort_2.csv',
                       '../../data/ea_runs/sorting_investigation/april_sort_3.csv']
    filenames_nov = ['../../data/ea_runs/sorting_investigation/november_sort_none.csv',
                     '../../data/ea_runs/sorting_investigation/november_sort_1.csv',
                     '../../data/ea_runs/sorting_investigation/november_sort_2.csv',
                     '../../data/ea_runs/sorting_investigation/november_sort_3.csv']
    filenames_all = [filenames_march, filenames_april, filenames_nov]
    base_title = 'Sorting investigation '
    titles = [base_title + 'March', base_title + 'April', base_title + 'November']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)
