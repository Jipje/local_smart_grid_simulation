import dateutil.tz

from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.IndividualFixedNormalDist import IndividualFixedNormalDist
from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual

utc = dateutil.tz.tzutc()

def run_all_months():
    for month in range(1, 13):
        for i in range(5):
            do_single_run(month)


def do_single_run(month=1):
    number_of_points = 4
    price_step_size = 2

    fitness_class = Fitness()
    fitness_class.set_month(month)
    evo = Evolution(
        pool_size=30,
        fitness=fitness_class.fitness,
        individual_class=IndividualFixedNormalDist,
        n_offsprings=10,
        pair_params={'strategy_price_step_size': price_step_size},
        mutate_params={},
        init_params={
            'number_of_points': number_of_points,
            'strategy_price_step_size': price_step_size
        }
    )
    n_epochs = 50

    month_filenames = ['january', 'february', 'march', 'april',
                       'may', 'june', 'july', 'august',
                       'september', 'october', 'november', 'december']
    month_filename = month_filenames[month - 1]

    for _ in range(n_epochs):
        evo.step()
        evo.report()
        evo.write_to_csv(f'../data/first_ea_runs/{month_filename}.csv')
        if evo.early_end():
            break

    print('BEST PERFORMING INDIVIDUALS')
    print(evo.pool.individuals[-1].fitness)
    print(evo.pool.individuals[-1])
    print(evo.pool.individuals[-2].fitness)
    print(evo.pool.individuals[-2])
    print(evo.pool.individuals[-3].fitness)
    print(evo.pool.individuals[-3])


if __name__ == '__main__':
    do_single_run(6)
