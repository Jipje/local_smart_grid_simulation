import unittest

from evolutionary_algorithm.Population import Population
from evolutionary_algorithm.fitness_functions.TestFitness import TestFitness
from evolutionary_algorithm.individuals.IndividualMiddleAndMutate import IndividualMiddleAndMutate


class TestPopulations(unittest.TestCase):
    def test_normal_population(self):
        fit_class = TestFitness()
        ind_class = IndividualMiddleAndMutate
        pop_size = 5

        pop = Population(pop_size, fit_class.fitness, ind_class, {'number_of_points': 4})
        self.assertEqual(pop_size, len(pop.individuals))

    def test_sorted_population(self):
        fit_class = TestFitness()
        ind_class = IndividualMiddleAndMutate
        pop_size = 5

        pop = Population(pop_size, fit_class.fitness, ind_class, {'number_of_points': 4})

        best_individual = pop.individuals[-1]
        worst_individual = pop.individuals[0]
        self.assertTrue(best_individual.fitness >= worst_individual.fitness)

    def test_get_parents(self):
        fit_class = TestFitness()
        ind_class = IndividualMiddleAndMutate
        pop_size = 5

        pop = Population(pop_size, fit_class.fitness, ind_class, {'number_of_points': 4})

        num_of_partners = 2
        mums, dads = pop.get_parents(num_of_partners)
        self.assertEqual(num_of_partners, len(mums))
        self.assertEqual(num_of_partners, len(dads))

        worst_individual = pop.individuals[0]
        self.assertTrue(mums[-1].fitness >= worst_individual.fitness)
        self.assertTrue(dads[-1].fitness >= worst_individual.fitness)

    def test_replace(self):
        fit_class = TestFitness()
        ind_class = IndividualMiddleAndMutate
        pop_size = 5

        pop = Population(pop_size, fit_class.fitness, ind_class, {'number_of_points': 4})
        org_worst = pop.individuals[0].fitness

        new_pop = Population(pop_size, fit_class.fitness, ind_class, {'number_of_points': 4})
        new_worst = new_pop.individuals[0].fitness

        pop.replace(new_pop.individuals)

        self.assertEqual(pop_size, len(pop.individuals))
        best_individual = pop.individuals[-1].fitness
        worst_individual = pop.individuals[0].fitness
        self.assertTrue(best_individual >= worst_individual)

        current_worst = pop.individuals[0].fitness
        self.assertTrue(current_worst >= org_worst or current_worst >= new_worst)


if __name__ == '__main__':
    unittest.main()
