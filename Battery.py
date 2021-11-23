import random


class Battery(object):
    def __init__(self, name, max_kwh, max_kw, starting_soc=0):
        self.name = name
        self.state_of_charge_perc = starting_soc
        self.state_of_charge_kwh = starting_soc / 100 * max_kwh

        self.max_kwh = max_kwh
        self.max_kw = max_kw

    def charge(self, charge_kw):
        self.state_of_charge_kwh = self.state_of_charge_kwh + int(charge_kw * 1/60)
        print('Charging {} - Charged to {}kWh'.format(self.name, self.state_of_charge_kwh))

    def discharge(self, discharge_kw):
        self.state_of_charge_kwh = self.state_of_charge_kwh - int(discharge_kw * 1/60)
        print('Discharging {} - Discharged to {}kWh'.format(self.name, self.state_of_charge_kwh))

    def wait(self):
        pass

    def take_action(self):
        chosen_action = random.randint(0, 5)
        if chosen_action == 0:
            self.charge(self.max_kw)
        elif chosen_action == 1:
            self.discharge(self.max_kw)
        else:
            self.wait()
