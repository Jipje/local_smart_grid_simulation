
class NetworkEnvironment(object):
    def __init__(self, verbose_lvl=2):
        self.network_objects = []
        self.verbose_lvl = verbose_lvl
        self.network_object_parameters = []

        self.number_of_steps = 0

    def add_object(self, network_object, action_parameters):
        self.network_objects.append(network_object)
        self.network_object_parameters.append(action_parameters)

    def take_step(self, environment_step) -> int:
        self.number_of_steps += 1
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
            res_msg = res_msg + network_object.done_in_mean_time() + '\n\t'
        res_msg = res_msg[:-2]

        if curr_msg is not None:
            res_msg = curr_msg + res_msg
        return res_msg

    def end_of_environment_message(self, environment_additions):
        num_of_ptus = self.number_of_steps / 15
        num_of_days = num_of_ptus / 96
        res_msg = 'Environment: ' \
                  f'\n\tNumber of 1m timesteps: {self.number_of_steps}' \
                  f'\n\tNumber of PTUs: {num_of_ptus}' \
                  f'\n\tNumber of days: {num_of_days}'
        for msg in environment_additions:
            res_msg = res_msg + '\n\t' + msg

        for network_object in self.network_objects:
            res_msg = res_msg + network_object.end_of_environment_message(num_of_days)
        return res_msg

    def end_of_environment_metrics(self, current_metrics):
        res_dict = current_metrics
        for object_index in range(len(self.network_objects)):
            network_object = self.network_objects[object_index]
            res_dict.update(network_object.end_of_environment_metrics())
        return res_dict
