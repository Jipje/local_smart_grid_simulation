import os

from pandas import NaT

from environment.ImbalanceEnvironment import ImbalanceEnvironment
from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual
from helper_objects.congestion_helper.month_congestion_size_and_timer import get_month_congestion_timings
from helper_objects.strategies.CsvStrategy import CsvStrategy
from helper_objects.strategies.DischargeUntilStrategy import DischargeUntilStrategy
from main import run_simulation_from_dict_of_df
import pandas as pd
import dateutil.tz
import datetime as dt

from network_objects.Battery import Battery
from network_objects.RenewableEnergyGenerator import RenewableEnergyGenerator
from network_objects.control_strategies.ModesOfOperationController import ModesOfOperationController
from network_objects.control_strategies.MonthOfModesOfOperationController import MonthOfModesOfOperationController
from network_objects.control_strategies.SolveCongestionAndLimitedChargeControlTower import \
    SolveCongestionAndLimitedChargeControlTower

utc = dateutil.tz.tzutc()


class Fitness(object):
    def __init__(self, verbose_lvl=-1, transportation_kw=2000, congestion_kw=14000, congestion_safety_margin=0.99):
        self.verbose_lvl = verbose_lvl
        self.transportation_kw = transportation_kw
        self.congestion_kw = congestion_kw
        self.congestion_safety_margin = congestion_safety_margin

        self.data_folder = '..{0}data{0}'.format(os.path.sep)
        self.scenario = self.data_folder + 'environments{0}lelystad_1_2021.csv'.format(os.path.sep)
        try:
            res_df = pd.read_csv(self.scenario)
        except FileNotFoundError:
            try:
                self.data_folder = f'data{os.path.sep}'
                self.scenario = self.data_folder + 'environments{0}lelystad_1_2021.csv'.format(os.path.sep)
                res_df = pd.read_csv(self.scenario)
            except FileNotFoundError:
                self.data_folder = '..{0}..{0}data{0}'.format(os.path.sep)
                self.scenario = self.data_folder + 'environments{0}lelystad_1_2021.csv'.format(os.path.sep)
                res_df = pd.read_csv(self.scenario)


        if 'lelystad_1' in self.scenario:
            self.scenario_name = 'Lelystad 1 - 19 MW Solar Farm, 14MW connection'
        self.scenario_df = res_df.to_dict('records')
        self.congestion_df = get_month_congestion_timings(
            solarvation_identifier='{1}environments{0}lelystad_1_2021.csv'.format(os.path.sep, self.data_folder),
            strategy=1, congestion_kw=congestion_kw)

        self.starting_timestep = 0
        with open(self.scenario) as file:
            self.number_of_steps = len(file.readlines()) + 1

    def set_month(self, month):
        starting_timesteps = [0, 60, 44700, 85020, 129600, 172800, 217440, 260475, 305115, 349755, 392955, 437595,
                              480795, 525376]
        assert 13 > month > 0

        dt_month = dt.datetime(2021, month, 1)
        month_str = dt_month.strftime('%B %Y')
        self.scenario_name = month_str + ' ' + self.scenario_name
        self.starting_timestep = starting_timesteps[month]
        self.number_of_steps = starting_timesteps[month + 1] - self.starting_timestep

    def run_simulation(self, individual):
        # Initialise environment
        imbalance_environment = NetworkEnvironment(verbose_lvl=self.verbose_lvl)
        ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
        TotalNetworkCapacityTracker(imbalance_environment, self.congestion_kw)

        # Initialise solar farm
        solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=self.verbose_lvl)
        # Initialise battery
        battery = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=1600,
                          verbose_lvl=self.verbose_lvl)

        # Initialise random strategy
        random_point_based_strategy = individual.value

        earn_money_mod = SolveCongestionAndLimitedChargeControlTower(name="Rhino strategy 1",
                                                                     network_object=battery,
                                                                     congestion_kw=self.congestion_kw,
                                                                     congestion_safety_margin=self.congestion_safety_margin,
                                                                     strategy=random_point_based_strategy,
                                                                     verbose_lvl=self.verbose_lvl,
                                                                     transportation_kw=self.transportation_kw)

        earning_money_until = self.congestion_df.loc['prep_start']
        preparing_for_congestion_until = self.congestion_df.loc['congestion_start']
        preparing_max_kwh = self.congestion_df.loc['prep_max_soc']
        solving_congestion_until = self.congestion_df.loc['congestion_end']

        main_controller = MonthOfModesOfOperationController(name='Wombat main controller',
                                                            network_object=battery,
                                                            verbose_lvl=self.verbose_lvl)
        for month in range(12):
            moo = ModesOfOperationController(name=f'Wombat controller month {month}',
                                             network_object=battery,
                                             verbose_lvl=self.verbose_lvl)
            if earning_money_until[month] is not NaT and earning_money_until[month] is not None:
                moo.add_mode_of_operation(earning_money_until[month], earn_money_mod)

                max_kwh_in_prep = float(preparing_max_kwh[month])
                max_soc_perc_in_prep = int(max_kwh_in_prep / battery.max_kwh * 100)
                discharge_until_strategy = DischargeUntilStrategy(base_strategy=random_point_based_strategy,
                                                                  name='Discharge Money Earner',
                                                                  discharge_until_soc_perc=max_soc_perc_in_prep
                                                                  )
                prepare_and_solve_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name=f"Earn money but discharge until {max_soc_perc_in_prep}",
                                                                                     network_object=battery,
                                                                                     congestion_kw=self.congestion_kw,
                                                                                     congestion_safety_margin=self.congestion_safety_margin,
                                                                                     strategy=discharge_until_strategy,
                                                                                     verbose_lvl=self.verbose_lvl)

                moo.add_mode_of_operation(preparing_for_congestion_until[month], prepare_and_solve_congestion_mod)
                moo.add_mode_of_operation(solving_congestion_until[month], prepare_and_solve_congestion_mod)
            moo.add_mode_of_operation(dt.time(23, 59, tzinfo=utc), earn_money_mod)
            main_controller.add_controller(moo)

        imbalance_environment.add_object(solarvation, [1, 3, 4])
        imbalance_environment.add_object(main_controller, [1, 3, 4, 0])

        # print('\nRunning scenario {}'.format(self.scenario_name))
        res_dict = run_simulation_from_dict_of_df(self.starting_timestep, self.number_of_steps, scenario=self.scenario,
                                                  verbose_lvl=self.verbose_lvl,
                                                  simulation_environment=imbalance_environment,
                                                  dict_of_df=self.scenario_df)
        return res_dict

    def fitness(self, individual):
        if individual.fitness is not None:
            return individual.fitness

        res_dict = self.run_simulation(individual)

        penalty = 1
        if res_dict['time_steps_with_congestion'] > 0:
            penalty = 0.5

        # if res_dict['wombat_battery_cycles'] > 54:
        #     num_of_cycles = res_dict['wombat_battery_cycles']
        #     print(f'Yowza! This strategy made a lot of cycles! {num_of_cycles}')
        #     print(individual)

        fitness_value = res_dict['wombat_battery_revenue'] * penalty
        individual.set_fitness(fitness_value)
        return fitness_value


if __name__ == '__main__':
    random_individual = StrategyIndividual(init_params={'number_of_points': 4})
    fitness = Fitness(verbose_lvl=1, congestion_kw=14000)
    fitness.set_month(7)
    print(fitness.fitness(random_individual))
