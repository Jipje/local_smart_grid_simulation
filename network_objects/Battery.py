from environment.InnaxMetre import InnaxMetre
from helper_objects.strategies.CsvStrategy import CsvStrategy
from helper_objects.cycle_counters.NaiveCycleCounter import NaiveCycleCounter
from network_objects.NetworkObject import NetworkObject


class Battery(NetworkObject):
    def __init__(self, name, max_kwh, max_kw, cycle_counter=None, battery_efficiency=0.9, starting_soc_kwh=None,
                 upper_safety_margin=0.95, lower_safety_margin=0.05, verbose_lvl=3):
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

        if upper_safety_margin > 1 or upper_safety_margin < 0:
            raise ValueError('upper_safety_margin must be between 0 and 1')
        if lower_safety_margin > 1 or lower_safety_margin < 0 or lower_safety_margin > upper_safety_margin:
            raise ValueError('lower_safety_margin must be between 0 and 1 and smaller than the upper safety margin')

        self.max_kwh = max_kwh
        self.max_kw = max_kw
        self.efficiency = battery_efficiency
        self.upper_safety_margin = upper_safety_margin
        self.lower_safety_margin = lower_safety_margin

        if cycle_counter is None:
            self.cycle_counter = NaiveCycleCounter(self.max_kwh)
        else:
            self.cycle_counter = cycle_counter

        self.innax_metre = InnaxMetre(verbose_lvl=verbose_lvl)

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
        self.update_state_of_charge(charged_kwh)

        return charged_kwh / self.time_step

    def discharge(self, discharge_kw):
        potential_discharged_kwh = -1 * int(discharge_kw * self.time_step)
        discharged_kwh = self.check_action(potential_discharged_kwh)
        self.update_state_of_charge(discharged_kwh)

        return discharged_kwh / self.time_step

    def wait(self):
        return 0

    def check_action(self, action_kwh):
        largest_kwh_action_battery = self.max_kw * self.time_step
        # The action can't be larger than the max_kw
        if abs(action_kwh) > largest_kwh_action_battery:
            if action_kwh > 0:
                adjusted_action_kwh = largest_kwh_action_battery
            elif action_kwh < 0:
                adjusted_action_kwh = -1 * largest_kwh_action_battery
        else:
            adjusted_action_kwh = action_kwh

        current_soc = self.state_of_charge_kwh
        future_soc = current_soc + adjusted_action_kwh
        adjusted_max = int(self.upper_safety_margin * self.max_kwh)
        adjusted_min = int(self.lower_safety_margin * self.max_kwh)
        # The SoC can't be higher than the max_kwh. Or lower than 0.
        if future_soc > adjusted_max:
            adjusted_action_kwh = int((adjusted_max - current_soc) * 1 / self.efficiency)
        if future_soc < adjusted_min:
            adjusted_action_kwh = adjusted_min - current_soc

        return adjusted_action_kwh

    def take_step(self, environment_step, action_parameters) -> int:
        charge_price = environment_step[action_parameters[0]]
        discharge_price = environment_step[action_parameters[1]]

        self.number_of_steps += 1
        self.average_soc_tracker = self.average_soc_tracker + self.state_of_charge_kwh
        self.average_soc = int(self.average_soc_tracker / self.number_of_steps)
        self.innax_metre.update_prices(charge_price, discharge_price)
        return 0

    def take_action(self, action, action_kw=None):
        if action not in ['CHARGE', 'DISCHARGE', 'WAIT']:
            raise AttributeError('Please offer an actual action to the battery object')
        if action_kw is None:
            action_kw = self.max_kw
        if action_kw > self.max_kw or action_kw < 0:
            raise AttributeError(f'action_kw should not be larger than the max_kw: {self.max_kw}kW\n'
                                 'action_kw should also be larger than 0. Discharge is handeled by the object.')

        if action != 'WAIT' and action != self.last_action:
            self.change_of_direction_tracker += 1
            self.last_action = action

        if action == 'CHARGE':
            action_kw = self.charge(action_kw)
        elif action == 'DISCHARGE':
            action_kw = self.discharge(action_kw)
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
        msg = f"{self.name} battery - " \
              f"Current SoC: {self.state_of_charge_kwh}kWh - " \
              f"Average SoC: {self.average_soc}kWh - " \
              f"{self.cycle_counter.done_in_mean_time()} - " \
              f"Changes of direction in mean time: {changes_of_direction_in_mean_time} - " \
              f"Earnings since last time: €{earnings_in_mean_time}"
        return msg

    def end_of_environment_message(self, num_of_days=None):
        if num_of_days is None:
            num_of_days = self.number_of_steps / self.time_step / 60 / 24
        earnings_str = '{:,.2f}'.format(self.earnings())
        average_num_changes_of_direction = round(self.change_of_direction_tracker / num_of_days, 2)
        average_num_of_cycles = round(self.cycle_counter.cycle_count / num_of_days, 2)
        average_earnings_str = '{:,.2f}'.format(self.earnings() / num_of_days)
        res_msg = f"\n{self.name} battery:\n\t" \
            f"Total changes of direction: {self.change_of_direction_tracker}\n\t" \
            f"Total number of cycles: {self.cycle_counter.cycle_count}\n\t" \
            f"Total earnings: €{earnings_str}\n\t" \
            "--------------------\n\t" \
            f"Average SoC: {self.average_soc}kWh\n\t" \
            f"Average changes of direction: {average_num_changes_of_direction}\n\t" \
            f"Average number of cycles: {average_num_of_cycles}\n\t" \
            f"Average earnings: €{average_earnings_str}"
        return res_msg

    def __str__(self):
        return f"{self.name} battery:\n" \
               f"Current SoC: {self.state_of_charge_kwh}kWh\n" \
               f"Average SoC: {self.average_soc}kWh\n" \
               f"Total number of changes of direction: {self.change_of_direction_tracker}\n" \
               f"Total number of cycles: {round(self.cycle_counter.cycle_count, 2)}\n" \
               f"Total Earnings: €{round(self.earnings(), 2)}"
