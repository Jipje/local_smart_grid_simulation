from csv import reader
import os
import random
import datetime as dt
import dateutil.tz
import pandas as pd
from pandas import NaT

from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from helper_objects.congestion_helper.month_congestion_size_and_timer import get_month_congestion_timings
from helper_objects.strategies.CsvStrategy import CsvStrategy
from helper_objects.strategies.DischargeUntilStrategy import DischargeUntilStrategy
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from helper_objects.strategies.RandomStrategyGenerator import generate_random_discharge_relative_strategy
from helper_objects.strategies.giga_baseline_strategies import get_month_strategy
from network_objects.Battery import Battery
from network_objects.control_strategies.ModesOfOperationController import ModesOfOperationController
from network_objects.control_strategies.MonthOfModesOfOperationController import MonthOfModesOfOperationController
from network_objects.control_strategies.SolveCongestionAndLimitedChargeControlTower import \
    SolveCongestionAndLimitedChargeControlTower
from network_objects.control_strategies.StrategyControlTower import StrategyControlTower
from environment.ImbalanceEnvironment import ImbalanceEnvironment
from network_objects.control_strategies.StrategyWithLimitedChargeCapacityControlTower import \
    StrategyWithLimitedChargeCapacityControlTower
from network_objects.control_strategies.SolveCongestionControlTower import \
    SolveCongestionControlTower
from network_objects.RenewableEnergyGenerator import RenewableEnergyGenerator
from main import run_full_scenario
import ast

base_scenario = 'data{0}environments{0}lelystad_1_2021.csv'.format(os.path.sep)
utc = dateutil.tz.tzutc()


def wombat_solarvation_limited_charging(verbose_lvl=1, twelve_strategies=None):
    # Wombat with limited charging simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, 14000)

    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(solarvation, [1, 3, 4])

    wombat = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=1600, verbose_lvl=verbose_lvl)

    main_controller = MonthOfModesOfOperationController(name='Wombat main controller',
                                                        network_object=wombat, verbose_lvl=verbose_lvl)
    for month_num in range(1, 13):
        money_earn_strat_month = twelve_strategies[month_num - 1]
        limited_charge_controller = StrategyWithLimitedChargeCapacityControlTower(
            name=f"Wombat Controller Month {month_num}", network_object=wombat, strategy=money_earn_strat_month,
            verbose_lvl=verbose_lvl, transportation_kw=2000)
        main_controller.add_controller(limited_charge_controller)
    imbalance_environment.add_object(main_controller, [1, 3, 4, 0])

    return run_full_scenario(simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def run_monthly_timed_baseline(verbose_lvl=2, transportation_kw=2000, congestion_kw=14000, congestion_strategy=1,
                               twelve_strategies=None):
    congestion_safety_margin = 0.99

    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, congestion_kw)

    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)

    battery = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=1600, verbose_lvl=verbose_lvl)

    res_df = get_month_congestion_timings(solarvation_identifier='data/environments/lelystad_1_2021.csv',
                                          strategy=congestion_strategy, congestion_kw=congestion_kw)
    print(res_df.to_string())

    earning_money_until = res_df.loc['prep_start']
    preparing_for_congestion_until = res_df.loc['congestion_start']
    preparing_max_kwh = res_df.loc['prep_max_soc']
    solving_congestion_until = res_df.loc['congestion_end']

    main_controller = MonthOfModesOfOperationController(name='Wombat main controller',
                                                        network_object=battery,
                                                        verbose_lvl=verbose_lvl)
    for month in range(12):
        moo = ModesOfOperationController(name=f'Wombat controller month {month}',
                                         network_object=battery,
                                         verbose_lvl=verbose_lvl)

        money_earning_strat = twelve_strategies[month]
        earn_money_mod = SolveCongestionAndLimitedChargeControlTower(name=f"Default Strategy Month {month + 1}",
                                                                     network_object=battery,
                                                                     congestion_kw=congestion_kw,
                                                                     congestion_safety_margin=congestion_safety_margin,
                                                                     strategy=money_earning_strat,
                                                                     verbose_lvl=verbose_lvl,
                                                                     transportation_kw=transportation_kw)
        if earning_money_until[month] is not NaT:
            moo.add_mode_of_operation(earning_money_until[month], earn_money_mod)

            max_kwh_in_prep = float(preparing_max_kwh[month])
            max_soc_perc_in_prep = int(max_kwh_in_prep / battery.max_kwh * 100)
            discharge_until_strategy = DischargeUntilStrategy(base_strategy=money_earning_strat,
                                                              name='Discharge Money Earner',
                                                              discharge_until_soc_perc=max_soc_perc_in_prep
                                                              )
            prepare_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name=f"Earn money but discharge until {max_soc_perc_in_prep}",
                                                                                 network_object=battery,
                                                                                 congestion_kw=congestion_kw,
                                                                                 congestion_safety_margin=congestion_safety_margin,
                                                                                 strategy=discharge_until_strategy,
                                                                                 verbose_lvl=verbose_lvl)

            moo.add_mode_of_operation(preparing_for_congestion_until[month], prepare_congestion_mod)
            moo.add_mode_of_operation(solving_congestion_until[month], prepare_congestion_mod)
        moo.add_mode_of_operation(dt.time(23, 59, tzinfo=utc), earn_money_mod)
        main_controller.add_controller(moo)

    imbalance_environment.add_object(solarvation, [1, 3, 4])
    imbalance_environment.add_object(main_controller, [1, 3, 4, 0])

    return run_full_scenario(scenario='data/environments/lelystad_1_2021.csv',
                             verbose_lvl=verbose_lvl,
                             simulation_environment=imbalance_environment)


