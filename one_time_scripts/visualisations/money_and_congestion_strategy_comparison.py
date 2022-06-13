from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy

month_shorts = ['Jan', 'Feb', 'Mar', 'Apr',
                'May', 'June', 'July', 'Aug',
                'Sep', 'Oct', 'Nov', 'Dec']

if __name__ == '__main__':
    # DEFAULT RUNS MONEY 1
    january_strategy= [(10, 220, 'CHARGE'), (18, 208, 'CHARGE'), (47, 68, 'CHARGE'), (95, 52, 'CHARGE'), (4, 60, 'DISCHARGE'), (6, -166, 'DISCHARGE'), (20, -176, 'DISCHARGE'), (95, -512, 'DISCHARGE')]
    february_strategy= [(3, 236, 'CHARGE'), (34, 116, 'CHARGE'), (65, 50, 'CHARGE'), (95, 26, 'CHARGE'), (7, 342, 'DISCHARGE'), (46, 98, 'DISCHARGE'), (79, 48, 'DISCHARGE'), (95, -260, 'DISCHARGE')]
    march_strategy= [(5, 272, 'CHARGE'), (50, 68, 'CHARGE'), (86, 50, 'CHARGE'), (95, 20, 'CHARGE'), (14, 198, 'DISCHARGE'), (23, 126, 'DISCHARGE'), (57, -178, 'DISCHARGE'), (95, -232, 'DISCHARGE')]
    april_strategy= [(12, 242, 'CHARGE'), (49, 64, 'CHARGE'), (73, 36, 'CHARGE'), (95, -10, 'CHARGE'), (8, 256, 'DISCHARGE'), (39, 88, 'DISCHARGE'), (54, 56, 'DISCHARGE'), (95, -3622, 'DISCHARGE')]
    may_strategy= [(11, 192, 'CHARGE'), (39, 70, 'CHARGE'), (79, 56, 'CHARGE'), (95, -8, 'CHARGE'), (34, 112, 'DISCHARGE'), (61, 70, 'DISCHARGE'), (95, 6, 'DISCHARGE'), (95, -326, 'DISCHARGE')]
    june_strategy = [(21, 256, 'CHARGE'), (26, 128, 'CHARGE'), (77, 74, 'CHARGE'), (95, 12, 'CHARGE'), (16, 134, 'DISCHARGE'), (42, 120, 'DISCHARGE'), (79, 72, 'DISCHARGE'), (95, -16, 'DISCHARGE')]
    july_strategy= [(13, 272, 'CHARGE'), (54, 86, 'CHARGE'), (76, 48, 'CHARGE'), (95, -98, 'CHARGE'), (23, 128, 'DISCHARGE'), (61, 86, 'DISCHARGE'), (68, -88, 'DISCHARGE'), (95, -220, 'DISCHARGE')]
    august_strategy = [(19, 228, 'CHARGE'), (38, 108, 'CHARGE'), (83, 60, 'CHARGE'), (95, -34, 'CHARGE'), (2, 410, 'DISCHARGE'), (4, 208, 'DISCHARGE'), (72, 114, 'DISCHARGE'), (95, -296, 'DISCHARGE')]
    september_strategy= [(23, 208, 'CHARGE'), (65, 136, 'CHARGE'), (95, 108, 'CHARGE'), (95, -110, 'CHARGE'), (13, 216, 'DISCHARGE'), (34, 176, 'DISCHARGE'), (81, 150, 'DISCHARGE'), (95, -18, 'DISCHARGE')]
    october_strategy= [(1, 364, 'CHARGE'), (10, 264, 'CHARGE'), (44, 218, 'CHARGE'), (95, 134, 'CHARGE'), (23, 298, 'DISCHARGE'), (60, 206, 'DISCHARGE'), (85, 180, 'DISCHARGE'), (95, 70, 'DISCHARGE')]
    november_strategy= [(15, 262, 'CHARGE'), (48, 196, 'CHARGE'), (57, 192, 'CHARGE'), (95, 176, 'CHARGE'), (20, 320, 'DISCHARGE'), (48, 292, 'DISCHARGE'), (66, 230, 'DISCHARGE'), (95, -226, 'DISCHARGE')]
    december_strategy= [(44, 460, 'CHARGE'), (67, 364, 'CHARGE'), (83, 218, 'CHARGE'), (95, 180, 'CHARGE'), (11, 524, 'DISCHARGE'), (20, 92, 'DISCHARGE'), (51, -48, 'DISCHARGE'), (95, -58, 'DISCHARGE')]

    twelve_strategy_lines_money = [january_strategy, february_strategy, march_strategy,
                             april_strategy, may_strategy, june_strategy,
                             july_strategy, august_strategy, september_strategy,
                             october_strategy, november_strategy, december_strategy]

    january_strategy= [(5, 278, 'CHARGE'), (29, 78, 'CHARGE'), (91, 50, 'CHARGE'), (95, 8, 'CHARGE'), (5, 330, 'DISCHARGE'), (19, 214, 'DISCHARGE'), (77, 64, 'DISCHARGE'), (95, -60, 'DISCHARGE')]
    february_strategy= [(35, 70, 'CHARGE'), (54, 48, 'CHARGE'), (76, 38, 'CHARGE'), (95, -12, 'CHARGE'), (12, 148, 'DISCHARGE'), (27, 112, 'DISCHARGE'), (43, -28, 'DISCHARGE'), (95, -1182, 'DISCHARGE')]
    march_strategy= [(41, 88, 'CHARGE'), (89, 48, 'CHARGE'), (95, -40, 'CHARGE'), (95, -288, 'CHARGE'), (19, 134, 'DISCHARGE'), (42, 60, 'DISCHARGE'), (63, 52, 'DISCHARGE'), (95, -174, 'DISCHARGE')]
    april_strategy= [(20, 208, 'CHARGE'), (66, 72, 'CHARGE'), (78, 2, 'CHARGE'), (81, -122, 'CHARGE'), (17, 224, 'DISCHARGE'), (31, 92, 'DISCHARGE'), (80, 62, 'DISCHARGE'), (95, -32, 'DISCHARGE')]
    may_strategy= [(17, 170, 'CHARGE'), (51, 66, 'CHARGE'), (70, 46, 'CHARGE'), (95, -4, 'CHARGE'), (23, 104, 'DISCHARGE'), (43, -4, 'DISCHARGE'), (68, -154, 'DISCHARGE'), (88, -206, 'DISCHARGE')]
    june_strategy= [(7, 212, 'CHARGE'), (44, 206, 'CHARGE'), (74, 78, 'CHARGE'), (95, 58, 'CHARGE'), (5, 232, 'DISCHARGE'), (7, 190, 'DISCHARGE'), (28, -6, 'DISCHARGE'), (95, -126, 'DISCHARGE')]
    july_strategy= [(13, 126, 'CHARGE'), (28, 86, 'CHARGE'), (49, 84, 'CHARGE'), (77, 80, 'CHARGE'), (9, 268, 'DISCHARGE'), (21, 132, 'DISCHARGE'), (82, 80, 'DISCHARGE'), (95, -274, 'DISCHARGE')]
    august_strategy= [(19, 204, 'CHARGE'), (23, 118, 'CHARGE'), (82, 102, 'CHARGE'), (95, 42, 'CHARGE'), (8, 128, 'DISCHARGE'), (10, -132, 'DISCHARGE'), (57, -162, 'DISCHARGE'), (95, -364, 'DISCHARGE')]
    september_strategy= [(23, 204, 'CHARGE'), (72, 112, 'CHARGE'), (82, 82, 'CHARGE'), (95, 48, 'CHARGE'), (41, 180, 'DISCHARGE'), (57, 156, 'DISCHARGE'), (83, 4, 'DISCHARGE'), (93, -198, 'DISCHARGE')]
    october_strategy= [(32, 284, 'CHARGE'), (67, 166, 'CHARGE'), (95, 98, 'CHARGE'), (95, -34, 'CHARGE'), (7, 352, 'DISCHARGE'), (63, 208, 'DISCHARGE'), (90, 180, 'DISCHARGE'), (95, 106, 'DISCHARGE')]
    november_strategy= [(12, 332, 'CHARGE'), (67, 208, 'CHARGE'), (89, 176, 'CHARGE'), (95, 140, 'CHARGE'), (7, 280, 'DISCHARGE'), (46, 276, 'DISCHARGE'), (74, 144, 'DISCHARGE'), (95, -96, 'DISCHARGE')]
    december_strategy= [(45, 460, 'CHARGE'), (66, 368, 'CHARGE'), (95, 218, 'CHARGE'), (95, -148, 'CHARGE'), (15, 240, 'DISCHARGE'), (32, -102, 'DISCHARGE'), (48, -174, 'DISCHARGE'), (95, -326, 'DISCHARGE')]

    twelve_strategy_lines_congestion = [january_strategy, february_strategy, march_strategy,
                                   april_strategy, may_strategy, june_strategy,
                                   july_strategy, august_strategy, september_strategy,
                                   october_strategy, november_strategy, december_strategy]

    twelve_strategies_money = []
    twelve_strategies_congestion = []
    for i in range(len(twelve_strategy_lines_congestion)):
        strategy_lines = twelve_strategy_lines_money[i]
        month_strategy = PointBasedStrategy(f'Disregard congestion optimized strategy for {month_shorts[i]}',
                                            price_step_size=2)
        for strat_point in strategy_lines:
            month_strategy.add_point(strat_point)
        month_strategy.upload_strategy()
        twelve_strategies_money.append(month_strategy)

        strategy_lines = twelve_strategy_lines_congestion[i]
        month_strategy = PointBasedStrategy(f'Congestion optimized strategy for {month_shorts[i]}',
                                            price_step_size=2)
        for strat_point in strategy_lines:
            month_strategy.add_point(strat_point)
        month_strategy.upload_strategy()
        twelve_strategies_congestion.append(month_strategy)

    for i in range(len(twelve_strategies_money)):
        money = twelve_strategies_money[i]
        congestion = twelve_strategies_congestion[i]

        visualize_strategy(money)
        visualize_strategy(congestion)
