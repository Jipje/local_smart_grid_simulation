import random
import sys

from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy


def generate_fully_random_strategy(seed=None, name=None):
    if seed is None:
        seed = random.randrange(sys.maxsize)
    random.seed(seed)
    if name is None:
        name = 'Randomly generated strategy. Seed={}'.format(seed)

    price_step_size = 5
    point_based_strat = PointBasedStrategy(name, price_step_size=price_step_size)
    number_of_points = random.randint(1, 5)

    for _ in range(number_of_points):
        state_of_charge_perc = random.randint(6, 95)
        imbalance_price = random.randrange(-100, 200, 5)
        point_based_strat.add_point((state_of_charge_perc, imbalance_price, 'CHARGE'))

        state_of_charge_perc = random.randint(6, 95)
        imbalance_price = random.randrange(-100, 200, 5)
        point_based_strat.add_point((state_of_charge_perc, imbalance_price, 'DISCHARGE'))

    point_based_strat.upload_strategy()
    return point_based_strat


def generate_random_discharge_relative_strategy(seed=None, name=None):
    if seed is None:
        seed = random.randrange(sys.maxsize)
    random.seed(seed)
    print(seed)
    if name is None:
        name = 'Randomly generated strategy. Seed={}'.format(seed)

    strategy_price_step_size = 5
    point_based_strat = PointBasedStrategy(name, price_step_size=strategy_price_step_size)
    number_of_points = random.randint(2, 4)

    soc_step_size = int(89/number_of_points)
    price_step_size = int(300/number_of_points)
    if price_step_size % strategy_price_step_size != 0:
        price_step_size = price_step_size - (price_step_size % strategy_price_step_size)
    charge_soc = 5
    charge_price = 201
    discharge_soc = 0
    discharge_price = 201
    for i in range(1, number_of_points + 1):
        charge_soc = random.randint(charge_soc + 1, i * soc_step_size)
        charge_price = random.randrange(200 - i * price_step_size, charge_price - 1, strategy_price_step_size)
        point_based_strat.add_point((charge_soc, charge_price, 'CHARGE'))

        discharge_soc = min(max(charge_soc, discharge_soc) + random.randint(5, soc_step_size), 94)
        discharge_price = random.randrange(charge_price, discharge_price - 1, strategy_price_step_size)
        point_based_strat.add_point((discharge_soc, discharge_price, 'DISCHARGE'))

    charge_soc = 95
    charge_price = random.randrange(-100, charge_price - 1, strategy_price_step_size)
    point_based_strat.add_point((charge_soc, charge_price, 'CHARGE'))
    discharge_soc = 95
    discharge_price = random.randrange(charge_price, discharge_price - 1, strategy_price_step_size)
    point_based_strat.add_point((discharge_soc, discharge_price, 'DISCHARGE'))

    point_based_strat.upload_strategy()
    return point_based_strat


if __name__ == '__main__':
    # fully_random = generate_fully_random_strategy()
    # visualize_strategy(fully_random)
    random_strategy = generate_random_discharge_relative_strategy()
    visualize_strategy(random_strategy)
