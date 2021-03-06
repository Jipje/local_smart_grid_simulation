from csv import reader
import os
import random
import datetime as dt
import dateutil.tz
import pandas as pd
from pandas import NaT

from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from helper_objects.congestion_helper.month_congestion_size_and_timer import get_month_congestion_timings
from helper_objects.strategies.CsvStrategy import CsvStrategy
from helper_objects.strategies.DischargeUntilStrategy import DischargeUntilStrategy
from helper_objects.strategies.PointBasedStrategy import PointBasedStrategy
from helper_objects.strategies.RandomStrategyGenerator import generate_random_discharge_relative_strategy
from helper_objects.strategies.giga_baseline_strategies import get_month_strategy
from network_objects.Battery import Battery
from network_objects.control_strategies.ModesOfOperationController import ModesOfOperationController
from network_objects.control_strategies.MonthOfModesOfOperationController import MonthOfModesOfOperationController
from network_objects.control_strategies.SolveCongestionAndLimitedChargeControlTower import \
    SolveCongestionAndLimitedChargeControlTower
from network_objects.control_strategies.StrategyControlTower import StrategyControlTower
from environment.ImbalanceEnvironment import ImbalanceEnvironment
from network_objects.control_strategies.StrategyWithLimitedChargeCapacityControlTower import \
    StrategyWithLimitedChargeCapacityControlTower
from network_objects.control_strategies.SolveCongestionControlTower import \
    SolveCongestionControlTower
from network_objects.RenewableEnergyGenerator import RenewableEnergyGenerator

base_scenario = 'data{0}environments{0}lelystad_1_2021.csv'.format(os.path.sep)
utc = dateutil.tz.tzutc()


def run_random_thirty_days(scenario=base_scenario, verbose_lvl=2, simulation_environment=None):
    start_day = random.randint(0, 333)
    starting_timestep = start_day * 24 * 60
    number_of_steps = 1 * 24 * 60
    print('Random thirty days - Starting timestep: {} - Number of Steps: {}'.format(starting_timestep, number_of_steps))
    res = run_simulation(starting_timestep, number_of_steps, scenario=scenario, verbose_lvl=verbose_lvl, simulation_environment=simulation_environment)
    print('Just ran random thirty days.- Starting timestep: {} - Number of Steps: {}'.format(starting_timestep, number_of_steps))
    return res


def run_single_month(month, scenario=base_scenario, verbose_lvl=2, simulation_environment=None):
    starting_timesteps = [0, 60, 44700, 85020, 129600, 172800, 217440, 260475, 305115, 349755, 392955, 437595, 480795, 525376]
    assert 13 > month > 0

    dt_month = dt.datetime(2021, month, 1)
    month_str = dt_month.strftime('%B %Y')

    starting_timestep = starting_timesteps[month]
    number_of_steps = starting_timesteps[month + 1] - starting_timestep
    print('Run {} - Starting timestep: {} - Number of Steps: {}'.format(month_str, starting_timestep, number_of_steps))
    res = run_simulation(starting_timestep, number_of_steps, scenario=scenario, verbose_lvl=verbose_lvl,
                   simulation_environment=simulation_environment)
    print('Just ran {} - Starting timestep: {} - Number of Steps: {}'.format(month_str, starting_timestep, number_of_steps))
    return res


def run_full_scenario(scenario=base_scenario, verbose_lvl=1, simulation_environment=None):
    starting_timestep = 0
    with open(scenario) as file:
        number_of_steps = len(file.readlines()) + 1
    print('Running full scenario {}'.format(scenario))
    res = run_simulation(starting_timestep, number_of_steps, scenario=scenario, verbose_lvl=verbose_lvl, simulation_environment=simulation_environment)
    print('Just ran full scenario {}\n'.format(scenario))
    return res


