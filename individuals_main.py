import os
import sys

from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.IndividualMutateNormalDist import IndividualMutateNormalDist
from evolutionary_algorithm.individuals.IndividualRandomNormalDist import IndividualRandomNormalDist
from evolutionary_algorithm.individuals.mutation_params import random_mutation


def do_single_run(individual_class, month=1, filename=None, label='RandomNormalDist'):
    number_of_points = 4
    price_step_size = 2

    fitness_class = Fitness()
    fitness_class.set_month(month)
    mutate_params = random_mutation
    mutate_params['strategy_price_step_size'] = price_step_size
    mutate_params['sort_strategy'] = 1

    evo = Evolution(
        pool_size=100,
        fitness=fitness_class.fitness,
        individual_class=individual_class,
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
        month_filenames = ['january', 'february', 'march', 'april',
                           'may', 'june', 'july', 'august',
                           'september', 'october', 'november', 'december']
        filename = month_filenames[month - 1] + f'_{label}'

    for _ in range(n_epochs):
        evo.step()
        evo.report()
        # evo.write_to_csv(f'..{os.path.sep}data{os.path.sep}ea_runs{os.path.sep}individual_investigation{os.path.sep}{filename}.csv')
        evo.write_to_csv(f'data{os.path.sep}ea_runs{os.path.sep}individual_investigation{os.path.sep}{filename}.csv')
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
        for _ in range(6):
            for month_index in [3, 4, 11]:
                other_individual = IndividualRandomNormalDist
                other_label = 'RandomNormalDist'
                do_single_run(month=month_index, individual_class=other_individual, label=other_label)
    else:
        print('Running setting other')
        for _ in range(6):
            for month_index in [3, 4, 11]:
                other_individual = IndividualMutateNormalDist
                other_label = 'MutateNormalDist'
                do_single_run(month=month_index, individual_class=other_individual, label=other_label)
