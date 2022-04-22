import unittest
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy

class TestSortingStrategies(unittest.TestCase):

    def test_no_sort_needed(self):
        charge_points = [(50, 55, 'CHARGE'), (60, 44, 'CHARGE'), (70, 33, 'CHARGE'), (95, 0, 'CHARGE')]
        discharge_points = [(40, 99, 'DISCHARGE'), (60, 88, 'DISCHARGE'), (70, 77, 'DISCHARGE'), (95, 66, 'DISCHARGE')]

        point_based_strat = PointBasedStrategy('test_no_sort_needed', price_step_size=11)
        for charge_point in charge_points:
            point_based_strat.add_point(charge_point)
        for discharge_point in discharge_points:
            point_based_strat.add_point(discharge_point)

        for i in range(4):
            point_based_strat.sort_and_fix_points(sort_strategy=i)
            self.assertListEqual(charge_points, point_based_strat.charge_points)
            self.assertListEqual(discharge_points, point_based_strat.discharge_points)

    def test_single_sort_needed(self):
        charge_points = [(50, 55, 'CHARGE'), (60, 33, 'CHARGE'), (70, 44, 'CHARGE'), (95, 0, 'CHARGE')]
        discharge_points = [(40, 88, 'DISCHARGE'), (60, 99, 'DISCHARGE'), (70, 77, 'DISCHARGE'), (95, 66, 'DISCHARGE')]

        for i in range(4):
            point_based_strat = PointBasedStrategy(f'test_single_sort_needed_{i}', price_step_size=11)
            for charge_point in charge_points:
                point_based_strat.add_point(charge_point)
            for discharge_point in discharge_points:
                point_based_strat.add_point(discharge_point)

            point_based_strat.sort_and_fix_points(sort_strategy=i)
            if i == 0:  # No sort is given
                self.assertListEqual(charge_points, point_based_strat.charge_points)
                self.assertListEqual(discharge_points, point_based_strat.discharge_points)
            elif i == 1:  # Prices are flipped
                assert_charge_points = [(50, 55, 'CHARGE'), (60, 44, 'CHARGE'), (70, 33, 'CHARGE'), (95, 0, 'CHARGE')]
                assert_discharge_points = [(40, 99, 'DISCHARGE'), (60, 88, 'DISCHARGE'), (70, 77, 'DISCHARGE'), (95, 66, 'DISCHARGE')]
                self.assertListEqual(assert_charge_points, point_based_strat.charge_points)
                self.assertListEqual(assert_discharge_points, point_based_strat.discharge_points)
            elif i == 2:  # Take best prices
                assert_charge_points = [(50, 55, 'CHARGE'), (60, 33, 'CHARGE'), (70, 33, 'CHARGE'), (95, 0, 'CHARGE')]
                assert_discharge_points = [(40, 99, 'DISCHARGE'), (60, 99, 'DISCHARGE'), (70, 77, 'DISCHARGE'), (95, 66, 'DISCHARGE')]
                self.assertListEqual(assert_charge_points, point_based_strat.charge_points)
                self.assertListEqual(assert_discharge_points, point_based_strat.discharge_points)
            elif i == 3:  # Take worst prices
                assert_charge_points = [(50, 55, 'CHARGE'), (60, 44, 'CHARGE'), (70, 44, 'CHARGE'), (95, 0, 'CHARGE')]
                assert_discharge_points = [(40, 88, 'DISCHARGE'), (60, 88, 'DISCHARGE'), (70, 77, 'DISCHARGE'), (95, 66, 'DISCHARGE')]
                self.assertListEqual(assert_charge_points, point_based_strat.charge_points)
                self.assertListEqual(assert_discharge_points, point_based_strat.discharge_points)

    def test_chained_sort_needed(self):
        charge_points = [(50, 55, 'CHARGE'), (60, 33, 'CHARGE'), (70, 44, 'CHARGE'), (95, 0, 'CHARGE')]
        discharge_points = [(40, 88, 'DISCHARGE'), (60, 99, 'DISCHARGE'), (70, 77, 'DISCHARGE'), (95, 66, 'DISCHARGE')]

        for i in range(4):
            point_based_strat = PointBasedStrategy(f'test_single_sort_needed_{i}', price_step_size=11)
            for charge_point in charge_points:
                point_based_strat.add_point(charge_point)
            for discharge_point in discharge_points:
                point_based_strat.add_point(discharge_point)

            point_based_strat.sort_and_fix_points(sort_strategy=i)
            if i == 0:  # No sort is given
                self.assertListEqual(charge_points, point_based_strat.charge_points)
                self.assertListEqual(discharge_points, point_based_strat.discharge_points)
            elif i == 1:  # Prices are flipped
                assert_charge_points = [(50, 55, 'CHARGE'), (60, 44, 'CHARGE'), (70, 33, 'CHARGE'), (95, 0, 'CHARGE')]
                assert_discharge_points = [(40, 99, 'DISCHARGE'), (60, 88, 'DISCHARGE'), (70, 77, 'DISCHARGE'), (95, 66, 'DISCHARGE')]
                self.assertListEqual(assert_charge_points, point_based_strat.charge_points)
                self.assertListEqual(assert_discharge_points, point_based_strat.discharge_points)
            elif i == 2:  # Take best prices
                assert_charge_points = [(50, 55, 'CHARGE'), (60, 33, 'CHARGE'), (70, 33, 'CHARGE'), (95, 0, 'CHARGE')]
                assert_discharge_points = [(40, 99, 'DISCHARGE'), (60, 99, 'DISCHARGE'), (70, 77, 'DISCHARGE'), (95, 66, 'DISCHARGE')]
                self.assertListEqual(assert_charge_points, point_based_strat.charge_points)
                self.assertListEqual(assert_discharge_points, point_based_strat.discharge_points)
            elif i == 3:  # Take worst prices
                assert_charge_points = [(50, 55, 'CHARGE'), (60, 44, 'CHARGE'), (70, 44, 'CHARGE'), (95, 0, 'CHARGE')]
                assert_discharge_points = [(40, 88, 'DISCHARGE'), (60, 88, 'DISCHARGE'), (70, 77, 'DISCHARGE'), (95, 66, 'DISCHARGE')]
                self.assertListEqual(assert_charge_points, point_based_strat.charge_points)
                self.assertListEqual(assert_discharge_points, point_based_strat.discharge_points)
