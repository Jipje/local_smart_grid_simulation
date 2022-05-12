import sys
from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, do_an_ea_run

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

if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    folder = 'population'

    if runnable_int == 1:
        print('Running setting 1')
        for _ in range(1):
            for month_index in [3, 4, 11]:
                month_filename = month_filenames[month_index - 1]
                custom_filename = month_filename + '_16_over_20'
                do_an_ea_run(run_settings_1, month=month_index, filename=custom_filename, folder=folder)
    elif runnable_int == 2:
        print('Running setting 2')
        for _ in range(1):
            for month_index in [3, 4, 11]:
                month_filename = month_filenames[month_index - 1]
                custom_filename = month_filename + '_32_over_40'
                do_an_ea_run(run_settings_2, month=month_index, filename=custom_filename, folder=folder)
    else:
        print('Running setting other')
        print(run_settings_3)
        for _ in range(1):
            for month_index in [3, 4, 11]:
                month_filename = month_filenames[month_index - 1]
                custom_filename = month_filename + '_160_over_200'
                do_an_ea_run(run_settings_3, month=month_index, filename=custom_filename, folder=folder)
