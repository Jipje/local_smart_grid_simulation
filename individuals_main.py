import sys

from evolutionary_algorithm.individuals.IndividualMutateNormalDist import IndividualMutateNormalDist
from evolutionary_algorithm.individuals.IndividualRandomNormalDist import IndividualRandomNormalDist
from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, do_an_ea_run

month_filenames = ['january', 'february', 'march', 'april',
                   'may', 'june', 'july', 'august',
                   'september', 'october', 'november', 'december']

run_settings_1 = default_ea_runnable_settings
run_settings_1['individual_class'] = IndividualRandomNormalDist

run_settings_2 = default_ea_runnable_settings
run_settings_2['individual_class'] = IndividualMutateNormalDist

if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    folder = 'individual'

    if runnable_int == 1:
        print('Running setting 1')
        for _ in range(4):
            for month_index in [3, 4, 11]:
                month_filename = month_filenames[month_index - 1]
                custom_filename = month_filename + '_double_dist'
                do_an_ea_run(run_settings_1, month=month_index, filename=custom_filename, folder=folder)
    else:
        print('Running setting other')
        for _ in range(4):
            for month_index in [3, 4, 11]:
                month_filename = month_filenames[month_index - 1]
                custom_filename = month_filename + '_single_dist'
                do_an_ea_run(run_settings_2, month=month_index, filename=custom_filename, folder=folder)
