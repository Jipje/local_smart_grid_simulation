
class SmartWindnetInterpolater(object):
    def __init__(self, number_of_minutes=5):
        self.number_of_minutes = number_of_minutes

    def trivial_kw_per_minute(self, total_kwh):
        return round(total_kwh / self.number_of_minutes * 60, 2)

    def kw_per_minute(self, total_kwh, previous_kwh=None, next_kwh=None):
        if previous_kwh is None:
            previous_average = self.trivial_kw_per_minute(total_kwh)
        else:
            previous_average = self.trivial_kw_per_minute(previous_kwh)

        if next_kwh is None:
            next_average = self.trivial_kw_per_minute(total_kwh)
        else:
            next_average = self.trivial_kw_per_minute(next_kwh)

        current_average = self.trivial_kw_per_minute(total_kwh)

        smallest_diff = min(abs(current_average - previous_average), (current_average - next_average))
        diff_per_step = smallest_diff / 6

        res = []
        for i in range(self.number_of_minutes):
            difference_this_step = (2 - i) * diff_per_step
            res.append(current_average + difference_this_step)
        return res
