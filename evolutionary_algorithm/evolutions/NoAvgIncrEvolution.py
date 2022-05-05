from evolutionary_algorithm.Evolution import Evolution


class NoAvgIncrEvolution(Evolution):
    def __init__(self, pool_size, fitness, individual_class, n_offsprings, pair_params, mutate_params, init_params,
                 offspring_per_couple=1, mutation_possibility=0.2):
        super().__init__(pool_size, fitness, individual_class, n_offsprings, pair_params, mutate_params, init_params,
                         offspring_per_couple, mutation_possibility)
        self.variation = 99
        self.avg_improvement = 99.99
        self.strike_out = 20
