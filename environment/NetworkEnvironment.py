
class NetworkEnvironment(object):
    def __init__(self, verbose_lvl=2):
        self.network_objects = []
        self.verbose_lvl = verbose_lvl
        self.network_object_parameters = []

    def add_object(self, network_object, action_parameters):
        self.network_objects.append(network_object)
        self.network_object_parameters.append(action_parameters)

    def take_step(self, environment_step) -> int:
        total_network_step = 0
        for object_index in range(len(self.network_objects)):
            network_object = self.network_objects[object_index]
            action_parameters = self.network_object_parameters[object_index]
            total_network_step += network_object.take_step(environment_step, action_parameters)
        return self.check_action(total_network_step)

    def check_action(self, network_step):
        if self.verbose_lvl > 2:
            print('Network is measuring: {}'.format(network_step))
        return network_step

    def done_in_mean_time(self, curr_msg=None):
        res_msg = ''
        for network_object in self.network_objects:
            res_msg = res_msg + network_object.done_in_mean_time() + '\n'
        res_msg = res_msg[:-1]
        if curr_msg is not None:
            res_msg = curr_msg + res_msg
        return res_msg