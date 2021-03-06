from helper_objects.strategies.Strategy import Strategy


class PointBasedStrategy(Strategy):
    def __init__(self, name, price_step_size=5):
        super().__init__(name, price_step_size)
        self.charge_points = []
        self.discharge_points = []

    def add_point(self, point):
        try:
            assert(0 < point[0] < 100)
            assert point[1] % self.price_step_size == 0
            assert point[2] in ['CHARGE', 'DISCHARGE']

            if point[1] > self.max_price:
                bonus = self.price_step_size
                self.max_price = point[1] + bonus
            elif point[1] < self.min_price:
                bonus = self.price_step_size
                self.min_price = point[1] - bonus

            if point[2] == 'CHARGE':
                self.charge_points.append(point)
            elif point[2] == 'DISCHARGE':
                self.discharge_points.append(point)

        except Exception:
            raise ValueError("The offered point should be tuple of (SoC%, Imb Price, ACTION)."
                             "First two integers respectively, other is a valid command, CHARGE, DISCHARGE.\n"
                             f"Received: {point} instead")

    def upload_strategy(self):
        self.initialize_strategy_matrix()

        self.charge_points = sorted(self.charge_points, key=lambda tup: tup[0])
        self.discharge_points = sorted(self.discharge_points, key=lambda tup: tup[0])
        charge_iter = iter(self.charge_points)
        discharge_iter = iter(self.discharge_points)

        latest_charge = next(charge_iter)
        latest_discharge = next(discharge_iter)
        strategy_matrix = self.strategy_matrix

        for current_soc in range(100 + 1):

            try:
                if current_soc == latest_charge[0]:
                    latest_charge = next(charge_iter)
                if current_soc == latest_discharge[0]:
                    latest_discharge = next(discharge_iter)
            except StopIteration:
                pass

            for current_price in range(self.min_price, self.max_price + self.price_step_size, self.price_step_size):
                if current_soc < 5:
                    command = 'CHARGE'
                elif current_soc >= 95:
                    command = 'DISCHARGE'
                elif current_soc <= latest_charge[0] and current_price <= latest_charge[1]:
                    command = 'CHARGE'
                elif current_soc <= latest_discharge[0] and current_price >= latest_discharge[1]:
                    command = 'DISCHARGE'
                else:
                    command = 'WAIT'

                current_soc_index = current_soc
                current_price_index = self.price_index(current_price)
                strategy_matrix[current_soc_index][current_price_index] = command

        self.uploaded = True
        self.strategy_matrix = strategy_matrix

    def sort_and_fix_points(self, sort_strategy=None):
        if sort_strategy is None:
            pass
        else:
            sort_strategy = int(sort_strategy)

        self.charge_points = sorted(self.charge_points, key=lambda tup: tup[0])
        self.discharge_points = sorted(self.discharge_points, key=lambda tup: tup[0])
        if sort_strategy == 1:
            self.sort_strategy_one_flip_prices()
        elif sort_strategy == 2:
            self.sort_strategy_two_take_high_price()
        elif sort_strategy == 3:
            self.sort_strategy_three_take_low_price()
        else:
            pass

    def sort_strategy_one_flip_prices(self, left_index=None, right_index=None):
        if left_index is None and right_index is None:
            return self.sort_strategy_one_flip_prices(left_index=0, right_index=1)

        flag_flipped = False

        left_charge_price = self.charge_points[left_index][1]
        right_charge_price = self.charge_points[right_index][1]
        if left_charge_price < right_charge_price:
            self.charge_points[left_index] = (self.charge_points[left_index][0], right_charge_price, 'CHARGE')
            self.charge_points[right_index] = (self.charge_points[right_index][0], left_charge_price, 'CHARGE')
            flag_flipped = True

        left_discharge_price = self.discharge_points[left_index][1]
        right_discharge_price = self.discharge_points[right_index][1]
        if left_discharge_price < right_discharge_price:
            self.discharge_points[left_index] = (self.discharge_points[left_index][0], right_discharge_price, 'DISCHARGE')
            self.discharge_points[right_index] = (self.discharge_points[right_index][0], left_discharge_price, 'DISCHARGE')
            flag_flipped = True

        if flag_flipped and left_index != 0 and right_index != 1:
            return self.sort_strategy_one_flip_prices(left_index=0, right_index=1)

        if left_index == len(self.charge_points) - 2 and right_index == len(self.charge_points) - 1:
            # Base case end of the list
            return

        return self.sort_strategy_one_flip_prices(left_index + 1, right_index + 1)

    def sort_strategy_two_take_high_price(self, left_index=None, right_index=None):
        if left_index is None and right_index is None:
            return self.sort_strategy_two_take_high_price(left_index=0, right_index=1)

        flag_flipped = False

        left_charge_price = self.charge_points[left_index][1]
        right_charge_price = self.charge_points[right_index][1]
        if left_charge_price < right_charge_price:
            self.charge_points[left_index] = (self.charge_points[left_index][0], left_charge_price, 'CHARGE')
            self.charge_points[right_index] = (self.charge_points[right_index][0], left_charge_price, 'CHARGE')
            flag_flipped = True

        left_discharge_price = self.discharge_points[left_index][1]
        right_discharge_price = self.discharge_points[right_index][1]
        if left_discharge_price < right_discharge_price:
            self.discharge_points[left_index] = (self.discharge_points[left_index][0], right_discharge_price, 'DISCHARGE')
            self.discharge_points[right_index] = (self.discharge_points[right_index][0], right_discharge_price, 'DISCHARGE')
            flag_flipped = True

        if flag_flipped and left_index != 0 and right_index != 1:
            return self.sort_strategy_two_take_high_price(left_index=0, right_index=1)

        if left_index == len(self.charge_points) - 2 and right_index == len(self.charge_points) - 1:
            # Base case end of the list
            return

        return self.sort_strategy_two_take_high_price(left_index + 1, right_index + 1)

    def sort_strategy_three_take_low_price(self, left_index=None, right_index=None):
        if left_index is None and right_index is None:
            return self.sort_strategy_three_take_low_price(left_index=0, right_index=1)

        flag_flipped = False

        left_charge_price = self.charge_points[left_index][1]
        right_charge_price = self.charge_points[right_index][1]
        if left_charge_price < right_charge_price:
            self.charge_points[left_index] = (self.charge_points[left_index][0], right_charge_price, 'CHARGE')
            self.charge_points[right_index] = (self.charge_points[right_index][0], right_charge_price, 'CHARGE')
            flag_flipped = True

        left_discharge_price = self.discharge_points[left_index][1]
        right_discharge_price = self.discharge_points[right_index][1]
        if left_discharge_price < right_discharge_price:
            self.discharge_points[left_index] = (self.discharge_points[left_index][0], left_discharge_price, 'DISCHARGE')
            self.discharge_points[right_index] = (self.discharge_points[right_index][0], left_discharge_price, 'DISCHARGE')
            flag_flipped = True

        if flag_flipped and left_index != 0 and right_index != 1:
            return self.sort_strategy_three_take_low_price(left_index=0, right_index=1)

        if left_index == len(self.charge_points) - 2 and right_index == len(self.charge_points) - 1:
            # Base case end of the list
            return

        return self.sort_strategy_three_take_low_price(left_index + 1, right_index + 1)


if __name__ == '__main__':
    # point_based_strat = PointBasedStrategy('TESTING')
    #
    # point_based_strat.add_point((50, 50, 'CHARGE'))
    # point_based_strat.add_point((70, 30, 'CHARGE'))
    # point_based_strat.add_point((95, 0, 'CHARGE'))
    #
    # point_based_strat.add_point((40, 100, 'DISCHARGE'))
    # point_based_strat.add_point((70, 80, 'DISCHARGE'))
    # point_based_strat.add_point((95, 65, 'DISCHARGE'))
    #
    # print(point_based_strat)
    #
    # point_based_strat.upload_strategy()

    point_based_strat = PointBasedStrategy('TESTING', price_step_size=11)

    point_based_strat.add_point((50, 55, 'CHARGE'))
    point_based_strat.add_point((70, 33, 'CHARGE'))
    point_based_strat.add_point((95, 0, 'CHARGE'))

    point_based_strat.add_point((40, 99, 'DISCHARGE'))
    point_based_strat.add_point((70, 88, 'DISCHARGE'))
    point_based_strat.add_point((95, 66, 'DISCHARGE'))

    print(point_based_strat)

    point_based_strat.upload_strategy()
