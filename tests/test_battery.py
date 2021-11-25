from unittest.mock import MagicMock

from Battery import Battery
import unittest
import mock


class TestBattery(unittest.TestCase):
    def test_nice_initialization(self):
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=0)
        self.assertEqual(rhino_battery.name, 'TEST')
        self.assertEqual(rhino_battery.efficiency, 0.9)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 0)
        self.assertEqual(rhino_battery.earnings, 0)

        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=0.8)
        self.assertEqual(rhino_battery.name, 'TEST')
        self.assertEqual(rhino_battery.efficiency, 0.8)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3750)
        self.assertEqual(rhino_battery.earnings, 0)

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
        self.assertEqual(rhino_battery.earnings, 0)
        rhino_battery.charge(6760, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3850)
        self.assertEqual(rhino_battery.earnings, -56.0)
        rhino_battery.discharge(6760, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3738)
        self.assertEqual(rhino_battery.earnings, 0)

        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=1)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3750)
        self.assertEqual(rhino_battery.earnings, 0)
        rhino_battery.charge(6760, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3862)
        self.assertEqual(rhino_battery.earnings, -56.0)
        rhino_battery.discharge(6760, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3750)
        self.assertEqual(rhino_battery.earnings, 0)

    def test_weird_charge(self):
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=7400)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 7400)
        self.assertEqual(rhino_battery.earnings, 0)
        rhino_battery.charge(12000, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 7499)
        self.assertEqual(rhino_battery.earnings, -55.5)

        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=7200)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 7200)
        self.assertEqual(rhino_battery.earnings, 0)
        rhino_battery.charge(15000, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 7380)
        self.assertEqual(rhino_battery.earnings, -100)

    def test_weird_discharge(self):
        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=100)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 100)
        self.assertEqual(rhino_battery.earnings, 0)
        rhino_battery.discharge(12000, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 0)
        self.assertEqual(rhino_battery.earnings, 50)

        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 500)
        self.assertEqual(rhino_battery.earnings, 0)
        rhino_battery.discharge(15000, 500)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 300)
        self.assertEqual(rhino_battery.earnings, 100)

    def test_check_action(self):
        rhino_battery = Battery('TEST', 7500, 12000)
        self.assertEqual(200, rhino_battery.check_action(200))
        self.assertEqual(200, rhino_battery.check_action(500))
        self.assertEqual(-200, rhino_battery.check_action(-200))
        self.assertEqual(-200, rhino_battery.check_action(-500))

        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=7400)
        self.assertEqual(111, rhino_battery.check_action(200))
        self.assertEqual(111, rhino_battery.check_action(500))

        rhino_battery = Battery('TEST', 7500, 12000, starting_soc_kwh=100)
        self.assertEqual(-100, rhino_battery.check_action(-200))
        self.assertEqual(-100, rhino_battery.check_action(-500))

    def test_take_action(self):
        rhino_battery = Battery('TEST', 7500, 12000)
        rhino_battery.charge = MagicMock(name='charge', return_value=0)
        rhino_battery.discharge = MagicMock(name='charge', return_value=1)
        rhino_battery.wait = MagicMock(name='charge', return_value=2)

        rhino_battery.take_action(-20, 500, action='CHARGE')
        rhino_battery.take_action(-20, 500, action='DISCHARGE')
        rhino_battery.take_action(-20, 500, action='WAIT')

        rhino_battery.charge.assert_called_with(12000, -20)
        rhino_battery.discharge.assert_called_with(12000, 500)
        rhino_battery.wait.assert_called()


if __name__ == '__main__':
    unittest.main()
