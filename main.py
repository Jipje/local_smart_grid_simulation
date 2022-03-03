from csv import reader

from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from helper_objects.strategies.CsvStrategy import CsvStrategy
from helper_objects.strategies.RandomStrategyGenerator import generate_random_discharge_relative_strategy
from network_objects.Battery import Battery
from network_objects.control_strategies.BatteryControlStrategy import BatteryControlStrategy
from environment.ImbalanceEnvironment import ImbalanceEnvironment
from network_objects.decorators.LimitedChargeOrDischargeCapacity import LimitedChargeOrDischargeCapacity
from network_objects.RenewableEnergyGenerator import RenewableEnergyGenerator
import os
import random
import datetime as dt

base_scenario = 'data{0}tennet_and_windnet{0}tennet_balans_delta_and_trivial_windnet.csv'.format(os.path.sep)


def run_random_thirty_days(scenario=base_scenario, verbose_lvl=2, simulation_environment=None):
    start_day = random.randint(0, 333)
    starting_timestep = start_day * 24 * 60
    number_of_steps = 1 * 24 * 60
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
        csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv')
        rhino = Battery('Rhino', 7500, 12000, strategy=csv_strategy, battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
        simulation_environment.add_object(rhino, [1, 3])

    # open file in read mode
    with open(scenario, 'r') as read_obj:
        csv_reader = reader(read_obj)

        steps_taken = 0
        old_week = 0
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
                curr_week = time_step_dt.isocalendar()[1]
                if curr_week != old_week and verbose_lvl > 1 or curr_month != old_month and verbose_lvl > 0:
                    msg = time_step_string[6:-4] + '\n\t' + simulation_environment.done_in_mean_time()
                    print(msg)
                    old_week = curr_week
                    old_month = curr_month

                # End simulation here if number of steps have been taken.
                if steps_taken >= number_of_steps:  # If we reach our maximum amount of steps. Stop the simulation
                    break
                else:
                    # Otherwise, ensure data of enviroment steps is correct
                    try:
                        if environment_data[1] == 'nan':
                            raise ValueError
                        if scenario.__contains__('windnet'):
                            environment_data[2] = float(environment_data[2])
                            environment_data[1] = float(environment_data[1])
                            environment_data[3] = float(environment_data[3])
                            environment_data[5] = float(environment_data[5])
                            environment_data[7] = float(environment_data[7])
                        elif scenario.__contains__('lelystad'):
                            environment_data[1] = float(environment_data[1])
                            environment_data[2] = float(environment_data[2])
                            environment_data[3] = float(environment_data[3])
                            environment_data[4] = float(environment_data[4])
                            environment_data[5] = None if environment_data[5] == '' else float(environment_data[5])
                            environment_data[6] = None if environment_data[6] == '' else float(environment_data[6])
                            environment_data[7] = None if environment_data[7] == '' else float(environment_data[7])
                            environment_data[8] = None if environment_data[8] == '' else float(environment_data[8])
                            environment_data[9] = None if environment_data[9] == '' else float(environment_data[9])
                            if verbose_lvl > 3:
                                print(f'Running environment step {time_step_string}')
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
        print('----------------------------------------')
        print('End of simulation, final PTU: {}'.format(time_step_string))
        print(simulation_environment.end_of_environment_message(environment_additions=[]))


def network_capacity_windnet_simulation(network_capacity=27000, verbose_lvl=1):
    # Setup environment
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, network_capacity)

    windnet = RenewableEnergyGenerator('Neushoorntocht wind farm', 23000, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(windnet, [1, 3, 5])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv', simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def baseline_rhino_simulation(verbose_lvl=1):
    # Baseline Rhino simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv')
    rhino = Battery('Rhino', 7500, 12000, battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
    simple_strategy_controller = BatteryControlStrategy(name="Rhino Battery Controller", network_object=rhino, strategy=csv_strategy, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(simple_strategy_controller, [1, 3])
    run_full_scenario(scenario='data/environments/lelystad_1_2021.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def rhino_windnet_limited_charging(verbose_lvl=1):
    # Rhino with limited charging simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv')
    rhino = Battery('Rhino', 7500, 12000, battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
    simple_strategy_controller = BatteryControlStrategy(name="Rhino Battery Controller", network_object=rhino,
                                                        strategy=csv_strategy, verbose_lvl=verbose_lvl)

    LimitedChargeOrDischargeCapacity(rhino, 5, -1)

    imbalance_environment.add_object(simple_strategy_controller, [1, 3])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def baseline_windnet(verbose_lvl=1):
    # Baseline Windnet simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    windnet = RenewableEnergyGenerator('Windnet wind farm', 23000, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(windnet, [1, 3, 5])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def baseline_solarvation(verbose_lvl=1):
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(solarvation, [1, 3, 4])
    run_full_scenario(scenario='data/environments/lelystad_1_2021.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def windnet_with_ppa(verbose_lvl=1):
    # Windnet with a PPA simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    windnet = RenewableEnergyGenerator('Windnet wind farm', 23000, verbose_lvl=verbose_lvl, ppa=40)
    imbalance_environment.add_object(windnet, [1, 3, 5])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=1)


def full_rhino_site_capacity(network_capacity=27000, verbose_lvl=1):
    # Rhino and Neushoorntocht with networkcapacity
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, network_capacity)
    csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv')
    rhino = Battery('Rhino', 7500, 12000, battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
    simple_strategy_controller = BatteryControlStrategy(name="Rhino Battery Controller", network_object=rhino,
                                                        strategy=csv_strategy, verbose_lvl=verbose_lvl)

    LimitedChargeOrDischargeCapacity(rhino, 5, -1)

    imbalance_environment.add_object(simple_strategy_controller, [1, 3])
    windnet = RenewableEnergyGenerator('Neushoorntocht wind farm', 23000, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(windnet, [1, 3, 5])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def random_rhino_strategy_simulation(verbose_lvl=1, seed=None):
    # Initialise environment
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)

    # Initialise random strategy
    random_point_based_strategy = generate_random_discharge_relative_strategy(seed=seed)
    random_step_battery = Battery('Random Rhino', 7500, 12000, battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
    simple_strategy_controller = BatteryControlStrategy(name="Random strategy Battery Controller", network_object=random_step_battery,
                                                        strategy=random_point_based_strategy, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(simple_strategy_controller, [1, 3])

    csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv')
    rhino = Battery('Rhino', 7500, 12000, battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
    simple_strategy_controller = BatteryControlStrategy(name="Rhino Battery Controller", network_object=rhino, strategy=csv_strategy, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(simple_strategy_controller, [1, 3])

    run_full_scenario(scenario='data/environments/lelystad_1_2021.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=1)


if __name__ == '__main__':
    verbose_lvl = 1

    baseline_rhino_simulation(verbose_lvl)

    # network_capacity = 14000
    # imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    # ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    # TotalNetworkCapacityTracker(imbalance_environment, network_capacity)
    #
    # solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)
    # battery = Battery('Wombat', 30000, 14000,
    #                   battery_strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv',
    #                   battery_efficiency=0.9, starting_soc_kwh=15000, verbose_lvl=verbose_lvl)
    # imbalance_environment.add_object(solarvation, [1, 3, 4])
    # imbalance_environment.add_object(battery, [1, 3])
    #
    # run_random_thirty_days(scenario='data/environments/lelystad_1_2021.csv', verbose_lvl=verbose_lvl,
    #                        simulation_environment=imbalance_environment)
    #
    random_rhino_strategy_simulation(verbose_lvl=verbose_lvl, seed=4899458002697043430)
