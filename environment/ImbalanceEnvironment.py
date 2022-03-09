from environment.NetworkEnvironment import NetworkEnvironment
from helper_objects.ImbalanceMessageInterpreter import ImbalanceMessageInterpreter


class ImbalanceEnvironment:
    def __init__(self, network_environment: NetworkEnvironment, mid_price_index, max_price_index, min_price_index):
        self.network_environment = network_environment

        self.imbalance_msg_interpreter = ImbalanceMessageInterpreter()
        self.mid_price_index = mid_price_index
        self.max_price_index = max_price_index
        self.min_price_index = min_price_index

        # Assign the correct functions to each object
        self.original_take_step = self.network_environment.take_step
        self.network_environment.take_step = self.take_step

    def take_step(self, environment_step):
        mid_price_msg = environment_step[self.mid_price_index]
        max_price_msg = environment_step[self.max_price_index]
        min_price_msg = environment_step[self.min_price_index]

        try:
            self.imbalance_msg_interpreter.update(mid_price_msg, max_price_msg, min_price_msg)
        except OverflowError:
            self.imbalance_msg_interpreter.reset()
            self.imbalance_msg_interpreter.update(mid_price_msg, max_price_msg, min_price_msg)

        environment_step[self.mid_price_index] = self.imbalance_msg_interpreter.mid_price
        environment_step[self.max_price_index] = self.imbalance_msg_interpreter.get_charge_price()
        environment_step[self.min_price_index] = self.imbalance_msg_interpreter.get_discharge_price()
        if self.network_environment.verbose_lvl > 3:
            print(f'\tCharge price: {environment_step[self.max_price_index]}\n'
                  f'\tDischarge price: {environment_step[self.min_price_index]}')
        return self.original_take_step(environment_step)
