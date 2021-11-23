from Battery import Battery


def run_simulation(number_of_steps=100):
    rhino = Battery('Rhino', 7500, 12000, 50)
    for _ in range(number_of_steps):
        rhino.take_action()
    print('END OF SIMULATION')


if __name__ == '__main__':
    run_simulation()
