from network_objects.NetworkObject import NetworkObject


class WindFarm(NetworkObject):
    def __init__(self, name, max_kw, ppa=None, verbose_lvl=3):
        super().__init__(name=name)
        self.max_kw = max_kw
        self.available_kw = 0
        self.ppa = ppa

        self.earnings = 0
        self.old_earnings = self.earnings

        self.ptu_tracker = 0
        self.ptu_total_action = 0
        self.ptu_charge_price = 9999
        self.ptu_discharge_price = -9999

        self.time_step = 1/60
        self.verbose_lvl = verbose_lvl

    def set_available_kw_this_action(self, available_kw):
        self.available_kw = available_kw

    def take_step(self, environment_step, action_parameters):
        charge_price = environment_step[action_parameters[0]]
        discharge_price = environment_step[action_parameters[1]]
        available_kw = environment_step[action_parameters[2]]

        self.set_available_kw_this_action(-1 * available_kw)
        return self.take_imbalance_action(charge_price, discharge_price)

    def take_imbalance_action(self, charge_price, discharge_price, action=None):
        if self.ptu_tracker >= 15:
            self.ptu_reset()
        self.ptu_tracker += 1

        self.ptu_charge_price = charge_price
        self.ptu_discharge_price = discharge_price

        return self.generate_electricity()

    def generate_electricity(self):
        generated_kwh = self.available_kw * self.time_step
        self.ptu_total_action = self.ptu_total_action + generated_kwh
        if self.verbose_lvl > 2:
            print('{} is generating {} kW'.format(self.name, self.available_kw))
        return generated_kwh / self.time_step

    def ptu_reset(self):
        if self.ptu_total_action > 0:
            price_to_use = self.ptu_charge_price
        elif self.ptu_total_action < 0:
            price_to_use = self.ptu_discharge_price
        else:
            price_to_use = 0

        ptu_profits = self.update_earnings(self.ptu_total_action, price_to_use)
        if self.verbose_lvl > 2 or self.verbose_lvl > 1 and abs(ptu_profits) > 100:
            print('PTU reset. Action this PTU was: {}kWh. Prices were {} charge, {} discharge. Earned €{}'.format(self.ptu_total_action, self.ptu_charge_price, self.ptu_discharge_price, ptu_profits))

        self.ptu_tracker = 0
        self.ptu_total_action = 0

    def update_earnings(self, action_kwh, cost):
        # Discharge is a negative action. However that pays us money so we invert the action * cost
        #     Same holds vice versa for charge. A positive action however it costs us money.
        if self.ppa is not None:
            cost = self.ppa
        cost_of_action = -1 * (action_kwh / 1000) * cost
        self.earnings = self.earnings + cost_of_action
        return cost_of_action

    def done_in_mean_time(self):
        earnings_in_mean_time = round(self.earnings - self.old_earnings, 2)
        self.old_earnings = self.earnings
        msg = "{} windfarm - Earnings since last time: €{}".format(self.name, earnings_in_mean_time)
        if 'nan' in msg:
            print('STOP')
        return msg

    def __str__(self):
        return "{} wind farm:\nTotal Earnings: €{}".format(self.name, round(self.earnings, 2))
