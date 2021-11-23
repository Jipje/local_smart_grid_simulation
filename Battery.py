import random


class Battery(object):
    def __init__(self, name, max_kwh, max_kw, starting_soc=0):
        self.name = name
        self.state_of_charge_perc = starting_soc
        self.state_of_charge_kwh = starting_soc / 100 * max_kwh

        self.max_kwh = max_kwh
        self.max_kw = max_kw
        self.earnings = 0

    def update_earnings(self, action, cost):
        cost_of_action = action / 1000 * cost
        self.earnings = self.earnings + cost_of_action

    def charge(self, charge_kw, charge_price):
        charged_kw = int(charge_kw * 1/60)
        self.state_of_charge_kwh = self.state_of_charge_kwh + charged_kw
        print('Charging {} - Charged to {}kWh'.format(self.name, self.state_of_charge_kwh))
        self.update_earnings(charged_kw, charge_price)

    def discharge(self, discharge_kw, discharge_price):
        discharged_kw = -1 * int(discharge_kw * 1/60)
        self.state_of_charge_kwh = self.state_of_charge_kwh + discharged_kw
        print('Discharging {} - Discharged to {}kWh'.format(self.name, self.state_of_charge_kwh))
        self.update_earnings(discharged_kw, discharge_price)

    def wait(self):
        pass

    def take_action(self, charge_price, discharge_price):
        chosen_action = random.randint(0, 5)
        if chosen_action == 0:
            self.charge(self.max_kw, charge_price)
        elif chosen_action == 1:
            self.discharge(self.max_kw, discharge_price)
        else:
            self.wait()
