import unittest
import os

from helper_objects.strategies.CsvStrategy import CsvStrategy
from network_objects.Battery import Battery
from network_objects.control_strategies.SolveCongestionAndLimitedChargeControlTower import \
    SolveCongestionAndLimitedChargeControlTower


class TestCongestionAndLimitedCharge(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        strategy_one_path = '..{0}..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        try:
            CsvStrategy('Rhino strategy 1', strategy_csv=strategy_one_path)
        except FileNotFoundError:
            strategy_one_path = '..{0}data{0}strategies{0}cleaner_simplified_passive_imbalance_1.csv'.format(os.path.sep)
        cls.strategy_one_path = strategy_one_path

    def test_initialisation(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_simple_congestion', 7500, 12000, starting_soc_kwh=0)
        limited_charge_control_tower = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller", network_object=rhino, congestion_kw=20000, strategy=csv_strategy, verbose_lvl=4)

    def test_normal_charge(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=6825)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller", network_object=rhino,
                                                                 congestion_kw=14000, congestion_safety_margin=1, strategy=csv_strategy)
        # Normal charging
        simple_strategy_controller.take_step([-200, -200, 12000], [0, 1, 2])
        self.assertEqual(7005, rhino.state_of_charge_kwh)

    def test_normal_charge_with_transportation(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=6825)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller", network_object=rhino,
                                                                 congestion_kw=14000, congestion_safety_margin=1, strategy=csv_strategy,
                                                                                 transportation_kw=2000)
        # Normal charging
        simple_strategy_controller.take_step([-200, -200, 10000], [0, 1, 2])
        self.assertEqual(7005, rhino.state_of_charge_kwh)

    def test_normal_discharge(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=7005)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller", network_object=rhino,
                                                                 congestion_kw=14000, congestion_safety_margin=1,
                                                                 strategy=csv_strategy)
        # Normal discharging
        simple_strategy_controller.take_step([500, 500, 1000], [0, 1, 2])
        self.assertEqual(6805, rhino.state_of_charge_kwh)

    def test_discharge_but_dont_cause_congestion(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=6805)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller",
                                                                 network_object=rhino,
                                                                 congestion_kw=14000, congestion_safety_margin=1,
                                                                 strategy=csv_strategy)
        # Discharging but do not cause network congestion
        simple_strategy_controller.take_step([500, 500, 8000], [0, 1, 2])
        self.assertEqual(6705, rhino.state_of_charge_kwh)

    def test_discharge_overwrite_due_to_congestion(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=6705)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller",
                                                                 network_object=rhino,
                                                                 congestion_kw=14000, congestion_safety_margin=1,
                                                                 strategy=csv_strategy)
        # Discharging overwrite due to congestion
        simple_strategy_controller.take_step([500, 500, 20000], [0, 1, 2])
        self.assertEqual(6795, rhino.state_of_charge_kwh)

    def test_wait_overwrite_due_to_congestion(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=6795)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller",
                                                                 network_object=rhino,
                                                                 congestion_kw=14000, congestion_safety_margin=1,
                                                                 strategy=csv_strategy)
        # Wait overwrite due to congestion
        simple_strategy_controller.take_step([50, 50, 20000], [0, 1, 2])
        self.assertEqual(6885, rhino.state_of_charge_kwh)

    def test_normal_charge(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=6825)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller", network_object=rhino, strategy=csv_strategy, congestion_kw=14000, congestion_safety_margin=1)
        # Normal charging
        simple_strategy_controller.take_step([-200, -200, 12000, -500], [0, 1, 2])
        self.assertEqual(7005, rhino.state_of_charge_kwh)

    def test_limited_charge(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=7005)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller",
                                                                                   network_object=rhino,
                                                                                   strategy=csv_strategy, congestion_kw=14000, congestion_safety_margin=1,)
        # Limited charging constraints
        simple_strategy_controller.take_step([-200, -200, 6000, -500], [0, 1, 2])
        self.assertEqual(7095, rhino.state_of_charge_kwh)

    def test_limited_charge_with_extra_transport(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=7005)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller",
                                                                                 network_object=rhino,
                                                                                 strategy=csv_strategy,
                                                                                 congestion_kw=14000,
                                                                                 congestion_safety_margin=1,
                                                                                 transportation_kw=2000)
        # Limited charging constraints
        simple_strategy_controller.take_step([-200, -200, 4000, -500], [0, 1, 2])
        self.assertEqual(7095, rhino.state_of_charge_kwh)

    def test_extra_transport_no_cause_congestion(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=6825)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller",
                                                                                 network_object=rhino,
                                                                                 strategy=csv_strategy,
                                                                                 congestion_kw=10000,
                                                                                 congestion_safety_margin=1,
                                                                                 transportation_kw=2000)
        # Limited charging constraints
        simple_strategy_controller.take_step([-200, -200, 10000, -500], [0, 1, 2])
        self.assertEqual(7005, rhino.state_of_charge_kwh)

    def test_extra_transport_congestion_limit(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=6825)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller",
                                                                                 network_object=rhino,
                                                                                 strategy=csv_strategy,
                                                                                 congestion_kw=5000,
                                                                                 congestion_safety_margin=1,
                                                                                 transportation_kw=5000)
        # Limited charging constraints
        simple_strategy_controller.take_step([-200, -200, 10000, -500], [0, 1, 2])
        self.assertEqual(7005, rhino.state_of_charge_kwh)

    def test_original_battery_constraint(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=7095)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller",
                                                                                   network_object=rhino,
                                                                                   strategy=csv_strategy, congestion_kw=14000, congestion_safety_margin=1)
        # Original battery constraints
        simple_strategy_controller.take_step([-200, -200, 12000, -500], [0, 1, 2])
        self.assertEqual(7125, rhino.state_of_charge_kwh)

    def test_normal_battery_discharge(self):
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv=self.strategy_one_path)
        rhino = Battery('test_max_charge', 7500, 12000, starting_soc_kwh=7125)
        simple_strategy_controller = SolveCongestionAndLimitedChargeControlTower(name="Rhino Battery Controller",
                                                                                   network_object=rhino,
                                                                                   strategy=csv_strategy, congestion_kw=14000, congestion_safety_margin=1)

        # Normal battery discharge
        simple_strategy_controller.take_step([500, 500, 2000, -500], [0, 1, 2])
        self.assertEqual(6925, rhino.state_of_charge_kwh)

