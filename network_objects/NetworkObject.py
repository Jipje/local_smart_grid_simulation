class NetworkObject(object):
    def __init__(self, name):
        self.name = name

    def take_imbalance_action(self, charge_price, discharge_price, action=None):
        pass

    def wait(self):
        pass

    def done_in_mean_time(self):
        return ''
