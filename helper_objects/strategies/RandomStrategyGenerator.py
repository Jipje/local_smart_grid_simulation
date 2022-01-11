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
    if name is None:
        name = 'Randomly generated strategy. Seed={}'.format(seed)

    price_step_size = 5
    point_based_strat = PointBasedStrategy(name, price_step_size=price_step_size)
    number_of_points = random.randint(1, 5)

    soc_step_size = int(89/number_of_points)
    price_step_size = int(300/number_of_points)
    if price_step_size % 5 != 0:
        price_step_size = price_step_size - (price_step_size % 5)
    charge_soc = None
    charge_price = None
    discharge_soc = None
    discharge_price = None
    for i in range(number_of_points):
        if charge_soc is None and charge_price is None:
            charge_soc = random.randint(6, 6 + soc_step_size)
            charge_price = random.randrange(int(200 - price_step_size), 200 - 5, 5)
        else:
            charge_soc = random.randint(charge_soc + 1, i * soc_step_size)
            charge_price = random.randrange(200 - i * price_step_size, charge_price - 1, 5)
        point_based_strat.add_point((charge_soc, charge_price, 'CHARGE'))

        if discharge_soc is None and discharge_price is None:
            discharge_soc = charge_soc + random.randint(5, soc_step_size)
            discharge_price = random.randrange(charge_price, 200, 5)
        else:
            discharge_soc = charge_soc + random.randint(5, soc_step_size)
            discharge_price = random.randrange(charge_price, discharge_price - 1, 5)
        point_based_strat.add_point((discharge_soc, discharge_price, 'DISCHARGE'))

    state_of_charge_perc = 95
    imbalance_price = random.randrange(-100, charge_price - 1, 5)
    point_based_strat.add_point((state_of_charge_perc, imbalance_price, 'CHARGE'))

    state_of_charge_perc = 95
    imbalance_price = random.randrange(imbalance_price, discharge_price - 1, 5)
    point_based_strat.add_point((state_of_charge_perc, imbalance_price, 'DISCHARGE'))

    point_based_strat.upload_strategy()
    return point_based_strat


if __name__ == '__main__':
    random_strategy = generate_random_discharge_relative_strategy(seed=3331977661887185251)
    visualize_strategy(random_strategy)
    random_strategy = generate_random_discharge_relative_strategy()
    visualize_strategy(random_strategy)
