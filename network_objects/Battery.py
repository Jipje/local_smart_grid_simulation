from helper_objects.StrategyBattery import StrategyBattery
from network_objects.NetworkObject import NetworkObject


class Battery(NetworkObject):
    def __init__(self, name, max_kwh, max_kw, battery_strategy_csv, battery_efficiency=0.9, starting_soc_kwh=None, verbose_lvl=3):
        super().__init__(name)

        if max_kwh <= 0:
            raise ValueError('Error while initiating Battery {}. max_kwh should be larger than 0.'.format(name))
        if max_kw <= 0:
            raise ValueError('Error while initiating Battery {}. max_kw should be larger than 0.'.format(name))
        if battery_efficiency <= 0 or battery_efficiency > 1:
            raise ValueError('Error while initiating Battery {}. battery_efficiency should be larger than 0 and '
                             'smaller than or equal to 1.'.format(name))

        if starting_soc_kwh is None:
            self.state_of_charge_kwh = int(0.5 * max_kwh)
        else:
            if starting_soc_kwh > max_kwh or starting_soc_kwh < 0:
                raise ValueError('Error while initiating Battery {}. starting_soc cant be larger than max_kwh or '
                                 'negative.'.format(name))
            self.state_of_charge_kwh = starting_soc_kwh

        self.max_kwh = max_kwh
        self.max_kw = max_kw
        self.efficiency = battery_efficiency

        self.strategy = StrategyBattery(strategy_csv=battery_strategy_csv)

        self.earnings = 0
        self.old_earnings = self.earnings
        self.naive_cycle_counter = 0

        self.ptu_tracker = 0
        self.ptu_total_action = 0
        self.ptu_charge_price = 9999
        self.ptu_discharge_price = -9999

        self.time_step = 1/60
        self.verbose_lvl = verbose_lvl

    def update_earnings(self, action_kwh, cost):
        # Discharge is a negative action. However that pays us money so we invert the action * cost
        #     Same holds vice versa for charge. A positive action however it costs us money.
        cost_of_action = -1 * (action_kwh / 1000) * cost
        self.earnings = self.earnings + cost_of_action
        return cost_of_action

    def update_state_of_charge(self, action_kwh):
        physical_action = action_kwh
        if action_kwh > 0:
            physical_action = int(action_kwh * self.efficiency)

        self.state_of_charge_kwh = self.state_of_charge_kwh + physical_action

        naive_cycle_count = abs(physical_action) / self.max_kwh / 2
        self.naive_cycle_counter += naive_cycle_count

    def charge(self, charge_kw, charge_price):
        potential_charged_kwh = int(charge_kw * self.time_step)
        charged_kwh = self.check_action(potential_charged_kwh)
        self.ptu_total_action = self.ptu_total_action + charged_kwh

        if potential_charged_kwh != charged_kwh and self.verbose_lvl > 2:
            print('Charge action adjusted due to constraints')

        self.update_state_of_charge(charged_kwh)
        if self.verbose_lvl > 2:
            print('Charging {} - Charged to {}kWh'.format(self.name, self.state_of_charge_kwh))

    def discharge(self, discharge_kw, discharge_price):
        potential_discharged_kwh = -1 * int(discharge_kw * self.time_step)
        discharged_kwh = self.check_action(potential_discharged_kwh)
        self.ptu_total_action = self.ptu_total_action + discharged_kwh

        if potential_discharged_kwh != discharged_kwh and self.verbose_lvl > 2:
            print('Discharge action adjusted due to constraints')

        self.update_state_of_charge(discharged_kwh)
        if self.verbose_lvl > 2:
            print('Discharging {} - Discharged to {}kWh'.format(self.name, self.state_of_charge_kwh))

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

    def wait(self):
        pass

    def check_action(self, action_kwh):
        largest_kwh_action_battery = self.max_kw * self.time_step
        # The action can't be larger than the max_kw
        if abs(action_kwh) > largest_kwh_action_battery:
            if action_kwh > 0:
                adjusted_action = largest_kwh_action_battery
            elif action_kwh < 0:
                adjusted_action = -1 * largest_kwh_action_battery
        else:
            adjusted_action = action_kwh

        current_soc = self.state_of_charge_kwh
        future_soc = current_soc + adjusted_action
        # The SoC can't be higher than the max_kwh. Or lower than 0.
        if future_soc > self.max_kwh:
            adjusted_action = int((self.max_kwh - current_soc) * 1 / self.efficiency)
        if future_soc < 0:
            adjusted_action = 0 - current_soc

        return adjusted_action

    def take_step(self, environment_step, action_parameters):
        charge_price = environment_step[action_parameters[0]]
        discharge_price = environment_step[action_parameters[1]]
        self.take_imbalance_action(charge_price, discharge_price)

    def take_imbalance_action(self, charge_price, discharge_price, action=None):
        if self.ptu_tracker >= 15:
            self.ptu_reset()
        self.ptu_tracker += 1

        self.ptu_charge_price = charge_price
        self.ptu_discharge_price = discharge_price

        if action is None:
            soc_perc = int(self.state_of_charge_kwh / self.max_kwh * 100)
            action = self.strategy.make_decision(charge_price, discharge_price, soc_perc)

        if action == 'CHARGE':
            chosen_action = 0
        elif action == 'DISCHARGE':
            chosen_action = 1
        else:
            chosen_action = 2

        if chosen_action == 0:
            self.charge(self.max_kw, charge_price)
        elif chosen_action == 1:
            self.discharge(self.max_kw, discharge_price)
        else:
            self.wait()

    def done_in_mean_time(self):
        earnings_in_mean_time = round(self.earnings - self.old_earnings, 2)
        self.old_earnings = self.earnings
        msg = "{} battery - Current SoC: {}kWh - Earnings since last time: €{} - Total cycles: {}".format(self.name, self.state_of_charge_kwh, earnings_in_mean_time, round(self.naive_cycle_counter, 2))
        return msg

    def __str__(self):
        return "{} battery:\nCurrent SoC: {}kWh\nTotal number of cycles: {}\nTotal Earnings: €{}".format(self.name, self.state_of_charge_kwh, round(self.naive_cycle_counter, 2), round(self.earnings, 2))
