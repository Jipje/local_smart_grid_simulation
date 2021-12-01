
class Environment(object):
    def __init__(self, verbose_lvl=2):
        self.network_objects = []
        self.verbose_lvl = verbose_lvl

    def add_object(self, network_object):
        self.network_objects.append(network_object)

    def take_step(self):
        pass

    def done_in_mean_time(self):
        res_msg = ''
        for network_object in self.network_objects:
            res_msg = res_msg + network_object.done_in_mean_time() + '\n'
        res_msg = res_msg[:-1]
        return res_msg
