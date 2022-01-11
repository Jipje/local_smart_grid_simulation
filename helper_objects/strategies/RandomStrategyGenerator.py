import random
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy


def generate_random_strategy(seed=None, name=None):
    if seed is not None:
        random.seed(seed)
        if name is None:
            name = 'Randomly generated strategy. Seed={}'.format(seed)

    if name is None:
        name = 'Randomly generated strategy.'

    price_step_size = 5
    point_based_strat = PointBasedStrategy(name, price_step_size=price_step_size)
    number_of_points = random.randint(1, 5)

    charge_soc = None
    charge_price = None
    discharge_soc = None
    discharge_price = None
    for _ in range(number_of_points):
        if charge_soc is None and charge_price is None:
            state_of_charge_perc = random.randint(6, 20)
            imbalance_price = random.randrange(0, 100, 5)
        else:
            state_of_charge_perc = random.randint(charge_soc + 1, 95)
            imbalance_price = random.randrange(-100, charge_price - 1, 5)
        charge_soc = state_of_charge_perc
        charge_price = imbalance_price
        point_based_strat.add_point((state_of_charge_perc, imbalance_price, 'CHARGE'))

        if discharge_soc is None and discharge_price is None:
            state_of_charge_perc = random.randint(6, 20)
            imbalance_price = random.randrange(100, 200, 5)
        else:
            state_of_charge_perc = random.randint(discharge_soc + 1, 95)
            imbalance_price = random.randrange(-100, discharge_price - 1, 5)
        discharge_soc = state_of_charge_perc
        discharge_price = imbalance_price
        point_based_strat.add_point((state_of_charge_perc, imbalance_price, 'DISCHARGE'))

    point_based_strat.upload_strategy()
    return point_based_strat


if __name__ == '__main__':
    random_strategy = generate_random_strategy()
    visualize_strategy(random_strategy)
