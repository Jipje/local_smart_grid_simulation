from pandas import NaT
import dateutil.tz
import datetime as dt

from environment.ImbalanceEnvironment import ImbalanceEnvironment
from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from evolutionary_algorithm.Evolution import Evolution
from evolutionary_algorithm.Fitness import Fitness
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


if __name__ == '__main__':
    fitness_class = Fitness()
    fitness_class.set_month(7)
    evo = Evolution(
        pool_size=10, fitness=fitness_class.fitness, individual_class=StrategyIndividual, n_offsprings=3,
        pair_params={},
        mutate_params={},
        init_params={'number_of_points': 4}
    )
    n_epochs = 50

    for i in range(n_epochs):
        evo.step()

    print(evo.pool.individuals[-1])
    print(evo.pool.individuals[-2])
    print(evo.pool.individuals[-3])
