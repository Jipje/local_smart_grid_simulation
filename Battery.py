import random


class Battery(object):
    def __init__(self, name, max_kwh, max_kw, starting_soc=0):
        self.name = name
        self.state_of_charge_kwh = starting_soc / 100 * max_kwh

        self.max_kwh = max_kwh
        self.max_kw = max_kw
        self.earnings = 0

    def update_earnings(self, action_kw, cost):
        # Discharge is a negative action. However that pays us money so we invert the action * cost
        #     Same holds vice versa for charge. A positive action however it costs us money.
        cost_of_action = -1 * (action_kw / 1000) * cost
        self.earnings = self.earnings + cost_of_action

    def charge(self, charge_kw, charge_price):
        charged_kw = int(charge_kw * 1/60)
        try:
            self.check_action(charged_kw)
            self.state_of_charge_kwh = self.state_of_charge_kwh + charged_kw
            print('Charging {} - Charged to {}kWh'.format(self.name, self.state_of_charge_kwh))
            self.update_earnings(charged_kw, charge_price)
        except OverflowError as err:
            print('No charge action allowed: {}'.format(err.args))

    def discharge(self, discharge_kw, discharge_price):
        discharged_kw = -1 * int(discharge_kw * 1/60)
        try:
            self.check_action(discharged_kw)
            self.state_of_charge_kwh = self.state_of_charge_kwh + discharged_kw
            print('Discharging {} - Discharged to {}kWh'.format(self.name, self.state_of_charge_kwh))
            self.update_earnings(discharged_kw, discharge_price)
        except OverflowError as err:
            print('No discharge action allowed: {}'.format(err.args))

    def wait(self):
        pass

    def check_action(self, action):
        current_soc = self.state_of_charge_kwh
        future_soc = current_soc + action
        # The SoC can't be higher than the max. Or lower than 0.
        if future_soc > self.max_kwh or future_soc < 0:
            raise OverflowError('Battery action is overwriting battery state of charge constraints')
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
