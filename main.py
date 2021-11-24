from csv import reader
from Battery import Battery
from StrategyBattery import StrategyBattery
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
    rhino_strat = StrategyBattery(strategy_csv='data/strategies/simplified_passive_imbalance_1.csv')
    print(rhino_strat.make_decision(90, 90, 4))
    # run_simulation(100000, 100)
