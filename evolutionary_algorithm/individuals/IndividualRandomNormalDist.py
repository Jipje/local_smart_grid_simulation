import random

from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategies


class IndividualRandomNormalDist(StrategyIndividual):

    def pair(self, other, pair_params):
        new_individual = self.make_new_individual(other, pair_params)
        return IndividualRandomNormalDist(new_individual)

    def mutate(self, mutate_params):
        return self

    def generate_new_point(self, new_point, original_point, other_point):
        for j in range(2):
            random_dist = random.random()
            new_point[j] = int(min(original_point[j], other_point[j]) +
                               random_dist * abs(original_point[j] - other_point[j]))
        return new_point


if __name__ == '__main__':
    init_params = {'number_of_points': 4}

    init_params['seed'] = 2668413331210231900
    other = IndividualRandomNormalDist(init_params=init_params)
    init_params['seed'] = 6618115003047519509
    current = IndividualRandomNormalDist(init_params=init_params)

    baby = current.pair(other, pair_params={})
    visualize_strategies([current.value, other.value, baby.value])
    print(baby)
    baby = baby.mutate(mutate_params={})
    print(baby)
