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
        filename = '../../data/ea_runs/different_mutations/FixedNormalDistBigMutationWithSort.csv'

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
        filename = '../../data/ea_runs/different_mutations/FixedNormalDistBigMutationWithSort.csv'
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


def visualise_ea_runs(filenames=None, title_file=None):
    if filenames is None:
        filenames = ['../../data/different_mutations/RandomNormalDistBigMutationWithSort.csv',
                     '../../data/different_mutations/RandomNormalDistBigMutation.csv',
                     '../../data/different_mutations/RandomNormalDistSmallMutation.csv']
    if title_file is None:
        title_file = filenames[0].split('/')[-1].split('Big')[0]

    legend_names = []
    for filename in filenames:
        legend_names.append(filename.split('/')[-1])

    all_dicts = []

    baseline_color = (0.11, 0.91, 0.99, 1)
    month_optimized = (0.43, 0.92, 0.51, 1)
    month_conservative = (0.07, 0.66, 0.91, 1)
    color_4 = (0.99, 0.35, 0.39, 1)

    colors = [baseline_color, month_optimized, month_conservative, color_4]

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
    plt.legend(own_lines, legend_names)

    plt.show()


def visualise_month_ea_runs(source_folder='../../data/ea_runs/random_init_first_runs/',
                            title='Random initialized Evolutionary Algorithm runs'):
    baseline_color = (0.64, 0.26, 0.75, 0.85)
    run_color = (0.26, 0.62, 0.75, 0.65)
    month_optimized = (0.75, 0.26, 0.62, 0.85)
    month_conservative = (0.75, 0.26, 0.37, 0.85)

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

        axs[axes_x, axes_y].set_title(f'{month_name}')
        axs[axes_x, axes_y].axhline(month_earn_money_earnings[month - 1], 0, max_generations, color=baseline_color, ls=':')
        axs[axes_x, axes_y].axhline(month_monthly_optimized[month - 1], 0, max_generations, color=month_optimized, ls=':')
        axs[axes_x, axes_y].axhline(month_monthly_conservative[month - 1], 0, max_generations, color=month_conservative, ls=':')
        axs[axes_x, axes_y].set_ylim((15000, 170000))

    for ax in axs.flat:
        ax.set(xlabel='Generation', ylabel='Fitness (Total EUR)')
        ax.label_outer()

    own_lines = [
        Line2D([0], [0], color=baseline_color, ls=':', lw=2),
        Line2D([0], [0], color=run_color, lw=2),
        Line2D([0], [0], color=run_color, ls='--', lw=2),
        Line2D([0], [0], color=month_optimized, ls=':', lw=2),
        Line2D([0], [0], color=month_conservative, ls=':', lw=2)
    ]
    plt.legend(own_lines, ['Pure Earn Money', 'Elite of generation',
                           'Average of generation', 'Monthly optimized timings', 'Monthly conservative timings'])

    fig.suptitle(title)
    plt.show()


def visualise_single_month_ea_run(source_folder='../../data/random_init_first_runs/', month=None, suffix=None,
                                  extra_title=None):
    baseline_color = (0.64, 0.26, 0.75, 0.85)
    run_color = (0.26, 0.62, 0.75, 0.65)
    month_optimized = (0.75, 0.26, 0.62, 0.85)
    month_conservative = (0.75, 0.26, 0.37, 0.85)

    if month is None:
        months = range(1, 13)
    else:
        assert 1 <= month <= 12
        months = [month]

    for month in months:
        month_name = month_filenames[month - 1]
        if suffix is not None:
            filename = source_folder + month_name + suffix + '.csv'
        else:
            filename = source_folder + month_name + '.csv'
        month_dict, num_of_runs = convert_file_into_dict(filename)

        max_generations = -1
        for i in range(num_of_runs):
            plt.plot(month_dict[f'run_{i}_best_individual'], color=run_color, ls='-')
            plt.plot(month_dict[f'run_{i}_avg_individual'], color=run_color, ls='--')
            if len(month_dict[f'run_{i}_avg_individual']) > max_generations:
                max_generations = len(month_dict[f'run_{i}_avg_individual'])

        plt.axhline(month_earn_money_earnings[month - 1], 0, max_generations, color=baseline_color, ls=':')
        plt.axhline(month_monthly_optimized[month - 1], 0, max_generations, color=month_optimized, ls=':')
        plt.axhline(month_monthly_conservative[month - 1], 0, max_generations, color=month_conservative, ls=':')

        plt.xlabel('Generation')
        plt.ylabel('Fitness (Total EUR)')
        title = f'EA runs for {month_name}'
        if extra_title is not None:
            title = title + '\n' + extra_title
        plt.title(title)

        own_lines = [
            Line2D([0], [0], color=baseline_color, ls=':', lw=2),
            Line2D([0], [0], color=run_color, lw=2),
            Line2D([0], [0], color=run_color, ls='--', lw=2),
            Line2D([0], [0], color=month_optimized, ls=':', lw=2),
            Line2D([0], [0], color=month_conservative, ls=':', lw=2)
        ]
        plt.legend(own_lines, ['Pure Earn Money', 'Elite of generation',
                               'Average of generation', 'Monthly optimized timings', 'Monthly conservative timings'])

        plt.show()


