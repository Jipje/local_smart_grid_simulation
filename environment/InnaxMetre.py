class InnaxMetre(object):
    def __init__(self, verbose_lvl=3):
        self.verbose_lvl = verbose_lvl
        self.earnings = 0

        self.ptu_tracker = 0
        self.ptu_total_action = 0
        self.ptu_charge_price = 9999
        self.ptu_discharge_price = -9999

    def get_earnings(self):
        return self.earnings

    def update_prices(self, charge_price, discharge_price):
        if self.ptu_tracker >= 15:
            self.ptu_reset()
        self.ptu_tracker += 1

        self.ptu_charge_price = charge_price
        self.ptu_discharge_price = discharge_price

    def measure_imbalance_action(self, action_kwh):
        self.ptu_total_action = self.ptu_total_action + action_kwh

    def ptu_reset(self):
        if self.ptu_total_action > 0:
            price_to_use = self.ptu_charge_price
        elif self.ptu_total_action < 0:
            price_to_use = self.ptu_discharge_price
        else:
            price_to_use = 0

        ptu_profits = self.update_earnings(self.ptu_total_action, price_to_use)
        if self.verbose_lvl > 3:
            print(f'\t\tPTU reset. Action this PTU was: {self.ptu_total_action}kWh. '
                  f'Prices were €{self.ptu_charge_price} charge, €{self.ptu_discharge_price} discharge. '
                  f'Earned €{ptu_profits}')

        self.ptu_tracker = 0
        self.ptu_total_action = 0

    def update_earnings(self, action_kwh, cost):
        # Discharge is a negative action. However that pays us money so we invert the action * cost
        #     Same holds vice versa for charge. A positive action however it costs us money.
        cost_of_action = -1 * (action_kwh / 1000) * cost
        self.earnings = self.earnings + cost_of_action
        return cost_of_action