if __name__ == '__main__':
    month_long = ['january', 'february', 'march', 'april',
                  'may', 'june', 'july', 'august',
                  'september', 'october', 'november', 'december']

    # january_strategy
    # february_strategy
    # march_strategy
    # april_strategy
    # may_strategy
    # june_strategy
    # july_strategy
    # august_strategy
    # september_strategy
    # october_strategy
    # november_strategy
    # december_strategy

    # DEFAULT RUNS MONEY 1
    january_strategy= [(10, 220, 'CHARGE'), (18, 208, 'CHARGE'), (47, 68, 'CHARGE'), (95, 52, 'CHARGE'), (4, 60, 'DISCHARGE'), (6, -166, 'DISCHARGE'), (20, -176, 'DISCHARGE'), (95, -512, 'DISCHARGE')]
    february_strategy= [(3, 236, 'CHARGE'), (34, 116, 'CHARGE'), (65, 50, 'CHARGE'), (95, 26, 'CHARGE'), (7, 342, 'DISCHARGE'), (46, 98, 'DISCHARGE'), (79, 48, 'DISCHARGE'), (95, -260, 'DISCHARGE')]
    march_strategy= [(5, 272, 'CHARGE'), (50, 68, 'CHARGE'), (86, 50, 'CHARGE'), (95, 20, 'CHARGE'), (14, 198, 'DISCHARGE'), (23, 126, 'DISCHARGE'), (57, -178, 'DISCHARGE'), (95, -232, 'DISCHARGE')]
    april_strategy= [(12, 242, 'CHARGE'), (49, 64, 'CHARGE'), (73, 36, 'CHARGE'), (95, -10, 'CHARGE'), (8, 256, 'DISCHARGE'), (39, 88, 'DISCHARGE'), (54, 56, 'DISCHARGE'), (95, -3622, 'DISCHARGE')]
    may_strategy= [(11, 192, 'CHARGE'), (39, 70, 'CHARGE'), (79, 56, 'CHARGE'), (95, -8, 'CHARGE'), (34, 112, 'DISCHARGE'), (61, 70, 'DISCHARGE'), (95, 6, 'DISCHARGE'), (95, -326, 'DISCHARGE')]
    june_strategy = [(21, 256, 'CHARGE'), (26, 128, 'CHARGE'), (77, 74, 'CHARGE'), (95, 12, 'CHARGE'), (16, 134, 'DISCHARGE'), (42, 120, 'DISCHARGE'), (79, 72, 'DISCHARGE'), (95, -16, 'DISCHARGE')]
    july_strategy= [(13, 272, 'CHARGE'), (54, 86, 'CHARGE'), (76, 48, 'CHARGE'), (95, -98, 'CHARGE'), (23, 128, 'DISCHARGE'), (61, 86, 'DISCHARGE'), (68, -88, 'DISCHARGE'), (95, -220, 'DISCHARGE')]
    august_strategy = [(19, 228, 'CHARGE'), (38, 108, 'CHARGE'), (83, 60, 'CHARGE'), (95, -34, 'CHARGE'), (2, 410, 'DISCHARGE'), (4, 208, 'DISCHARGE'), (72, 114, 'DISCHARGE'), (95, -296, 'DISCHARGE')]
    september_strategy= [(23, 208, 'CHARGE'), (65, 136, 'CHARGE'), (95, 108, 'CHARGE'), (95, -110, 'CHARGE'), (13, 216, 'DISCHARGE'), (34, 176, 'DISCHARGE'), (81, 150, 'DISCHARGE'), (95, -18, 'DISCHARGE')]
    october_strategy= [(1, 364, 'CHARGE'), (10, 264, 'CHARGE'), (44, 218, 'CHARGE'), (95, 134, 'CHARGE'), (23, 298, 'DISCHARGE'), (60, 206, 'DISCHARGE'), (85, 180, 'DISCHARGE'), (95, 70, 'DISCHARGE')]
    november_strategy= [(15, 262, 'CHARGE'), (48, 196, 'CHARGE'), (57, 192, 'CHARGE'), (95, 176, 'CHARGE'), (20, 320, 'DISCHARGE'), (48, 292, 'DISCHARGE'), (66, 230, 'DISCHARGE'), (95, -226, 'DISCHARGE')]
    december_strategy= [(44, 460, 'CHARGE'), (67, 364, 'CHARGE'), (83, 218, 'CHARGE'), (95, 180, 'CHARGE'), (11, 524, 'DISCHARGE'), (20, 92, 'DISCHARGE'), (51, -48, 'DISCHARGE'), (95, -58, 'DISCHARGE')]

    # DEFAULT RUNS MONEY 2
    january_strategy= [(13, 214, 'CHARGE'), (24, 162, 'CHARGE'), (51, 70, 'CHARGE'), (95, 44, 'CHARGE'), (8, 200, 'DISCHARGE'), (47, 68, 'DISCHARGE'), (82, 64, 'DISCHARGE'), (95, -86, 'DISCHARGE')]
    february_strategy= [(4, 94, 'CHARGE'), (45, 76, 'CHARGE'), (78, 42, 'CHARGE'), (95, 10, 'CHARGE'), (2, 230, 'DISCHARGE'), (26, 114, 'DISCHARGE'), (60, 48, 'DISCHARGE'), (95, 28, 'DISCHARGE')]
    march_strategy= [(23, 114, 'CHARGE'), (53, 70, 'CHARGE'), (85, 50, 'CHARGE'), (95, -34, 'CHARGE'), (6, 160, 'DISCHARGE'), (15, 124, 'DISCHARGE'), (75, 30, 'DISCHARGE'), (95, -108, 'DISCHARGE')]
    april_strategy= [(8, 264, 'CHARGE'), (14, 240, 'CHARGE'), (73, 58, 'CHARGE'), (95, 18, 'CHARGE'), (19, 164, 'DISCHARGE'), (76, 68, 'DISCHARGE'), (82, -126, 'DISCHARGE'), (95, -306, 'DISCHARGE')]
    may_strategy= [(7, 136, 'CHARGE'), (31, 106, 'CHARGE'), (67, 64, 'CHARGE'), (95, 36, 'CHARGE'), (7, 200, 'DISCHARGE'), (14, 38, 'DISCHARGE'), (44, -62, 'DISCHARGE'), (95, -136, 'DISCHARGE')]
    june_strategy= [(28, 260, 'CHARGE'), (70, 74, 'CHARGE'), (95, 32, 'CHARGE'), (95, -120, 'CHARGE'), (21, 226, 'DISCHARGE'), (48, 92, 'DISCHARGE'), (71, 76, 'DISCHARGE'), (95, -226, 'DISCHARGE')]
    july_strategy= [(19, 244, 'CHARGE'), (63, 82, 'CHARGE'), (76, 62, 'CHARGE'), (95, -22, 'CHARGE'), (13, 200, 'DISCHARGE'), (25, 106, 'DISCHARGE'), (64, 84, 'DISCHARGE'), (95, -104, 'DISCHARGE')]
    august_strategy= [(19, 172, 'CHARGE'), (51, 102, 'CHARGE'), (87, 64, 'CHARGE'), (95, -8, 'CHARGE'), (17, 156, 'DISCHARGE'), (36, 108, 'DISCHARGE'), (82, 102, 'DISCHARGE'), (95, -228, 'DISCHARGE')]
    september_strategy= [(11, 234, 'CHARGE'), (36, 176, 'CHARGE'), (83, 110, 'CHARGE'), (95, 48, 'CHARGE'), (4, 278, 'DISCHARGE'), (87, 150, 'DISCHARGE'), (88, 54, 'DISCHARGE'), (95, 12, 'DISCHARGE')]
    october_strategy= [(20, 320, 'CHARGE'), (35, 260, 'CHARGE'), (80, 178, 'CHARGE'), (95, 132, 'CHARGE'), (7, 320, 'DISCHARGE'), (41, 252, 'DISCHARGE'), (93, 86, 'DISCHARGE'), (95, 64, 'DISCHARGE')]
    november_strategy= [(31, 286, 'CHARGE'), (61, 224, 'CHARGE'), (95, 176, 'CHARGE'), (95, -292, 'CHARGE'), (17, 180, 'DISCHARGE'), (34, 26, 'DISCHARGE'), (65, -68, 'DISCHARGE'), (95, -196, 'DISCHARGE')]
    december_strategy= [(22, 394, 'CHARGE'), (60, 352, 'CHARGE'), (88, 218, 'CHARGE'), (95, 120, 'CHARGE'), (39, 502, 'DISCHARGE'), (68, 364, 'DISCHARGE'), (95, 184, 'DISCHARGE'), (95, 178, 'DISCHARGE')]

    # DEFAULT RUNS SOLVE CONGESTION 1
    january_strategy= [(5, 278, 'CHARGE'), (29, 78, 'CHARGE'), (91, 50, 'CHARGE'), (95, 8, 'CHARGE'), (5, 330, 'DISCHARGE'), (19, 214, 'DISCHARGE'), (77, 64, 'DISCHARGE'), (95, -60, 'DISCHARGE')]
    february_strategy= [(35, 70, 'CHARGE'), (54, 48, 'CHARGE'), (76, 38, 'CHARGE'), (95, -12, 'CHARGE'), (12, 148, 'DISCHARGE'), (27, 112, 'DISCHARGE'), (43, -28, 'DISCHARGE'), (95, -1182, 'DISCHARGE')]
    march_strategy= [(41, 88, 'CHARGE'), (89, 48, 'CHARGE'), (95, -40, 'CHARGE'), (95, -288, 'CHARGE'), (19, 134, 'DISCHARGE'), (42, 60, 'DISCHARGE'), (63, 52, 'DISCHARGE'), (95, -174, 'DISCHARGE')]
    april_strategy= [(20, 208, 'CHARGE'), (66, 72, 'CHARGE'), (78, 2, 'CHARGE'), (81, -122, 'CHARGE'), (17, 224, 'DISCHARGE'), (31, 92, 'DISCHARGE'), (80, 62, 'DISCHARGE'), (95, -32, 'DISCHARGE')]
    may_strategy= [(17, 170, 'CHARGE'), (51, 66, 'CHARGE'), (70, 46, 'CHARGE'), (95, -4, 'CHARGE'), (23, 104, 'DISCHARGE'), (43, -4, 'DISCHARGE'), (68, -154, 'DISCHARGE'), (88, -206, 'DISCHARGE')]
    june_strategy= [(7, 212, 'CHARGE'), (44, 206, 'CHARGE'), (74, 78, 'CHARGE'), (95, 58, 'CHARGE'), (5, 232, 'DISCHARGE'), (7, 190, 'DISCHARGE'), (28, -6, 'DISCHARGE'), (95, -126, 'DISCHARGE')]
    july_strategy= [(13, 126, 'CHARGE'), (28, 86, 'CHARGE'), (49, 84, 'CHARGE'), (77, 80, 'CHARGE'), (9, 268, 'DISCHARGE'), (21, 132, 'DISCHARGE'), (82, 80, 'DISCHARGE'), (95, -274, 'DISCHARGE')]
    august_strategy= [(19, 204, 'CHARGE'), (23, 118, 'CHARGE'), (82, 102, 'CHARGE'), (95, 42, 'CHARGE'), (8, 128, 'DISCHARGE'), (10, -132, 'DISCHARGE'), (57, -162, 'DISCHARGE'), (95, -364, 'DISCHARGE')]
    september_strategy= [(23, 204, 'CHARGE'), (72, 112, 'CHARGE'), (82, 82, 'CHARGE'), (95, 48, 'CHARGE'), (41, 180, 'DISCHARGE'), (57, 156, 'DISCHARGE'), (83, 4, 'DISCHARGE'), (93, -198, 'DISCHARGE')]
    october_strategy= [(32, 284, 'CHARGE'), (67, 166, 'CHARGE'), (95, 98, 'CHARGE'), (95, -34, 'CHARGE'), (7, 352, 'DISCHARGE'), (63, 208, 'DISCHARGE'), (90, 180, 'DISCHARGE'), (95, 106, 'DISCHARGE')]
    november_strategy= [(12, 332, 'CHARGE'), (67, 208, 'CHARGE'), (89, 176, 'CHARGE'), (95, 140, 'CHARGE'), (7, 280, 'DISCHARGE'), (46, 276, 'DISCHARGE'), (74, 144, 'DISCHARGE'), (95, -96, 'DISCHARGE')]
    december_strategy= [(45, 460, 'CHARGE'), (66, 368, 'CHARGE'), (95, 218, 'CHARGE'), (95, -148, 'CHARGE'), (15, 240, 'DISCHARGE'), (32, -102, 'DISCHARGE'), (48, -174, 'DISCHARGE'), (95, -326, 'DISCHARGE')]

    # DEFAULT RUNS SOLVE CONGESTION 2
    january_strategy= [(4, 280, 'CHARGE'), (15, 160, 'CHARGE'), (31, 70, 'CHARGE'), (95, 50, 'CHARGE'), (2, -26, 'DISCHARGE'), (5, -426, 'DISCHARGE'), (6, -450, 'DISCHARGE'), (95, -1024, 'DISCHARGE')]
    february_strategy= [(8, 212, 'CHARGE'), (42, 64, 'CHARGE'), (76, 44, 'CHARGE'), (95, 12, 'CHARGE'), (11, 194, 'DISCHARGE'), (41, 80, 'DISCHARGE'), (76, 4, 'DISCHARGE'), (95, -232, 'DISCHARGE')]
    march_strategy= [(23, 110, 'CHARGE'), (36, 76, 'CHARGE'), (54, 52, 'CHARGE'), (95, 44, 'CHARGE'), (6, 420, 'DISCHARGE'), (14, -286, 'DISCHARGE'), (65, -500, 'DISCHARGE'), (95, -1672, 'DISCHARGE')]
    april_strategy= [(17, 184, 'CHARGE'), (40, 84, 'CHARGE'), (56, 68, 'CHARGE'), (95, 48, 'CHARGE'), (6, 48, 'DISCHARGE'), (16, -24, 'DISCHARGE'), (95, -46, 'DISCHARGE'), (95, -1070, 'DISCHARGE')]
    may_strategy= [(10, 194, 'CHARGE'), (27, 108, 'CHARGE'), (52, 64, 'CHARGE'), (66, 48, 'CHARGE'), (8, -20, 'DISCHARGE'), (29, -28, 'DISCHARGE'), (82, -112, 'DISCHARGE'), (86, -1612, 'DISCHARGE')]
    june_strategy= [(28, 140, 'CHARGE'), (59, 88, 'CHARGE'), (75, 70, 'CHARGE'), (92, 58, 'CHARGE'), (5, 322, 'DISCHARGE'), (29, -154, 'DISCHARGE'), (30, -318, 'DISCHARGE'), (95, -652, 'DISCHARGE')]
    july_strategy= [(2, 274, 'CHARGE'), (46, 88, 'CHARGE'), (54, 80, 'CHARGE'), (82, 74, 'CHARGE'), (13, 228, 'DISCHARGE'), (26, 112, 'DISCHARGE'), (38, 70, 'DISCHARGE'), (86, -362, 'DISCHARGE')]
    august_strategy= [(16, 234, 'CHARGE'), (37, 106, 'CHARGE'), (71, 82, 'CHARGE'), (95, -54, 'CHARGE'), (1, 262, 'DISCHARGE'), (15, 230, 'DISCHARGE'), (60, 104, 'DISCHARGE'), (72, 42, 'DISCHARGE')]
    september_strategy= [(24, 204, 'CHARGE'), (55, 122, 'CHARGE'), (71, 62, 'CHARGE'), (74, 18, 'CHARGE'), (8, 342, 'DISCHARGE'), (38, 176, 'DISCHARGE'), (82, 146, 'DISCHARGE'), (85, -72, 'DISCHARGE')]
    october_strategy= [(29, 280, 'CHARGE'), (64, 178, 'CHARGE'), (93, 126, 'CHARGE'), (95, 34, 'CHARGE'), (5, 380, 'DISCHARGE'), (17, 308, 'DISCHARGE'), (42, 254, 'DISCHARGE'), (95, 174, 'DISCHARGE')]
    november_strategy= [(44, 270, 'CHARGE'), (49, 270, 'CHARGE'), (94, 174, 'CHARGE'), (95, 22, 'CHARGE'), (31, 322, 'DISCHARGE'), (65, 208, 'DISCHARGE'), (93, 20, 'DISCHARGE'), (95, 16, 'DISCHARGE')]
    december_strategy= [(42, 446, 'CHARGE'), (68, 362, 'CHARGE'), (86, 220, 'CHARGE'), (95, 176, 'CHARGE'), (3, 22, 'DISCHARGE'), (4, -144, 'DISCHARGE'), (6, -304, 'DISCHARGE'), (95, -714, 'DISCHARGE')]

    twelve_strategy_lines = [january_strategy, february_strategy, march_strategy,
                             april_strategy, may_strategy, june_strategy,
                             july_strategy, august_strategy, september_strategy,
                             october_strategy, november_strategy, december_strategy]
    twelve_strategy_set = []
    for strat_points_list in twelve_strategy_lines:
        month_strategy = PointBasedStrategy('Strategy month', price_step_size=2)
        for strat_point in strat_points_list:
            month_strategy.add_point(strat_point)
        month_strategy.upload_strategy()
        twelve_strategy_set.append(month_strategy)

    # wombat_solarvation_limited_charging(verbose_lvl=1, twelve_strategies=twelve_strategy_set)
    run_monthly_timed_baseline(verbose_lvl=1, twelve_strategies=twelve_strategy_set, congestion_strategy=1)
