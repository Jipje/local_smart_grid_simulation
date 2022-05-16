import sys
from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, do_an_ea_run, execute_ea_runs

month_filenames = ['january', 'february', 'march', 'april',
                   'may', 'june', 'july', 'august',
                   'september', 'october', 'november', 'december']

run_settings_1 = default_ea_runnable_settings
run_settings_1['mutation_possibility'] = 0.25

run_settings_2 = default_ea_runnable_settings
run_settings_2['mutation_possibility'] = 0.75

run_settings_3 = default_ea_runnable_settings
run_settings_3['mutation_possibility'] = 0.50


if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    folder = 'mutation_possibility'

    if runnable_int == 1:
        print('Running setting 1')
        execute_ea_runs('_mutate_prob_25', run_settings_1, folder)
    elif runnable_int == 2:
        print('Running setting 2')
        execute_ea_runs('_mutate_prob_75', run_settings_2, folder)
    else:
        print('Running setting other')
        execute_ea_runs('_mutate_prob_50', run_settings_3, folder)
