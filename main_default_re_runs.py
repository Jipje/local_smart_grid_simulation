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

    # DEFAULT RUNS MONEY 3
    january_strategy= [(6, 236, 'CHARGE'), (49, 70, 'CHARGE'), (80, 48, 'CHARGE'), (95, 44, 'CHARGE'), (6, 380, 'DISCHARGE'), (20, 206, 'DISCHARGE'), (75, 64, 'DISCHARGE'), (95, -210, 'DISCHARGE')]
    february_strategy= [(10, 184, 'CHARGE'), (44, 78, 'CHARGE'), (77, 42, 'CHARGE'), (95, 20, 'CHARGE'), (8, 226, 'DISCHARGE'), (25, 114, 'DISCHARGE'), (50, 52, 'DISCHARGE'), (95, -582, 'DISCHARGE')]
    march_strategy= [(17, 202, 'CHARGE'), (55, 74, 'CHARGE'), (90, 46, 'CHARGE'), (95, -46, 'CHARGE'), (1, 280, 'DISCHARGE'), (20, 156, 'DISCHARGE'), (73, 54, 'DISCHARGE'), (95, -40, 'DISCHARGE')]
    april_strategy= [(38, 88, 'CHARGE'), (67, 48, 'CHARGE'), (83, 20, 'CHARGE'), (95, -34, 'CHARGE'), (4, 146, 'DISCHARGE'), (44, 74, 'DISCHARGE'), (45, -18, 'DISCHARGE'), (95, -156, 'DISCHARGE')]
    may_strategy= [(1, 258, 'CHARGE'), (27, 108, 'CHARGE'), (77, 56, 'CHARGE'), (95, 16, 'CHARGE'), (27, 92, 'DISCHARGE'), (58, 72, 'DISCHARGE'), (67, 30, 'DISCHARGE'), (95, -62, 'DISCHARGE')]
    june_strategy= [(35, 246, 'CHARGE'), (55, 88, 'CHARGE'), (82, 74, 'CHARGE'), (95, 34, 'CHARGE'), (9, 96, 'DISCHARGE'), (15, 20, 'DISCHARGE'), (31, -254, 'DISCHARGE'), (95, -276, 'DISCHARGE')]
    july_strategy= [(19, 154, 'CHARGE'), (65, 82, 'CHARGE'), (76, 66, 'CHARGE'), (95, -98, 'CHARGE'), (17, 232, 'DISCHARGE'), (26, 108, 'DISCHARGE'), (32, 48, 'DISCHARGE'), (95, -314, 'DISCHARGE')]
    august_strategy= [(29, 114, 'CHARGE'), (59, 102, 'CHARGE'), (80, 80, 'CHARGE'), (95, -58, 'CHARGE'), (17, 300, 'DISCHARGE'), (24, 92, 'DISCHARGE'), (95, -222, 'DISCHARGE'), (95, -228, 'DISCHARGE')]
    september_strategy= [(4, 540, 'CHARGE'), (25, 204, 'CHARGE'), (77, 126, 'CHARGE'), (95, 78, 'CHARGE'), (13, 244, 'DISCHARGE'), (55, 170, 'DISCHARGE'), (86, 148, 'DISCHARGE'), (95, -46, 'DISCHARGE')]
    october_strategy= [(51, 212, 'CHARGE'), (64, 174, 'CHARGE'), (86, 134, 'CHARGE'), (95, 62, 'CHARGE'), (15, 300, 'DISCHARGE'), (32, 282, 'DISCHARGE'), (88, 184, 'DISCHARGE'), (95, 110, 'DISCHARGE')]
    november_strategy= [(13, 348, 'CHARGE'), (46, 272, 'CHARGE'), (61, 206, 'CHARGE'), (95, 174, 'CHARGE'), (7, 404, 'DISCHARGE'), (65, 178, 'DISCHARGE'), (85, 148, 'DISCHARGE'), (95, 14, 'DISCHARGE')]
    december_strategy= [(41, 466, 'CHARGE'), (67, 362, 'CHARGE'), (84, 220, 'CHARGE'), (95, 182, 'CHARGE'), (7, 714, 'DISCHARGE'), (11, 98, 'DISCHARGE'), (20, -74, 'DISCHARGE'), (95, -424, 'DISCHARGE')]

    # DEFAULT RUNS MONEY 4
    january_strategy= [(2, 238, 'CHARGE'), (18, 142, 'CHARGE'), (40, 74, 'CHARGE'), (95, 50, 'CHARGE'), (13, 242, 'DISCHARGE'), (41, -40, 'DISCHARGE'), (82, -70, 'DISCHARGE'), (95, -118, 'DISCHARGE')]
    february_strategy= [(19, 112, 'CHARGE'), (48, 80, 'CHARGE'), (76, 48, 'CHARGE'), (95, 26, 'CHARGE'), (1, 144, 'DISCHARGE'), (8, -306, 'DISCHARGE'), (13, -662, 'DISCHARGE'), (95, -1396, 'DISCHARGE')]
    march_strategy= [(27, 94, 'CHARGE'), (55, 74, 'CHARGE'), (88, 50, 'CHARGE'), (95, -28, 'CHARGE'), (1, 62, 'DISCHARGE'), (17, -38, 'DISCHARGE'), (50, -82, 'DISCHARGE'), (95, -228, 'DISCHARGE')]
    april_strategy= [(4, 384, 'CHARGE'), (9, 198, 'CHARGE'), (64, 64, 'CHARGE'), (95, 18, 'CHARGE'), (8, 218, 'DISCHARGE'), (21, 144, 'DISCHARGE'), (70, 56, 'DISCHARGE'), (95, -230, 'DISCHARGE')]
    may_strategy= [(5, 102, 'CHARGE'), (48, 80, 'CHARGE'), (79, 56, 'CHARGE'), (95, 8, 'CHARGE'), (14, 146, 'DISCHARGE'), (48, 82, 'DISCHARGE'), (58, 70, 'DISCHARGE'), (95, 6, 'DISCHARGE')]
    june_strategy= [(17, 204, 'CHARGE'), (33, 122, 'CHARGE'), (74, 74, 'CHARGE'), (95, 34, 'CHARGE'), (44, 86, 'DISCHARGE'), (68, 84, 'DISCHARGE'), (78, 76, 'DISCHARGE'), (95, -20, 'DISCHARGE')]
    july_strategy= [(22, 122, 'CHARGE'), (58, 84, 'CHARGE'), (71, 54, 'CHARGE'), (95, -24, 'CHARGE'), (1, 344, 'DISCHARGE'), (12, 260, 'DISCHARGE'), (63, 84, 'DISCHARGE'), (95, -54, 'DISCHARGE')]
    august_strategy= [(12, 170, 'CHARGE'), (39, 108, 'CHARGE'), (85, 66, 'CHARGE'), (95, -2, 'CHARGE'), (14, 300, 'DISCHARGE'), (21, 160, 'DISCHARGE'), (81, 104, 'DISCHARGE'), (95, 50, 'DISCHARGE')]
    september_strategy= [(11, 246, 'CHARGE'), (36, 176, 'CHARGE'), (82, 116, 'CHARGE'), (95, 68, 'CHARGE'), (1, 262, 'DISCHARGE'), (19, 188, 'DISCHARGE'), (84, 146, 'DISCHARGE'), (95, -98, 'DISCHARGE')]
    october_strategy= [(20, 280, 'CHARGE'), (28, 196, 'CHARGE'), (56, 166, 'CHARGE'), (95, 134, 'CHARGE'), (19, 288, 'DISCHARGE'), (38, 224, 'DISCHARGE'), (75, 194, 'DISCHARGE'), (95, -10, 'DISCHARGE')]
    november_strategy= [(41, 272, 'CHARGE'), (63, 198, 'CHARGE'), (87, 174, 'CHARGE'), (95, 164, 'CHARGE'), (20, 330, 'DISCHARGE'), (27, 204, 'DISCHARGE'), (45, 48, 'DISCHARGE'), (95, -38, 'DISCHARGE')]
    december_strategy= [(42, 464, 'CHARGE'), (68, 364, 'CHARGE'), (85, 218, 'CHARGE'), (95, 182, 'CHARGE'), (7, 328, 'DISCHARGE'), (29, 190, 'DISCHARGE'), (56, 94, 'DISCHARGE'), (95, -144, 'DISCHARGE')]

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

    # DEFAULT RUNS SOLVE CONGESTION 3
    january_strategy= [(8, 202, 'CHARGE'), (43, 68, 'CHARGE'), (67, 52, 'CHARGE'), (95, 50, 'CHARGE'), (16, 210, 'DISCHARGE'), (18, 146, 'DISCHARGE'), (44, 32, 'DISCHARGE'), (95, 24, 'DISCHARGE')]
    february_strategy= [(42, 82, 'CHARGE'), (61, 48, 'CHARGE'), (74, 38, 'CHARGE'), (95, -8, 'CHARGE'), (5, 62, 'DISCHARGE'), (12, -38, 'DISCHARGE'), (90, -80, 'DISCHARGE'), (95, -242, 'DISCHARGE')]
    march_strategy= [(10, 164, 'CHARGE'), (40, 76, 'CHARGE'), (54, 52, 'CHARGE'), (95, 44, 'CHARGE'), (5, 172, 'DISCHARGE'), (12, 134, 'DISCHARGE'), (79, -18, 'DISCHARGE'), (95, -78, 'DISCHARGE')]
    april_strategy= [(11, 218, 'CHARGE'), (66, 74, 'CHARGE'), (70, 10, 'CHARGE'), (86, 10, 'CHARGE'), (23, 188, 'DISCHARGE'), (43, 70, 'DISCHARGE'), (80, 62, 'DISCHARGE'), (93, -70, 'DISCHARGE')]
    may_strategy= [(26, 108, 'CHARGE'), (52, 62, 'CHARGE'), (82, 46, 'CHARGE'), (95, -12, 'CHARGE'), (6, 178, 'DISCHARGE'), (16, 130, 'DISCHARGE'), (76, -332, 'DISCHARGE'), (93, -422, 'DISCHARGE')]
    june_strategy= [(39, 224, 'CHARGE'), (63, 84, 'CHARGE'), (76, 70, 'CHARGE'), (83, 62, 'CHARGE'), (4, 378, 'DISCHARGE'), (8, 50, 'DISCHARGE'), (39, -632, 'DISCHARGE'), (95, -736, 'DISCHARGE')]
    july_strategy= [(9, 278, 'CHARGE'), (23, 120, 'CHARGE'), (53, 86, 'CHARGE'), (92, 76, 'CHARGE'), (4, 142, 'DISCHARGE'), (11, 94, 'DISCHARGE'), (17, 78, 'DISCHARGE'), (95, -122, 'DISCHARGE')]
    august_strategy= [(15, 276, 'CHARGE'), (64, 106, 'CHARGE'), (85, 76, 'CHARGE'), (95, 2, 'CHARGE'), (17, 238, 'DISCHARGE'), (29, 88, 'DISCHARGE'), (61, -98, 'DISCHARGE'), (66, -222, 'DISCHARGE')]
    september_strategy= [(12, 250, 'CHARGE'), (22, 210, 'CHARGE'), (40, 126, 'CHARGE'), (79, 112, 'CHARGE'), (5, 322, 'DISCHARGE'), (29, 180, 'DISCHARGE'), (57, 146, 'DISCHARGE'), (95, 68, 'DISCHARGE')]
    october_strategy= [(28, 280, 'CHARGE'), (61, 172, 'CHARGE'), (87, 134, 'CHARGE'), (95, 92, 'CHARGE'), (3, 298, 'DISCHARGE'), (36, 268, 'DISCHARGE'), (89, 178, 'DISCHARGE'), (95, 112, 'DISCHARGE')]
    november_strategy= [(46, 272, 'CHARGE'), (60, 208, 'CHARGE'), (83, 174, 'CHARGE'), (95, 124, 'CHARGE'), (13, 356, 'DISCHARGE'), (54, 200, 'DISCHARGE'), (95, 172, 'DISCHARGE'), (95, -1668, 'DISCHARGE')]
    december_strategy= [(41, 466, 'CHARGE'), (66, 360, 'CHARGE'), (87, 218, 'CHARGE'), (95, 146, 'CHARGE'), (21, 396, 'DISCHARGE'), (53, 384, 'DISCHARGE'), (69, 300, 'DISCHARGE'), (95, 174, 'DISCHARGE')]

    # DEFAULT RUNS SOLVE CONGESTION 4
    january_strategy= [(3, 330, 'CHARGE'), (22, 192, 'CHARGE'), (45, 68, 'CHARGE'), (95, 46, 'CHARGE'), (6, 142, 'DISCHARGE'), (32, 88, 'DISCHARGE'), (70, 62, 'DISCHARGE'), (95, -438, 'DISCHARGE')]
    february_strategy= [(18, 108, 'CHARGE'), (45, 80, 'CHARGE'), (74, 44, 'CHARGE'), (95, 12, 'CHARGE'), (6, 116, 'DISCHARGE'), (56, 52, 'DISCHARGE'), (81, 44, 'DISCHARGE'), (95, -284, 'DISCHARGE')]
    march_strategy= [(9, 150, 'CHARGE'), (15, 92, 'CHARGE'), (41, 80, 'CHARGE'), (95, 42, 'CHARGE'), (2, 350, 'DISCHARGE'), (18, 156, 'DISCHARGE'), (89, 52, 'DISCHARGE'), (95, -346, 'DISCHARGE')]
    april_strategy= [(2, 430, 'CHARGE'), (19, 224, 'CHARGE'), (66, 56, 'CHARGE'), (69, -184, 'CHARGE'), (2, 478, 'DISCHARGE'), (8, 288, 'DISCHARGE'), (68, 74, 'DISCHARGE'), (88, -374, 'DISCHARGE')]
    may_strategy= [(26, 106, 'CHARGE'), (53, 64, 'CHARGE'), (68, 48, 'CHARGE'), (95, -202, 'CHARGE'), (5, 310, 'DISCHARGE'), (7, 186, 'DISCHARGE'), (27, 88, 'DISCHARGE'), (89, -36, 'DISCHARGE')]
    june_strategy= [(40, 240, 'CHARGE'), (67, 82, 'CHARGE'), (80, 62, 'CHARGE'), (84, -50, 'CHARGE'), (10, 154, 'DISCHARGE'), (72, 74, 'DISCHARGE'), (73, -42, 'DISCHARGE'), (95, -96, 'DISCHARGE')]
    july_strategy= [(33, 88, 'CHARGE'), (50, 84, 'CHARGE'), (61, 78, 'CHARGE'), (89, 72, 'CHARGE'), (4, 490, 'DISCHARGE'), (11, 236, 'DISCHARGE'), (23, 106, 'DISCHARGE'), (95, -1144, 'DISCHARGE')]
    august_strategy= [(19, 198, 'CHARGE'), (30, 106, 'CHARGE'), (47, 104, 'CHARGE'), (83, 76, 'CHARGE'), (2, 374, 'DISCHARGE'), (15, 120, 'DISCHARGE'), (77, 104, 'DISCHARGE'), (95, -1160, 'DISCHARGE')]
    september_strategy= [(20, 208, 'CHARGE'), (48, 138, 'CHARGE'), (78, 112, 'CHARGE'), (95, 40, 'CHARGE'), (1, 354, 'DISCHARGE'), (33, 176, 'DISCHARGE'), (59, 142, 'DISCHARGE'), (94, 112, 'DISCHARGE')]
    october_strategy= [(38, 280, 'CHARGE'), (59, 192, 'CHARGE'), (71, 140, 'CHARGE'), (95, 72, 'CHARGE'), (36, 268, 'DISCHARGE'), (50, 216, 'DISCHARGE'), (90, 178, 'DISCHARGE'), (95, 48, 'DISCHARGE')]
    november_strategy= [(30, 302, 'CHARGE'), (47, 260, 'CHARGE'), (63, 194, 'CHARGE'), (95, 176, 'CHARGE'), (16, 338, 'DISCHARGE'), (45, 112, 'DISCHARGE'), (61, 40, 'DISCHARGE'), (95, -42, 'DISCHARGE')]
    december_strategy= [(42, 460, 'CHARGE'), (67, 362, 'CHARGE'), (81, 218, 'CHARGE'), (95, 182, 'CHARGE'), (6, 152, 'DISCHARGE'), (8, 134, 'DISCHARGE'), (72, -182, 'DISCHARGE'), (95, -228, 'DISCHARGE')]

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
