import unittest
import os
import datetime as dt
from unittest.mock import MagicMock

import dateutil.tz

from helper_objects.strategies.CsvStrategy import CsvStrategy
from network_objects.Battery import Battery
from network_objects.control_strategies.ModesOfOperationController import ModesOfOperationController
from network_objects.control_strategies.MonthOfModesOfOperationController import MonthOfModesOfOperationController
from network_objects.control_strategies.SolveCongestionAndLimitedChargeControlTower import \
    SolveCongestionAndLimitedChargeControlTower
from network_objects.control_strategies.StrategyWithLimitedChargeCapacityControlTower import \
    StrategyWithLimitedChargeCapacityControlTower

ams = dateutil.tz.gettz('Europe/Amsterdam')
utc = dateutil.tz.tzutc()


class TestMonthOfModesOfOperationController(unittest.TestCase):

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

    def test_base_workings(self):
        rhino = Battery('test_simple_congestion', 7500, 12000, starting_soc_kwh=3000, verbose_lvl=4)
        month_of_modes_of_operation_control_tower = MonthOfModesOfOperationController('test_base', rhino)

        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                        'July', 'August', 'September', 'October', 'November', 'December']
        month_moo = []
        for i in range(12):
            name = month_names[i]
            moo = ModesOfOperationController(name, rhino)
            moo.determine_step = MagicMock(name='determine_step')
            moo.determine_step.return_value = 'CHARGE', i * 500

            month_moo.append(moo)
            month_of_modes_of_operation_control_tower.add_controller(moo)

        month_of_modes_of_operation_control_tower.determine_step([-200, -200, 12000, dt.datetime(2021, 5, 6, 1, 30, tzinfo=utc)], [0, 1, 2, 3])
        month_moo[4].determine_step.assert_called_once_with([-200, -200, 12000, dt.datetime(2021, 5, 6, 1, 30, tzinfo=utc)], [0, 1, 2, 3])

        month_of_modes_of_operation_control_tower.determine_step([500, 500, 8000, dt.datetime(2021, 6, 6, 1, 31, tzinfo=utc)], [0, 1, 2, 3])
        month_moo[5].determine_step.assert_called_once_with([500, 500, 8000, dt.datetime(2021, 6, 6, 1, 31, tzinfo=utc)], [0, 1, 2, 3])

        month_of_modes_of_operation_control_tower.take_step([-200, -200, 6000, dt.datetime(2021, 7, 6, 1, 32, tzinfo=utc)], [0, 1, 2, 3])
        month_moo[6].determine_step.assert_called_once_with([-200, -200, 6000, dt.datetime(2021, 7, 6, 1, 32, tzinfo=utc)], [0, 1, 2, 3])
        self.assertEqual(3045, rhino.state_of_charge_kwh)

    def test_faulty_initialization(self):
        rhino = Battery('test_simple_congestion', 7500, 12000, starting_soc_kwh=3000, verbose_lvl=4)
        month_of_modes_of_operation_control_tower = MonthOfModesOfOperationController('test_base', rhino)

        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_moo = []
        for i in range(12):
            name = month_names[i]
            moo = ModesOfOperationController(name, rhino)
            moo.determine_step = MagicMock(name='determine_step')
            moo.determine_step.return_value = 'CHARGE', i * 500

            month_moo.append(moo)
            month_of_modes_of_operation_control_tower.add_controller(moo)

        self.assertRaises(AttributeError, month_of_modes_of_operation_control_tower.add_controller, None)

    def test_not_ready_yet(self):
        rhino = Battery('test_simple_congestion', 7500, 12000, starting_soc_kwh=3000, verbose_lvl=4)
        month_of_modes_of_operation_control_tower = MonthOfModesOfOperationController('test_base', rhino)

        month_names = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December']
        month_moo = []
        for i in range(10):
            name = month_names[i]
            moo = ModesOfOperationController(name, rhino)
            moo.determine_step = MagicMock(name='determine_step')
            moo.determine_step.return_value = 'CHARGE', i * 500

            month_moo.append(moo)
            month_of_modes_of_operation_control_tower.add_controller(moo)

        self.assertRaises(AttributeError, month_of_modes_of_operation_control_tower.determine_step, [], [])
