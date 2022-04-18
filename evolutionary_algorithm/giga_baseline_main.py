import os

from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.guided_initialisation.GuidedInitRandomNormalDist import \
    GuidedInitRandomNormalDist
from evolutionary_algorithm.individuals.mutation_params import random_mutation, big_mutation_with_overshoot


def do_single_run(month=1, filename=None, pool_size=64, n_offsprings=32):
    number_of_points = 4
    price_step_size = 2

    fitness_class = Fitness()
    fitness_class.set_month(month)
    mutate_params = big_mutation_with_overshoot
    mutate_params['strategy_price_step_size'] = price_step_size
    mutate_params['sort_strategy'] = 1

    evo = Evolution(
        pool_size=pool_size,
        fitness=fitness_class.fitness,
        individual_class=GuidedInitRandomNormalDist,
        n_offsprings=n_offsprings,
        pair_params={'strategy_price_step_size': price_step_size},
        mutate_params=mutate_params,
        init_params={
            'number_of_points': number_of_points,
            'strategy_price_step_size': price_step_size
        }
    )
    n_epochs = 20

    if filename is None:
        month_filenames = ['january', 'february', 'march', 'april',
                           'may', 'june', 'july', 'august',
                           'september', 'october', 'november', 'december']
        filename = month_filenames[month - 1]

    for _ in range(n_epochs):
        evo.step()
        evo.report()
        evo.write_to_csv(f'..{os.path.sep}data{os.path.sep}ea_runs{os.path.sep}giga_baseline{os.path.sep}{filename}.csv')
        # evo.write_to_csv(f'data{os.path.sep}ea_runs{os.path.sep}population_investigation{os.path.sep}{filename}.csv')
        if evo.early_end():
            break

    print(f'Best performing individual:\tElite fitness: {evo.pool.individuals[-1].fitness}')
    print(evo.pool.individuals[-1])


if __name__ == '__main__':
    for month in [3, 4, 12]:
        for _ in range(5):
            do_single_run(month=month)
