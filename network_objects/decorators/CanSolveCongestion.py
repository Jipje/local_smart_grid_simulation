class CanSolveCongestion:
    def __init__(self, network_object, congestion_kw, congestion_power_index, safety_margin=0.95):
        self.network_object = network_object
        self.congestion_kw = congestion_kw
        self.congestion_power_index = congestion_power_index

        self.excess_power_kw = 0
        self.safety_margin = safety_margin

        # Assign the correct functions to each object
        self.original_check = self.network_object.check_action
        self.original_step = self.network_object.take_step
        self.network_object.take_step = self.take_step
        self.network_object.check_action = self.check_action

    def check_action(self, action_kwh):
        adjusted_action_kwh = action_kwh

        action_kw = adjusted_action_kwh / self.network_object.time_step
        if self.excess_power_kw > 0:
            action_kw = self.excess_power_kw
        adjusted_action_kwh = action_kw * self.network_object.time_step

        if adjusted_action_kwh != action_kwh and self.network_object.verbose_lvl > 3:
            print(f'\t\t{self.network_object.name} battery wanted to do {action_kwh / self.network_object.time_step} but was adjusted to {action_kw} to solve congestion')

        return self.original_check(adjusted_action_kwh)

    def take_step(self, environment_step, action_parameters):
        congestion_power_kw = environment_step[self.congestion_power_index]
        if abs(congestion_power_kw) > abs(self.safety_margin * self.congestion_kw):
            self.excess_power_kw = abs(congestion_power_kw - self.congestion_kw)
        else:
            self.excess_power_kw = 0

        return self.original_step(environment_step, action_parameters)
