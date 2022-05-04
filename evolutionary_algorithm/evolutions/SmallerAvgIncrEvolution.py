from evolutionary_algorithm.Evolution import Evolution


class NoAvgIncrEvolution(Evolution):
    def __init__(self, pool_size, fitness, individual_class, n_offsprings, pair_params, mutate_params, init_params):
        super().__init__(pool_size, fitness, individual_class, n_offsprings, pair_params, mutate_params, init_params)

    def early_end(self):
        res = False

        best_performing = self.pool.individuals[-1].fitness
        worst_performing = self.pool.individuals[0].fitness
        if worst_performing / best_performing * 100 >= 90:
            print('\tToo little variation in population')
            res = True

        total_fitness = 0
        for individual in self.pool.individuals:
            total_fitness += individual.fitness
        avg_fitness = total_fitness / len(self.pool.individuals)

        if self.previous_average is not None:
            if self.previous_average / avg_fitness * 100 >= 99.9:
                print('\tToo little average improvement in population')
                res = True

        self.previous_average = avg_fitness

        if res:
            if not self.strike_one:
                self.strike_one = res
                res = False

        return res
