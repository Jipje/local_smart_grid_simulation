import random

from evolutionary_algorithm.populations.TournamentSelectionPopulation import TournamentSelectionPopulation


class Evolution:
    def __init__(self, pool_size, fitness, individual_class, n_offsprings, pair_params, mutate_params, init_params,
                 offspring_per_couple=1, mutation_possibility=0.2):
        self.pair_params = pair_params
        self.mutate_params = mutate_params
        self.pool = TournamentSelectionPopulation(pool_size, fitness, individual_class, init_params, tournament_size=4)
        self.n_offsprings = n_offsprings
        self.offspring_per_couple = offspring_per_couple
        self.mutation_possibility = mutation_possibility

        assert n_offsprings % offspring_per_couple == 0, 'Offsprings per couple and n_offspring should be divisible'

        self.previous_average = None
        self.total_steps = 0
        self.strike_counter = 0
        self.strike_out = 1

    def step(self):
        num_of_partners = int(self.n_offsprings / self.offspring_per_couple)
        mothers, fathers = self.pool.get_parents(num_of_partners)
        offsprings = []

        for mother, father in zip(mothers, fathers):
            for _ in range(self.offspring_per_couple):
                offspring = mother.pair(father, self.pair_params)
                if random.random() > self.mutation_possibility:
                    offspring = offspring.mutate(self.mutate_params)
                offsprings.append(offspring)

        for individual in self.pool.individuals:
            if random.random() > self.mutation_possibility:
                mutated_individual = individual.mutate(self.mutate_params)
                offsprings.append(mutated_individual)

        self.pool.replace(offsprings)
        self.total_steps += 1

    def early_end(self):
        res = False

        best_performing = self.pool.individuals[-1].fitness
        worst_performing = self.pool.individuals[0].fitness
        if worst_performing / best_performing * 100 >= 95:
            print('\tToo little variation in population')
            res = True

        total_fitness = 0
        for individual in self.pool.individuals:
            total_fitness += individual.fitness
        avg_fitness = total_fitness / len(self.pool.individuals)

        if self.previous_average is not None:
            if self.previous_average / avg_fitness * 100 >= 99:
                print('\tToo little average improvement in population')
                res = True

        self.previous_average = avg_fitness

        if res:
            self.strike_counter += 1
            if not self.strike_counter > self.strike_out:
                res = False

        return res

    def report(self):
        best_performing_individual = self.pool.individuals[-1]
        middle_index = int(0.5 * len(self.pool.individuals))
        median_performing_individual = self.pool.individuals[middle_index]

        total_fitness = 0
        for individual in self.pool.individuals:
            total_fitness += individual.fitness
        average_fitness = total_fitness / len(self.pool.individuals)

        msg = f'Generation {self.total_steps}: ' \
              f'Best individual {best_performing_individual.fitness}. ' \
              f'Average fitness: {average_fitness}'

        print(msg)
        # print(best_performing_individual)
        # print(median_performing_individual)
        return msg

    def write_to_csv(self, filename=None):
        if filename is None:
            return None
        best_performing_individual = self.pool.individuals[-1]

        total_fitness = 0
        for individual in self.pool.individuals:
            total_fitness += individual.fitness
        average_fitness = total_fitness / len(self.pool.individuals)

        csv_msg = f'{self.total_steps}, {best_performing_individual.fitness}, {average_fitness}'
        with open(filename, 'a+') as file:
            file.seek(0)
            data = file.read(100)
            if len(data) > 0:
                file.write("\n")
            file.write(csv_msg)