def run_simulation(starting_time_step=0, number_of_steps=100, scenario=base_scenario, verbose_lvl=3, simulation_environment=None):
    if simulation_environment is None:
        baseline_rhino_simulation(verbose_lvl=verbose_lvl)

    # open file in read mode
    with open(scenario, 'r') as read_obj:
        csv_reader = reader(read_obj)

        steps_taken = 0
        old_day = 0
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
                environment_data[0] = time_step_dt
                time_step_string = time_step_dt.strftime('%H:%M %d-%m-%Y UTC')

                # Announce start of simulation
                if steps_taken == 0 and verbose_lvl >= 0:
                    print('Starting simulation from PTU {}'.format(time_step_string))

                # Give an update of how it is going in the mean_time
                curr_month = time_step_dt.month
                curr_week = time_step_dt.isocalendar()[1]
                curr_day = time_step_dt.day
                if curr_day != old_day and verbose_lvl > 2 or \
                        curr_week != old_week and verbose_lvl > 1 or \
                        curr_month != old_month and verbose_lvl > 0:
                    msg = time_step_string[6:-4] + '\n\t' + simulation_environment.done_in_mean_time()
                    print(msg)
                    old_day = curr_day
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
        msg = time_step_string[6:-4] + '\n\t' + simulation_environment.done_in_mean_time()
        print(msg)
        print('----------------------------------------')
        print('End of simulation, final PTU: {}'.format(time_step_string))
        print(simulation_environment.end_of_environment_message(environment_additions=[]))
    return simulation_environment.end_of_environment_metrics(current_metrics={})


