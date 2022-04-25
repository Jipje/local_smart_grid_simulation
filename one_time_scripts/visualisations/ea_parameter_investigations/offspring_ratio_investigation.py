from one_time_scripts.visualisations.visualise_ea_runs import visualise_ea_runs

if __name__ == '__main__':
    filenames_april = ['../../../data/ea_runs/offspring_ratio/april_10off_100pop.csv',
                       '../../../data/ea_runs/offspring_ratio/april_25off_100pop.csv',
                       '../../../data/ea_runs/offspring_ratio/april_40off_100pop.csv',
                       '../../../data/ea_runs/offspring_ratio/april_75off_100pop.csv',
                       '../../../data/ea_runs/offspring_ratio/april_90off_100pop.csv']
    filenames_november = ['../../../data/ea_runs/offspring_ratio/november_10off_100pop.csv',
                          '../../../data/ea_runs/offspring_ratio/november_25off_100pop.csv',
                          '../../../data/ea_runs/offspring_ratio/november_40off_100pop.csv',
                          '../../../data/ea_runs/offspring_ratio/november_75off_100pop.csv',
                          '../../../data/ea_runs/offspring_ratio/november_90off_100pop.csv']
    filenames_march = ['../../../data/ea_runs/offspring_ratio/march_10off_100pop.csv',
                       '../../../data/ea_runs/offspring_ratio/march_25off_100pop.csv',
                       '../../../data/ea_runs/offspring_ratio/march_40off_100pop.csv',
                       '../../../data/ea_runs/offspring_ratio/march_50off_100pop.csv',
                       '../../../data/ea_runs/offspring_ratio/march_75off_100pop.csv',
                       '../../../data/ea_runs/offspring_ratio/march_90off_100pop.csv']
    filesnames_pop = ['../../../data/ea_runs/offspring_ratio/march_100off_1000pop.csv',
                      '../../../data/ea_runs/offspring_ratio/march_10off_100pop.csv',
                      '../../../data/ea_runs/offspring_ratio/march_250off_1000pop.csv',
                      '../../../data/ea_runs/offspring_ratio/march_25off_100pop.csv',
                      '../../../data/ea_runs/offspring_ratio/march_400off_1000pop.csv',
                      '../../../data/ea_runs/offspring_ratio/march_40off_100pop.csv']
    filenames_all = [filenames_march, filenames_april, filenames_november, filesnames_pop]
    base_title = 'Offspring investigation '
    titles = [base_title + 'March', base_title + 'April', base_title + 'November', 'Offspring comparison with '
                                                                                   'population increase']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)
