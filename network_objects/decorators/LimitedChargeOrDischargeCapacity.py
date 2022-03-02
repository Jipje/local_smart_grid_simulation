class LimitedChargeOrDischargeCapacity:
    def __init__(self, network_object, max_charge_index, max_discharge_index):
        self.network_object = network_object
        self.max_charge_index = max_charge_index
        self.max_discharge_index = max_discharge_index

        self.maximum_charge_kwh = 0
        self.maximum_discharge_kwh = 0

        # Assign the correct functions to each object
        self.original_check = self.network_object.check_action
        self.original_step = self.network_object.take_step
        self.network_object.take_step = self.take_step
        self.network_object.check_action = self.check_action

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

        if adjusted_action != action_kwh and self.network_object.verbose_lvl > 2:
            print(f'\t\tAction was limited from {action_kwh}kWh to {adjusted_action}kWh based on generated power')

        return self.original_check(adjusted_action)

    def take_step(self, environment_step, action_parameters):
        if self.max_charge_index > 0:
            self.set_maximum_charge(int(environment_step[self.max_charge_index]))
        else:
            self.set_maximum_charge(99999)

        if self.max_discharge_index > 0:
            self.set_maximum_discharge(int(environment_step[self.max_discharge_index]))
        else:
            self.set_maximum_discharge(-99999)

        return self.original_step(environment_step, action_parameters)
