import dateutil.tz

from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.IndividualFixedUniformDist import IndividualFixedUniformDist
from evolutionary_algorithm.individuals.IndividualMiddleAndMutate import IndividualMiddleAndMutate
from evolutionary_algorithm.individuals.IndividualMutateNormalDist import IndividualMutateNormalDist
from evolutionary_algorithm.individuals.IndividualRandomNormalDist import IndividualRandomNormalDist
from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual
from evolutionary_algorithm.individuals.mutation_params import aggressive_mutation, small_mutation, big_mutation, \
    big_mutation_with_overshoot, random_mutation

utc = dateutil.tz.tzutc()


def run_all_months():
    for month in range(1, 13):
        for _ in range(5):
            do_single_run(month)


def do_single_run(month=1, filename=None, pool_size=30, n_offsprings=15):
    number_of_points = 4
    price_step_size = 2

    fitness_class = Fitness()
    fitness_class.set_month(month)
    mutate_params = random_mutation
    mutate_params['strategy_price_step_size'] = price_step_size

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
    n_epochs = 50

    if filename is None:
        month_filenames = ['january', 'february', 'march', 'april',
                       'may', 'june', 'july', 'august',
                       'september', 'october', 'november', 'december']
        filename = month_filenames[month - 1]

    for _ in range(n_epochs):
        evo.step()
        evo.report()
        evo.write_to_csv(f'../data/ea_runs/population_investigation/{filename}.csv')
        if evo.early_end():
            break

    # print('BEST PERFORMING INDIVIDUALS')
    print('Best performing individual for run:\n'
          f'\tPop size: {pool_size}\n'
          f'\tElite fitness: {evo.pool.individuals[-1].fitness}')
    # print(evo.pool.individuals[-1].fitness)
    # print(evo.pool.individuals[-1])
    # print(evo.pool.individuals[-2].fitness)
    # print(evo.pool.individuals[-2])
    # print(evo.pool.individuals[-3].fitness)
    # print(evo.pool.individuals[-3])


if __name__ == '__main__':
    for pop_size in [32, 64, 128, 256, 512, 1024, 2048, 4096]:
        offspring_ratio = 0.5
        offspring_size = int(pop_size * offspring_ratio)
        filename = f'pop_size_{pop_size}'
        do_single_run(4, filename, pop_size, offspring_size)
        break

    #####################################
    # run_all_months()
    #####################################
    # for _ in range(5):
    #     do_single_run(4, filename='RandomNormalDistSmallMutation')
    #####################################
    # month = 1
    # number_of_points = 4
    # price_step_size = 2
    #
    # fitness_class = Fitness()
    # fitness_class.set_month(month)
    # mutate_params = aggressive_mutation
    # mutate_params['strategy_price_step_size'] = price_step_size
    # mutate_params['soc_lower'] = -2
    # mutate_params['soc_upper'] = 2
    #
    # evo = Evolution(
    #     pool_size=30,
    #     fitness=fitness_class.fitness,
    #     individual_class=IndividualRandomNormalDist,
    #     n_offsprings=15,
    #     pair_params={'strategy_price_step_size': price_step_size},
    #     mutate_params=mutate_params,
    #     init_params={
    #         'number_of_points': number_of_points,
    #         'strategy_price_step_size': price_step_size
    #     }
    # )
    # n_epochs = 20
    #
    # month_filenames = ['january', 'february', 'march', 'april',
    #                    'may', 'june', 'july', 'august',
    #                    'september', 'october', 'november', 'december']
    # month_filename = month_filenames[month - 1]
    #
    # for _ in range(n_epochs):
    #     evo.step()
    #     evo.report()
    #     evo.write_to_csv(f'../data/aggressive_ea_runs/{month_filename}.csv')
    #     if evo.early_end():
    #         break
    #
    # print('BEST PERFORMING INDIVIDUALS')
    # print(evo.pool.individuals[-1].fitness)
    # print(evo.pool.individuals[-1])
    # print(evo.pool.individuals[-2].fitness)
    # print(evo.pool.individuals[-2])
    # print(evo.pool.individuals[-3].fitness)
    # print(evo.pool.individuals[-3])
