from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy

january_points = [(15, 162, 'CHARGE'), (30, 74, 'CHARGE'), (60, 68, 'CHARGE'), (75, 28, 'CHARGE'), (95, -60, 'CHARGE'),
                  (35, 164, 'DISCHARGE'), (50, 82, 'DISCHARGE'), (80, 70, 'DISCHARGE'), (90, 64, 'DISCHARGE'),
                  (95, -8, 'DISCHARGE')]

february_points = [(20, 168, 'CHARGE'), (35, 80, 'CHARGE'), (40, 54, 'CHARGE'), (70, 50, 'CHARGE'), (95, 24, 'CHARGE'),
                  (35, 184, 'DISCHARGE'), (45, 182, 'DISCHARGE'), (50, 178, 'DISCHARGE'), (80, 52, 'DISCHARGE'),
                  (95, 30, 'DISCHARGE')]

march_points = [(15, 140, 'CHARGE'), (35, 86, 'CHARGE'), (55, 54, 'CHARGE'), (75, 34, 'CHARGE'), (95, -40, 'CHARGE'),
                  (30, 142, 'DISCHARGE'), (50, 126, 'DISCHARGE'), (65, 62, 'DISCHARGE'), (90, 36, 'DISCHARGE'),
                  (95, 30, 'DISCHARGE')]

april_points = [(15, 136, 'CHARGE'), (45, 70, 'CHARGE'), (50, 18, 'CHARGE'), (85, 14, 'CHARGE'), (95, -34, 'CHARGE'),
                  (20, 156, 'DISCHARGE'), (60, 104, 'DISCHARGE'), (75, 26, 'DISCHARGE'), (90, 24, 'DISCHARGE'),
                  (95, -30, 'DISCHARGE')]

may_points = [(20, 138, 'CHARGE'), (40, 114, 'CHARGE'), (60, 38, 'CHARGE'), (80, 12, 'CHARGE'), (95, -42, 'CHARGE'),
                  (30, 150, 'DISCHARGE'), (60, 114, 'DISCHARGE'), (75, 98, 'DISCHARGE'), (85, 58, 'DISCHARGE'),
                  (95, 48, 'DISCHARGE')]

june_points = [(10, 176, 'CHARGE'), (40, 126, 'CHARGE'), (60, 122, 'CHARGE'), (70, 76, 'CHARGE'), (95, -28, 'CHARGE'),
                  (25, 194, 'DISCHARGE'), (55, 156, 'DISCHARGE'), (65, 138, 'DISCHARGE'), (80, 86, 'DISCHARGE'),
                  (95, 80, 'DISCHARGE')]

july_points = [(20, 186, 'CHARGE'), (30, 88, 'CHARGE'), (55, 84, 'CHARGE'), (80, 58, 'CHARGE'), (95, 32, 'CHARGE'),
                  (30, 200, 'DISCHARGE'), (40, 114, 'DISCHARGE'), (60, 86, 'DISCHARGE'), (85, 72, 'DISCHARGE'),
                  (95, 52, 'DISCHARGE')]

august_points = [(20, 136, 'CHARGE'), (30, 128, 'CHARGE'), (55, 122, 'CHARGE'), (75, 58, 'CHARGE'), (95, 24, 'CHARGE'),
                  (35, 176, 'DISCHARGE'), (45, 172, 'DISCHARGE'), (65, 130, 'DISCHARGE'), (85, 98, 'DISCHARGE'),
                  (95, 96, 'DISCHARGE')]

september_points = [(10, 176, 'CHARGE'), (30, 158, 'CHARGE'), (60, 152, 'CHARGE'), (80, 94, 'CHARGE'), (95, -34, 'CHARGE'),
                  (15, 200, 'DISCHARGE'), (45, 178, 'DISCHARGE'), (75, 154, 'DISCHARGE'), (90, 114, 'DISCHARGE'),
                  (95, -2, 'DISCHARGE')]

october_points = [(10, 190, 'CHARGE'), (40, 178, 'CHARGE'), (45, 160, 'CHARGE'), (85, 14, 'CHARGE'), (95, -20, 'CHARGE'),
                  (20, 192, 'DISCHARGE'), (55, 184, 'DISCHARGE'), (75, 174, 'DISCHARGE'), (90, 110, 'DISCHARGE'),
                  (95, 96, 'DISCHARGE')]

november_points = [(20, 194, 'CHARGE'), (40, 188, 'CHARGE'), (50, 128, 'CHARGE'), (55, 80, 'CHARGE'), (95, -4, 'CHARGE'),
                  (25, 198, 'DISCHARGE'), (60, 190, 'DISCHARGE'), (75, 162, 'DISCHARGE'), (90, 112, 'DISCHARGE'),
                  (95, 94, 'DISCHARGE')]

december_points = [(15, 282, 'CHARGE'), (25, 150, 'CHARGE'), (40, -12, 'CHARGE'), (80, -50, 'CHARGE'), (95, -116, 'CHARGE'),
                  (30, 284, 'DISCHARGE'), (35, 178, 'DISCHARGE'), (85, 26, 'DISCHARGE'), (90, 6, 'DISCHARGE'),
                  (95, -28, 'DISCHARGE')]

strategy_points = [january_points, february_points, march_points, april_points,
                   may_points, june_points, july_points, august_points,
                   september_points, october_points, november_points, december_points]


def get_month_strategy(month):
    assert month >= 1
    assert month <= 12

    month_index = month - 1

    strategy = PointBasedStrategy(f'Giga Baseline Month {month}', price_step_size=2)
    for point in strategy_points[month_index]:
        strategy.add_point(point)

    strategy.upload_strategy()
    return strategy


if __name__ == '__main__':
    for month_num in range(1, 13):
        visualize_strategy(get_month_strategy(month_num))
