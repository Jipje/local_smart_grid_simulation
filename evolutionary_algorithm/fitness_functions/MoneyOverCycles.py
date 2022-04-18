from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual


class MoneyOverCycles(Fitness):
    def __init__(self, verbose_lvl=-1, transportation_kw=2000, congestion_kw=14000, congestion_safety_margin=0.99):
        super().__init__(verbose_lvl, transportation_kw, congestion_kw, congestion_safety_margin)

    def fitness(self, individual):
        res_dict = self.run_simulation(individual)

        penalty = 1
        if res_dict['time_steps_with_congestion'] > 0:
            penalty = 0.5

        fitness_value = res_dict['wombat_battery_revenue'] / res_dict['wombat_battery_cycles']
        fitness_value = fitness_value * penalty
        individual.set_fitness(fitness_value)
        return fitness_value


if __name__ == '__main__':
    random_individual = StrategyIndividual(init_params={'number_of_points': 4})
    fitness = MoneyOverCycles(verbose_lvl=1)
    fitness.set_month(4)
    print(fitness.fitness(random_individual))
