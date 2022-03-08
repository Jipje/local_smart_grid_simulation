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

    def base_initialisation(self):
        congestion_kw = 20000
        congestion_safety_margin = 1
        verbose_lvl = 4

        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        greedy_discharge_strat = CsvStrategy('Greedy discharge', strategy_csv=self.greedy_discharge_path)
        always_discharge_strat = CsvStrategy('Always discharge', strategy_csv=self.always_discharge_path)

        rhino = Battery('test_simple_congestion', 7500, 12000, starting_soc_kwh=3000, verbose_lvl=verbose_lvl)

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

        moo.add_mode_of_operation(dt.time(4, 45, tzinfo=utc), earn_money_mod)
        moo.add_mode_of_operation(dt.time(6, 45, tzinfo=utc), prepare_congestion_mod)
        moo.add_mode_of_operation(dt.time(16, 45, tzinfo=utc), solve_congestion_mod)
        moo.add_mode_of_operation(dt.time(23, 59, tzinfo=utc), earn_money_mod)
        return moo, rhino

    def test_initialisation(self):
        moo, rhino = self.base_initialisation()

        self.assertEqual(3000, rhino.state_of_charge_kwh)
        moo.take_step([-200, -200, 12000, dt.datetime(2021, 5, 6, 1, 30, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(3180, rhino.state_of_charge_kwh)

    def test_earning_money_in_the_morning(self):
        moo, rhino = self.base_initialisation()

        # Test normal charge
        self.assertEqual(3000, rhino.state_of_charge_kwh)
        moo.take_step([-200, -200, 12000, dt.datetime(2021, 5, 6, 1, 30, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(3180, rhino.state_of_charge_kwh)
        # Test normal discharge
        self.assertEqual(3180, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 8000, dt.datetime(2021, 5, 6, 1, 31, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2980, rhino.state_of_charge_kwh)
        # Test limited charge
        self.assertEqual(2980, rhino.state_of_charge_kwh)
        moo.take_step([-200, -200, 6000, dt.datetime(2021, 5, 6, 1, 32, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(3070, rhino.state_of_charge_kwh)
        # Test don't solve congestion
        self.assertEqual(3070, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 24000, dt.datetime(2021, 5, 6, 1, 33, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2870, rhino.state_of_charge_kwh)
        # Test physical limitations
        rhino.state_of_charge_kwh = 7100
        self.assertEqual(7100, rhino.state_of_charge_kwh)
        moo.take_step([-200, -200, 12000, dt.datetime(2021, 5, 6, 1, 34, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(7125, rhino.state_of_charge_kwh)

    def test_preparing_for_congestion_later_in_the_morning(self):
        moo, rhino = self.base_initialisation()

        # Test normal charge at 4:44
        self.assertEqual(3000, rhino.state_of_charge_kwh)
        moo.take_step([-200, -200, 12000, dt.datetime(2021, 5, 6, 4, 44, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(3180, rhino.state_of_charge_kwh)
        # Same state at 4:45 will now be a discharge
        self.assertEqual(3180, rhino.state_of_charge_kwh)
        moo.take_step([-200, -200, 7500, dt.datetime(2021, 5, 6, 4, 45, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2980, rhino.state_of_charge_kwh)

        # Will carry on discharging
        self.assertEqual(2980, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 8000, dt.datetime(2021, 5, 6, 4, 46, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2780, rhino.state_of_charge_kwh)
        # Bad prices will still be discharging at this time
        self.assertEqual(2780, rhino.state_of_charge_kwh)
        moo.take_step([-200, -200, 6000, dt.datetime(2021, 5, 6, 4, 47, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2580, rhino.state_of_charge_kwh)

        # Test do keep track of congestion -> Solve it
        self.assertEqual(2580, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 26000, dt.datetime(2021, 5, 6, 4, 48, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2670, rhino.state_of_charge_kwh)
        # Test do keep track of congestion -> don't cause it
        self.assertEqual(2670, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 14000, dt.datetime(2021, 5, 6, 4, 49, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2570, rhino.state_of_charge_kwh)

        # Test physical limitations
        rhino.state_of_charge_kwh = 400
        self.assertEqual(400, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 12000, dt.datetime(2021, 5, 6, 4, 50, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(375, rhino.state_of_charge_kwh)

    def test_solving_congestion(self):
        moo, rhino = self.base_initialisation()

        # Test forced discharge at 6:44
        self.assertEqual(3000, rhino.state_of_charge_kwh)
        moo.take_step([-200, -200, 7500, dt.datetime(2021, 5, 6, 6, 44, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2800, rhino.state_of_charge_kwh)
        # Same state at 6:45 will now be wait (waiting for congestion)
        self.assertEqual(2800, rhino.state_of_charge_kwh)
        moo.take_step([-200, -200, 12000, dt.datetime(2021, 5, 6, 6, 45, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2800, rhino.state_of_charge_kwh)

        # Good prices and room on the line allow discharging
        self.assertEqual(2800, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 8000, dt.datetime(2021, 5, 6, 6, 46, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2600, rhino.state_of_charge_kwh)
        # Good charge prices however will be wait actions due to expected congestion
        self.assertEqual(2600, rhino.state_of_charge_kwh)
        moo.take_step([-200, -200, 12000, dt.datetime(2021, 5, 6, 6, 47, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2600, rhino.state_of_charge_kwh)

        # Congestion should be solved
        self.assertEqual(2600, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 26000, dt.datetime(2021, 5, 6, 6, 48, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2690, rhino.state_of_charge_kwh)
        # And congestion shouldn't be caused by good prices
        self.assertEqual(2690, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 14000, dt.datetime(2021, 5, 6, 6, 49, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(2590, rhino.state_of_charge_kwh)

        # Test physical limitations
        rhino.state_of_charge_kwh = 400
        self.assertEqual(400, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 8000, dt.datetime(2021, 5, 6, 6, 50, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(375, rhino.state_of_charge_kwh)
        # Phyiscal charge limitations
        rhino.state_of_charge_kwh = 7100
        self.assertEqual(7100, rhino.state_of_charge_kwh)
        moo.take_step([500, 500, 26000, dt.datetime(2021, 5, 6, 6, 51, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(7125, rhino.state_of_charge_kwh)
