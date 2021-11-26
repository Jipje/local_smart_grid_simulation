from csv import reader
from Battery import Battery
from ImbalanceMessageInterpreter import ImbalanceMessageInterpreter
import random


def run_random_month(scenario='data/tennet_balans_delta_nov_2020_nov_2021.csv', verbose_lvl=2):
    start_day = random.randint(0, 333)
    starting_timestep = start_day * 24 * 60
    number_of_steps = 30 * 24 * 60
    run_simulation(starting_timestep, number_of_steps, scenario=scenario, verbose_lvl=verbose_lvl)


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
                if steps_taken >= number_of_steps:  # If we reach our maximum amount of steps. Stop the simulation
                    break
                else:
                    try:
                        mid_price_msg = float(environment_data[2])
                        max_price_msg = float(environment_data[1])
                        min_price_msg = float(environment_data[3])
                    except ValueError:
                        continue
                    # The environment should take a step here.
                    try:
                        imbalance_msg_interpreter.update(mid_price_msg, max_price_msg, min_price_msg)
                    except OverflowError:
                        imbalance_msg_interpreter.reset()
                        imbalance_msg_interpreter.update(mid_price_msg, max_price_msg, min_price_msg)
                    rhino.take_action(imbalance_msg_interpreter.get_charge_price(), imbalance_msg_interpreter.get_discharge_price())
                steps_taken = steps_taken + 1

    print('END OF SIMULATION, TOOK {} STEPS'.format(steps_taken))
    print(rhino)


if __name__ == '__main__':
    # run_simulation(1440, 1440, verbose_lvl=2)
    run_random_month(verbose_lvl=2)
