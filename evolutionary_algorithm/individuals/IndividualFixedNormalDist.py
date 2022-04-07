import random

from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual
from evolutionary_algorithm.individuals.mutation_params import aggressive_mutation, small_mutation
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategies


class IndividualFixedNormalDist(StrategyIndividual):

    def pair(self, other, pair_params):
        new_individual = self.make_new_individual(other, pair_params)
        return IndividualFixedNormalDist(new_individual)

    def mutate(self, mutate_params):
        new_individual = self.mutate_individual(mutate_params)
        return IndividualFixedNormalDist(new_individual)

    def generate_new_point(self, new_point, original_point, other_point):
        random_dist = random.random()
        for j in range(2):
            new_point[j] = int(min(original_point[j], other_point[j]) +
                               random_dist * abs(original_point[j] - other_point[j]))
        return new_point


if __name__ == '__main__':
    price_step_size = 2

    init_params = {
        'number_of_points': 4,
        'strategy_price_step_size': price_step_size
    }
    pair_params = {
        'strategy_price_step_size': price_step_size
    }

    mutate_params = small_mutation
    mutate_params['strategy_price_step_size'] = price_step_size

    init_params['seed'] = 2668413331210231900
    other = IndividualFixedNormalDist(init_params=init_params)
    init_params['seed'] = 6618115003047519509
    current = IndividualFixedNormalDist(init_params=init_params)

    print(current)
    print(other)

    baby = current.pair(other, pair_params=pair_params)
    visualize_strategies([current.value, other.value, baby.value])
    print(baby)
    baby = baby.mutate(mutate_params=mutate_params)
    print(baby)
