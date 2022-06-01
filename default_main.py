from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, do_an_ea_run, execute_ea_runs

if __name__ == '__main__':
    run_settings = default_ea_runnable_settings
    execute_ea_runs('', run_settings, 'default_runs',
                    month_indexes=[1, 2, 5, 6, 7, 8, 9, 10, 12], num_of_runs=6)