def run_simulation_from_dict_of_df(starting_time_step=0, number_of_steps=100, scenario=base_scenario, verbose_lvl=3,
                                   simulation_environment=None, dict_of_df=None):
    if simulation_environment is None or dict_of_df is None:
        baseline_rhino_simulation(verbose_lvl=verbose_lvl)

    steps_taken = 0
    old_day = 0
    old_week = 0
    old_month = 0

    # Open the scenario
    for environment_dict in dict_of_df:
        if starting_time_step >= 0:  # Skip lines until we reach the starting step.
            starting_time_step = starting_time_step - 1
        else:
            environment_data = []
            # Figure out date of the data
            time_step_dt = dt.datetime.strptime(environment_dict['time_utc'], '%Y-%m-%d %H:%M:%S%z')
            time_step_dt = time_step_dt.astimezone(tz=dt.timezone.utc)
            environment_data.append(time_step_dt)
            time_step_string = time_step_dt.strftime('%H:%M %d-%m-%Y UTC')

            # Announce start of simulation
            if steps_taken == 0 and verbose_lvl >= 0:
                print('Starting simulation from PTU {}'.format(time_step_string))

            # Give an update of how it is going in the mean_time
            curr_month = time_step_dt.month
            curr_week = time_step_dt.isocalendar()[1]
            curr_day = time_step_dt.day
            if curr_day != old_day and verbose_lvl > 2 or \
                    curr_week != old_week and verbose_lvl > 1 or \
                    curr_month != old_month and verbose_lvl > 0:
                msg = time_step_string[6:-4] + '\n\t' + simulation_environment.done_in_mean_time()
                print(msg)
                old_day = curr_day
                old_week = curr_week
                old_month = curr_month

            # End simulation here if number of steps have been taken.
            if steps_taken >= number_of_steps:  # If we reach our maximum amount of steps. Stop the simulation
                break
            else:
                # Otherwise, ensure data of enviroment steps is correct
                try:
                    if environment_dict['tennet_balansdelta.mean_max_price'] == 'nan':
                        raise ValueError
                    if scenario.__contains__('windnet'):
                        environment_data.append(float(environment_dict['tennet_balansdelta.mean_max_price']))
                        environment_data.append(float(environment_dict['tennet_balansdelta.mean_mid_price']))
                        environment_dict[3] = float(environment_dict[3])
                        environment_dict[5] = float(environment_dict[5])
                        environment_dict[7] = float(environment_dict[7])
                    elif scenario.__contains__('lelystad'):
                        environment_data.append(float(environment_dict['tennet_balansdelta.mean_max_price']))
                        environment_data.append(float(environment_dict['tennet_balansdelta.mean_mid_price']))
                        environment_data.append(float(environment_dict['tennet_balansdelta.mean_min_price']))
                        environment_data.append(float(environment_dict['power']))
                        environment_data.append(None if environment_dict['irradiance'] == '' else float(environment_dict['irradiance']))
                        environment_data.append(None if environment_dict['expected_power'] == '' else float(environment_dict['expected_power']))
                        environment_data.append(None if environment_dict['lower_range'] == '' else float(environment_dict['lower_range']))
                        environment_data.append(None if environment_dict['upper_range'] == '' else float(environment_dict['upper_range']))
                        environment_data.append(None if environment_dict['losses'] == '' else float(environment_dict['losses']))
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
    return simulation_environment.end_of_environment_metrics(current_metrics={})


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
    simple_strategy_controller = StrategyControlTower(name="Rhino Battery Controller", network_object=rhino, strategy=csv_strategy, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(simple_strategy_controller, [1, 3])
    run_full_scenario(scenario='data/environments/lelystad_1_2021.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def rhino_windnet_limited_charging(verbose_lvl=1):
    # Rhino with limited charging simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv')
    rhino = Battery('Rhino', 7500, 12000, battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
    strategy_limited_charge_controller = StrategyWithLimitedChargeCapacityControlTower(name="Rhino Battery Controller", network_object=rhino, strategy=csv_strategy, verbose_lvl=verbose_lvl)

    imbalance_environment.add_object(strategy_limited_charge_controller, [1, 3, 5])
    run_full_scenario(scenario='data/tennet_and_windnet/tennet_balans_delta_and_pandas_windnet.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def wombat_solarvation_limited_charging(verbose_lvl=1, base_money_strat=True):
    # Wombat with limited charging simulation
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, 14000)

    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(solarvation, [1, 3, 4])

    wombat = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=1600, verbose_lvl=verbose_lvl)

    if base_money_strat:
        csv_strategy = CsvStrategy('Rhino strategy 1',
                                   strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv')

        main_controller = StrategyWithLimitedChargeCapacityControlTower(
            name="Wombat Battery Controller", network_object=wombat, strategy=csv_strategy, verbose_lvl=verbose_lvl,
            transportation_kw=2000)
        imbalance_environment.add_object(main_controller, [1, 3, 4])
    else:
        main_controller = MonthOfModesOfOperationController(name='Wombat main controller',
                                                            network_object=wombat, verbose_lvl=verbose_lvl)
        for month_num in range(1, 13):
            money_earn_strat_month = get_month_strategy(month_num)
            limited_charge_controller = StrategyWithLimitedChargeCapacityControlTower(
                name=f"Wombat Controller Month {month_num}", network_object=wombat, strategy=money_earn_strat_month,
                verbose_lvl=verbose_lvl, transportation_kw=2000)
            main_controller.add_controller(limited_charge_controller)
        imbalance_environment.add_object(main_controller, [1, 3, 4, 0])

    return run_full_scenario(simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


def solarvation_dumb_discharging(verbose_lvl=1, congestion_kw=14000):
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, congestion_kw)

    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(solarvation, [1, 3, 4])
    return run_full_scenario(simulation_environment=imbalance_environment, verbose_lvl=verbose_lvl)


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
    simple_strategy_controller = StrategyWithLimitedChargeCapacityControlTower(name="Rhino Battery Controller", network_object=rhino,
                                                      strategy=csv_strategy, verbose_lvl=verbose_lvl)

    imbalance_environment.add_object(simple_strategy_controller, [1, 3, 5])
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
    simple_strategy_controller = StrategyControlTower(name="Random strategy Battery Controller", network_object=random_step_battery,
                                                      strategy=random_point_based_strategy, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(simple_strategy_controller, [1, 3])

    csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv')
    rhino = Battery('Rhino', 7500, 12000, battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
    simple_strategy_controller = StrategyControlTower(name="Rhino Battery Controller", network_object=rhino, strategy=csv_strategy, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(simple_strategy_controller, [1, 3])

    run_full_scenario(scenario='data/environments/lelystad_1_2021.csv',
                      simulation_environment=imbalance_environment, verbose_lvl=1)


def super_naive_baseline(verbose_lvl=1):
    network_capacity = 14000
    congestion_safety_margin = 0.99

    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, network_capacity)

    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)
    battery = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=15000, verbose_lvl=verbose_lvl)
    csv_strategy = CsvStrategy('Discharge above 60', strategy_csv='data/strategies/greedy_discharge_60.csv')
    congestion_controller = SolveCongestionControlTower(name="Solarvation Congestion Controller", network_object=battery,
                                                        congestion_kw=network_capacity, congestion_safety_margin=congestion_safety_margin,
                                                        strategy=csv_strategy, verbose_lvl=verbose_lvl)

    imbalance_environment.add_object(solarvation, [1, 3, 4])
    imbalance_environment.add_object(congestion_controller, [1, 3, 4])

    return run_full_scenario(scenario='data/environments/lelystad_1_2021.csv', verbose_lvl=verbose_lvl, simulation_environment=imbalance_environment)


def baseline(verbose_lvl=1, base_money_strat=True):
    congestion_kw = 14000
    congestion_safety_margin = 0.99
    transportation_kw = 2000

    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, congestion_kw)

    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(solarvation, [1, 3, 4])

    battery = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=1600, verbose_lvl=verbose_lvl)

    csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv')
    greedy_discharge_strat = CsvStrategy('Greedy discharge', strategy_csv='data/strategies/greedy_discharge_60.csv')
    always_discharge_strat = CsvStrategy('Always discharge', strategy_csv='data/strategies/always_discharge.csv')

    solve_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Solve Congestion Controller",
                                                                       network_object=battery,
                                                                       congestion_kw=congestion_kw,
                                                                       congestion_safety_margin=congestion_safety_margin,
                                                                       strategy=greedy_discharge_strat,
                                                                       verbose_lvl=verbose_lvl)
    prepare_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Prepare Congestion",
                                                                         network_object=battery,
                                                                         congestion_kw=congestion_kw,
                                                                         congestion_safety_margin=congestion_safety_margin,
                                                                         strategy=always_discharge_strat,
                                                                         verbose_lvl=verbose_lvl)
    earn_money_mod = SolveCongestionAndLimitedChargeControlTower(name="Rhino strategy 1",
                                                                 network_object=battery,
                                                                 congestion_kw=congestion_kw,
                                                                 congestion_safety_margin=congestion_safety_margin,
                                                                 strategy=csv_strategy,
                                                                 verbose_lvl=verbose_lvl,
                                                                 transportation_kw=transportation_kw)
    if base_money_strat:
        main_controller = ModesOfOperationController(name='Wombat main controller',
                                         network_object=battery,
                                         verbose_lvl=verbose_lvl)
        main_controller.add_mode_of_operation(dt.time(4, 30, tzinfo=utc), earn_money_mod)
        main_controller.add_mode_of_operation(dt.time(6, 45, tzinfo=utc), prepare_congestion_mod)
        main_controller.add_mode_of_operation(dt.time(16, 45, tzinfo=utc), solve_congestion_mod)
        main_controller.add_mode_of_operation(dt.time(23, 59, tzinfo=utc), earn_money_mod)
    else:
        main_controller = MonthOfModesOfOperationController(name='Wombat main controller',
                                                            network_object=battery, verbose_lvl=verbose_lvl)
        for month_num in range(1, 13):
            money_earn_strat_month = get_month_strategy(month_num)
            earn_money_mod = SolveCongestionAndLimitedChargeControlTower(name=f"GIGA Baseline Month {month_num}",
                                                                         network_object=battery,
                                                                         congestion_kw=congestion_kw,
                                                                         congestion_safety_margin=congestion_safety_margin,
                                                                         strategy=money_earn_strat_month,
                                                                         verbose_lvl=verbose_lvl,
                                                                         transportation_kw=transportation_kw)
            single_month_controller = ModesOfOperationController(name='Wombat month controller',
                                                         network_object=battery,
                                                         verbose_lvl=verbose_lvl)
            single_month_controller.add_mode_of_operation(dt.time(4, 30, tzinfo=utc), earn_money_mod)
            single_month_controller.add_mode_of_operation(dt.time(6, 45, tzinfo=utc), prepare_congestion_mod)
            single_month_controller.add_mode_of_operation(dt.time(16, 45, tzinfo=utc), solve_congestion_mod)
            single_month_controller.add_mode_of_operation(dt.time(23, 59, tzinfo=utc), earn_money_mod)
            main_controller.add_controller(single_month_controller)

    imbalance_environment.add_object(main_controller, [1, 3, 4, 0])

    # Run single day
    # starting_timestep = 270555
    # number_of_steps = 1440
    # run_simulation(starting_timestep, number_of_steps, verbose_lvl=verbose_lvl, simulation_environment=imbalance_environment)

    # Run single month
    # run_single_month(7, verbose_lvl=verbose_lvl, simulation_environment=imbalance_environment)

    # Run full scenario
    return run_full_scenario(scenario='data/environments/lelystad_1_2021.csv', verbose_lvl=verbose_lvl, simulation_environment=imbalance_environment)


