from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy

january_points = [(14, 162, 'CHARGE'), (27, 74, 'CHARGE'), (63, 68, 'CHARGE'), (73, 28, 'CHARGE'), (95, -60, 'CHARGE'),
                  (33, 162, 'DISCHARGE'), (48, 82, 'DISCHARGE'), (80, 70, 'DISCHARGE'), (94, 64, 'DISCHARGE'),
                  (95, -8, 'DISCHARGE')]

february_points = [(19, 168, 'CHARGE'), (35, 80, 'CHARGE'), (36, 54, 'CHARGE'), (72, 50, 'CHARGE'), (95, 24, 'CHARGE'),
                  (35, 184, 'DISCHARGE'), (46, 182, 'DISCHARGE'), (52, 178, 'DISCHARGE'), (83, 52, 'DISCHARGE'),
                  (95, 30, 'DISCHARGE')]

march_points = [(14, 140, 'CHARGE'), (33, 86, 'CHARGE'), (56, 54, 'CHARGE'), (77, 34, 'CHARGE'), (95, -40, 'CHARGE'),
                  (28, 140, 'DISCHARGE'), (52, 126, 'DISCHARGE'), (66, 62, 'DISCHARGE'), (94, 36, 'DISCHARGE'),
                  (95, 30, 'DISCHARGE')]

april_points = [(14, 136, 'CHARGE'), (44, 70, 'CHARGE'), (47, 18, 'CHARGE'), (88, 14, 'CHARGE'), (95, -34, 'CHARGE'),
                  (19, 156, 'DISCHARGE'), (59, 104, 'DISCHARGE'), (77, 26, 'DISCHARGE'), (94, 24, 'DISCHARGE'),
                  (95, -30, 'DISCHARGE')]

may_points = [(21, 138, 'CHARGE'), (37, 114, 'CHARGE'), (61, 38, 'CHARGE'), (79, 12, 'CHARGE'), (95, -42, 'CHARGE'),
                  (28, 150, 'DISCHARGE'), (56, 114, 'DISCHARGE'), (75, 98, 'DISCHARGE'), (84, 58, 'DISCHARGE'),
                  (95, 48, 'DISCHARGE')]

june_points = [(11, 176, 'CHARGE'), (37, 126, 'CHARGE'), (57, 122, 'CHARGE'), (72, 76, 'CHARGE'), (95, -28, 'CHARGE'),
                  (25, 194, 'DISCHARGE'), (56, 156, 'DISCHARGE'), (62, 138, 'DISCHARGE'), (79, 86, 'DISCHARGE'),
                  (95, 80, 'DISCHARGE')]

july_points = [(17, 186, 'CHARGE'), (26, 88, 'CHARGE'), (55, 84, 'CHARGE'), (79, 58, 'CHARGE'), (95, 32, 'CHARGE'),
                  (29, 200, 'DISCHARGE'), (37, 114, 'DISCHARGE'), (60, 86, 'DISCHARGE'), (85, 72, 'DISCHARGE'),
                  (95, 52, 'DISCHARGE')]

august_points = [(18, 136, 'CHARGE'), (31, 128, 'CHARGE'), (55, 122, 'CHARGE'), (73, 58, 'CHARGE'), (95, 24, 'CHARGE'),
                  (35, 176, 'DISCHARGE'), (44, 172, 'DISCHARGE'), (63, 130, 'DISCHARGE'), (86, 98, 'DISCHARGE'),
                  (95, 96, 'DISCHARGE')]

september_points = [(11, 176, 'CHARGE'), (31, 158, 'CHARGE'), (62, 152, 'CHARGE'), (78, 94, 'CHARGE'), (95, -34, 'CHARGE'),
                  (16, 200, 'DISCHARGE'), (45, 178, 'DISCHARGE'), (74, 154, 'DISCHARGE'), (94, 114, 'DISCHARGE'),
                  (95, -2, 'DISCHARGE')]

october_points = [(9, 190, 'CHARGE'), (39, 178, 'CHARGE'), (45, 160, 'CHARGE'), (86, 14, 'CHARGE'), (95, -20, 'CHARGE'),
                  (20, 190, 'DISCHARGE'), (54, 184, 'DISCHARGE'), (76, 174, 'DISCHARGE'), (94, 110, 'DISCHARGE'),
                  (95, 96, 'DISCHARGE')]

november_points = [(21, 194, 'CHARGE'), (41, 188, 'CHARGE'), (49, 128, 'CHARGE'), (54, 80, 'CHARGE'), (95, -4, 'CHARGE'),
                  (26, 198, 'DISCHARGE'), (56, 190, 'DISCHARGE'), (73, 162, 'DISCHARGE'), (88, 112, 'DISCHARGE'),
                  (95, 94, 'DISCHARGE')]

december_points = [(14, 282, 'CHARGE'), (24, 150, 'CHARGE'), (41, -12, 'CHARGE'), (78, -50, 'CHARGE'), (95, -116, 'CHARGE'),
                  (30, 184, 'DISCHARGE'), (31, 178, 'DISCHARGE'), (89, 26, 'DISCHARGE'), (95, 6, 'DISCHARGE'),
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
