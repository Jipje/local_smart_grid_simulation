from StrategyBattery import StrategyBattery
import unittest


class TestStrategyBattery(unittest.TestCase):

    def test_nice_initialization(self):
        rhino_strategy = StrategyBattery(strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\simplified_passive_imbalance_1.csv')
        self.assertEqual(rhino_strategy.max_price, 105)
        self.assertEqual(rhino_strategy.min_price, -5)
        self.assertEqual(rhino_strategy.price_step_size, 5)

    def test_wrong_file_initialization(self):
        self.assertRaises(FileNotFoundError, StrategyBattery, strategy_csv='simplified_passive_imbalance_1.csv')

    def test_nice_charge_buckets(self):
        rhino_strategy = StrategyBattery(strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\simplified_passive_imbalance_1.csv')
        # Second bucket
        self.assertEqual(rhino_strategy.make_decision(-50, -50, 5), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(0, 0, 6), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(49, 49, 48), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(50, 50, 49), 'CHARGE')
        # Third bucket
        self.assertEqual(rhino_strategy.make_decision(30, 30, 50), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(29, 29, 51), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(0, 0, 68), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(-50, -50, 69), 'CHARGE')
        # Fourth bucket
        self.assertEqual(rhino_strategy.make_decision(-50, -50, 70), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(-1, -1, 71), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(-50, -50, 93), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(-1, -1, 94), 'CHARGE')

        self.assertEqual(rhino_strategy.make_decision(60, 60, 9), 'WAIT')
        self.assertEqual(rhino_strategy.make_decision(100, 100, 10), 'WAIT')

    def test_charge_extreme_buckets(self):
        rhino_strategy = StrategyBattery(strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\cleaner_simplified_passive_imbalance_1.csv')
        # First bucket
        self.assertEqual(rhino_strategy.make_decision(100, 100, 0), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(1000, 1000, 1), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(500, 500, 2), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(50, 50, 3), 'CHARGE')
        self.assertEqual(rhino_strategy.make_decision(-50, -50, 4), 'CHARGE')
        # Last bucket
        self.assertEqual(rhino_strategy.make_decision(-9996, -9996, 95), 'DISCHARGE')
        self.assertEqual(rhino_strategy.make_decision(-9996, -9996, 99), 'DISCHARGE')
        self.assertEqual(rhino_strategy.make_decision(-9996, -9996, 100), 'DISCHARGE')


if __name__ == '__main__':
    unittest.main()

