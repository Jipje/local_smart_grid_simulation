from StrategyBattery import StrategyBattery
import unittest


class TestStrategyBattery(unittest.TestCase):

    def test_nice_initialization(self):
        rhino_strategy = StrategyBattery(strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\cleaner_simplified_passive_imbalance_1.csv')
        self.assertEqual(rhino_strategy.max_price, 105)
        self.assertEqual(rhino_strategy.min_price, -5)
        self.assertEqual(rhino_strategy.price_step_size, 5)

    def test_wrong_file_initialization(self):
        self.assertRaises(FileNotFoundError, StrategyBattery, strategy_csv='bla_bla_simplified_passive_imbalance_1.csv')

    def test_weird_strategy_files(self):
        self.assertRaises(AssertionError, StrategyBattery, strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\weird_strategies\strategy_not_0.csv')
        self.assertRaises(AssertionError, StrategyBattery, strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\weird_strategies\strategy_not_100.csv')
        self.assertRaises(ValueError, StrategyBattery, strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\weird_strategies\strategy_not_step_5.csv')
        self.assertRaises(ValueError, StrategyBattery, strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\weird_strategies\strategy_unknown_action.csv')

    def test_faulty_soc_make_decision(self):
        rhino_strategy = StrategyBattery(strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\cleaner_simplified_passive_imbalance_1.csv')
        self.assertRaises(ValueError, rhino_strategy.make_decision, 20, 20, -1)
        self.assertRaises(ValueError, rhino_strategy.make_decision, 20, 20, 101)

    def test_nice_charge_buckets(self):
        rhino_strategy = StrategyBattery(strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\cleaner_simplified_passive_imbalance_1.csv')
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

    def test_nice_waiting_charge_buckets(self):
        rhino_strategy = StrategyBattery(strategy_csv='F:\Documents\GitHub\local_smart_grid_simulation\data\strategies\cleaner_simplified_passive_imbalance_1.csv')
        # Second bucket
        self.assertEqual(rhino_strategy.make_decision(51, 51, 5), 'WAIT')
        self.assertEqual(rhino_strategy.make_decision(98, 98, 6), 'WAIT')
        self.assertEqual(rhino_strategy.make_decision(52, 52, 38), 'WAIT')
        self.assertEqual(rhino_strategy.make_decision(99, 99, 39), 'WAIT')
        # Third bucket
        self.assertEqual(rhino_strategy.make_decision(52, 52, 40), 'WAIT')
        self.assertEqual(rhino_strategy.make_decision(78, 78, 41), 'WAIT')
        self.assertEqual(rhino_strategy.make_decision(51, 51, 68), 'WAIT')
        self.assertEqual(rhino_strategy.make_decision(79, 79, 69), 'WAIT')
        # Fourth bucket
        self.assertEqual(rhino_strategy.make_decision(1, 1, 70), 'WAIT')
        self.assertEqual(rhino_strategy.make_decision(63, 63, 93), 'WAIT')
        self.assertEqual(rhino_strategy.make_decision(2, 2, 71), 'WAIT')
        self.assertEqual(rhino_strategy.make_decision(64, 64, 94), 'WAIT')

    def test_extreme_buckets(self):
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
