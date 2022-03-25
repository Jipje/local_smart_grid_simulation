import dateutil.tz

from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.IndividualFixedNormalDist import IndividualFixedNormalDist
from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual

utc = dateutil.tz.tzutc()


if __name__ == '__main__':
    fitness_class = Fitness()
    fitness_class.set_month(4)
    evo = Evolution(
        pool_size=500, fitness=fitness_class.fitness, individual_class=IndividualFixedNormalDist, n_offsprings=200,
        pair_params={},
        mutate_params={},
        init_params={'number_of_points': 4}
    )
    n_epochs = 50

    for i in range(n_epochs):
        evo.step()
        if evo.early_end():
            break

    print(evo.pool.individuals[-1].fitness)
    print(evo.pool.individuals[-1])
    print(evo.pool.individuals[-2].fitness)
    print(evo.pool.individuals[-2])
    print(evo.pool.individuals[-3].fitness)
    print(evo.pool.individuals[-3])
