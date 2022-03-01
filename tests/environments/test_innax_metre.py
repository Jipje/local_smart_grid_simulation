import unittest
import os
from unittest.mock import MagicMock

from environment.InnaxMetre import InnaxMetre


class TestInnaxMetre(unittest.TestCase):

    def test_clean_init(self):
        innax_metre = InnaxMetre()
        self.assertEqual(0, innax_metre.ptu_tracker)
        self.assertEqual(0, innax_metre.ptu_total_action)
        self.assertEqual(9999, innax_metre.ptu_charge_price)
        self.assertEqual(-9999, innax_metre.ptu_discharge_price)
        self.assertEqual(0, innax_metre.earnings)

    def test_clean_update_prices(self):
        innax_metre = InnaxMetre()
        innax_metre.update_prices(100, 100)
        self.assertEqual(1, innax_metre.ptu_tracker)
        self.assertEqual(0, innax_metre.ptu_total_action)
        self.assertEqual(100, innax_metre.ptu_charge_price)
        self.assertEqual(100, innax_metre.ptu_discharge_price)
        self.assertEqual(0, innax_metre.earnings)

    def test_charge_update_earnings(self):
        innax_metre = InnaxMetre()
        cost_of_action = innax_metre.update_earnings(1000, 10)
        self.assertEqual(-10, cost_of_action)
        self.assertEqual(-10, innax_metre.earnings)

    def test_discharge_update_earnings(self):
        innax_metre = InnaxMetre()
        cost_of_action = innax_metre.update_earnings(-1000, 100)
        self.assertEqual(100, cost_of_action)
        self.assertEqual(100, innax_metre.earnings)

    def test_discharge_measure_imbalance_action(self):
        innax_metre = InnaxMetre()
        innax_metre.measure_imbalance_action(-1000)
        innax_metre.measure_imbalance_action(-1000)
        self.assertEqual(-2000, innax_metre.ptu_total_action)

    def test_charge_measure_imbalance_action(self):
        innax_metre = InnaxMetre()
        innax_metre.measure_imbalance_action(2000)
        innax_metre.measure_imbalance_action(1000)
        self.assertEqual(3000, innax_metre.ptu_total_action)

    def test_update_prices(self):
        innax_metre = InnaxMetre()
        innax_metre.update_prices(100, -100)
        self.assertEqual(1, innax_metre.ptu_tracker)
        self.assertEqual(0, innax_metre.ptu_total_action)
        self.assertEqual(100, innax_metre.ptu_charge_price)
        self.assertEqual(-100, innax_metre.ptu_discharge_price)
        self.assertEqual(0, innax_metre.earnings)

    def test_full_quarter(self):
        innax_metre = InnaxMetre()
        innax_metre.update_prices(50, 50)
        innax_metre.measure_imbalance_action(0)
        innax_metre.update_prices(50, 50)
        innax_metre.measure_imbalance_action(0)
        innax_metre.update_prices(50, 50)
        innax_metre.measure_imbalance_action(0)
        innax_metre.update_prices(50, 50)
        innax_metre.measure_imbalance_action(200)
        innax_metre.update_prices(50, 50)
        innax_metre.measure_imbalance_action(200)
        innax_metre.update_prices(50, 50)
        innax_metre.measure_imbalance_action(200)
        innax_metre.update_prices(50, 50)
        innax_metre.measure_imbalance_action(200)
        innax_metre.update_prices(50, 3)
        innax_metre.measure_imbalance_action(200)
        innax_metre.update_prices(50, 200)
        innax_metre.measure_imbalance_action(200)
        innax_metre.update_prices(50, 450)
        innax_metre.measure_imbalance_action(200)
        innax_metre.update_prices(50, 200)
        innax_metre.measure_imbalance_action(200)
        innax_metre.update_prices(50, 100)
        innax_metre.measure_imbalance_action(200)
        innax_metre.update_prices(50, 12)
        innax_metre.measure_imbalance_action(200)
        innax_metre.update_prices(50, 30)
        innax_metre.measure_imbalance_action(200)

        self.assertEqual(14, innax_metre.ptu_tracker)
        self.assertEqual(2200, innax_metre.ptu_total_action)
        self.assertEqual(50, innax_metre.ptu_charge_price)
        self.assertEqual(30, innax_metre.ptu_discharge_price)
        self.assertEqual(0, innax_metre.earnings)

        innax_metre.update_prices(100, -30)
        innax_metre.measure_imbalance_action(-600)

        self.assertEqual(15, innax_metre.ptu_tracker)
        self.assertEqual(1600, innax_metre.ptu_total_action)
        self.assertEqual(100, innax_metre.ptu_charge_price)
        self.assertEqual(-30, innax_metre.ptu_discharge_price)
        self.assertEqual(0, innax_metre.earnings)

        innax_metre.update_prices(50, 50)
        innax_metre.measure_imbalance_action(0)

        self.assertEqual(1, innax_metre.ptu_tracker)
        self.assertEqual(0, innax_metre.ptu_total_action)
        self.assertEqual(50, innax_metre.ptu_charge_price)
        self.assertEqual(50, innax_metre.ptu_discharge_price)
        self.assertEqual(-160, innax_metre.earnings)
