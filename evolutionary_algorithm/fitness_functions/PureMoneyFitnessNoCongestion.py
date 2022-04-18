from environment.ImbalanceEnvironment import ImbalanceEnvironment
from environment.NetworkEnvironment import NetworkEnvironment
from environment.TotalNetworkCapacityTracker import TotalNetworkCapacityTracker
from evolutionary_algorithm.Fitness import Fitness
from evolutionary_algorithm.individuals.StrategyIndividual import StrategyIndividual
from main import run_simulation_from_dict_of_df
from network_objects.Battery import Battery
from network_objects.RenewableEnergyGenerator import RenewableEnergyGenerator
from network_objects.control_strategies.StrategyWithLimitedChargeCapacityControlTower import \
    StrategyWithLimitedChargeCapacityControlTower


class PureMoneyFitnessNoCongestion(Fitness):
    def __init__(self, verbose_lvl=-1, transportation_kw=2000, congestion_kw=14000, congestion_safety_margin=0.99):
        super().__init__(verbose_lvl, transportation_kw, congestion_kw, congestion_safety_margin)

    def run_simulation(self, individual):
        if individual.fitness is not None:
            return individual.fitness
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
        money_earning_strategy = individual.value
        strategy_limited_charge_controller = StrategyWithLimitedChargeCapacityControlTower(
            name="Wombat Battery Controller", network_object=battery, strategy=money_earning_strategy,
            verbose_lvl=self.verbose_lvl, transportation_kw=self.transportation_kw)

        imbalance_environment.add_object(solarvation, [1, 3, 4])
        imbalance_environment.add_object(strategy_limited_charge_controller, [1, 3, 4])

        res_dict = run_simulation_from_dict_of_df(self.starting_timestep, self.number_of_steps, scenario=self.scenario,
                                                  verbose_lvl=self.verbose_lvl,
                                                  simulation_environment=imbalance_environment,
                                                  dict_of_df=self.scenario_df)
        return res_dict

    def fitness(self, individual):
        res_dict = self.run_simulation(individual)

        fitness_value = res_dict['wombat_battery_revenue']
        individual.set_fitness(fitness_value)

        return fitness_value


if __name__ == '__main__':
    random_individual = StrategyIndividual(init_params={'number_of_points': 4})
    fitness = PureMoneyFitnessNoCongestion(verbose_lvl=1)
    fitness.set_month(4)
    print(fitness.fitness(random_individual))
