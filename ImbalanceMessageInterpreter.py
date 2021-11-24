min_default = 99999
max_default = -99999


class ImbalanceMessageInterpreter:
    def __init__(self):
        self.max_price = 0
        self.min_price = 0
        self.mid_price = 0
        self.actual_max = 0
        self.actual_min = 0
        self.update_counter = 0
        self.reset()

    def reset(self):
        self.max_price = max_default
        self.min_price = min_default
        self.mid_price = 0
        self.actual_max = max_default
        self.actual_min = min_default
        self.update_counter = 0

    def update(self, new_mid_price, new_max_price=max_default, new_min_price=min_default):
        # The sent mid price is always leading
        self.mid_price = new_mid_price

        self.update_counter += 1
        if self.update_counter > 15:
            raise OverflowError("Giga Forecast works for quarterly data, you have offered this generator more than 15 minute data")

        # If a max price is offered, check to see if it is higher than the previously known max price
        if new_max_price != max_default and new_max_price > self.actual_max:
            self.max_price = new_max_price
            self.actual_max = new_max_price
        # If a min price is offered, check to see if it is lower than the previously known min price
        if new_min_price != min_default and new_min_price < self.actual_min:
            self.min_price = new_min_price
            self.actual_min = new_min_price

        # If there has never been a min measurement. Take the max_price (if that has been given)
        if self.actual_min == min_default and self.actual_max != max_default:
            self.min_price = self.actual_max
        # If there has never been a max measurement. Take the min_price (if that has been given)
        if self.actual_max == max_default and self.actual_min != min_default:
            self.max_price = self.actual_min

        # If both have never been defined
        # Take mid-price
        if self.actual_max == max_default and self.actual_min == min_default:
            self.max_price = self.mid_price
            self.min_price = self.mid_price

    def get_current_price(self):
        return self.mid_price, self.max_price, self.min_price

    def get_charge_price(self):
        return self.max_price

    def get_discharge_price(self):
        return self.min_price
