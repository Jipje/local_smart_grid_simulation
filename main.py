from csv import reader
from Battery import Battery
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


def run_simulation(starting_time_step=0, number_of_steps=100, scenario='data/tennet_balans_delta_nov_2020_nov_2021.csv', verbose_lvl=3):
    rhino = Battery('Rhino', 7500, 12000, battery_efficiency=0.9, starting_soc_kwh=3750, verbose_lvl=verbose_lvl)

    # open file in read mode
    with open(scenario, 'r') as read_obj:
        csv_reader = reader(read_obj)
        steps_taken = 0
        imbalance_msg_interpreter = ImbalanceMessageInterpreter()

        # Open the scenario
        for environment_data in csv_reader:
            if starting_time_step >= 0:  # Skip lines until we reach the starting step.
                starting_time_step = starting_time_step - 1
            else:
                time_step_dt = dt.datetime.strptime(environment_data[0], '%Y-%m-%dT%H:%M:%S.000Z')
                time_step_dt = time_step_dt.astimezone(tz=dt.timezone.utc)
                time_step_string = time_step_dt.strftime('%H:%M %d-%m-%Y UTC')
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
                    try:
                        imbalance_msg_interpreter.update(mid_price_msg, max_price_msg, min_price_msg)
                    except OverflowError:
                        if verbose_lvl > 2:
                            print('Start of PTU {}'.format(time_step_string))
                        imbalance_msg_interpreter.reset()
                        imbalance_msg_interpreter.update(mid_price_msg, max_price_msg, min_price_msg)
                    rhino.take_action(imbalance_msg_interpreter.get_charge_price(), imbalance_msg_interpreter.get_discharge_price())
                steps_taken = steps_taken + 1
                if steps_taken == number_of_steps and verbose_lvl >= 0:
                    print('End of simulation, final PTU: {}'.format(time_step_string))

    num_of_days = int(steps_taken / 60 / 24)
    print('Number of 1m timesteps: {}\nNumber of PTUs: {}\nNumber of days: {}\n'.format(steps_taken, steps_taken / 15, num_of_days))
    earnings_per_day = round(rhino.earnings / num_of_days, 2)
    print(rhino)
    print('Average earnings per day: {}'.format(earnings_per_day))


if __name__ == '__main__':
    # run_simulation(1440, 1440, verbose_lvl=2)
    run_random_thirty_days(verbose_lvl=1)
