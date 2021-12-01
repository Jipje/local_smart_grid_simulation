class NetworkObject(object):
    def __init__(self, name):
        self.name = name

    def take_step(self, environment_step, action_parameters):
        pass

    def wait(self):
        pass

    def done_in_mean_time(self):
        return ''
