import random

from evolutionary_algorithm.Population import Population


class TournamentSelectionPopulation(Population):
    def __init__(self, size, fitness, individual_class, init_params, tournament_size, n_offspring):
        super().__init__(size, fitness, individual_class, init_params)
        self.tournament_size = tournament_size
        self.n_offspring = n_offspring

    def get_parents(self, n_offsprings):
        pop_max_index = len(self.individuals) - 1
        selection = []
        mothers = []
        fathers = []

        while len(selection) < 2 * self.n_offspring:

            best = self.individuals[random.randint(0, pop_max_index)]
            for _ in range(self.tournament_size - 1):
                contestant = self.individuals[random.randint(0, pop_max_index)]
                if contestant.fitness < best.fitness:
                    best = contestant

            selection.append(best)

        mothers = selection[:self.n_offspring]
        fathers = selection[self.n_offspring:]

        return mothers, fathers
