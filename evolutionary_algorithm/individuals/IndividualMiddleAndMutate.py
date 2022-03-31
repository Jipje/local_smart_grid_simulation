import random

from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual
from helper_objects.strategies import RandomStrategyGenerator
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy, visualize_strategies


class IndividualMiddleAndMutate(StrategyIndividual):

    def pair(self, other, pair_params):
        new_individual = self.make_new_individual(other, pair_params)
        return IndividualMiddleAndMutate(new_individual)

    def mutate_point(self, original_point, mutate_params):
        try:
            strategy_price_step_size = mutate_params['strategy_price_step_size']
        except KeyError:
            strategy_price_step_size = 5

        new_point = [None, None, original_point[2]]
        new_point[0] = original_point[0] + random.randint(-2, 2)
        new_point[1] = original_point[1] + random.randint(-1, 1) * strategy_price_step_size
        return new_point[0], new_point[1], new_point[2]


if __name__ == '__main__':
    price_step_size = 3

    init_params = {
        'number_of_points': 4,
        'strategy_price_step_size': price_step_size,
        'min_soc_perc': 3,
        'max_soc_perc': 96
    }
    pair_params = {
        'strategy_price_step_size': price_step_size,
        'min_soc_perc': 3,
        'max_soc_perc': 96
    }
    mutate_params = {
        'strategy_price_step_size': price_step_size,
    }

    init_params['seed'] = 2668413331210231900
    other = IndividualMiddleAndMutate(init_params=init_params)
    init_params['seed'] = 6618115003047519509
    current = IndividualMiddleAndMutate(init_params=init_params)

    baby = current.pair(other, pair_params=pair_params)
    visualize_strategies([current.value, other.value, baby.value])
    print(baby)
    baby = baby.mutate(mutate_params=mutate_params)
    print(baby)
