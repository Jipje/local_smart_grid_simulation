from evolutionary_algorithm.individuals.guided_initialisation.GuidedInitRandomNormalDist import \
    GuidedInitRandomNormalDist
from evolutionary_algorithm.runnable_main import default_ea_runnable_settings, do_an_ea_run


if __name__ == '__main__':
    run_settings_1 = default_ea_runnable_settings
    default_ea_runnable_settings['individual_class'] = GuidedInitRandomNormalDist
    # for month_index in range(1, 13):
    month_index = 9
    do_an_ea_run(ea_runnable_settings=run_settings_1, month=month_index, folder='giga_baseline_with_congestion')
