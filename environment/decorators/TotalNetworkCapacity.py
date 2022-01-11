from environment.NetworkEnvironment import NetworkEnvironment


class TotalNetworkCapacity(object):
    def __init__(self, network_environment: NetworkEnvironment, max_kw: int):
        self.network_environment = network_environment
        self.maximum_kw = abs(max_kw)

        # Assign the correct functions to each object
        self.original_step = self.network_environment.take_step
        self.network_environment.take_step = self.take_step

    def take_step(self, environment_step) -> int:
        total_network_step = self.original_step(environment_step)
        if abs(total_network_step) > self.maximum_kw:
            raise Exception('NETWORK CONGESTION')
