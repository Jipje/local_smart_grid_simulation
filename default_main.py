import sys

from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, do_an_ea_run, execute_ea_runs

if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    default_run_settings = default_ea_runnable_settings

    if runnable_int == 1:
        print('Running setting 1')
        execute_ea_runs('', default_run_settings, 'default_runs',
                        month_indexes=[1, 2, 3, 4, 5, 6], num_of_runs=2)
    elif runnable_int == 2:
        print('Running setting 2')
        execute_ea_runs('', default_run_settings, 'default_runs',
                        month_indexes=[7, 8, 9, 10, 11, 12], num_of_runs=2)
    elif runnable_int == 3:
        print('Running setting 3')
        execute_ea_runs('', default_run_settings, 'default_runs_money',
                        month_indexes=[1, 2, 3, 4, 5, 6], num_of_runs=2, congestion_kw=34000)
    else:
        print('Running setting other')
        execute_ea_runs('', default_run_settings, 'default_runs_money',
                        month_indexes=[7, 8, 9, 10, 11, 12], num_of_runs=2, congestion_kw=34000)
