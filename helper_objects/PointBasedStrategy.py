
class PointBasedStrategy(object):
    def __init__(self, name):
        self.ready_to_use = False
        self.charge_points = []
        self.discharge_points = []
        self.strategy = None
        self.name = name
        self.max_price = -9999
        self.min_price = 9999
        self.price_step_size = 5

    def add_point(self, point):
        try:
            assert(0 < point[0] < 100)
            assert point[1] % self.price_step_size == 0
            assert point[2] in ['CHARGE', 'DISCHARGE']

            if point[1] > self.max_price:
                self.max_price = point[1] + self.price_step_size
            elif point[1] < self.min_price:
                self.min_price = point[1] - self.price_step_size

            if point[2] == 'CHARGE':
                self.charge_points.append(point)
            elif point[2] == 'DISCHARGE':
                self.discharge_points.append(point)

        except Exception:
            raise ValueError("The offered point should be tuple of (SoC%, Imb Price, ACTION)."
                             "First two integers respectively, other is a valid command, CHARGE, DISCHARGE.")

    def price_index(self, price):
        price = self.clean_price(price)
        price = price - self.min_price
        price_index = price / self.price_step_size
        price_index = int(price_index)
        return price_index

    def clean_price(self, price, discharge_price=True):
        if price % self.price_step_size == 0:
            res = price
        else:
            if discharge_price:
                res = price - price % self.price_step_size
            else:
                res = price + self.price_step_size - (price % self.price_step_size)

        if price > self.max_price:
            res = self.max_price
        elif price < self.min_price:
            res = self.min_price
        return res

    def upload_strategy(self):
        num_of_price_buckets = int((self.max_price - self.min_price) / self.price_step_size)
        strategy_matrix = []
        for i in range(100 + 1):
            strategy_matrix.append([])
            for _ in range(num_of_price_buckets + 1):
                strategy_matrix[i].append('WAIT')

        self.charge_points = sorted(self.charge_points, key=lambda tup: tup[0])
        self.discharge_points = sorted(self.discharge_points, key=lambda tup: tup[0])
        charge_iter = iter(self.charge_points)
        discharge_iter = iter(self.discharge_points)

        latest_charge = next(charge_iter)
        latest_discharge = next(discharge_iter)

        for current_soc in range(100 + 1):
            for current_price in range(self.min_price, self.max_price + self.price_step_size, self.price_step_size):
                if current_soc <= 5:
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

            try:
                if current_soc == latest_charge[0]:
                    latest_charge = next(charge_iter)
                if current_soc == latest_discharge[0]:
                    latest_discharge = next(discharge_iter)
            except StopIteration:
                pass

        self.uploaded = True
        self.strategy_matrix = strategy_matrix


if __name__ == '__main__':
    point_based_strat = PointBasedStrategy('TESTING')

    point_based_strat.add_point((50, 50, 'CHARGE'))
    point_based_strat.add_point((70, 30, 'CHARGE'))
    point_based_strat.add_point((95, 0, 'CHARGE'))

    point_based_strat.add_point((40, 100, 'DISCHARGE'))
    point_based_strat.add_point((70, 80, 'DISCHARGE'))
    point_based_strat.add_point((95, 65, 'DISCHARGE'))

    print(point_based_strat)

    point_based_strat.upload_strategy()


