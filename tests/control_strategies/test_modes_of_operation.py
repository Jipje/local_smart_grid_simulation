import unittest
import os
import datetime as dt
import dateutil.tz

from helper_objects.strategies.CsvStrategy import CsvStrategy
from network_objects.Battery import Battery
from network_objects.control_strategies.ModesOfOperationController import ModesOfOperationController
from network_objects.control_strategies.SolveCongestionAndLimitedChargeControlTower import \
    SolveCongestionAndLimitedChargeControlTower
from network_objects.control_strategies.StrategyWithLimitedChargeCapacityControlTower import \
    StrategyWithLimitedChargeCapacityControlTower

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


class TestModesOfOperationController(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        strategy_one_path = '..{0}..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        greedy_discharge_path = '..{0}..{0}data{0}strategies{0}greedy_discharge_60.csv'.format(os.path.sep)
        always_discharge_path = '..{0}..{0}data{0}strategies{0}always_discharge.csv'.format(os.path.sep)
        try:
            CsvStrategy('Rhino strategy 1', strategy_csv=strategy_one_path)
        except FileNotFoundError:
            strategy_one_path = '..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
            greedy_discharge_path = '..{0}data{0}strategies{0}greedy_discharge_60.csv'.format(os.path.sep)
            always_discharge_path = '..{0}data{0}strategies{0}always_discharge.csv'.format(os.path.sep)
        cls.strategy_one_path = strategy_one_path
        cls.greedy_discharge_path = greedy_discharge_path
        cls.always_discharge_path = always_discharge_path

    def test_initialisation(self):
        congestion_kw = 20000
        congestion_safety_margin = 1
        verbose_lvl = 4

        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        greedy_discharge_strat = CsvStrategy('Greedy discharge', strategy_csv=self.greedy_discharge_path)
        always_discharge_strat = CsvStrategy('Always discharge', strategy_csv=self.always_discharge_path)

        rhino = Battery('test_simple_congestion', 7500, 12000, starting_soc_kwh=0)

        solve_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Solve Congestion Controller",
                                                                           network_object=rhino,
                                                                           congestion_kw=congestion_kw,
                                                                           congestion_safety_margin=congestion_safety_margin,
                                                                           strategy=greedy_discharge_strat,
                                                                           verbose_lvl=verbose_lvl)

        prepare_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Prepare Congestion",
                                                                             network_object=rhino,
                                                                             congestion_kw=congestion_kw,
                                                                             congestion_safety_margin=congestion_safety_margin,
                                                                             strategy=always_discharge_strat,
                                                                             verbose_lvl=verbose_lvl)

        earn_money_mod = StrategyWithLimitedChargeCapacityControlTower(name="Rhino strategy 1",
                                                                       network_object=rhino,
                                                                       strategy=csv_strategy,
                                                                       verbose_lvl=verbose_lvl)

        moo = ModesOfOperationController(name='Rhino main controller',
                                         network_object=rhino,
                                         verbose_lvl=verbose_lvl)

        moo.add_mode_of_operation(dt.time(4, 45, tzinfo=utc), prepare_congestion_mod)
        moo.add_mode_of_operation(dt.time(6, 45, tzinfo=utc), solve_congestion_mod)
        moo.add_mode_of_operation(dt.time(16, 45, tzinfo=utc), earn_money_mod)
