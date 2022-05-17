import sys

from evolutionary_algorithm.individuals.IndividualMutateNormalDist import IndividualMutateNormalDist
from evolutionary_algorithm.individuals.IndividualRandomNormalDist import IndividualRandomNormalDist
from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, do_an_ea_run, execute_ea_runs

run_settings_1 = default_ea_runnable_settings
run_settings_1['individual_class'] = IndividualMutateNormalDist

run_settings_2 = default_ea_runnable_settings
run_settings_2['individual_class'] = IndividualRandomNormalDist

if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    folder = 'individual'

    if runnable_int == 1:
        print('Running setting 1')
        execute_ea_runs('_single_dist', run_settings_1, folder)
    else:
        print('Running setting other')
        execute_ea_runs('_double_dist', run_settings_2, folder)
