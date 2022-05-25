import sys
from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, execute_ea_runs

run_settings_1 = default_ea_runnable_settings
run_settings_1['sort_strategy'] = None

run_settings_2 = default_ea_runnable_settings
run_settings_2['sort_strategy'] = 3

run_settings_3 = default_ea_runnable_settings
run_settings_3['sort_strategy'] = 2

run_settings_4 = default_ea_runnable_settings
run_settings_4['sort_strategy'] = 1


if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    folder = 'sorting'

    if runnable_int == 1:
        print('Running setting 1')
        execute_ea_runs('_no_sort', run_settings_1, folder, num_of_runs=2)
    elif runnable_int == 2:
        print('Running setting 2')
        execute_ea_runs('_sort_3', run_settings_2, folder)
    elif runnable_int == 3:
        print('Running setting 3')
        execute_ea_runs('_sort_2', run_settings_3, folder)
    else:
        print('Running setting other')
        execute_ea_runs('_sort_1', run_settings_4, folder)
