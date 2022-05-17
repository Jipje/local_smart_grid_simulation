import sys
from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, do_an_ea_run, execute_ea_runs

month_filenames = ['january', 'february', 'march', 'april',
                   'may', 'june', 'july', 'august',
                   'september', 'october', 'november', 'december']

run_settings_1 = default_ea_runnable_settings
run_settings_1['pop_size'] = 20
run_settings_1['n_offsprings'] = 16

run_settings_2 = default_ea_runnable_settings
run_settings_2['pop_size'] = 40
run_settings_2['n_offsprings'] = 32

run_settings_3 = default_ea_runnable_settings
run_settings_3['pop_size'] = 200
run_settings_3['n_offsprings'] = 160

run_settings_4 = default_ea_runnable_settings
run_settings_4['pop_size'] = 100
run_settings_4['n_offsprings'] = 80

if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    folder = 'population'

    if runnable_int == 1:
        print('Running setting 1')
        execute_ea_runs('_16_over_20', run_settings_1, folder)
    elif runnable_int == 2:
        print('Running setting 2')
        execute_ea_runs('_32_over_40', run_settings_2, folder)
    elif runnable_int == 3:
        print('Running setting 3')
        execute_ea_runs('_160_over_200', run_settings_3, folder)
    else:
        print('Running setting other')
        execute_ea_runs('_80_over_100', run_settings_4, folder)
