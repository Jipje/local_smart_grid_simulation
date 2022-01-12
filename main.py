from csv import reader

from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from network_objects.Battery import Battery
from environment.ImbalanceEnvironment import ImbalanceEnvironment
from network_objects.decorators.LimitedChargeOrDischargeCapacity import LimitedChargeOrDischargeCapacity
from network_objects.WindFarm import WindFarm
import os
import random
import datetime as dt

base_scenario = 'data{0}tennet_and_windnet{0}tennet_balans_delta_and_trivial_windnet.csv'.format(os.path.sep)


def run_random_thirty_days(scenario=base_scenario, verbose_lvl=2, simulation_environment=None):
    start_day = random.randint(0, 333)
    starting_timestep = start_day * 24 * 60
    number_of_steps = 30 * 24 * 60
    print('Random thirty days - Starting timestep: {} - Number of Steps: {}'.format(starting_timestep, number_of_steps))
    run_simulation(starting_timestep, number_of_steps, scenario=scenario, verbose_lvl=verbose_lvl, simulation_environment=simulation_environment)
    print('Just ran random thirty days.- Starting timestep: {} - Number of Steps: {}'.format(starting_timestep, number_of_steps))


def run_full_scenario(scenario=base_scenario, verbose_lvl=1, simulation_environment=None):
    starting_timestep = 0
    with open(scenario) as file:
        number_of_steps = len(file.readlines()) + 1
    print('Running full scenario {}'.format(scenario))
    run_simulation(starting_timestep, number_of_steps, scenario=scenario, verbose_lvl=verbose_lvl, simulation_environment=simulation_environment)
    print('Just ran full scenario {}\n'.format(scenario))


def run_simulation(starting_time_step=0, number_of_steps=100, scenario=base_scenario, verbose_lvl=3, simulation_environment=None):
    if simulation_environment is None:
        simulation_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
        ImbalanceEnvironment(simulation_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
        rhino = Battery('Rhino', 7500, 12000, battery_strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv',battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
        simulation_environment.add_object(rhino, [1, 3])

    # open file in read mode
    with open(scenario, 'r') as read_obj:
        csv_reader = reader(read_obj)

        steps_taken = 0
        old_day = 0
        old_month = 0

        # Open the scenario
        for environment_data in csv_reader:
            if starting_time_step >= 0:  # Skip lines until we reach the starting step.
                starting_time_step = starting_time_step - 1
            else:
                # Figure out date of the data
                time_step_dt = dt.datetime.strptime(environment_data[0], '%Y-%m-%d %H:%M:%S%z')
                time_step_dt = time_step_dt.astimezone(tz=dt.timezone.utc)
                time_step_string = time_step_dt.strftime('%H:%M %d-%m-%Y UTC')

                # Announce start of simulation
                if steps_taken == 0 and verbose_lvl >= 0:
                    print('Starting simulation from PTU {}'.format(time_step_string))

                # Give an update of how it is going in the mean_time
                curr_month = time_step_dt.month
                curr_day = time_step_dt.day
                if curr_day != old_day and verbose_lvl > 1 or curr_month != old_month and verbose_lvl > 0:
                    msg = time_step_string[6:-4] + '\n\t' + simulation_environment.done_in_mean_time()
                    print(msg)
                    old_day = curr_day
                    old_month = curr_month

                # End simulation here if number of steps have been taken.
                if steps_taken >= number_of_steps:  # If we reach our maximum amount of steps. Stop the simulation
                    break
                else:
                    # Otherwise, ensure data of enviroment steps is correct
                    try:
                        if environment_data[1] == 'nan':
                            raise ValueError
                        environment_data[2] = float(environment_data[2])
                        environment_data[1] = float(environment_data[1])
                        environment_data[3] = float(environment_data[3])
                        environment_data[5] = float(environment_data[5])
                        environment_data[7] = float(environment_data[7])
                    except ValueError:
                        if verbose_lvl > 2:
                            print("Skipping timestep {} as data is missing".format(time_step_string))
                        continue
                    # The environment should take a step here.
                    simulation_environment.take_step(environment_data)

                # Update steps taken
                steps_taken = steps_taken + 1

        # Print information at the end of the simulation.
        if verbose_lvl >= 0:
            print('End of simulation, final PTU: {}'.format(time_step_string))

    print(simulation_environment.end_of_environment_message())
    # num_of_days = int(steps_taken / 60 / 24)
    # print('Number of 1m timesteps: {}\nNumber of PTUs: {}\nNumber of days: {}'.format(steps_taken, steps_taken / 15, num_of_days))
    # for network_object in simulation_environment.network_objects:
    #     print(network_object)
    #     if num_of_days != 0:
    #         earnings_per_day = round(network_object.earnings / num_of_days, 2)
    #         print('Average earnings per day: {}'.format(earnings_per_day))
    #         try:
    #             cycles_per_day = round(network_object.cycle_counter.cycle_count / num_of_days, 2)
    #             print('Average cycles per day: {}'.format(cycles_per_day))
    #         except:
    #             pass


def network_capacity_windnet_simulation(network_capacity=25000, verbose_lvl=1):
    # Setup environment
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, network_capacity)

    windnet = WindFarm('Windnet', 23000, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(windnet, [1, 3, 7])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv', simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def baseline_rhino_simulation(verbose_lvl=1):
    # Baseline Rhino simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    rhino = Battery('Rhino', 7500, 12000,
                    battery_strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv',
                    battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(rhino, [1, 3])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=1)


def rhino_with_limited_charging(verbose_lvl=1):
    # Rhino with limited charging simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    rhino = Battery('Rhino', 7500, 12000,
                    battery_strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv',
                    battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
    LimitedChargeOrDischargeCapacity(rhino, 5, -1)
    imbalance_environment.add_object(rhino, [1, 3])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def baseline_windnet(verbose_lvl=1):
    # Baseline Windnet simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    windnet = WindFarm('Windnet', 23000, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(windnet, [1, 3, 7])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def windnet_with_ppa(verbose_lvl=1):
    # Windnet with a PPA simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    windnet = WindFarm('Windnet', 23000, verbose_lvl=verbose_lvl, ppa=40)
    imbalance_environment.add_object(windnet, [1, 3, 7])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=1)


if __name__ == '__main__':
    verbose_lvl = 1

    # baseline_rhino_simulation(verbose_lvl)
    # rhino_with_limited_charging(verbose_lvl)
    # baseline_windnet(verbose_lvl)
    # windnet_with_ppa(verbose_lvl)

    network_capacity_windnet_simulation(20000)
