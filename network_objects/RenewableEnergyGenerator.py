from environment.InnaxMetre import InnaxMetre
from network_objects.NetworkObject import NetworkObject


class RenewableEnergyGenerator(NetworkObject):
    def __init__(self, name, max_kw, ppa=None, verbose_lvl=3):
        super().__init__(name=name)
        self.max_kw = max_kw
        self.available_kw = 0
        self.ppa = ppa

        self.innax_metre = InnaxMetre(verbose_lvl=verbose_lvl)

        self.earnings = self.innax_metre.get_earnings
        self.old_earnings = self.earnings()

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
        if self.verbose_lvl > 3:
            print('\t{} deciding what to do.'.format(self.name))
        self.innax_metre.update_prices(charge_price, discharge_price)
        return self.generate_electricity()

    def generate_electricity(self):
        generated_kwh = self.available_kw * self.time_step
        if self.verbose_lvl > 3:
            print('\t{} is generating {} kW'.format(self.name, self.available_kw))

        self.innax_metre.measure_imbalance_action(generated_kwh)
        return generated_kwh / self.time_step

    def done_in_mean_time(self):
        earnings_in_mean_time = round(self.earnings() - self.old_earnings, 2)
        self.old_earnings = self.earnings()
        msg = "{} renewable energy generator - Earnings since last time: €{}".format(self.name, earnings_in_mean_time)
        if 'nan' in msg:
            print('STOP')
        return msg

    def end_of_environment_message(self, num_of_days=None):
        res_msg = "\n{} renewable energy generator:\n\t" \
            "Total earnings: €{}".format(self.name, '{:,.2f}'.format(self.earnings()))
        if num_of_days is not None:
            avg_earnings_str = '{:,.2f}'.format(self.earnings() / num_of_days)
            res_msg = res_msg + "\n\t --------------------\n\tAverage earnings: €{}".format(avg_earnings_str)
        return res_msg

    def end_of_environment_metrics(self):
        earnings_str = '{:,.2f}'.format(self.earnings())
        snake_case_name = (self.name.lower()).replace(' ', '_')
        res = {
            f'{snake_case_name}_revenue': earnings_str
        }
        return res

    def __str__(self):
        return "{} renewable energy generator:\nTotal Earnings: €{}".format(self.name, round(self.earnings(), 2))
