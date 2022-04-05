import random

import matplotlib.pyplot as plt
import csv

from matplotlib.lines import Line2D

month_filenames = ['january', 'february', 'march', 'april',
                   'may', 'june', 'july', 'august',
                   'september', 'october', 'november', 'december']

month_earn_money_earnings = [130500.87, 107192.03, 142600.56,
                             109017.08, 156271.58, 104721.36,
                             114247.94, 139900.91, 42786.29,
                             61004.36, 19284.03, 16843.24]

month_yearly_conservative = [8933.13, 8811.59, 31063.05,
                             35778.22, 33732.25, 59726.94,
                             27623.87, 26580.90, 7583.99,
                             11982.21, 3436.14, 10799.56]

month_monthly_conservative = [124241.32, 84140.65, 66311.19,
                              50313.49, 39865.07, 62377.17,
                              29378.14, 30846.15, 9692.89,
                              23074.21, 20071.13, 16862.47]

month_monthly_optimized = [124241.32, 98744.28, 101843.76,
                           50753.54, 39487.02, 61665.89,
                           31980.34, 38298.46, 12016.82,
                           40636.44, 20071.13, 16862.47]


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
    title_file = filename.split('/')[-1]

    res_dict, num_of_runs = convert_file_into_dict(filename)
    base_color = (0.26, 0.62, 0.75, 1)
    colors = []

    for i in range(num_of_runs):
        colors.append('#%06X' % random.randint(0, 0xFFFFFF))

    max_generations = -1
    for i in range(num_of_runs):
        color = colors[i]
        plt.plot(res_dict[f'run_{i}_best_individual'], color=color, ls='-', alpha=0.75)
        plt.plot(res_dict[f'run_{i}_avg_individual'], color=color, ls='--', alpha=0.75)
        if len(res_dict[f'run_{i}_avg_individual']) > max_generations:
            max_generations = len(res_dict[f'run_{i}_avg_individual'])

    for i in range(len(month_filenames)):
        month_name = month_filenames[i]
        if month_name in filename:
            plt.hlines(month_earn_money_earnings[i], 0, max_generations, color=base_color, ls=':')
            plt.hlines(month_monthly_optimized[i], 0, max_generations, color=base_color, ls=':')
            plt.hlines(month_monthly_conservative[i], 0, max_generations, color=base_color, ls=':')
            break

    plt.title(f'Performance of 5 runs {title_file}')
    plt.xlabel('Generation')
    plt.ylabel('Performance (Total EUR)')
    plt.show()


def visualise_ea_runs(filenames=None):
    if filenames is None:
        filenames = ['../../data/different_mutations/RandomNormalDistBigMutationWithSort.csv',
                     '../../data/different_mutations/RandomNormalDistBigMutation.csv',
                     '../../data/different_mutations/RandomNormalDistSmallMutation.csv']
    title_file = filenames[0].split('/')[-1].split('Big')[0]

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

    plt.title(f'Performance runs with {title_file}')
    plt.xlabel('Generation')
    plt.ylabel('Performance (Total EUR)')

    own_lines = []
    for i in range(len(all_dicts)):
        own_lines.append(Line2D([0], [0], color=colors[i], lw=2))
    plt.legend(own_lines, filenames)

    plt.show()


def visualise_month_ea_runs():
    source_folder = '../../data/first_ea_runs/'
    baseline_color = (0.64, 0.26, 0.75, 0.85)
    run_color = (0.26, 0.62, 0.75, 1)

    fig, axs = plt.subplots(4, 3, figsize=(12, 9))
    for month in range(1, 13):
        if month in [1, 4, 7, 10]:
            axes_y = 0
        elif month in [2, 5, 8, 11]:
            axes_y = 1
        else:
            axes_y = 2

        axes_x = None
        for j in range(1, 5):
            if month <= (j * 3):
                axes_x = j - 1
                break

        month_name = month_filenames[month - 1]
        filename = source_folder + month_name + '.csv'
        month_dict, num_of_runs = convert_file_into_dict(filename)

        max_generations = -1
        for i in range(num_of_runs):
            axs[axes_x, axes_y].plot(month_dict[f'run_{i}_best_individual'], color=run_color, ls='-')
            axs[axes_x, axes_y].plot(month_dict[f'run_{i}_avg_individual'], color=run_color, ls='--')
            if len(month_dict[f'run_{i}_avg_individual']) > max_generations:
                max_generations = len(month_dict[f'run_{i}_avg_individual'])

        axs[axes_x, axes_y].axhline(month_earn_money_earnings[month - 1], 0, max_generations, color=baseline_color, ls=':')
        axs[axes_x, axes_y].axhline(month_monthly_optimized[month - 1], 0, max_generations, color=baseline_color, ls=':')
        axs[axes_x, axes_y].axhline(month_monthly_conservative[month - 1], 0, max_generations, color=baseline_color, ls=':')
        axs[axes_x, axes_y].set_ylim((15000, 170000))

    for ax in axs.flat:
        ax.set(xlabel='Generation', ylabel='Fitness (Total EUR)')
        ax.label_outer()
    plt.show()


if __name__ == '__main__':
    # visualise_ea_run(filename='../../data/first_ea_runs/april.csv')
    # filenames = ['../../data/different_mutations/RandomNormalDistBigMutationWithSort.csv',
    #              '../../data/different_mutations/RandomNormalDistBigMutation.csv',
    #              '../../data/different_mutations/RandomNormalDistSmallMutation.csv']
    # filenames = ['../../data/different_mutations/FixedNormalDistBigMutationWithSort.csv',
    #              '../../data/different_mutations/FixedNormalDistBigMutation.csv',
    #              '../../data/different_mutations/FixedNormalDistSmallMutation.csv']
    filenames = ['../../data/different_mutations/MiddleBigMutationWithSort.csv',
                 '../../data/different_mutations/MiddleBigMutation.csv',
                 '../../data/different_mutations/MiddleSmallMutation.csv']
    visualise_ea_runs(filenames)
    # visualise_month_ea_runs()
