from environment.NetworkEnvironment import NetworkEnvironment


class TotalNetworkCapacityTracker(NetworkEnvironment):
    def __init__(self, verbose_lvl: int, max_kw: int):
        super().__init__(verbose_lvl)
        self.maximum_kw = abs(max_kw)

        self.number_of_congestion_time_steps = 0
        self.old_number_of_congestion_time_steps = self.number_of_congestion_time_steps

    def take_step(self, environment_step) -> int:
        total_network_step = super().take_step(environment_step)
        if abs(total_network_step) > self.maximum_kw:
            self.number_of_congestion_time_steps += 1
            if self.verbose_lvl > 2:
                print('Network congestion measured')
        return total_network_step

    def done_in_mean_time(self):
        congestion_time_steps_since = self.number_of_congestion_time_steps - self.old_number_of_congestion_time_steps
        self.old_number_of_congestion_time_steps = self.number_of_congestion_time_steps
        msg = 'Timesteps with congestion since last time: {}m\n'.format(congestion_time_steps_since)
        res_msg = super().done_in_mean_time()
        return msg + res_msg