def run_monthly_timed_baseline(verbose_lvl=2, transportation_kw=2000, congestion_kw=14000, congestion_strategy=1, base_money_strat=True):
    congestion_safety_margin = 0.99

    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, congestion_kw)

    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)

    battery = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=1600, verbose_lvl=verbose_lvl)

    csv_strategy = CsvStrategy('Rhino strategy 1', strategy_csv='data/strategies/cleaner_simplified_passive_imbalance_1.csv')

    earn_money_mod = SolveCongestionAndLimitedChargeControlTower(name="Rhino strategy 1",
                                                                 network_object=battery,
                                                                 congestion_kw=congestion_kw,
                                                                 congestion_safety_margin=congestion_safety_margin,
                                                                 strategy=csv_strategy,
                                                                 verbose_lvl=verbose_lvl,
                                                                 transportation_kw=transportation_kw)

    res_df = get_month_congestion_timings(solarvation_identifier='data/environments/lelystad_1_2021.csv', strategy=congestion_strategy)
    print(res_df.to_string())

    earning_money_until = res_df.loc['prep_start']
    preparing_for_congestion_until = res_df.loc['congestion_start']
    preparing_max_kwh = res_df.loc['prep_max_soc']
    solving_congestion_until = res_df.loc['congestion_end']

    main_controller = MonthOfModesOfOperationController(name='Wombat main controller',
                                                        network_object=battery,
                                                        verbose_lvl=verbose_lvl)
    for month in range(12):
        moo = ModesOfOperationController(name=f'Wombat controller month {month}',
                                         network_object=battery,
                                         verbose_lvl=verbose_lvl)
        if not base_money_strat:
            month_num = month + 1
            money_earning_strat = get_month_strategy(month_num)
            earn_money_mod = SolveCongestionAndLimitedChargeControlTower(name=f"GIGA Baseline Month {month_num}",
                                                                         network_object=battery,
                                                                         congestion_kw=congestion_kw,
                                                                         congestion_safety_margin=congestion_safety_margin,
                                                                         strategy=money_earning_strat,
                                                                         verbose_lvl=verbose_lvl,
                                                                         transportation_kw=transportation_kw)
        if earning_money_until[month] is not NaT:
            moo.add_mode_of_operation(earning_money_until[month], earn_money_mod)

            max_kwh_in_prep = float(preparing_max_kwh[month])
            max_soc_perc_in_prep = int(max_kwh_in_prep / battery.max_kwh * 100)
            discharge_until_strategy = DischargeUntilStrategy(base_strategy=csv_strategy,
                                                              name='Discharge Money Earner',
                                                              discharge_until_soc_perc=max_soc_perc_in_prep
                                                              )
            prepare_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name=f"Earn money but discharge until {max_soc_perc_in_prep}",
                                                                                 network_object=battery,
                                                                                 congestion_kw=congestion_kw,
                                                                                 congestion_safety_margin=congestion_safety_margin,
                                                                                 strategy=discharge_until_strategy,
                                                                                 verbose_lvl=verbose_lvl)

            moo.add_mode_of_operation(preparing_for_congestion_until[month], prepare_congestion_mod)
            moo.add_mode_of_operation(solving_congestion_until[month], prepare_congestion_mod)
        moo.add_mode_of_operation(dt.time(23, 59, tzinfo=utc), earn_money_mod)
        main_controller.add_controller(moo)

    imbalance_environment.add_object(solarvation, [1, 3, 4])
    imbalance_environment.add_object(main_controller, [1, 3, 4, 0])

    return run_full_scenario(scenario='data/environments/lelystad_1_2021.csv',
                             verbose_lvl=verbose_lvl,
                             simulation_environment=imbalance_environment)


