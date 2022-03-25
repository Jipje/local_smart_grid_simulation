from evolutionary_algorithm.Population import Population


class Evolution:
    def __init__(self, pool_size, fitness, individual_class, n_offsprings, pair_params, mutate_params, init_params):
        self.pair_params = pair_params
        self.mutate_params = mutate_params
        self.pool = Population(pool_size, fitness, individual_class, init_params)
        self.n_offsprings = n_offsprings
        self.previous_best = None

    def step(self):
        mothers, fathers = self.pool.get_parents(self.n_offsprings)
        offsprings = []

        for mother, father in zip(mothers, fathers):
            offspring = mother.pair(father, self.pair_params)
            offspring.mutate(self.mutate_params)
            offsprings.append(offspring)

        self.pool.replace(offsprings)

    def early_end(self):
        res = False

        best_performing = self.pool.individuals[0].fitness
        worst_performing = self.pool.individuals[-1].fitness
        if worst_performing / best_performing * 100 >= 95:
            res = True

        if self.previous_best is not None:
            if self.previous_best / best_performing * 100 >= 95:
                res = True

        self.previous_best = best_performing

        return res
