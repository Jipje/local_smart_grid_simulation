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
        new_individual = self.mutate_individual(mutate_params)
        return StrategyIndividual(new_individual)

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

        new_point = self.generate_new_point(new_point, original_point, other_point, pair_params)

        new_point[0] = max(new_point[0], min_soc_perc)
        new_point[0] = min(new_point[0], max_soc_perc)
        new_point[1] = new_point[1] - new_point[1] % price_step_size
        new_point[2] = original_point[2]
        return new_point[0], new_point[1], new_point[2]

    def generate_new_point(self, new_point, original_point, other_point, pair_params):
        for j in range(2):
            new_point[j] = int(min(original_point[j], other_point[j]) + 0.5 * abs(original_point[j] - other_point[j]))
        return new_point

    def mutate_individual(self, mutate_params):
        try:
            strategy_price_step_size = mutate_params['strategy_price_step_size']
        except KeyError:
            strategy_price_step_size = 5

        original_charge = self.value.charge_points
        original_discharge = self.value.discharge_points

        new_individual = PointBasedStrategy(name=f'Mutated {self.value.name}', price_step_size=strategy_price_step_size)
        for i in range(len(original_charge)):
            original_charge_point = original_charge[i]
            original_discharge_point = original_discharge[i]
            new_individual.add_point(self.mutate_point(original_charge_point, mutate_params))
            new_individual.add_point(self.mutate_point(original_discharge_point, mutate_params))

        new_individual.sort_and_fix_points()
        new_individual.upload_strategy()
        return new_individual

    def mutate_point(self, original_point, mutate_params):
        try:
            strategy_price_step_size = mutate_params['strategy_price_step_size']
        except KeyError:
            strategy_price_step_size = 5

        try:
            soc_lower = mutate_params['soc_lower']
            soc_upper = mutate_params['soc_upper']
        except KeyError:
            soc_lower = 0
            soc_upper = 0

        try:
            charge_price_lower = mutate_params['charge_price_lower']
            charge_price_upper = mutate_params['charge_price_upper']
        except KeyError:
            charge_price_lower = 0
            charge_price_upper = 0

        try:
            discharge_price_lower = mutate_params['discharge_price_lower']
            discharge_price_upper = mutate_params['discharge_price_upper']
        except KeyError:
            discharge_price_lower = 0
            discharge_price_upper = 0

        new_point = [None, None, original_point[2]]
        if original_point[0] == 95:
            new_point[0] = original_point[0]
        else:
            new_point[0] = original_point[0] + random.randint(soc_lower, soc_upper)

        if new_point[0] >= 95:
            new_point[0] = 95
        if new_point[0] <= 0:
            new_point[0] = 1

        if original_point[2] == 'CHARGE':
            new_point[1] = original_point[1] + \
                           random.randint(charge_price_lower, charge_price_upper) * strategy_price_step_size
        elif original_point[2] == 'DISCHARGE':
            new_point[1] = original_point[1] + \
                           random.randint(discharge_price_lower, discharge_price_upper) * strategy_price_step_size
        return new_point[0], new_point[1], new_point[2]

    def set_fitness(self, fitness_value):
        self.fitness = fitness_value

    def _random_init(self, init_params):
        try:
            seed = init_params['seed']
        except KeyError:
            seed = None

        try:
            strategy_price_step_size = init_params['strategy_price_step_size']
        except KeyError:
            strategy_price_step_size = 5

        # return RandomStrategyGenerator.generate_random_discharge_relative_strategy(
        #     number_of_points=init_params['number_of_points'],
        #     strategy_price_step_size=strategy_price_step_size,
        #     seed=seed, flag_visualise=False)

        return RandomStrategyGenerator.generate_fully_random_strategy(
            number_of_points=init_params['number_of_points'],
            strategy_price_step_size=strategy_price_step_size,
            seed=seed)

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
    price_step_size = 5

    init_params = {
        'number_of_points': 4,
        'strategy_price_step_size': price_step_size
    }
    pair_params = {
        'strategy_price_step_size': price_step_size
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
