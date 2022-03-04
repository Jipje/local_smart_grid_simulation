import unittest
import os

from helper_objects.strategies.CsvStrategy import CsvStrategy
from network_objects.Battery import Battery
from network_objects.control_strategies.StrategyWithLimitedChargeCapacityControlTower import \
    StrategyWithLimitedChargeCapacityControlTower
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
        rhino = Battery('test_simple_congestion', 7500, 12000, starting_soc_kwh=0)
        limited_charge_control_tower = StrategyWithLimitedChargeCapacityControlTower(name="Rhino Battery Controller", network_object=rhino, strategy=csv_strategy, verbose_lvl=4)

    def test_max_charge(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=6825)
        simple_strategy_controller = StrategyWithLimitedChargeCapacityControlTower(name="Rhino Battery Controller",                                                                         network_object=rhino,
                                                                                   strategy=csv_strategy)
        # Normal charging
        simple_strategy_controller.take_step([-200, -200, 12000, -500], [0, 1, 2])
        self.assertEqual(7005, rhino.state_of_charge_kwh)
        # Limited charging constraints
        simple_strategy_controller.take_step([-200, -200, 6000, -500], [0, 1, 2])
        self.assertEqual(7095, rhino.state_of_charge_kwh)
        # Original battery constraints
        simple_strategy_controller.take_step([-200, -200, 12000, -500], [0, 1, 2])
        self.assertEqual(7124, rhino.state_of_charge_kwh)
