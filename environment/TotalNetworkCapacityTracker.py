from environment.NetworkEnvironment import NetworkEnvironment


class TotalNetworkCapacityTracker:
    def __init__(self, network_environment: NetworkEnvironment, max_kw: int):
        self.network_environment = network_environment
        self.maximum_kw = abs(max_kw)

        self.number_of_congestion_time_steps = 0
        self.old_number_of_congestion_time_steps = self.number_of_congestion_time_steps

        # Assign the correct functions to each object
        self.original_check_action = self.network_environment.check_action
        self.original_done_in_mean_time = self.network_environment.done_in_mean_time
        self.network_environment.check_action = self.check_action
        self.network_environment.done_in_mean_time = self.done_in_mean_time

    def check_action(self, action_kw):
        if abs(action_kw) > self.maximum_kw:
            self.number_of_congestion_time_steps += 1
            if self.network_environment.verbose_lvl > 2:
                print('Network congestion measured')
        return self.original_check_action

    def done_in_mean_time(self):
        congestion_time_steps_since = self.number_of_congestion_time_steps - self.old_number_of_congestion_time_steps
        self.old_number_of_congestion_time_steps = self.number_of_congestion_time_steps
        msg = 'Timesteps with congestion since last time: {}m\n'.format(congestion_time_steps_since)
        return self.original_done_in_mean_time(curr_msg=msg)
