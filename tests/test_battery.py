from Battery import Battery
import unittest


class TestBattery(unittest.TestCase):
    def test_nice_initialization(self):
        rhino_battery = Battery('TEST', 7500, 12000)
        self.assertEqual(rhino_battery.name, 'TEST')
        self.assertEqual(rhino_battery.efficiency, 0.9)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 0)
        self.assertEqual(rhino_battery.earnings, 0)

        rhino_battery = Battery('TEST', 7500, 12000, battery_efficiency=0.8)
        self.assertEqual(rhino_battery.name, 'TEST')
        self.assertEqual(rhino_battery.efficiency, 0.8)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 0)
        self.assertEqual(rhino_battery.earnings, 0)

        rhino_battery = Battery('TEST', 7500, 12000, starting_soc=50)
        self.assertEqual(rhino_battery.name, 'TEST')
        self.assertEqual(rhino_battery.efficiency, 0.9)
        self.assertEqual(rhino_battery.state_of_charge_kwh, 3750)
        self.assertEqual(rhino_battery.earnings, 0)


if __name__ == '__main__':
    unittest.main()