if __name__ == '__main__':
    # visualise_ea_run(filename='../../data/first_ea_runs/april.csv')
    filenames_0 = ['../../data/ea_runs/different_mutations/RandomNormalDistBigMutationWithSort.csv',
                 '../../data/ea_runs/different_mutations/RandomNormalDistBigMutation.csv',
                 '../../data/ea_runs/different_mutations/RandomNormalDistSmallMutation.csv']
    filenames_1 = ['../../data/ea_runs/different_mutations/FixedNormalDistBigMutationWithSort.csv',
                 '../../data/ea_runs/different_mutations/FixedNormalDistBigMutation.csv',
                 '../../data/ea_runs/different_mutations/FixedNormalDistSmallMutation.csv']
    filenames_2 = ['../../data/ea_runs/different_mutations/MiddleBigMutationWithSort.csv',
                 '../../data/ea_runs/different_mutations/MiddleBigMutation.csv',
                 '../../data/ea_runs/different_mutations/MiddleSmallMutation.csv']
    filenames_3 = ['../../data/ea_runs/different_mutations/IndividualMutateNormalDistBigMutationWithSort.csv',
                   '../../data/ea_runs/different_mutations/IndividualMutateNormalDistBigMutation.csv',
                   '../../data/ea_runs/different_mutations/IndividualMutateNormalDistSmallMutation.csv']
    filenames_4 = ['../../data/ea_runs/different_mutations/RandomNormalDistBigMutation.csv',
                   '../../data/ea_runs/different_mutations/FixedNormalDistBigMutation.csv',
                   '../../data/ea_runs/different_mutations/MiddleBigMutation.csv',
                   '../../data/ea_runs/different_mutations/IndividualMutateNormalDistBigMutation.csv']
    filenames_5 = ['../../data/ea_runs/fixed_normal_dist/FixedUniformDistBigMutation.csv',
                   '../../data/ea_runs/fixed_normal_dist/MiddleBigMutation.csv',
                   '../../data/ea_runs/fixed_normal_dist/MutateNormalDistBigMutation.csv',
                   '../../data/ea_runs/fixed_normal_dist/RandomNormalDistBigMutation.csv']
    filesnames_6 = ['../../data/ea_runs/fixed_normal_dist/MutateNormalDistBigMutation.csv',
                    '../../data/ea_runs/fixed_normal_dist/MutateNormalDistSmallMutation.csv',
                    '../../data/ea_runs/fixed_normal_dist/RandomNormalDistBigMutation.csv',
                    '../../data/ea_runs/fixed_normal_dist/RandomNormalDistSmallMutation.csv']
    filenames_7 = ['../../data/ea_runs/offspring_ratio/april_10off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/april_25off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/april_40off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/april_75off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/april_90off_100pop.csv']
    filenames_8 = ['../../data/ea_runs/offspring_ratio/november_10off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/november_25off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/november_40off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/november_75off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/november_90off_100pop.csv']
    filenames_9 = ['../../data/ea_runs/offspring_ratio/march_10off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/march_25off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/march_40off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/march_50off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/march_75off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/march_90off_100pop.csv',
                   '../../data/ea_runs/offspring_ratio/march_100off_1000pop.csv',
                   '../../data/ea_runs/offspring_ratio/march_250off_1000pop.csv',
                   '../../data/ea_runs/offspring_ratio/march_400off_1000pop.csv']
    filenames_all = [filenames_0, filenames_1, filenames_2,
                     filenames_3, filenames_4, filenames_5,
                     filesnames_6, filenames_7, filenames_8,
                     filenames_9]
    titles = [None, None, None,
              None,
              'Guided Initialisation. Uniform Dist. Big Mutation.\nDifferent (Uniform dist based) pairing methods',
              'Random Initialisation Different Pairing Methods', None,
              'Offspring ratio investigation April', 'Offspring ratio investigation November',
              'Offspring ratio investigation March']
    for i in range(len(filenames_all)):
        filenames = filenames_all[i]
        title = titles[i]
        visualise_ea_runs(filenames, title)
    visualise_month_ea_runs()
    visualise_month_ea_runs(source_folder='../../data/ea_runs/first_ea_runs/', title='Initial Evolutionary Algorithm Runs')

    # GIGA BASELINE RUNS
    visualise_single_month_ea_run(source_folder='../../data/ea_runs/giga_baseline/', month=3, extra_title='Pure money 100 Pop')
    visualise_single_month_ea_run(source_folder='../../data/ea_runs/giga_baseline/', month=3, suffix='_30', extra_title='Pure money 30 Pop')
    visualise_single_month_ea_run(source_folder='../../data/ea_runs/giga_baseline/', month=4, extra_title='Pure money 100 Pop')
    visualise_single_month_ea_run(source_folder='../../data/ea_runs/giga_baseline/', month=4, suffix='_30', extra_title='Pure money 30 Pop')
    visualise_single_month_ea_run(source_folder='../../data/ea_runs/giga_baseline/', month=12, extra_title='Pure money 100 Pop')
    visualise_single_month_ea_run(source_folder='../../data/ea_runs/giga_baseline/', month=12, suffix='_30', extra_title='Pure money 30 Pop')
