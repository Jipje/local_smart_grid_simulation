class LimitedChargeOrDischargeCapacity:
    def __init__(self, network_object, max_charge_index, max_discharge_index):
        self.network_object = network_object
        self.max_charge_index = max_charge_index
        self.max_discharge_index = max_discharge_index

        self.maximum_charge_kwh = 0
        self.maximum_discharge_kwh = 0

    def set_maximum_charge(self, maximum_charge):
        self.maximum_charge_kwh = maximum_charge

    def set_maximum_discharge(self, maximum_discharge):
        self.maximum_discharge_kwh = maximum_discharge

    def check_action(self, action_kwh):
        adjusted_action = action_kwh
        if adjusted_action > self.maximum_charge_kwh:
            adjusted_action = self.maximum_charge_kwh
        elif adjusted_action < self.maximum_discharge_kwh:
            adjusted_action = self.maximum_discharge_kwh
        return self.network_object.check_action(adjusted_action)

    def take_step(self, environment_step, action_parameters):
        self.set_maximum_charge(environment_step[self.max_charge_index])
        self.set_maximum_discharge(environment_step[self.max_discharge_index])
        return self.network_object.take_step(environment_step, action_parameters)
