import random

from evolutionary_algorithm.Population import Population


class TournamentSelectionPopulation(Population):
    def __init__(self, size, fitness, individual_class, init_params, tournament_size):
        super().__init__(size, fitness, individual_class, init_params)
        self.tournament_size = tournament_size

    def get_parents(self, n_offsprings):
        pop_max_index = len(self.individuals) - 1
        selection = []

        while len(selection) < 2 * n_offsprings:

            best = self.individuals[random.randint(0, pop_max_index)]
            for _ in range(self.tournament_size - 1):
                contestant = self.individuals[random.randint(0, pop_max_index)]
                if contestant.fitness < best.fitness:
                    best = contestant

            selection.append(best)

        mothers = selection[:n_offsprings]
        fathers = selection[n_offsprings:]

        return mothers, fathers
