import unittest
import os
from unittest.mock import MagicMock

from environment.ImbalanceEnvironment import ImbalanceEnvironment
from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from helper_objects.strategies.CsvStrategy import CsvStrategy
from network_objects.Battery import Battery


class TestNetworkEnvironment(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        strategy_one_path = '..{0}..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        try:
            CsvStrategy('Rhino strategy 1', strategy_csv=strategy_one_path)
        except FileNotFoundError:
            strategy_one_path = '..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        cls.strategy_one_path = strategy_one_path

    def test_simple_congestion(self):
        network = NetworkEnvironment(verbose_lvl=3)
        TotalNetworkCapacityTracker(network, 10000)
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_simple_congestion', 7500, 12000, strategy=csv_strategy, starting_soc_kwh=3750)
        network.add_object(rhino, [0, 1])
        network.take_step([200, 200])
        self.assertIn('Timesteps with congestion since last time: 1m', network.done_in_mean_time())

    def test_simple_imbalance(self):
        network = NetworkEnvironment(verbose_lvl=3)
        ImbalanceEnvironment(network, 1, 0, 2)
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_simple_imbalance', 7500, 12000, strategy=csv_strategy, starting_soc_kwh=3750)
        network.add_object(rhino, [0, 2])

        rhino.take_imbalance_action = MagicMock(name='take_imbalance_action', return_value=0)
        network.take_step([200, 100, 99999])
        rhino.take_imbalance_action.assert_called_with(200, 200)

    def test_congestion_and_imbalance(self):
        network = NetworkEnvironment(verbose_lvl=3)
        TotalNetworkCapacityTracker(network, 10000)
        ImbalanceEnvironment(network, 1, 0, 2)
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_congestion_and_imbalance', 7500, 12000, strategy=csv_strategy, starting_soc_kwh=3750)
        network.add_object(rhino, [0, 2])
        network.take_step([200, 100, 99999])

        self.assertEqual(rhino.state_of_charge_kwh, 3550)
        self.assertIn('Timesteps with congestion since last time: 1m', network.done_in_mean_time())

        network = NetworkEnvironment(verbose_lvl=3)
        TotalNetworkCapacityTracker(network, 12000)
        ImbalanceEnvironment(network, 1, 0, 2)
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_congestion_and_imbalance', 7500, 12000, strategy=csv_strategy, starting_soc_kwh=3750)
        network.add_object(rhino, [0, 2])
        network.take_step([-99999, 100, -100])
        self.assertEqual(rhino.state_of_charge_kwh, 3930)
        self.assertIn('Timesteps with congestion since last time: 0m', network.done_in_mean_time())
