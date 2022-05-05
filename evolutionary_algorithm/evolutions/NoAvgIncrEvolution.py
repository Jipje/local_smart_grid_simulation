from evolutionary_algorithm.Evolution import Evolution


class NoAvgIncrEvolution(Evolution):
    def __init__(self, pool_size, fitness, individual_class, n_offsprings, pair_params, mutate_params, init_params,
                 offspring_per_couple=1, mutation_possibility=0.2):
        super().__init__(pool_size, fitness, individual_class, n_offsprings, pair_params, mutate_params, init_params,
                         offspring_per_couple, mutation_possibility)

    def early_end(self):
        res = False

        best_performing = self.pool.individuals[-1].fitness
        worst_performing = self.pool.individuals[0].fitness
        if worst_performing / best_performing * 100 >= 99:
            print('\tToo little variation in population')
            res = True

        if res:
            self.strike_counter += 1
            if not self.strike_counter > self.strike_out:
                res = False

        return res
