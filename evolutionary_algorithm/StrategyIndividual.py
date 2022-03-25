import random

from evolutionary_algorithm.Individual import Individual
from helper_objects.strategies import RandomStrategyGenerator
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from one_time_scripts.visualisations.strategy_visualisation import visualize_strategy, visualize_strategies


class StrategyIndividual(Individual):

    def pair(self, other, pair_params):
        pass

    def mutate(self, mutate_params):
        pass

    def _random_init(self, init_params):
        try:
            seed = init_params['seed']
        except KeyError:
            seed = None
        return RandomStrategyGenerator.generate_random_discharge_relative_strategy(
            number_of_points=init_params['number_of_points'], seed=seed, flag_visualise=True)

    def __str__(self):
        visualize_strategy(self.value)
        msg = f'{self.value.name}:\n CHARGING POINTS\n'
        for point in self.value.charge_points:
            msg = msg + f'\t({point[0]}, {point[1]})\n'
        msg = msg + 'DISCHARGING POINTS\n'
        for point in self.value.discharge_points:
            msg = msg + f'\t({point[0]}, {point[1]})\n'
        return msg
