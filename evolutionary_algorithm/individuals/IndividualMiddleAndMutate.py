import random

from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual
from helper_objects.strategies import RandomStrategyGenerator
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy, visualize_strategies


class IndividualMiddleAndMutate(StrategyIndividual):

    def pair(self, other, pair_params):
        new_individual = self.make_new_individual(other, pair_params)
        return IndividualMiddleAndMutate(new_individual)

    def mutate(self, mutate_params):
        try:
            strategy_price_step_size = init_params['strategy_price_step_size']
        except KeyError:
            strategy_price_step_size = 5

        original_charge = self.value.charge_points
        original_discharge = self.value.discharge_points

        new_individual = PointBasedStrategy(name=f'Mutated {self.value.name}')
        for i in range(len(original_charge)):
            original_charge_point = original_charge[i]
            original_discharge_point = original_discharge[i]
            new_charge_point = [None, None, 'CHARGE']
            new_discharge_point = [None, None, 'DISCHARGE']

            new_charge_point[0] = original_charge_point[0] + random.randint(-2, 2)
            new_charge_point[1] = original_charge_point[1] + random.randint(-1, 1) * strategy_price_step_size
            new_discharge_point[0] = original_discharge_point[0] + random.randint(-2, 2)
            new_discharge_point[1] = original_discharge_point[1] + random.randint(-1, 1) * strategy_price_step_size

            new_individual.add_point((new_charge_point[0], new_charge_point[1], new_charge_point[2]))
            new_individual.add_point((new_discharge_point[0], new_discharge_point[1], new_discharge_point[2]))
        new_individual.upload_strategy()
        return IndividualMiddleAndMutate(new_individual)


if __name__ == '__main__':
    strategy_price_step_size = 3

    init_params = {
        'number_of_points': 4,
        'strategy_price_step_size': strategy_price_step_size,
        'min_soc_perc': 3,
        'max_soc_perc': 96
    }
    pair_params = {
        'strategy_price_step_size': strategy_price_step_size,
        'min_soc_perc': 3,
        'max_soc_perc': 96
    }
    mutate_params = {
        'strategy_price_step_size': strategy_price_step_size,
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
