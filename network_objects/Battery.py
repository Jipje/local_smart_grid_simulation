from environment.InnaxMetre import InnaxMetre
from helper_objects.strategies.CsvStrategy import CsvStrategy
from helper_objects.cycle_counters.NaiveCycleCounter import NaiveCycleCounter
from network_objects.NetworkObject import NetworkObject


class Battery(NetworkObject):
    def __init__(self, name, max_kwh, max_kw, battery_strategy_csv, cycle_counter=None, battery_efficiency=0.9, starting_soc_kwh=None, verbose_lvl=3):
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

        if cycle_counter is None:
            self.cycle_counter = NaiveCycleCounter(self.max_kwh)
        else:
            self.cycle_counter = cycle_counter

        self.strategy = CsvStrategy(name=battery_strategy_csv, strategy_csv=battery_strategy_csv)
        self.innax_metre = InnaxMetre()

        self.earnings = self.innax_metre.get_earnings
        self.old_earnings = 0
        self.average_soc_tracker = 0
        self.average_soc = 0
        self.last_action = 'WAIT'
        self.change_of_direction_tracker = 0
        self.old_changes_of_direction = self.change_of_direction_tracker

        self.number_of_steps = 0
        self.time_step = 1/60
        self.verbose_lvl = verbose_lvl

    def update_state_of_charge(self, action_kwh):
        physical_action = action_kwh
        if action_kwh > 0:
            physical_action = int(action_kwh * self.efficiency)

        self.cycle_counter.add_cycle(physical_action)
        self.state_of_charge_kwh = self.state_of_charge_kwh + physical_action

    def charge(self, charge_kw):
        potential_charged_kwh = int(charge_kw * self.time_step)
        charged_kwh = self.check_action(potential_charged_kwh)

        if potential_charged_kwh != charged_kwh and self.verbose_lvl > 3:
            print('\t\tCharge action adjusted due to constraints')

        self.update_state_of_charge(charged_kwh)

        return charged_kwh / self.time_step

    def discharge(self, discharge_kw):
        potential_discharged_kwh = -1 * int(discharge_kw * self.time_step)
        discharged_kwh = self.check_action(potential_discharged_kwh)

        if potential_discharged_kwh != discharged_kwh and self.verbose_lvl > 3:
            print('\t\tDischarge action adjusted due to constraints')

        self.update_state_of_charge(discharged_kwh)

        return discharged_kwh / self.time_step

    def wait(self):
        return 0

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
        adjusted_max = int(0.95 * self.max_kwh)
        adjusted_min = int(0.05 * self.max_kwh)
        # The SoC can't be higher than the max_kwh. Or lower than 0.
        if future_soc > adjusted_max:
            adjusted_action = int((adjusted_max - current_soc) * 1 / self.efficiency)
        if future_soc < adjusted_min:
            adjusted_action = adjusted_min - current_soc

        return adjusted_action

    def take_step(self, environment_step, action_parameters) -> int:
        charge_price = environment_step[action_parameters[0]]
        discharge_price = environment_step[action_parameters[1]]

        self.number_of_steps += 1
        self.average_soc_tracker = self.average_soc_tracker + self.state_of_charge_kwh
        self.average_soc = int(self.average_soc_tracker / self.number_of_steps)

        return self.take_imbalance_action(charge_price, discharge_price)

    def take_imbalance_action(self, charge_price, discharge_price, action=None):
        self.innax_metre.update_prices(charge_price, discharge_price)

        if action is None:
            soc_perc = int(self.state_of_charge_kwh / self.max_kwh * 100)
            action = self.strategy.make_decision(charge_price, discharge_price, soc_perc)

        if action != 'WAIT' and action != self.last_action:
            self.change_of_direction_tracker += 1
            self.last_action = action

        if action == 'CHARGE':
            chosen_action = 0
        elif action == 'DISCHARGE':
            chosen_action = 1
        else:
            chosen_action = 2

        if chosen_action == 0:
            action_kw = self.charge(self.max_kw)
        elif chosen_action == 1:
            action_kw = self.discharge(self.max_kw)
        else:
            action_kw = self.wait()

        action_kwh = action_kw * self.time_step
        self.innax_metre.measure_imbalance_action(action_kwh)

        if self.verbose_lvl > 3:
            print('\t{} battery is doing {}. Current SoC: {}kWh'.format(self.name, action_kw, self.state_of_charge_kwh))

        return action_kw

    def done_in_mean_time(self):
        earnings_in_mean_time = round(self.earnings() - self.old_earnings, 2)
        changes_of_direction_in_mean_time = round(self.change_of_direction_tracker - self.old_changes_of_direction, 2)
        self.old_changes_of_direction = self.change_of_direction_tracker
        self.old_earnings = self.earnings()
        msg = "{} battery - " \
              "Current SoC: {}kWh - " \
              "Average SoC: {}kWh - " \
              "{} - " \
              "Changes of direction in mean time: {} - " \
              "Earnings since last time: €{}".format(self.name, self.state_of_charge_kwh, self.average_soc, self.cycle_counter.done_in_mean_time(), changes_of_direction_in_mean_time, earnings_in_mean_time)
        return msg

    def end_of_environment_message(self, num_of_days=None):
        if num_of_days is None:
            num_of_days = self.number_of_steps / self.time_step / 60 / 24
        earnings_str = '{:,.2f}'.format(self.earnings())
        average_num_changes_of_direction = round(self.change_of_direction_tracker / num_of_days, 2)
        average_num_of_cycles = round(self.cycle_counter.cycle_count / num_of_days, 2)
        average_earnings_str = '{:,.2f}'.format(self.earnings() / num_of_days)
        res_msg = "\n{} battery:\n\t" \
            "Total changes of direction: {}\n\t" \
            "Total number of cycles: {}\n\t" \
            "Total earnings: €{}\n\t" \
            "--------------------\n\t" \
            "Average SoC: {}kWh\n\t" \
            "Average changes of direction: {}\n\t" \
            "Average number of cycles: {}\n\t" \
            "Average earnings: €{}".format(self.name,
                                          self.change_of_direction_tracker, self.cycle_counter.cycle_count,
                                          earnings_str, self.average_soc, average_num_changes_of_direction,
                                          average_num_of_cycles, average_earnings_str)
        return res_msg

    def __str__(self):
        return "{} battery:\nCurrent SoC: {}kWh\nAverage SoC: {}kWh\nTotal number of changes of direction: {}\nTotal number of cycles: {}\nTotal Earnings: €{}".format(self.name, self.state_of_charge_kwh, self.average_soc, self.change_of_direction_tracker, round(self.cycle_counter.cycle_count, 2), round(self.earnings(), 2))
