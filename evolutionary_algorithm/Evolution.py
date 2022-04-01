from evolutionary_algorithm.Population import Population


class Evolution:
    def __init__(self, pool_size, fitness, individual_class, n_offsprings, pair_params, mutate_params, init_params):
        self.pair_params = pair_params
        self.mutate_params = mutate_params
        self.pool = Population(pool_size, fitness, individual_class, init_params)
        self.n_offsprings = n_offsprings

        assert pool_size >= (2 * n_offsprings)

        self.previous_average = None
        self.total_steps = 0
        self.strike_one = False

    def step(self):
        mothers, fathers = self.pool.get_parents(self.n_offsprings)
        offsprings = []

        for mother, father in zip(mothers, fathers):
            offspring = mother.pair(father, self.pair_params)
            offspring = offspring.mutate(self.mutate_params)
            offsprings.append(offspring)

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
            if not self.strike_one:
                self.strike_one = res
                res = False

        return res

    def report(self):
        best_performing_individual = self.pool.individuals[-1]

        total_fitness = 0
        for individual in self.pool.individuals:
            total_fitness += individual.fitness
        average_fitness = total_fitness / len(self.pool.individuals)

        msg = f'Generation {self.total_steps}: ' \
              f'Best individual {best_performing_individual.fitness}. ' \
              f'Average fitness: {average_fitness}'
        # print(best_performing_individual)
        print(msg)
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
