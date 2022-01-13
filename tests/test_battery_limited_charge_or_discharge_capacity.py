import unittest
import os

from helper_objects.strategies.CsvStrategy import CsvStrategy
from network_objects.Battery import Battery
from network_objects.decorators.LimitedChargeOrDischargeCapacity import LimitedChargeOrDischargeCapacity


class TestLimitedChargeOrDischargeCapacity(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        strategy_one_path = '..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        try:
            CsvStrategy('Rhino strategy 1', strategy_csv=strategy_one_path)
        except FileNotFoundError:
            strategy_one_path = 'data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        cls.strategy_one_path = strategy_one_path

    def test_initialisation(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_simple_congestion', 7500, 12000, strategy=csv_strategy, starting_soc_kwh=0)
        LimitedChargeOrDischargeCapacity(rhino, 5, 6)

    def test_max_charge(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, strategy=csv_strategy, starting_soc_kwh=6825)
        LimitedChargeOrDischargeCapacity(rhino, 2, 3)
        # Normal charging
        rhino.take_step([-200, -200, 500, -500], [0, 1])
        self.assertEqual(7005, rhino.state_of_charge_kwh)
        # Limited charging constraints
        rhino.take_step([-200, -200, 100, -500], [0, 1])
        self.assertEqual(7095, rhino.state_of_charge_kwh)
        # Original battery constraints
        rhino.take_step([-200, -200, 500, -500], [0, 1])
        self.assertEqual(7124, rhino.state_of_charge_kwh)

    def test_max_discharge(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_discharge', 7500, 12000, strategy=csv_strategy, starting_soc_kwh=700)
        LimitedChargeOrDischargeCapacity(rhino, 2, 3)
        # Normal discharging
        rhino.take_step([500, 500, 500, -500], [0, 1])
        self.assertEqual(500, rhino.state_of_charge_kwh)
        # Limited discharging constraints
        rhino.take_step([500, 500, 500, -100], [0, 1])
        self.assertEqual(400, rhino.state_of_charge_kwh)
        # Original battery constraints
        rhino.take_step([500, 500, 500, -500], [0, 1])
        self.assertEqual(375, rhino.state_of_charge_kwh)
