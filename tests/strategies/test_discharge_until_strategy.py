import os
import unittest

from helper_objects.strategies.CsvStrategy import CsvStrategy
from helper_objects.strategies.DischargeUntilStrategy import DischargeUntilStrategy
from helper_objects.strategies.StrategyDecorator import StrategyDecorator


class TestCaseDischargeUntilStrategy(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        strategy_one_path = '..{0}..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        try:
            CsvStrategy('Rhino Strategy One', strategy_csv=strategy_one_path)
        except FileNotFoundError:
            strategy_one_path = '..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        cls.strategy_one_path = strategy_one_path

    def test_initialisation(self):
        base_strategy = CsvStrategy('Rhino Strategy One', strategy_csv=self.strategy_one_path)
        discharge_decorator = DischargeUntilStrategy(base_strategy, 'Discharge decorator', 50)
        self.assertEqual('CHARGE', discharge_decorator.make_decision(-200, -200, 40))

    def test_charges(self):
        base_strategy = CsvStrategy('Rhino Strategy One', strategy_csv=self.strategy_one_path)
        discharge_decorator = DischargeUntilStrategy(base_strategy, 'Discharge decorator', 50)

        self.assertEqual('CHARGE', discharge_decorator.make_decision(-50, -50, 5))
        self.assertEqual('CHARGE', discharge_decorator.make_decision(49, 49, 48))
        self.assertEqual('CHARGE', discharge_decorator.make_decision(30, 30, 50))
        # However 51 SoC should be brought down
        self.assertEqual('CHARGE', base_strategy.make_decision(29, 29, 51))
        self.assertEqual('DISCHARGE', discharge_decorator.make_decision(29, 29, 51))

    def test_discharges(self):
        base_strategy = CsvStrategy('Rhino Strategy One', strategy_csv=self.strategy_one_path)
        discharge_decorator = DischargeUntilStrategy(base_strategy, 'Discharge decorator', 50)

        self.assertEqual('DISCHARGE',  base_strategy.make_decision(500, 500, 40))
        self.assertEqual('DISCHARGE', discharge_decorator.make_decision(500, 500, 40))


if __name__ == '__main__':
    unittest.main()
