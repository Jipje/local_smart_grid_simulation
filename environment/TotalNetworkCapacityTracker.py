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
        self.original_end_of_environment_message = self.network_environment.end_of_environment_message
        self.original_end_of_environment_metrics = self.network_environment.end_of_environment_metrics

        self.network_environment.check_action = self.check_action
        self.network_environment.done_in_mean_time = self.done_in_mean_time
        self.network_environment.end_of_environment_message = self.end_of_environment_message
        self.network_environment.end_of_environment_metrics = self.end_of_environment_metrics

    def check_action(self, action_kw):
        if self.network_environment.verbose_lvl > 3:
            print(f'\tNetwork connection measuring: {action_kw}kW')

        if abs(action_kw) > self.maximum_kw:
            self.number_of_congestion_time_steps += 1
            if self.network_environment.verbose_lvl > 3:
                print('\t\tNetwork congestion measured')
        return self.original_check_action

    def done_in_mean_time(self):
        congestion_time_steps_since = self.number_of_congestion_time_steps - self.old_number_of_congestion_time_steps
        self.old_number_of_congestion_time_steps = self.number_of_congestion_time_steps
        msg = 'Network capacity tracker - Timesteps with congestion since last time: {}m\n\t'.format(congestion_time_steps_since)
        return self.original_done_in_mean_time(curr_msg=msg)

    def end_of_environment_message(self, environment_additions=None):
        if environment_additions is None:
            environment_additions = []

        total_msg = 'Number of timesteps with congestion: {}'.format(self.number_of_congestion_time_steps)

        perc_congestion = round(self.number_of_congestion_time_steps / self.network_environment.number_of_steps * 100, 2)
        avg_msg = 'Percentage of congestion issues: {}%'.format(perc_congestion)

        environment_additions.append(total_msg)
        environment_additions.append(avg_msg)
        return self.original_end_of_environment_message(environment_additions)

    def end_of_environment_metrics(self, current_metrics=None):
        if current_metrics is None:
            current_metrics = {}

        current_metrics['time_steps_with_congestion'] = self.number_of_congestion_time_steps
        perc_congestion = round(self.number_of_congestion_time_steps / self.network_environment.number_of_steps * 100, 2)
        current_metrics['perc_of_congestion'] = perc_congestion

        return self.original_end_of_environment_metrics(current_metrics)
