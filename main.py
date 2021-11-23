from csv import reader
from Battery import Battery
from ImbalanceMessageInterpreter import ImbalanceMessageInterpreter


def run_simulation(starting_time_step=0, number_of_steps=100, scenario='data/tennet_balans_delta_nov_2020_nov_2021.csv'):
    rhino = Battery('Rhino', 7500, 12000, 50)

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
                    # The environment should take a step here.
                    try:
                        imbalance_msg_interpreter.update(float(environment_data[2]), float(environment_data[1]), float(environment_data[3]))
                    except OverflowError:
                        imbalance_msg_interpreter.reset()
                        imbalance_msg_interpreter.update(float(environment_data[2]), float(environment_data[1]), float(environment_data[3]))
                    rhino.take_action(imbalance_msg_interpreter.get_charge_price(), imbalance_msg_interpreter.get_discharge_price())
                    print(imbalance_msg_interpreter.get_current_price())
                steps_taken = steps_taken + 1

    print('END OF SIMULATION, TOOK {} STEPS'.format(steps_taken))


if __name__ == '__main__':
    run_simulation(100000, 100)
