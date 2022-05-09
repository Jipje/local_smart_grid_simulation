from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_march = ['../../../data/new_ea_runs/offspring_ratio/march_80_over_100.csv',
                       '../../../data/new_ea_runs/offspring_ratio/march_160_over_100.csv',
                       '../../../data/ea_runs/offspring_ratio/march_75off_100pop.csv']
    filenames_april = ['../../../data/new_ea_runs/offspring_ratio/april_80_over_100.csv']
    filenames_november = []
    filenames_all = [filenames_march]
    base_title = 'Offspring investigation '
    titles = [base_title + 'March']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)
