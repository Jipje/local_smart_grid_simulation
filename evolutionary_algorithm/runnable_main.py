from pandas import NaT
import dateutil.tz
import datetime as dt

from environment.ImbalanceEnvironment import ImbalanceEnvironment
from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.StrategyIndividual import StrategyIndividual
from helper_objects.congestion_helper.month_congestion_size_and_timer import get_month_congestion_timings
from helper_objects.strategies.CsvStrategy import CsvStrategy
from helper_objects.strategies.DischargeUntilStrategy import DischargeUntilStrategy
from main import run_full_scenario
from network_objects.Battery import Battery
from network_objects.RenewableEnergyGenerator import RenewableEnergyGenerator
from network_objects.control_strategies.ModesOfOperationController import ModesOfOperationController
from network_objects.control_strategies.MonthOfModesOfOperationController import MonthOfModesOfOperationController
from network_objects.control_strategies.SolveCongestionAndLimitedChargeControlTower import \
    SolveCongestionAndLimitedChargeControlTower

utc = dateutil.tz.tzutc()


def fitness(individual):
    verbose_lvl=-1
    transportation_kw=2000
    congestion_kw=14000
    congestion_safety_margin = 0.99

    # Initialise environment
    imbalance_environment = NetworkEnvironment(verbose_lvl=verbose_lvl)
    ImbalanceEnvironment(imbalance_environment, mid_price_index=2, max_price_index=1, min_price_index=3)
    TotalNetworkCapacityTracker(imbalance_environment, congestion_kw)

    # Initialise solar farm
    solarvation = RenewableEnergyGenerator('Solarvation solar farm', 19000, verbose_lvl=verbose_lvl)
    # Initialise battery
    battery = Battery('Wombat', 30000, 14000, battery_efficiency=0.9, starting_soc_kwh=1600, verbose_lvl=verbose_lvl)

    # Initialise random strategy
    random_point_based_strategy = individual.value
    greedy_discharge_strat = CsvStrategy('Greedy discharge', strategy_csv='../data/strategies/greedy_discharge_60.csv')
    always_discharge_strat = CsvStrategy('Always discharge', strategy_csv='../data/strategies/always_discharge.csv')

    solve_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Solve Congestion Controller",
                                                                       network_object=battery,
                                                                       congestion_kw=congestion_kw,
                                                                       congestion_safety_margin=congestion_safety_margin,
                                                                       strategy=greedy_discharge_strat,
                                                                       verbose_lvl=verbose_lvl,
                                                                       transportation_kw=transportation_kw)
    prepare_congestion_mod = SolveCongestionAndLimitedChargeControlTower(name="Prepare Congestion",
                                                                         network_object=battery,
                                                                         congestion_kw=congestion_kw,
                                                                         congestion_safety_margin=congestion_safety_margin,
                                                                         strategy=always_discharge_strat,
                                                                         verbose_lvl=verbose_lvl,
                                                                         transportation_kw=transportation_kw)
    earn_money_mod = SolveCongestionAndLimitedChargeControlTower(name="Rhino strategy 1",
                                                                 network_object=battery,
                                                                 congestion_kw=congestion_kw,
                                                                 congestion_safety_margin=congestion_safety_margin,
                                                                 strategy=random_point_based_strategy,
                                                                 verbose_lvl=verbose_lvl,
                                                                 transportation_kw=transportation_kw)

    res_df = get_month_congestion_timings(solarvation_identifier='../data/environments/lelystad_1_2021.csv', strategy=1)

    earning_money_until = res_df.loc['prep_start']
    preparing_for_congestion_until = res_df.loc['congestion_start']
    preparing_max_kwh = res_df.loc['prep_max_soc']
    solving_congestion_until = res_df.loc['congestion_end']

    main_controller = MonthOfModesOfOperationController(name='Wombat main controller',
                                                        network_object=battery,
                                                        verbose_lvl=verbose_lvl)
    for month in range(12):
        moo = ModesOfOperationController(name=f'Wombat controller month {month}',
                                         network_object=battery,
                                         verbose_lvl=verbose_lvl)
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
                                                                                 congestion_kw=congestion_kw,
                                                                                 congestion_safety_margin=congestion_safety_margin,
                                                                                 strategy=discharge_until_strategy,
                                                                                 verbose_lvl=verbose_lvl)

            moo.add_mode_of_operation(preparing_for_congestion_until[month], prepare_congestion_mod)
            moo.add_mode_of_operation(solving_congestion_until[month], solve_congestion_mod)
        moo.add_mode_of_operation(dt.time(23, 59, tzinfo=utc), earn_money_mod)
        main_controller.add_controller(moo)

    imbalance_environment.add_object(solarvation, [1, 3, 4])
    imbalance_environment.add_object(main_controller, [1, 3, 4, 0])

    res = run_full_scenario(scenario='../data/environments/lelystad_1_2021.csv',
                             verbose_lvl=verbose_lvl,
                             simulation_environment=imbalance_environment)['wombat_battery_revenue']
    print(res)
    return res


if __name__ == '__main__':
    evo = Evolution(
        pool_size=10, fitness=fitness, individual_class=StrategyIndividual, n_offsprings=3,
        pair_params={},
        mutate_params={},
        init_params={'number_of_points': 4}
    )
    n_epochs = 50

    for i in range(n_epochs):
        evo.step()

    print(evo.pool.individuals[-1].value)
