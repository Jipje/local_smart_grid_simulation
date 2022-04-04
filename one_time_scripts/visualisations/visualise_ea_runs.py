import random

import matplotlib.pyplot as plt
import csv

from matplotlib.lines import Line2D


def convert_file_into_dict(filename=None):
    if filename is None:
        filename = '../../data/different_mutations/FixedNormalDistBigMutationWithSort.csv'

    with open(filename) as csv_file:
        csv_reader = csv.reader(csv_file)
        res_dict = {}
        best_individuals_this_run = []
        average_fitness_this_run = []
        last_generation = 0
        run = 0

        header = True
        for row in csv_reader:
            if header:
                header = False
                continue
            generation = int(row[0])
            best_individual = float(row[1])
            average_fitness = float(row[2])

            if generation < last_generation and generation == 1 and last_generation != 0:
                res_dict[f'run_{run}_best_individual'] = best_individuals_this_run
                res_dict[f'run_{run}_avg_individual'] = average_fitness_this_run

                best_individuals_this_run = []
                average_fitness_this_run = []
                run = run + 1

            best_individuals_this_run.append(best_individual)
            average_fitness_this_run.append(average_fitness)
            last_generation = generation
        res_dict[f'run_{run}_best_individual'] = best_individuals_this_run
        res_dict[f'run_{run}_avg_individual'] = average_fitness_this_run
        return res_dict, run + 1


def visualise_ea_run(filename=None):
    if filename is None:
        filename = '../../data/different_mutations/FixedNormalDistBigMutationWithSort.csv'

    res_dict, num_of_runs = convert_file_into_dict(filename)
    colors = []

    for i in range(num_of_runs):
        colors.append('#%06X' % random.randint(0, 0xFFFFFF))

    for i in range(num_of_runs):
        color = colors[i]
        plt.plot(res_dict[f'run_{i}_best_individual'], color=color, ls='-')
        plt.plot(res_dict[f'run_{i}_avg_individual'], color=color, ls='--')
    plt.title('Performance of 5 different runs with:')
    plt.xlabel('Generation')
    plt.ylabel('Performance (Total EUR)')
    plt.show()


def visualise_ea_runs(filenames=None):
    if filenames is None:
        filenames = ['../../data/different_mutations/RandomNormalDistBigMutationWithSort.csv',
                     '../../data/different_mutations/RandomNormalDistBigMutation.csv',
                     '../../data/different_mutations/RandomNormalDistSmallMutation.csv']

    all_dicts = []
    colors = []
    for filename in filenames:
        res_dict, num_of_runs = convert_file_into_dict(filename)
        all_dicts.append((res_dict, num_of_runs))

        colors.append('#%06X' % random.randint(0, 0xFFFFFF))

    for i in range(len(all_dicts)):
        color = colors[i]
        res_dict = all_dicts[i][0]

        avg_best_individual = []
        avg_avg_individual = []
        avg_tracker = []
        for j in range(all_dicts[i][1]):
            arr_of_best_individuals = res_dict[f'run_{j}_best_individual']
            arr_of_avg_individuals = res_dict[f'run_{j}_avg_individual']

            plt.plot(arr_of_best_individuals, color=color, ls='-', alpha=0.2)
            plt.plot(arr_of_avg_individuals, color=color, ls='--', alpha=0.2)

            for k in range(len(arr_of_best_individuals)):
                if len(avg_avg_individual) <= k:
                    avg_best_individual.append(arr_of_best_individuals[k])
                    avg_avg_individual.append(arr_of_avg_individuals[k])
                    avg_tracker.append(1)
                else:
                    avg_best_individual[k] = avg_best_individual[k] + arr_of_best_individuals[k]
                    avg_avg_individual[k] = avg_avg_individual[k] + arr_of_avg_individuals[k]
                    avg_tracker[k] = avg_tracker[k] + 1

        for k in range(len(avg_best_individual)):
            avg_best_individual[k] = avg_best_individual[k] / avg_tracker[k]
            avg_avg_individual[k] = avg_avg_individual[k] / avg_tracker[k]

        plt.plot(avg_best_individual, color=color, ls='-')
        plt.plot(avg_avg_individual, color=color, ls='--')

    plt.title('Performance runs with:')
    plt.xlabel('Generation')
    plt.ylabel('Performance (Total EUR)')

    own_lines = []
    for i in range(len(all_dicts)):
        own_lines.append(Line2D([0], [0], color=colors[i], lw=2))
    plt.legend(own_lines, filenames)

    plt.show()


if __name__ == '__main__':
    # visualise_ea_run()
    visualise_ea_runs()