def run_random_strategy_with_monthly_times(verbose_lvl=1, seed=None, transportation_kw=2000, congestion_kw=14000):
    congestion_safety_margin = 0.99

    # Initialise environment
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, congestion_kw)

    # Initialise solar farm
    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)
    # Initialise battery
    battery = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=1600, verbose_lvl=verbose_lvl)

    # Initialise random strategy
    random_point_based_strategy = generate_random_discharge_relative_strategy(seed=seed)
    if seed is None:
        print(f'{random_point_based_strategy.name}')
    greedy_discharge_strat = CsvStrategy('Greedy discharge', strategy_csv='data/strategies/greedy_discharge_60.csv')
    always_discharge_strat = CsvStrategy('Always discharge', strategy_csv='data/strategies/always_discharge.csv')

    solve_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Solve Congestion Controller",
                                                                       network_object=battery,
                                                                       congestion_kw=congestion_kw,
                                                                       congestion_safety_margin=congestion_safety_margin,
                                                                       strategy=greedy_discharge_strat,
                                                                       verbose_lvl=verbose_lvl,
                                                                       transportation_kw=transportation_kw)
    prepare_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Prepare Congestion",
                                                                         network_object=battery,
                                                                         congestion_kw=congestion_kw,
                                                                         congestion_safety_margin=congestion_safety_margin,
                                                                         strategy=always_discharge_strat,
                                                                         verbose_lvl=verbose_lvl,
                                                                         transportation_kw=transportation_kw)
    earn_money_mod = SolveCongestionAndLimitedChargeControlTower(name="Rhino strategy 1",
                                                                 network_object=battery,
                                                                 congestion_kw=congestion_kw,
                                                                 congestion_safety_margin=congestion_safety_margin,
                                                             strategy=random_point_based_strategy,
                                                                 verbose_lvl=verbose_lvl,
                                                                 transportation_kw=transportation_kw)

    res_df = get_month_congestion_timings(solarvation_identifier='data/environments/lelystad_1_2021.csv', strategy=1)
    print(res_df.to_string())

    earning_money_until = res_df.loc['prep_start']
    preparing_for_congestion_until = res_df.loc['congestion_start']
    preparing_max_kwh = res_df.loc['prep_max_soc']
    solving_congestion_until = res_df.loc['congestion_end']

    main_controller = MonthOfModesOfOperationController(name='Wombat main controller',
                                                        network_object=battery,
                                                        verbose_lvl=verbose_lvl)
    for month in range(12):
        moo = ModesOfOperationController(name=f'Wombat controller month {month}',
                                         network_object=battery,
                                         verbose_lvl=verbose_lvl)
        if earning_money_until[month] is not NaT:
            moo.add_mode_of_operation(earning_money_until[month], earn_money_mod)

            max_kwh_in_prep = float(preparing_max_kwh[month])
            max_soc_perc_in_prep = int(max_kwh_in_prep / battery.max_kwh * 100)
            discharge_until_strategy = DischargeUntilStrategy(base_strategy=random_point_based_strategy,
                                                              name='Discharge Money Earner',
                                                              discharge_until_soc_perc=max_soc_perc_in_prep
                                                              )
            prepare_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Prepare Congestion",
                                                                                 network_object=battery,
                                                                                 congestion_kw=congestion_kw,
                                                                                 congestion_safety_margin=congestion_safety_margin,
                                                                                 strategy=discharge_until_strategy,
                                                                                 verbose_lvl=verbose_lvl)

            moo.add_mode_of_operation(preparing_for_congestion_until[month], prepare_congestion_mod)
            moo.add_mode_of_operation(solving_congestion_until[month], solve_congestion_mod)
        moo.add_mode_of_operation(dt.time(23, 59, tzinfo=utc), earn_money_mod)
        main_controller.add_controller(moo)

    imbalance_environment.add_object(solarvation, [1, 3, 4])
    imbalance_environment.add_object(main_controller, [1, 3, 4, 0])

    return run_full_scenario(scenario='data/environments/lelystad_1_2021.csv',
                             verbose_lvl=verbose_lvl,
                             simulation_environment=imbalance_environment)


