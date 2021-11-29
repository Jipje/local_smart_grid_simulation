from unittest.mock import MagicMock
from Battery import Battery
import unittest


class TestBattery(unittest.TestCase):
    def test_nice_initialization(self):
        # Empty battery
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=0)
        self.assertEqual(rhino_battery.name, 'TEST')
        self.assertEqual(rhino_battery.efficiency, 0.9)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 0)
        self.assertEqual(rhino_battery.earnings, 0)
        # Less efficient battery
        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=0.8)
        self.assertEqual(rhino_battery.name, 'TEST')
        self.assertEqual(rhino_battery.efficiency, 0.8)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3750)
        self.assertEqual(rhino_battery.earnings, 0)
        # Different starting SoC
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=3000)
        self.assertEqual(rhino_battery.name, 'TEST')
        self.assertEqual(rhino_battery.efficiency, 0.9)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3000)
        self.assertEqual(rhino_battery.earnings, 0)

    def test_faulty_initialization(self):
        # Faulty max_kwh
        self.assertRaises(ValueError, Battery, 'TEST', 0, 12000)
        self.assertRaises(ValueError, Battery, 'TEST', -7500, 12000)
        # Faulty max_kw
        self.assertRaises(ValueError, Battery, 'TEST', 7500, 0)
        self.assertRaises(ValueError, Battery, 'TEST', 7500, -12000)
        # Faulty battery_efficiency
        self.assertRaises(ValueError, Battery, 'TEST', 7500, 12000, battery_efficiency=-0.9)
        self.assertRaises(ValueError, Battery, 'TEST', 7500, 12000, battery_efficiency=0)
        self.assertRaises(ValueError, Battery, 'TEST', 7500, 12000, battery_efficiency=1.1)
        # Faulty starting_soc_kwh
        self.assertRaises(ValueError, Battery, 'TEST', 7500, 12000, starting_soc_kwh=-100)
        self.assertRaises(ValueError, Battery, 'TEST', 7500, 12000, starting_soc_kwh=7501)

    def test_nice_update_earnings(self):
        rhino_battery = Battery('TEST', 7500, 12000)
        # Charge 1 MWh for 50 €/MWh
        rhino_battery.update_earnings(1000, 50)
        self.assertEqual(rhino_battery.earnings, -50)
        # Discharge 2 MWh for 50 €/MWh
        rhino_battery.update_earnings(-2000, 50)
        self.assertEqual(rhino_battery.earnings, 50)
        # Charge 1 MWh for -50 €/MWh
        rhino_battery.update_earnings(1000, -50)
        self.assertEqual(rhino_battery.earnings, 100)
        # Discharge 1 MWh for -50 €/MWh
        rhino_battery.update_earnings(-1000, -50)
        self.assertEqual(rhino_battery.earnings, 50)

    def test_nice_charge_and_discharge(self):
        rhino_battery = Battery('TEST', 7500, 12000)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3750)
        rhino_battery.charge(6760, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3850)
        rhino_battery.discharge(6760, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3738)

        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=1)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3750)
        rhino_battery.charge(6760, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3862)
        rhino_battery.discharge(6760, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3750)

    def test_weird_charge(self):
        # Battery too full
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=7400)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 7400)
        rhino_battery.charge(12000, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 7499)
        # Asking too much power from battery
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=7200)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 7200)
        rhino_battery.charge(15000, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 7380)

    def test_weird_discharge(self):
        # Battery too empty
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=100)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 100)
        rhino_battery.discharge(12000, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 0)
        # Discharge too large
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 500)
        rhino_battery.discharge(15000, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 300)

    def test_check_action(self):
        # Battery not powerful enough
        rhino_battery = Battery('TEST', 7500, 12000)
        self.assertEqual(200, rhino_battery.check_action(200))
        self.assertEqual(200, rhino_battery.check_action(500))
        self.assertEqual(-200, rhino_battery.check_action(-200))
        self.assertEqual(-200, rhino_battery.check_action(-500))
        # Battery too full. Keeps track of battery efficiency
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=7400)
        self.assertEqual(111, rhino_battery.check_action(200))
        self.assertEqual(111, rhino_battery.check_action(500))
        # Battery too empty
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=100)
        self.assertEqual(-100, rhino_battery.check_action(-200))
        self.assertEqual(-100, rhino_battery.check_action(-500))

    def test_take_action(self):
        rhino_battery = Battery('TEST', 7500, 12000)
        rhino_battery.charge = MagicMock(name='charge', return_value=0)
        rhino_battery.discharge = MagicMock(name='charge', return_value=1)
        rhino_battery.wait = MagicMock(name='charge', return_value=2)

        rhino_battery.take_imbalance_action(-20, 500, action='CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, action='DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, action='WAIT')
        # Test that the correct charge price is used for charge action and vice versa with discharge
        rhino_battery.charge.assert_called_with(12000, -20)
        rhino_battery.discharge.assert_called_with(12000, 500)
        rhino_battery.wait.assert_called()

    def test_wait(self):
        rhino_battery = Battery('TEST', 7500, 12000)
        self.assertEqual(rhino_battery.name, 'TEST')
        self.assertEqual(rhino_battery.efficiency, 0.9)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3750)
        self.assertEqual(rhino_battery.earnings, 0)
        rhino_battery.wait()
        self.assertEqual(rhino_battery.name, 'TEST')
        self.assertEqual(rhino_battery.efficiency, 0.9)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3750)
        self.assertEqual(rhino_battery.earnings, 0)

    def test_to_string(self):
        rhino_battery = Battery('TEST', 7500, 12000)
        res = "{} battery:\nCurrent SoC: {}kWh\nTotal Earnings: €{}".format('TEST', 3750, 0)
        self.assertEqual(res, rhino_battery.__str__())

    def test_ptu_reset(self):
        rhino_battery = Battery('TEST', 7500, 12000)
        rhino_battery.update_earnings = MagicMock(name='update_earnings', return_value=1500)
        rhino_battery.ptu_total_action = -3000
        rhino_battery.ptu_charge_price = -20
        rhino_battery.ptu_discharge_price = 500
        rhino_battery.ptu_reset()
        rhino_battery.update_earnings.assert_called_with(-3000, 500)

        rhino_battery = Battery('TEST', 7500, 12000)
        rhino_battery.ptu_total_action = -3000
        rhino_battery.ptu_charge_price = -20
        rhino_battery.ptu_discharge_price = 500
        rhino_battery.ptu_reset()
        self.assertEqual(1500, rhino_battery.earnings)

        rhino_battery = Battery('TEST', 7500, 12000)
        rhino_battery.update_earnings = MagicMock(name='update_earnings', return_value=60)
        rhino_battery.ptu_total_action = 3000
        rhino_battery.ptu_charge_price = -20
        rhino_battery.ptu_discharge_price = 500
        rhino_battery.ptu_reset()
        rhino_battery.update_earnings.assert_called_with(3000, -20)

        rhino_battery = Battery('TEST', 7500, 12000)
        rhino_battery.ptu_total_action = 3000
        rhino_battery.ptu_charge_price = -20
        rhino_battery.ptu_discharge_price = 500
        rhino_battery.ptu_reset()
        self.assertEqual(60, rhino_battery.earnings)

        rhino_battery = Battery('TEST', 7500, 12000)
        rhino_battery.update_earnings = MagicMock(name='update_earnings', return_value=0)
        rhino_battery.ptu_total_action = 0
        rhino_battery.ptu_charge_price = -20
        rhino_battery.ptu_discharge_price = 500
        rhino_battery.ptu_reset()
        rhino_battery.update_earnings.assert_called_with(0, 0)

    def test_all_pos_ptu(self):
        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=1)
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-40, 1000, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        self.assertEqual(3000, rhino_battery.ptu_total_action)
        self.assertEqual(15, rhino_battery.ptu_tracker)
        self.assertEqual(0, rhino_battery.earnings)
        rhino_battery.take_imbalance_action(50, 50, 'CHARGE')
        self.assertEqual(200, rhino_battery.ptu_total_action)
        self.assertEqual(1, rhino_battery.ptu_tracker)
        self.assertEqual(60, rhino_battery.earnings)

    def test_first_pos_then_neg_end_pos_ptu(self):
        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=1)
        rhino_battery.ptu_tracker = 10
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        self.assertEqual(200, rhino_battery.ptu_total_action)
        self.assertEqual(15, rhino_battery.ptu_tracker)
        self.assertEqual(0, rhino_battery.earnings)
        rhino_battery.take_imbalance_action(50, 50, 'CHARGE')
        self.assertEqual(200, rhino_battery.ptu_total_action)
        self.assertEqual(1, rhino_battery.ptu_tracker)
        self.assertEqual(4, rhino_battery.earnings)

    def test_first_pos_end_neg_ptu(self):
        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=1)
        rhino_battery.ptu_tracker = 10
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        self.assertEqual(-600, rhino_battery.ptu_total_action)
        self.assertEqual(15, rhino_battery.ptu_tracker)
        self.assertEqual(0, rhino_battery.earnings)
        rhino_battery.take_imbalance_action(50, 50, 'CHARGE')
        self.assertEqual(200, rhino_battery.ptu_total_action)
        self.assertEqual(1, rhino_battery.ptu_tracker)
        self.assertEqual(300, rhino_battery.earnings)

    def test_all_neg_ptu(self):
        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=1)
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-40, 9999, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        self.assertEqual(-3000, rhino_battery.ptu_total_action)
        self.assertEqual(15, rhino_battery.ptu_tracker)
        self.assertEqual(0, rhino_battery.earnings)
        rhino_battery.take_imbalance_action(50, 50, 'CHARGE')
        self.assertEqual(200, rhino_battery.ptu_total_action)
        self.assertEqual(1, rhino_battery.ptu_tracker)
        self.assertEqual(1500, rhino_battery.earnings)

    def test_first_neg_then_pos_end_neg_ptu(self):
        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=1)
        rhino_battery.ptu_tracker = 10
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        self.assertEqual(-200, rhino_battery.ptu_total_action)
        self.assertEqual(15, rhino_battery.ptu_tracker)
        self.assertEqual(0, rhino_battery.earnings)
        rhino_battery.take_imbalance_action(50, 50, 'CHARGE')
        self.assertEqual(200, rhino_battery.ptu_total_action)
        self.assertEqual(1, rhino_battery.ptu_tracker)
        self.assertEqual(100, rhino_battery.earnings)

    def test_first_neg_end_pos_ptu(self):
        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=1)
        rhino_battery.ptu_tracker = 10
        rhino_battery.take_imbalance_action(-20, 500, 'DISCHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        rhino_battery.take_imbalance_action(-20, 500, 'CHARGE')
        self.assertEqual(600, rhino_battery.ptu_total_action)
        self.assertEqual(15, rhino_battery.ptu_tracker)
        self.assertEqual(0, rhino_battery.earnings)
        rhino_battery.take_imbalance_action(50, 50, 'CHARGE')
        self.assertEqual(200, rhino_battery.ptu_total_action)
        self.assertEqual(1, rhino_battery.ptu_tracker)
        self.assertEqual(12, rhino_battery.earnings)


if __name__ == '__main__':
    unittest.main()
