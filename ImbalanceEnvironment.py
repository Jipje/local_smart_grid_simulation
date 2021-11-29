from Environment import Environment
from ImbalanceMessageInterpreter import ImbalanceMessageInterpreter


class ImbalanceEnvironment(Environment):
    def __init__(self, verbose_lvl):
        super().__init__(verbose_lvl=verbose_lvl)
        self.imbalance_msg_interpreter = ImbalanceMessageInterpreter()

    def take_step(self, mid_price_msg=0.0, max_price_msg=9999.0, min_price_msg=-9999.0):
        try:
            self.imbalance_msg_interpreter.update(mid_price_msg, max_price_msg, min_price_msg)
        except OverflowError:
            self.imbalance_msg_interpreter.reset()
            self.imbalance_msg_interpreter.update(mid_price_msg, max_price_msg, min_price_msg)

        for network_object in self.network_objects:
            charge_price = self.imbalance_msg_interpreter.get_charge_price()
            discharge_price = self.imbalance_msg_interpreter.get_discharge_price()
            network_object.take_imbalance_action(charge_price, discharge_price)


