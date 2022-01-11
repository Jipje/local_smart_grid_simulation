from environment.NetworkEnvironment import NetworkEnvironment
from helper_objects.ImbalanceMessageInterpreter import ImbalanceMessageInterpreter


class ImbalanceEnvironment(NetworkEnvironment):
    def __init__(self, verbose_lvl, mid_price_index, max_price_index, min_price_index):
        super().__init__(verbose_lvl=verbose_lvl)
        self.imbalance_msg_interpreter = ImbalanceMessageInterpreter()
        self.mid_price_index = mid_price_index
        self.max_price_index = max_price_index
        self.min_price_index = min_price_index

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
        super().take_step(environment_step)
