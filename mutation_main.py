import sys

from evolutionary_algorithm.individuals.mutation_params import random_mutation, big_random_mutation, \
    big_mutation_with_overshoot
from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, do_an_ea_run, execute_ea_runs

month_filenames = ['january', 'february', 'march', 'april',
                   'may', 'june', 'july', 'august',
                   'september', 'october', 'november', 'december']

run_settings_1 = default_ea_runnable_settings
run_settings_1['mutate_params'] = big_mutation_with_overshoot

run_settings_2 = default_ea_runnable_settings
run_settings_2['mutate_params'] = big_random_mutation

run_settings_3 = default_ea_runnable_settings
run_settings_3['mutate_params'] = random_mutation


if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    folder = 'mutation'

    if runnable_int == 1:
        print('Running setting 1')
        execute_ea_runs('_big_sided_mutation', run_settings_1, folder)
    elif runnable_int == 2:
        print('Running setting 2')
        execute_ea_runs('_big_random_mutation', run_settings_2, folder)
    else:
        print('Running setting other')
        execute_ea_runs('_random_mutation', run_settings_3, folder)