def run_single_month_random_strategy(verbose_lvl=1, seed=None, transportation_kw=2000, congestion_kw=14000, month=None):
    random_point_based_strategy = generate_random_discharge_relative_strategy(seed=seed)
    run_single_month_set_strategy(verbose_lvl, random_point_based_strategy, transportation_kw, congestion_kw, month)


def run_single_month_set_strategy(verbose_lvl=1, strategy=None, transportation_kw=2000, congestion_kw=14000, month=None):
    if month is None and strategy is None:
        return run_random_strategy_with_monthly_times(verbose_lvl, None, transportation_kw, congestion_kw)
    congestion_safety_margin = 0.99

    # Initialise environment
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, congestion_kw)

    # Initialise solar farm
    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)
    # Initialise battery
    battery = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=1600, verbose_lvl=verbose_lvl)

    # Initialise random strategy
    if strategy is None:
        money_earning_strategy = generate_random_discharge_relative_strategy()
    else:
        money_earning_strategy = strategy
    greedy_discharge_strat = CsvStrategy('Greedy discharge', strategy_csv='data/strategies/greedy_discharge_60.csv')
    always_discharge_strat = CsvStrategy('Always discharge', strategy_csv='data/strategies/always_discharge.csv')

    solve_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Solve Congestion Controller",
                                                                       network_object=battery,
                                                                       congestion_kw=congestion_kw,
                                                                       congestion_safety_margin=congestion_safety_margin,
                                                                       strategy=greedy_discharge_strat,
                                                                       verbose_lvl=verbose_lvl,
                                                                       transportation_kw=transportation_kw)
    earn_money_mod = SolveCongestionAndLimitedChargeControlTower(name="Rhino strategy 1",
                                                                 network_object=battery,
                                                                 congestion_kw=congestion_kw,
                                                                 congestion_safety_margin=congestion_safety_margin,
                                                                 strategy=money_earning_strategy,
                                                                 verbose_lvl=verbose_lvl,
                                                                 transportation_kw=transportation_kw)

    res_df = get_month_congestion_timings(solarvation_identifier='data/environments/lelystad_1_2021.csv', strategy=1)

    earning_money_until = res_df.loc['prep_start']
    preparing_for_congestion_until = res_df.loc['congestion_start']
    preparing_max_kwh = res_df.loc['prep_max_soc']
    solving_congestion_until = res_df.loc['congestion_end']

    assert 12 >= month >= 1
    month = month - 1
    print(res_df[month].to_string())
    moo = ModesOfOperationController(name=f'Wombat controller month {month}',
                                     network_object=battery,
                                     verbose_lvl=verbose_lvl)
    if earning_money_until[month] is not NaT:
        moo.add_mode_of_operation(earning_money_until[month], earn_money_mod)

        max_kwh_in_prep = float(preparing_max_kwh[month])
        max_soc_perc_in_prep = int(max_kwh_in_prep / battery.max_kwh * 100)
        discharge_until_strategy = DischargeUntilStrategy(base_strategy=money_earning_strategy,
                                                          name=f'Discharge until {max_kwh_in_prep} -> Money Earner',
                                                          discharge_until_soc_perc=max_soc_perc_in_prep
                                                          )
        prepare_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Prepare Congestion",
                                                                             network_object=battery,
                                                                             congestion_kw=congestion_kw,
                                                                             congestion_safety_margin=congestion_safety_margin,
                                                                             strategy=discharge_until_strategy,
                                                                             verbose_lvl=verbose_lvl)

        moo.add_mode_of_operation(preparing_for_congestion_until[month], prepare_congestion_mod)
        moo.add_mode_of_operation(solving_congestion_until[month], solve_congestion_mod)
    moo.add_mode_of_operation(dt.time(23, 59, tzinfo=utc), earn_money_mod)

    imbalance_environment.add_object(solarvation, [1, 3, 4])
    imbalance_environment.add_object(moo, [1, 3, 4, 0])

    # Run single day
    starting_timestep = 129600 + 25 * 1440
    number_of_steps = 2 * 1440
    return run_simulation(starting_timestep, number_of_steps, verbose_lvl=verbose_lvl, simulation_environment=imbalance_environment)

    # return run_single_month(month + 1, verbose_lvl=verbose_lvl, simulation_environment=imbalance_environment)


