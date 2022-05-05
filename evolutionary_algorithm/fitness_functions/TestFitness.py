class TestFitness(object):
    def __init__(self):
        self.name = 'I am a test'

    def fitness(self, individual):
        if individual.fitness is not None:
            return individual.fitness

        fitness_value = 0
        random_strat = individual.value
        for point in random_strat.charge_points:
            fitness_value += point[1]
        for point in random_strat.discharge_points:
            fitness_value -= point[1]
        individual.set_fitness(fitness_value)
        return fitness_value
