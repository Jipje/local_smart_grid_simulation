
class SmartWindnetInterpolater(object):
    def __init__(self, number_of_minutes=5):
        self.number_of_minutes = number_of_minutes

    def trivial_kw_per_minute(self, total_kwh):
        return round(total_kwh / self.number_of_minutes * 60, 2)

    def kw_per_minute(self, current_kw, previous_kw=None, next_kw=None):
        average_diff = abs(current_kw - previous_kw) + abs(current_kw - next_kw) / 2
        smallest_diff = min(current_kw, average_diff)

        slope_factor = 0.3
        parabole_factor = 0.2

        if previous_kw > current_kw and next_kw > current_kw:
            # current_kw is a dip
            first_kw = current_kw + (smallest_diff * 0.3 * parabole_factor)
            second_kw = current_kw + (smallest_diff * 0.2 * parabole_factor)

            third_kw = current_kw + (smallest_diff * 0.2 * parabole_factor)
            fourth_kw = current_kw + (smallest_diff * 0.3 * parabole_factor)

            current_kw = current_kw - (smallest_diff * parabole_factor)

        elif previous_kw < current_kw and next_kw < current_kw:
            # current_kw is a peak
            first_kw = current_kw - (smallest_diff * 0.3 * parabole_factor)
            second_kw = current_kw - (smallest_diff * 0.2 * parabole_factor)

            third_kw = current_kw - (smallest_diff * 0.2 * parabole_factor)
            fourth_kw = current_kw - (smallest_diff * 0.3 * parabole_factor)

            current_kw = current_kw + (smallest_diff * parabole_factor)

        elif previous_kw <= current_kw and next_kw > current_kw:
            # current_kw will be increasing
            first_kw = current_kw - (smallest_diff * slope_factor)
            second_kw = current_kw - (smallest_diff * 0.5 * slope_factor)
            third_kw = current_kw + (smallest_diff * 0.5 * slope_factor)
            fourth_kw = current_kw + (smallest_diff * slope_factor)
        elif previous_kw > current_kw and next_kw <= current_kw:
            # current_kw will be decreasing
            first_kw = current_kw + (smallest_diff * slope_factor)
            second_kw = current_kw + (smallest_diff * 0.5 * slope_factor)
            third_kw = current_kw - (smallest_diff * 0.5 * slope_factor)
            fourth_kw = current_kw - (smallest_diff * slope_factor)
        else:
            first_kw = current_kw
            second_kw = current_kw
            third_kw = current_kw
            fourth_kw = current_kw

        res = [first_kw, second_kw, current_kw, third_kw, fourth_kw]
        return res


if __name__ == '__main__':
    smart_windnet_interpolater = SmartWindnetInterpolater()
    print(smart_windnet_interpolater.kw_per_minute(10, 20, 30))
    print(smart_windnet_interpolater.kw_per_minute(20, 10, 30))
