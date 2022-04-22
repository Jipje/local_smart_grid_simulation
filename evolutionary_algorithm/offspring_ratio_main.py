import os

from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.IndividualRandomNormalDist import IndividualRandomNormalDist
from evolutionary_algorithm.individuals.guided_initialisation.GuidedInitRandomNormalDist import \
    GuidedInitRandomNormalDist
from evolutionary_algorithm.individuals.mutation_params import big_mutation_with_overshoot, random_mutation

month_filenames = ['january', 'february', 'march', 'april',
                           'may', 'june', 'july', 'august',
                           'september', 'october', 'november', 'december']


def do_single_run(month=1, filename=None, pool_size=100, n_offsprings=50):
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


if __name__ == '__main__':
    for _ in range(2):
        for month_index in [3, 4, 11]:
            month_filename = month_filenames[month_index - 1]
            for num_of_offspring in [75, 90]:
                population = 100
                custom_filename = month_filename + f'_{num_of_offspring}off_{population}pop'
                do_single_run(month=month_index, filename=custom_filename, pool_size=population, n_offsprings=num_of_offspring)
