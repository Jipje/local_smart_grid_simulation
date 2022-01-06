from helper_objects.StrategyBattery import StrategyBattery
from helper_objects.PointBasedStrategy import PointBasedStrategy
import unittest
import os


class TestPointBasedStrategy(unittest.TestCase):

    def test_nice_initialization(self):
        strategy_one_path = '..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        rhino_strategy = StrategyBattery(strategy_csv=strategy_one_path)

        self.assertEqual(rhino_strategy.max_price, 105)
        self.assertEqual(rhino_strategy.min_price, -5)
        self.assertEqual(rhino_strategy.price_step_size, 5)

        point_based_strat = PointBasedStrategy('TESTING')
        point_based_strat.add_point((50, 50, 'CHARGE'))
        point_based_strat.add_point((70, 30, 'CHARGE'))
        point_based_strat.add_point((95, 0, 'CHARGE'))

        point_based_strat.add_point((40, 100, 'DISCHARGE'))
        point_based_strat.add_point((70, 80, 'DISCHARGE'))
        point_based_strat.add_point((95, 65, 'DISCHARGE'))

        point_based_strat.upload_strategy()

        self.assertEqual(point_based_strat.max_price, 105)
        self.assertEqual(point_based_strat.min_price, -5)
        self.assertEqual(point_based_strat.price_step_size, 5)

        self.assertEqual(point_based_strat.strategy_matrix, point_based_strat.strategy_matrix)
