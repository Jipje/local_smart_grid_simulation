

class NaiveCycleCounter(object):
    def __init__(self, max_kwh):
        self.max_kwh = max_kwh
        self.cycle_count = 0

        self.old_cycle_count = 0

    def add_cycle(self, physical_action_kwh):
        naive_cycle_count = abs(physical_action_kwh) / self.max_kwh / 2
        self.cycle_count = self.cycle_count + naive_cycle_count

    def done_in_mean_time(self):
        cycles_in_mean_time = round(self.cycle_count - self.old_cycle_count, 2)
        self.old_cycle_count = self.cycle_count
        return "Cycles in mean time: {}".format(cycles_in_mean_time)
