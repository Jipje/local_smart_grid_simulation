class NetworkObject(object):
    def __init__(self, name):
        self.name = name

    def take_step(self, environment_step, action_parameters) -> int:
        return 0

    def done_in_mean_time(self):
        return ''

    def check_action(self, action_kwh):
        return action_kwh

    def end_of_environment_message(self, num_of_days=None):
        return ''

    def end_of_environment_metrics(self):
        return {}
