import os
import sys

from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.IndividualRandomNormalDist import IndividualRandomNormalDist
from evolutionary_algorithm.individuals.guided_initialisation.GuidedInitRandomNormalDist import \
    GuidedInitRandomNormalDist
from evolutionary_algorithm.individuals.mutation_params import big_mutation_with_overshoot, random_mutation, \
    big_mutation
from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, do_default_run

month_filenames = ['january', 'february', 'march', 'april',
                           'may', 'june', 'july', 'august',
                           'september', 'october', 'november', 'december']

run_settings_1 = default_ea_runnable_settings
run_settings_1['pop_size'] = 100
run_settings_1['n_offsprings'] = 40

run_settings_2 = default_ea_runnable_settings
run_settings_2['pop_size'] = 100
run_settings_2['n_offsprings'] = 80

run_settings_3 = default_ea_runnable_settings
run_settings_3['pop_size'] = 100
run_settings_3['n_offsprings'] = 160

if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    if runnable_int == 1:
        print('Running setting 1')
        for _ in range(5):
            for month_index in [3, 4, 11]:
                month_filename = month_filenames[month_index - 1]
                custom_filename = month_filename + '_40_over_100'
                do_default_run(run_settings_1, month=month_index, filename=custom_filename, folder='offspring_ratio')
    elif runnable_int == 2:
        print('Running setting 2')
        for _ in range(5):
            for month_index in [3, 4, 11]:
                month_filename = month_filenames[month_index - 1]
                custom_filename = month_filename + '_160_over_100'
                do_default_run(run_settings_2, month=month_index, filename=custom_filename, folder='offspring_ratio')
    else:
        print('Running setting other')
        for _ in range(5):
            for month_index in [3, 4, 11]:
                month_filename = month_filenames[month_index - 1]
                custom_filename = month_filename + '_80_over_100'
                do_default_run(run_settings_3, month=month_index, filename=custom_filename, folder='offspring_ratio')
