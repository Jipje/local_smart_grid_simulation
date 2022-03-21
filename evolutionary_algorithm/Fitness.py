from pandas import NaT

from environment.ImbalanceEnvironment import ImbalanceEnvironment
from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from evolutionary_algorithm.StrategyIndividual import StrategyIndividual
from helper_objects.congestion_helper.month_congestion_size_and_timer import get_month_congestion_timings
from helper_objects.strategies import RandomStrategyGenerator
from helper_objects.strategies.CsvStrategy import CsvStrategy
from helper_objects.strategies.DischargeUntilStrategy import DischargeUntilStrategy
from main import run_full_scenario, run_simulation_from_dict_of_df
import pandas as pd
import dateutil.tz
import datetime as dt

utc = dateutil.tz.tzutc()

from network_objects.Battery import Battery
from network_objects.RenewableEnergyGenerator import RenewableEnergyGenerator
from network_objects.control_strategies.ModesOfOperationController import ModesOfOperationController
from network_objects.control_strategies.MonthOfModesOfOperationController import MonthOfModesOfOperationController
from network_objects.control_strategies.SolveCongestionAndLimitedChargeControlTower import \
    SolveCongestionAndLimitedChargeControlTower

class Fitness(object):
    def __init__(self, verbose_lvl=-1, transportation_kw=2000, congestion_kw=14000, congestion_safety_margin=0.99):
        self.verbose_lvl = verbose_lvl
        self.transportation_kw = transportation_kw
        self.congestion_kw = congestion_kw
        self.congestion_safety_margin = congestion_safety_margin

        self.scenario = '../data/environments/lelystad_1_2021.csv'
        res_df = pd.read_csv(self.scenario)
        self.scenario_df = res_df.to_dict('records')
        self.congestion_df = get_month_congestion_timings(solarvation_identifier='../data/environments/lelystad_1_2021.csv', strategy=1)

    def fitness(self, individual):
        # Initialise environment
        imbalance_environment = NetworkEnvironment(verbose_lvl=self.verbose_lvl)
        ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
        TotalNetworkCapacityTracker(imbalance_environment, self.congestion_kw)

        # Initialise solar farm
        solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=self.verbose_lvl)
        # Initialise battery
        battery = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=1600, verbose_lvl=self.verbose_lvl)

        # Initialise random strategy
        random_point_based_strategy = individual.value
        greedy_discharge_strat = CsvStrategy('Greedy discharge', strategy_csv='../data/strategies/greedy_discharge_60.csv')
        always_discharge_strat = CsvStrategy('Always discharge', strategy_csv='../data/strategies/always_discharge.csv')

        solve_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Solve Congestion Controller",
                                                                           network_object=battery,
                                                                           congestion_kw=self.congestion_kw,
                                                                           congestion_safety_margin=self.congestion_safety_margin,
                                                                           strategy=greedy_discharge_strat,
                                                                           verbose_lvl=self.verbose_lvl,
                                                                           transportation_kw=self.transportation_kw)
        prepare_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Prepare Congestion",
                                                                             network_object=battery,
                                                                             congestion_kw=self.congestion_kw,
                                                                             congestion_safety_margin=self.congestion_safety_margin,
                                                                             strategy=always_discharge_strat,
                                                                             verbose_lvl=self.verbose_lvl,
                                                                             transportation_kw=self.transportation_kw)
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
            if earning_money_until[month] is not NaT:
                moo.add_mode_of_operation(earning_money_until[month], earn_money_mod)

                max_kwh_in_prep = float(preparing_max_kwh[month])
                max_soc_perc_in_prep = int(max_kwh_in_prep / battery.max_kwh * 100)
                discharge_until_strategy = DischargeUntilStrategy(base_strategy=random_point_based_strategy,
                                                                  name='Discharge Money Earner',
                                                                  discharge_until_soc_perc=max_soc_perc_in_prep
                                                                  )
                prepare_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Prepare Congestion",
                                                                                     network_object=battery,
                                                                                     congestion_kw=self.congestion_kw,
                                                                                     congestion_safety_margin=self.congestion_safety_margin,
                                                                                     strategy=discharge_until_strategy,
                                                                                     verbose_lvl=self.verbose_lvl)

                moo.add_mode_of_operation(preparing_for_congestion_until[month], prepare_congestion_mod)
                moo.add_mode_of_operation(solving_congestion_until[month], solve_congestion_mod)
            moo.add_mode_of_operation(dt.time(23, 59, tzinfo=utc), earn_money_mod)
            main_controller.add_controller(moo)

        imbalance_environment.add_object(solarvation, [1, 3, 4])
        imbalance_environment.add_object(main_controller, [1, 3, 4, 0])

        starting_timestep = 0
        with open(self.scenario) as file:
            number_of_steps = len(file.readlines()) + 1 - starting_timestep
        print('\nRunning full scenario {}'.format(self.scenario))
        res_dict = run_simulation_from_dict_of_df(starting_timestep, number_of_steps, scenario=self.scenario, verbose_lvl=self.verbose_lvl,
                                       simulation_environment=imbalance_environment, dict_of_df=self.scenario_df)
        print('Just ran full scenario {}'.format(self.scenario))
        print(res_dict)
        return res_dict['wombat_battery_revenue']


if __name__ == '__main__':
    random_individual = StrategyIndividual(init_params={'number_of_points': 4})
    fitness = Fitness(verbose_lvl=1)
    print(fitness.fitness(random_individual))
