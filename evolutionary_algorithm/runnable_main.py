import os

import dateutil.tz

from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.evolutions.NoAvgIncrEvolution import NoAvgIncrEvolution
from evolutionary_algorithm.individuals.IndividualRandomNormalDist import IndividualRandomNormalDist
from evolutionary_algorithm.individuals.mutation_params import random_mutation

utc = dateutil.tz.tzutc()

default_ea_runnable_settings = {
    'mutation_possibility': 0.5,
    'mutate_params': random_mutation,
    'sort_strategy': 1,
    'pop_size': 100,
    'n_offsprings': 80,
    'individual_class': IndividualRandomNormalDist
}

month_filenames = ['january', 'february', 'march', 'april',
                   'may', 'june', 'july', 'august',
                   'september', 'october', 'november', 'december']


def do_an_ea_run(ea_runnable_settings, month=1, filename=None, folder=None, congestion_kw=14000):
    number_of_points = 4
    price_step_size = 2
    fitness_class = Fitness(congestion_kw=congestion_kw)
    fitness_class.set_month(month)

    if ea_runnable_settings is None:
        ea_runnable_settings = default_ea_runnable_settings

    population_size = ea_runnable_settings['pop_size']
    n_offsprings = ea_runnable_settings['n_offsprings']
    mutate_params = ea_runnable_settings['mutate_params']
    mutate_params['strategy_price_step_size'] = price_step_size
    mutate_params['sort_strategy'] = ea_runnable_settings['sort_strategy']
    mutation_possibility = ea_runnable_settings['mutation_possibility']
    individual_class = ea_runnable_settings['individual_class']

    evo = NoAvgIncrEvolution(
        pool_size=population_size,
        fitness=fitness_class.fitness,
        individual_class=individual_class,
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

    evo.report()
    evo.write_to_csv(f'data{os.path.sep}new_ea_runs{os.path.sep}{folder}{os.path.sep}{filename}.csv')
    for _ in range(n_epochs):
        evo.step()
        evo.report()
        if folder is not None:
            evo.write_to_csv(f'data{os.path.sep}new_ea_runs{os.path.sep}{folder}{os.path.sep}{filename}.csv')
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


def execute_ea_runs(suffix, run_settings, folder, month_indexes=None, num_of_runs=3, congestion_kw=14000):
    if month_indexes is None:
        month_indexes = [3, 4, 11]

    for _ in range(num_of_runs):
        for month_index in month_indexes:
            month_filename = month_filenames[month_index - 1]
            custom_filename = month_filename + suffix
            do_an_ea_run(run_settings, month=month_index, filename=custom_filename,
                         folder=folder, congestion_kw=congestion_kw)


if __name__ == '__main__':
    # run_all_months()
    #####################################
    # for _ in range(5):
    do_an_ea_run(None, month=4)
