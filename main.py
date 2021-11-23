from csv import reader
from Battery import Battery


def run_simulation(starting_time_step=0, number_of_steps=100, scenario='data/tennet_balans_delta_nov_2020_nov_2021.csv'):
    rhino = Battery('Rhino', 7500, 12000, 50)

    # open file in read mode
    with open(scenario, 'r') as read_obj:
        csv_reader = reader(read_obj)
        steps_taken = 0
        for environment_data in csv_reader:
            if starting_time_step < 0:
                if steps_taken >= number_of_steps:
                    break
                else:
                    rhino.take_action()
                steps_taken = steps_taken + 1
            else:
                starting_time_step = starting_time_step - 1
    print('END OF SIMULATION, TOOK {} STEPS'.format(steps_taken))


if __name__ == '__main__':
    run_simulation(100000, 100)
