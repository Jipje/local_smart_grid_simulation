import random


class Battery(object):
    def __init__(self, name, max_kwh, max_kw, battery_efficiency=0.9, starting_soc_kwh=None):
        self.name = name

        if max_kwh <= 0:
            raise ValueError('Error while initiating Battery {}. max_kwh should be larger than 0.'.format(name))
        if max_kw <= 0:
            raise ValueError('Error while initiating Battery {}. max_kw should be larger than 0.'.format(name))
        if battery_efficiency <= 0 or battery_efficiency > 1:
            raise ValueError('Error while initiating Battery {}. battery_efficiency should be larger than 0 and '
                             'smaller than or equal to 1.'.format(name))

        if starting_soc_kwh is None:
            self.state_of_charge_kwh = 0.5 * max_kwh
        else:
            if starting_soc_kwh > max_kwh or starting_soc_kwh < 0:
                raise ValueError('Error while initiating Battery {}. starting_soc cant be larger than max_kwh or '
                                 'negative.'.format(name))
            self.state_of_charge_kwh = starting_soc_kwh

        self.max_kwh = max_kwh
        self.max_kw = max_kw
        self.efficiency = battery_efficiency
        self.earnings = 0

    def update_earnings(self, action_kw, cost):
        # Discharge is a negative action. However that pays us money so we invert the action * cost
        #     Same holds vice versa for charge. A positive action however it costs us money.
        cost_of_action = -1 * (action_kw / 1000) * cost
        self.earnings = self.earnings + cost_of_action

    def charge(self, charge_kw, charge_price):
        charged_kw = int(charge_kw * 1/60)
        try:
            charged_kw = self.check_action(charged_kw)
            self.state_of_charge_kwh = self.state_of_charge_kwh + int(charged_kw * self.efficiency)
            print('Charging {} - Charged to {}kWh'.format(self.name, self.state_of_charge_kwh))
            self.update_earnings(charged_kw, charge_price)
        except OverflowError as err:
            print('No charge action allowed: {}'.format(err.args))

    def discharge(self, discharge_kw, discharge_price):
        discharged_kw = -1 * int(discharge_kw * 1/60)
        try:
            discharged_kw = self.check_action(discharged_kw)
            self.state_of_charge_kwh = self.state_of_charge_kwh + discharged_kw
            print('Discharging {} - Discharged to {}kWh'.format(self.name, self.state_of_charge_kwh))
            self.update_earnings(discharged_kw, discharge_price)
        except OverflowError as err:
            print('No discharge action allowed: {}'.format(err.args))

    def wait(self):
        pass

    def check_action(self, action):
        adjusted_action = action
        current_soc = self.state_of_charge_kwh
        future_soc = current_soc + action
        # The SoC can't be higher than the max. Or lower than 0.
        if future_soc > self.max_kwh:
            adjusted_action = self.max_kwh - current_soc
        if future_soc < 0:
            adjusted_action = current_soc - 0
        if abs(action) > self.max_kw:
            raise OverflowError('Battery action is overwriting battery action constraints')
        return adjusted_action

    def take_action(self, charge_price, discharge_price):
        chosen_action = random.randint(0, 5)
        if chosen_action == 0:
            self.charge(self.max_kw, charge_price)
        elif chosen_action == 1:
            self.discharge(self.max_kw, discharge_price)
        else:
            self.wait()

    def __str__(self):
        return "{} battery:\nCurrent SoC: {}\nTotal Earnings: {}\n".format(self.name, self.state_of_charge_kwh, self.earnings)
