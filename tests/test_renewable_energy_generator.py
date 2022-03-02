import unittest
from unittest.mock import MagicMock

from network_objects.RenewableEnergyGenerator import RenewableEnergyGenerator


class TestRenewableEnergyGenerator(unittest.TestCase):
    def test_nice_initialization(self):
        wind_farm = RenewableEnergyGenerator('TEST', 10000)
        self.assertEqual(10000, wind_farm.max_kw)
        self.assertEqual(0, wind_farm.available_kw)
        self.assertEqual(0, wind_farm.earnings())

    def test_set_available_kw_this_action(self):
        wind_farm = RenewableEnergyGenerator('TEST', 10000)
        self.assertEqual(10000, wind_farm.max_kw)
        self.assertEqual(0, wind_farm.available_kw)
        self.assertEqual(0, wind_farm.earnings())

        wind_farm.set_available_kw_this_action(7500)

        self.assertEqual(10000, wind_farm.max_kw)
        self.assertEqual(7500, wind_farm.available_kw)
        self.assertEqual(0, wind_farm.earnings())

    def test_take_step_mock(self):
        wind_farm = RenewableEnergyGenerator('TEST', 10000)

        wind_farm.set_available_kw_this_action = MagicMock(name='set_available_kw_this_action', return_value=0)
        wind_farm.take_imbalance_action = MagicMock(name='take_imbalance_action', return_value=1)

        environment_step = [30, 50, 7500]
        action_parameters = [0, 1, 2]

        wind_farm.take_step(environment_step, action_parameters)

        wind_farm.set_available_kw_this_action.assert_called_with(-7500)
        wind_farm.take_imbalance_action.assert_called_with(30, 50)

        environment_step = [75, 25, 300]
        action_parameters = [0, 1, 2]

        wind_farm.take_step(environment_step, action_parameters)

        wind_farm.set_available_kw_this_action.assert_called_with(-300)
        wind_farm.take_imbalance_action.assert_called_with(75, 25)

    def test_take_step_real(self):
        wind_farm = RenewableEnergyGenerator('TEST', 10000)
        environment_step = [-100, -100, 12000]
        action_parameters = [0, 1, 2]
        wind_farm.take_step(environment_step, action_parameters)
        self.assertEqual(-12000, wind_farm.available_kw)
        self.assertEqual(-200, wind_farm.innax_metre.ptu_total_action)

    def test_take_imbalance_action(self):
        wind_farm = RenewableEnergyGenerator('TEST', 10000)
        wind_farm.set_available_kw_this_action(-12000)
        wind_farm.take_imbalance_action(50, 50)
        self.assertEqual(-200, wind_farm.innax_metre.ptu_total_action)
