
class Environment(object):
    def __init__(self, verbose_lvl=2):
        self.network_objects = []
        self.verbose_lvl = verbose_lvl

    def add_object(self, network_object):
        self.network_objects.append(network_object)

    def take_step(self):
        pass
        