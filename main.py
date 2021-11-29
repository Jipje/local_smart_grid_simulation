from csv import reader
from Battery import Battery
from ImbalanceEnvironment import ImbalanceEnvironment
from ImbalanceMessageInterpreter import ImbalanceMessageInterpreter
import random
import datetime as dt


def run_random_thirty_days(scenario='data/tennet_balans_delta_nov_2020_nov_2021.csv', verbose_lvl=2):
    start_day = random.randint(0, 333)
    starting_timestep = start_day * 24 * 60
    number_of_steps = 30 * 24 * 60
    print('Random thirty days - Starting timestep: {} - Number of Steps: {}'.format(starting_timestep, number_of_steps))
    run_simulation(starting_timestep, number_of_steps, scenario=scenario, verbose_lvl=verbose_lvl)
    print('Just ran random thirty days.- Starting timestep: {} - Number of Steps: {}'.format(starting_timestep, number_of_steps))


def run_full_scenario(scenario='data/tennet_balans_delta_nov_2020_nov_2021.csv', verbose_lvl=1):
    starting_timestep = 0
    with open(scenario) as file:
        number_of_steps = len(file.readlines()) + 1
    print('Running full scenario {}'.format(scenario))
    run_simulation(starting_timestep, number_of_steps, scenario=scenario, verbose_lvl=verbose_lvl)
    print('Just ran full scenario {}'.format(scenario))


def run_simulation(starting_time_step=0, number_of_steps=100, scenario='data/tennet_balans_delta_nov_2020_nov_2021.csv', verbose_lvl=3):
    imbalance_environment = ImbalanceEnvironment(verbose_lvl=verbose_lvl)
    rhino = Battery('Rhino', 7500, 12000, battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)
    imbalance_environment.add_object(rhino)

    # open file in read mode
    with open(scenario, 'r') as read_obj:
        csv_reader = reader(read_obj)
        steps_taken = 0

        curr_day = 0
        old_day = 0
        old_earnings = 0

        # Open the scenario
        for environment_data in csv_reader:
            if starting_time_step >= 0:  # Skip lines until we reach the starting step.
                starting_time_step = starting_time_step - 1
            else:
                time_step_dt = dt.datetime.strptime(environment_data[0], '%Y-%m-%dT%H:%M:%S.000Z')
                time_step_dt = time_step_dt.astimezone(tz=dt.timezone.utc)
                time_step_string = time_step_dt.strftime('%H:%M %d-%m-%Y UTC')

                curr_day = time_step_dt.day
                if curr_day != old_day:
                    if verbose_lvl > 0:
                        day_earnings = round(rhino.earnings - old_earnings, 2)
                        print('Earnings for {}: €{}'.format(time_step_string, day_earnings))
                    old_day = curr_day
                    old_earnings = rhino.earnings

                if steps_taken == 0 and verbose_lvl >= 0:
                    print('Starting simulation from PTU {}'.format(time_step_string))
                if steps_taken >= number_of_steps:  # If we reach our maximum amount of steps. Stop the simulation
                    break
                else:
                    try:
                        mid_price_msg = float(environment_data[2])
                        max_price_msg = float(environment_data[1])
                        min_price_msg = float(environment_data[3])
                    except ValueError:
                        if verbose_lvl > 2:
                            print("Skipping timestep {} as data is missing".format(time_step_string))
                        continue
                    # The environment should take a step here.
                    imbalance_environment.take_step(mid_price_msg, max_price_msg, min_price_msg)

                steps_taken = steps_taken + 1
                if steps_taken == number_of_steps and verbose_lvl >= 0:
                    print('End of simulation, final PTU: {}'.format(time_step_string))

    num_of_days = int(steps_taken / 60 / 24)
    print('Number of 1m timesteps: {}\nNumber of PTUs: {}\nNumber of days: {}\n'.format(steps_taken, steps_taken / 15, num_of_days))
    print(rhino)
    if num_of_days != 0:
        earnings_per_day = round(rhino.earnings / num_of_days, 2)
    print('Average earnings per day: {}'.format(earnings_per_day))


if __name__ == '__main__':
    # run_simulation(525500, 1440, verbose_lvl=3)
    run_full_scenario()
    # run_random_thirty_days(verbose_lvl=2)
