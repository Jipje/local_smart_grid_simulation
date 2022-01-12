import unittest
import os
from unittest.mock import MagicMock

from environment.ImbalanceEnvironment import ImbalanceEnvironment
from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from network_objects.Battery import Battery


class TestNetworkEnvironment(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        strategy_one_path = '..{0}..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        try:
            Battery('NetworkEnvironmentTest', 7500, 12000, battery_strategy_csv=strategy_one_path, starting_soc_kwh=0)
        except FileNotFoundError:
            strategy_one_path = '..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        cls.strategy_one_path = strategy_one_path

    def test_simple_congestion(self):
        network = NetworkEnvironment(verbose_lvl=3)
        TotalNetworkCapacityTracker(network, 10000)
        rhino = Battery('rhinoNetworkEnvironmentTest', 7500, 12000, battery_strategy_csv=self.strategy_one_path, starting_soc_kwh=3750)
        network.add_object(rhino, [0, 1])
        network.take_step([200, 200])
        self.assertIn('Timesteps with congestion since last time: 1m', network.done_in_mean_time())

    def test_simple_imbalance(self):
        network = NetworkEnvironment(verbose_lvl=3)
        ImbalanceEnvironment(network, 1, 0, 2)
        rhino = Battery('rhinoNetworkEnvironmentTest', 7500, 12000, battery_strategy_csv=self.strategy_one_path, starting_soc_kwh=3750)
        network.add_object(rhino, [0, 2])

        rhino.take_imbalance_action = MagicMock(name='take_imbalance_action', return_value=0)
        network.take_step([200, 100, 99999])
        rhino.take_imbalance_action.assert_called_with(200, 200)
