import sys
from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, execute_ea_runs

run_settings_1 = default_ea_runnable_settings
run_settings_1['n_offsprings'] = 40

run_settings_2 = default_ea_runnable_settings
run_settings_2['n_offsprings'] = 160

run_settings_3 = default_ea_runnable_settings
run_settings_3['n_offsprings'] = 80


if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    folder = 'offspring_ratio'

    if runnable_int == 1:
        print('Running setting 1')
        execute_ea_runs('_40_over_100', run_settings_1, folder)
    elif runnable_int == 2:
        print('Running setting 2')
        execute_ea_runs('_160_over_100', run_settings_2, folder)
    else:
        print('Running setting other')
        execute_ea_runs('_80_over_100', run_settings_3, folder)
