import random

from evolutionary_algorithm.Individual import Individual
from helper_objects.strategies import RandomStrategyGenerator
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy, visualize_strategies


class StrategyIndividual(Individual):

    def pair(self, other, pair_params):
        new_individual = self.make_new_individual(other, pair_params)
        return StrategyIndividual(new_individual)

    def mutate(self, mutate_params):
        return self

    def make_new_individual(self, other, pair_params):
        original_charge = self.value.charge_points
        original_discharge = self.value.discharge_points
        other_charge = other.value.charge_points
        other_discharge = other.value.discharge_points

        assert len(original_charge) == len(other_charge)
        assert len(original_discharge) == len(other_discharge)

        try:
            strategy_price_step_size = pair_params['strategy_price_step_size']
        except KeyError:
            strategy_price_step_size = 5

        new_individual = PointBasedStrategy(name=f'Child of {self.value.name} and\n{other.value.name}',
                                            price_step_size=strategy_price_step_size)
        for i in range(len(original_charge)):
            original_point = original_charge[i]
            other_point = other_charge[i]
            new_individual.add_point(self.create_new_point(original_point, other_point, pair_params))

            original_point = original_discharge[i]
            other_point = other_discharge[i]
            new_individual.add_point(self.create_new_point(original_point, other_point, pair_params))
        new_individual.upload_strategy()
        return new_individual

    def create_new_point(self, original_point, other_point, pair_params):
        try:
            max_soc_perc = pair_params['max_soc_perc']
            min_soc_perc = pair_params['min_soc_perc']
        except KeyError:
            max_soc_perc = 95
            min_soc_perc = 5

        try:
            price_step_size = pair_params['strategy_price_step_size']
        except KeyError:
            price_step_size = 5

        assert original_point[2] == other_point[2]
        new_point = [None, None, None]

        new_point = self.generate_new_point(new_point, original_point, other_point)

        new_point[0] = max(new_point[0], min_soc_perc)
        new_point[0] = min(new_point[0], max_soc_perc)
        new_point[1] = new_point[1] - new_point[1] % price_step_size
        new_point[2] = original_point[2]
        return new_point[0], new_point[1], new_point[2]

    def generate_new_point(self, new_point, original_point, other_point):
        for j in range(2):
            new_point[j] = int(min(original_point[j], other_point[j]) + 0.5 * abs(original_point[j] - other_point[j]))
        return new_point

    def _random_init(self, init_params):
        try:
            seed = init_params['seed']
        except KeyError:
            seed = None

        try:
            strategy_price_step_size = init_params['strategy_price_step_size']
        except KeyError:
            strategy_price_step_size = 5

        return RandomStrategyGenerator.generate_random_discharge_relative_strategy(
            number_of_points=init_params['number_of_points'],
            strategy_price_step_size=strategy_price_step_size,
            seed=seed, flag_visualise=True)

    def __str__(self):
        visualize_strategy(self.value)
        msg = f'{self.value.name}:\n CHARGING POINTS\n'
        for point in self.value.charge_points:
            msg = msg + f'\t({point[0]}, {point[1]})\n'
        msg = msg + 'DISCHARGING POINTS\n'
        for point in self.value.discharge_points:
            msg = msg + f'\t({point[0]}, {point[1]})\n'
        return msg


if __name__ == '__main__':
    strategy_price_step_size = 7

    init_params = {
        'number_of_points': 4,
        'strategy_price_step_size': strategy_price_step_size,
        'min_soc_perc': 7,
        'max_soc_perc': 98
    }
    pair_params = {
        'strategy_price_step_size': strategy_price_step_size,
        'min_soc_perc': 7,
        'max_soc_perc': 98
    }

    init_params['seed'] = 2668413331210231900
    other = StrategyIndividual(init_params=init_params)
    init_params['seed'] = 6618115003047519509
    current = StrategyIndividual(init_params=init_params)

    baby = current.pair(other, pair_params=pair_params)
    visualize_strategies([current.value, other.value, baby.value])
    print(baby)
    baby = baby.mutate(mutate_params={})
    print(baby)
