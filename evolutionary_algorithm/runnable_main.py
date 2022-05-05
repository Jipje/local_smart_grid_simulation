import os

import dateutil.tz

from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.evolutions.NoAvgIncrEvolution import NoAvgIncrEvolution
from evolutionary_algorithm.individuals.IndividualFixedUniformDist import IndividualFixedUniformDist
from evolutionary_algorithm.individuals.IndividualMiddleAndMutate import IndividualMiddleAndMutate
from evolutionary_algorithm.individuals.IndividualMutateNormalDist import IndividualMutateNormalDist
from evolutionary_algorithm.individuals.IndividualRandomNormalDist import IndividualRandomNormalDist
from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual
from evolutionary_algorithm.individuals.mutation_params import aggressive_mutation, small_mutation, big_mutation, \
    big_mutation_with_overshoot, random_mutation
import sys

utc = dateutil.tz.tzutc()

default_ea_runnable_settings = {
    'mutation_possibility': 0.2,
    'mutate_params': random_mutation,
    'sort_strategy': 1,
    'pop_size': 20,
    'n_offsprings': 16
}


def do_default_run(ea_runnable_settings, month=1, filename=None):
    number_of_points = 4
    price_step_size = 2
    fitness_class = Fitness()
    fitness_class.set_month(month)

    if ea_runnable_settings is None:
        ea_runnable_settings = default_ea_runnable_settings

    population_size = ea_runnable_settings['pop_size']
    n_offsprings = ea_runnable_settings['n_offsprings']
    mutate_params = ea_runnable_settings['mutate_params']
    mutate_params['strategy_price_step_size'] = price_step_size
    mutate_params['sort_strategy'] = ea_runnable_settings['sort_strategy']
    mutation_possibility = ea_runnable_settings['mutation_possibility']

    evo = NoAvgIncrEvolution(
        pool_size=population_size,
        fitness=fitness_class.fitness,
        individual_class=IndividualRandomNormalDist,
        n_offsprings=n_offsprings,
        pair_params={'strategy_price_step_size': price_step_size},
        mutate_params=mutate_params,
        init_params={
            'number_of_points': number_of_points,
            'strategy_price_step_size': price_step_size
        },
        offspring_per_couple=4,
        mutation_possibility=mutation_possibility
    )
    n_epochs = 200

    if filename is None:
        month_filenames = ['january', 'february', 'march', 'april',
                       'may', 'june', 'july', 'august',
                       'september', 'october', 'november', 'december']
        filename = month_filenames[month - 1]

    for _ in range(n_epochs):
        evo.step()
        evo.report()
        # evo.write_to_csv(f'..{os.path.sep}data{os.path.sep}ea_runs{os.path.sep}population_investigation{os.path.sep}{filename}.csv')
        # evo.write_to_csv(f'data{os.path.sep}ea_runs{os.path.sep}population_investigation{os.path.sep}{filename}.csv')
        if evo.early_end():
            break

    # print('BEST PERFORMING INDIVIDUALS')
    print('Best performing individual for run:\n'
          f'\tElite fitness: {evo.pool.individuals[-1].fitness}')
    print(evo.pool.individuals[-1])
    # print(evo.pool.individuals[-2].fitness)
    # print(evo.pool.individuals[-2])
    # print(evo.pool.individuals[-3].fitness)
    # print(evo.pool.individuals[-3])


if __name__ == '__main__':
    # run_all_months()
    #####################################
    # for _ in range(5):
    do_default_run(None, month=4)
