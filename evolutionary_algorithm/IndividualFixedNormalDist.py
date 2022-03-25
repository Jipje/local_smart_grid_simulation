import random

from evolutionary_algorithm.StrategyIndividual import StrategyIndividual
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy, visualize_strategies


class IndividualFixedNormalDist(StrategyIndividual):

    def pair(self, other, pair_params):
        original_charge = self.value.charge_points
        original_discharge = self.value.discharge_points
        other_charge = other.value.charge_points
        other_discharge = other.value.discharge_points

        assert len(original_charge) == len(other_charge)
        assert len(original_discharge) == len(other_discharge)

        new_individual = PointBasedStrategy(name=f'Child of {self.value.name} and\n{other.value.name}')
        for i in range(len(original_charge)):
            original_point = original_charge[i]
            other_point = other_charge[i]
            assert original_point[2] == other_point[2]
            new_point = [None, None, None]
            random_dist = random.random()
            for j in range(2):
                new_point[j] = int(min(original_point[j], other_point[j]) +
                                   random_dist * abs(original_point[j] - other_point[j]))
            new_point[0] = max(new_point[0], 5)
            new_point[0] = min(new_point[0], 95)
            new_point[1] = new_point[1] - new_point[1] % 5
            new_point[2] = 'CHARGE'
            new_individual.add_point((new_point[0], new_point[1], new_point[2]))

            original_point = original_discharge[i]
            other_point = other_discharge[i]
            assert original_point[2] == other_point[2]
            new_point = [None, None, None]
            random_dist = random.random()
            for j in range(2):
                new_point[j] = int(min(original_point[j], other_point[j]) +
                                   random_dist * abs(original_point[j] - other_point[j]))
            new_point[0] = max(new_point[0], 5)
            new_point[0] = min(new_point[0], 95)
            new_point[1] = new_point[1] + 5 - new_point[1] % 5
            new_point[2] = 'DISCHARGE'
            new_individual.add_point((new_point[0], new_point[1], new_point[2]))
        new_individual.upload_strategy()
        return IndividualFixedNormalDist(new_individual)

    def mutate(self, mutate_params):
        return self


if __name__ == '__main__':
    init_params = {'number_of_points': 4}

    init_params['seed'] = 2668413331210231900
    other = IndividualFixedNormalDist(init_params=init_params)
    init_params['seed'] = 6618115003047519509
    current = IndividualFixedNormalDist(init_params=init_params)

    baby = current.pair(other, pair_params=None)
    visualize_strategies([current.value, other.value, baby.value])
    print(baby)
    baby = baby.mutate(mutate_params=None)
    print(baby)
