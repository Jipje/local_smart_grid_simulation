import dateutil.tz

from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.IndividualFixedNormalDist import IndividualFixedNormalDist
from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual

utc = dateutil.tz.tzutc()


if __name__ == '__main__':
    number_of_points = 4
    price_step_size = 2

    fitness_class = Fitness()
    fitness_class.set_month(11)
    evo = Evolution(
        pool_size=30, fitness=fitness_class.fitness, individual_class=IndividualFixedNormalDist, n_offsprings=10,
        pair_params={'strategy_price_step_size': price_step_size},
        mutate_params={},
        init_params={
            'number_of_points': number_of_points,
            'strategy_price_step_size': price_step_size
        }
    )
    n_epochs = 50

    for i in range(n_epochs):
        evo.step()
        evo.report()
        if evo.early_end():
            break

    print('BEST PERFORMING INDIVIDUALS')
    print(evo.pool.individuals[-1].fitness)
    print(evo.pool.individuals[-1])
    print(evo.pool.individuals[-2].fitness)
    print(evo.pool.individuals[-2])
    print(evo.pool.individuals[-3].fitness)
    print(evo.pool.individuals[-3])
