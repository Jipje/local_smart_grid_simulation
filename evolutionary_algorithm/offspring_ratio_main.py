import os
import sys

from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.IndividualRandomNormalDist import IndividualRandomNormalDist
from evolutionary_algorithm.individuals.guided_initialisation.GuidedInitRandomNormalDist import \
    GuidedInitRandomNormalDist
from evolutionary_algorithm.individuals.mutation_params import big_mutation_with_overshoot, random_mutation, \
    big_mutation

month_filenames = ['january', 'february', 'march', 'april',
                           'may', 'june', 'july', 'august',
                           'september', 'october', 'november', 'december']


def do_fully_random_single_run(month=1, filename=None, pool_size=100, n_offsprings=50):
    number_of_points = 4
    price_step_size = 2

    fitness_class = Fitness()
    fitness_class.set_month(month)
    mutate_params = random_mutation
    mutate_params['strategy_price_step_size'] = price_step_size
    mutate_params['sort_strategy'] = None

    evo = Evolution(
        pool_size=pool_size,
        fitness=fitness_class.fitness,
        individual_class=IndividualRandomNormalDist,
        n_offsprings=n_offsprings,
        pair_params={'strategy_price_step_size': price_step_size},
        mutate_params=mutate_params,
        init_params={
            'number_of_points': number_of_points,
            'strategy_price_step_size': price_step_size
        }
    )
    n_epochs = 40

    if filename is None:
        filename = month_filenames[month - 1]

    for _ in range(n_epochs):
        evo.step()
        evo.report()
        evo.write_to_csv(f'..{os.path.sep}data{os.path.sep}ea_runs{os.path.sep}offspring_ratio{os.path.sep}{filename}.csv')
        # evo.write_to_csv(f'data{os.path.sep}ea_runs{os.path.sep}population_investigation{os.path.sep}{filename}.csv')
        if evo.early_end():
            break

    print(f'Best performing individual {filename}:\tElite fitness: {evo.pool.individuals[-1].fitness}\n')
    print(evo.pool.individuals[-1])


def do_single_run(month=1, filename=None, mutate_params=None):
    number_of_points = 4
    price_step_size = 2

    fitness_class = Fitness()
    fitness_class.set_month(month)
    if mutate_params is None:
        mutate_params = big_mutation_with_overshoot
    mutate_params['strategy_price_step_size'] = price_step_size
    mutate_params['sort_strategy'] = None

    evo = Evolution(
        pool_size=100,
        fitness=fitness_class.fitness,
        individual_class=IndividualRandomNormalDist,
        n_offsprings=50,
        pair_params={'strategy_price_step_size': price_step_size},
        mutate_params=mutate_params,
        init_params={
            'number_of_points': number_of_points,
            'strategy_price_step_size': price_step_size
        }
    )
    n_epochs = 40

    if filename is None:
        filename = month_filenames[month - 1]

    for _ in range(n_epochs):
        evo.step()
        evo.report()
        evo.write_to_csv(f'..{os.path.sep}data{os.path.sep}ea_runs{os.path.sep}mutation_investigation{os.path.sep}{filename}.csv')
        # evo.write_to_csv(f'data{os.path.sep}ea_runs{os.path.sep}population_investigation{os.path.sep}{filename}.csv')
        if evo.early_end():
            break

    print(f'Best performing individual {filename}:\tElite fitness: {evo.pool.individuals[-1].fitness}\n')
    print(evo.pool.individuals[-1])


if __name__ == '__main__':
    try:
        runnable_int = int(sys.argv[1])
    except IndexError:
        runnable_int = 0

    if runnable_int == 1:
        print('Running setting 1')
        for _ in range(4):
            for month_index in [3, 4, 11]:
                month_filename = month_filenames[month_index - 1]
                custom_filename = month_filename + f'_big_mutation_with_overshoot'
                do_single_run(month=month_index, filename=custom_filename)
    else:
        print('Running setting other')
        for _ in range(4):
            for month_index in [3, 4, 11]:
                month_filename = month_filenames[month_index - 1]
                custom_filename = month_filename + f'_big_mutation'
                custom_mutate_params = big_mutation
                do_single_run(month=month_index, filename=custom_filename, mutate_params=custom_mutate_params)
