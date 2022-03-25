import random

from evolutionary_algorithm.Individual import StrategyIndividual
from helper_objects.strategies import RandomStrategyGenerator
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy, visualize_strategies


class IndividualMiddleAndMutate(StrategyIndividual):

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
            for j in range(2):
                new_point[j] = int(min(original_point[j], other_point[j]) + 0.5 * abs(original_point[j] - other_point[j]))
            new_point[1] = new_point[1] - new_point[1] % 5
            new_point[2] = 'CHARGE'
            new_individual.add_point((new_point[0], new_point[1], new_point[2]))

            original_point = original_discharge[i]
            other_point = other_discharge[i]
            assert original_point[2] == other_point[2]
            new_point = [None, None, None]
            for j in range(2):
                new_point[j] = int(min(original_point[j], other_point[j]) + 0.5 * abs(original_point[j] - other_point[j]))
            new_point[1] = new_point[1] + 5 - new_point[1] % 5
            new_point[2] = 'DISCHARGE'
            new_individual.add_point((new_point[0], new_point[1], new_point[2]))
        new_individual.upload_strategy()
        return IndividualMiddleAndMutate(new_individual)

    def mutate(self, mutate_params):
        original_charge = self.value.charge_points
        original_discharge = self.value.discharge_points

        new_individual = PointBasedStrategy(name=f'Mutated {self.value.name}')
        for i in range(len(original_charge)):
            original_charge_point = original_charge[i]
            original_discharge_point = original_discharge[i]
            new_charge_point = [None, None, 'CHARGE']
            new_discharge_point = [None, None, 'DISCHARGE']

            new_charge_point[0] = original_charge_point[0] + random.randint(-2, 2)
            new_charge_point[1] = original_charge_point[1] + random.randint(-1, 1) * 5
            new_discharge_point[0] = original_discharge_point[0] + random.randint(-2, 2)
            new_discharge_point[1] = original_discharge_point[1] + random.randint(-1, 1) * 5

            new_individual.add_point((new_charge_point[0], new_charge_point[1], new_charge_point[2]))
            new_individual.add_point((new_discharge_point[0], new_discharge_point[1], new_discharge_point[2]))
        new_individual.upload_strategy()
        return IndividualMiddleAndMutate(new_individual)

    def _random_init(self, init_params):
        try:
            seed = init_params['seed']
        except KeyError:
            seed = None
        return RandomStrategyGenerator.generate_random_discharge_relative_strategy(
            number_of_points=init_params['number_of_points'], seed=seed, flag_visualise=True)


if __name__ == '__main__':
    init_params = {'number_of_points': 4}

    init_params['seed'] = 2668413331210231900
    other = IndividualMiddleAndMutate(init_params=init_params)
    init_params['seed'] = 6618115003047519509
    current = IndividualMiddleAndMutate(init_params=init_params)

    baby = current.pair(other, pair_params=None)
    visualize_strategies([current.value, other.value, baby.value])
    print(baby)
    baby = baby.mutate(mutate_params=None)
    print(baby)