if __name__ == '__main__':
    verbose_lvl = 1

    # baseline_rhino_simulation(verbose_lvl)
    # random_rhino_strategy_simulation(verbose_lvl=verbose_lvl, seed=4899458002697043430)
    # rhino_windnet_limited_charging(verbose_lvl)
    # full_rhino_site_capacity()

    ####################################################################
    # congestion_causing_strategy = PointBasedStrategy('Congestion cause', price_step_size=2)
    #
    # congestion_causing_strategy.add_point((13, 152, 'CHARGE'))
    # congestion_causing_strategy.add_point((25, 126, 'CHARGE'))
    # congestion_causing_strategy.add_point((48, 108, 'CHARGE'))
    # congestion_causing_strategy.add_point((61, 80, 'CHARGE'))
    # congestion_causing_strategy.add_point((95, 26, 'CHARGE'))
    # congestion_causing_strategy.add_point((32, 192, 'DISCHARGE'))
    # congestion_causing_strategy.add_point((45, 154, 'DISCHARGE'))
    # congestion_causing_strategy.add_point((76, 178, 'DISCHARGE'))
    # congestion_causing_strategy.add_point((94, 164, 'DISCHARGE'))
    # congestion_causing_strategy.add_point((95, -68, 'DISCHARGE'))
    #
    # congestion_causing_strategy.upload_strategy()
    # print(congestion_causing_strategy)
    # print(run_single_month_set_strategy(verbose_lvl, strategy=congestion_causing_strategy, month=4))
    ####################################################################

    res_arr = []

    temp_dict = solarvation_dumb_discharging(verbose_lvl)
    temp_dict['name'] = 'Solarvation only discharging'
    res_arr.append(temp_dict)

    temp_dict = wombat_solarvation_limited_charging(verbose_lvl)
    temp_dict['name'] = 'Wombat disregard congestion (with base money strat)'
    res_arr.append(temp_dict)

    temp_dict = wombat_solarvation_limited_charging(verbose_lvl, base_money_strat=False)
    temp_dict['name'] = 'Wombat disregard congestion GIGA Baseline'
    res_arr.append(temp_dict)

    temp_dict = super_naive_baseline(verbose_lvl)
    temp_dict['name'] = 'Wombat only solve congestion'
    res_arr.append(temp_dict)

    temp_dict = baseline(verbose_lvl)
    temp_dict['name'] = 'Wombat yearly timing (with base money strat)'
    res_arr.append(temp_dict)

    temp_dict = baseline(verbose_lvl, base_money_strat=False)
    temp_dict['name'] = 'Wombat yearly timing GIGA Baseline'
    res_arr.append(temp_dict)

    temp_dict = run_monthly_timed_baseline(verbose_lvl, congestion_strategy=2)
    print(temp_dict)
    temp_dict['name'] = 'Wombat conservative monthly timed (with base money strat)'
    res_arr.append(temp_dict)

    temp_dict = run_monthly_timed_baseline(verbose_lvl, congestion_strategy=2, base_money_strat=False)
    print(temp_dict)
    temp_dict['name'] = 'Wombat conservative monthly timed GIGA Baseline'
    res_arr.append(temp_dict)

    temp_dict = run_monthly_timed_baseline(verbose_lvl, congestion_strategy=1)
    print(temp_dict)
    temp_dict['name'] = 'Wombat smart monthly timed (with base money strat)'
    res_arr.append(temp_dict)

    temp_dict = run_monthly_timed_baseline(verbose_lvl, congestion_strategy=1, base_money_strat=False)
    print(temp_dict)
    temp_dict['name'] = 'Wombat smart monthly timed GIGA Baseline'
    res_arr.append(temp_dict)

    temp_dict = run_monthly_timed_baseline(verbose_lvl, congestion_strategy=5)
    print(temp_dict)
    temp_dict['name'] = 'Wombat max smart monthly timed (with base money strat)'
    res_arr.append(temp_dict)

    temp_dict = run_monthly_timed_baseline(verbose_lvl, congestion_strategy=5, base_money_strat=False)
    print(temp_dict)
    temp_dict['name'] = 'Wombat max smart monthly timed GIGA Baseline'
    res_arr.append(temp_dict)

    temp_dict = run_monthly_timed_baseline(verbose_lvl, congestion_strategy=6)
    print(temp_dict)
    temp_dict['name'] = 'Wombat avg smart monthly timed (with base money strat)'
    res_arr.append(temp_dict)

    temp_dict = run_monthly_timed_baseline(verbose_lvl, congestion_strategy=6, base_money_strat=False)
    print(temp_dict)
    temp_dict['name'] = 'Wombat avg smart monthly timed GIGA Baseline'
    res_arr.append(temp_dict)

    print(res_arr)
    res_df = pd.DataFrame(res_arr)
    print(res_df)
    res_df.to_csv('data/baseline_earnings/auto_overview.csv')
