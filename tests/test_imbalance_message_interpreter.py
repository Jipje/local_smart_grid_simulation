from helper_objects.ImbalanceMessageInterpreter import ImbalanceMessageInterpreter
import unittest

max_def = -99999
min_def = 99999


class TestImbalanceMessageInterpreter(unittest.TestCase):
    def test_nice_forecast_max(self):
        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        mid_prices = [29.12, 29.12, 29.12, 29.12, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62]
        max_prices = [max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, 28.33, 31.13, 33.27, 35.82, 38.21, 38.21, 38.21]
        min_prices = [min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def]
        for i in range(len(min_prices)):
            imbalance_message_interpreter.update(mid_prices[i], max_prices[i], min_prices[i])
            if i == 5:
                mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
                self.assertEqual(29.62, mid_price)
                self.assertEqual(mid_price, max_price)
                self.assertEqual(mid_price, min_price)
            if i == 8:
                mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
                self.assertEqual(28.33, max_price)
                self.assertEqual(max_price, min_price)
            if i == 14:
                self.assertEqual((29.62, 38.21, 38.21), imbalance_message_interpreter.get_current_price())
        mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
        self.assertEqual(max_price, imbalance_message_interpreter.get_charge_price())
        self.assertEqual(min_price, imbalance_message_interpreter.get_discharge_price())


    def test_nice_forecast_min(self):
        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        mid_prices = [32.12, 32.12, 32.12, 32.12, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62]
        max_prices = [max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def]
        min_prices = [min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, 38.21, 38.21, 38.21, 35.82, 33.27, 31.13, 28.33]
        for i in range(len(min_prices)):
            imbalance_message_interpreter.update(mid_prices[i], max_prices[i], min_prices[i])
            if i == 5:
                mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
                self.assertEqual(35.62, mid_price)
                self.assertEqual(mid_price, max_price)
                self.assertEqual(mid_price, min_price)
            if i == 8:
                mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
                self.assertEqual(38.21, min_price)
                self.assertEqual(min_price, max_price)
            if i == 14:
                self.assertEqual((35.62, 28.33, 28.33), imbalance_message_interpreter.get_current_price())

    def test_forecast_min(self):
        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        mid_prices = [32.12, 32.12, 32.12, 32.12, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62, 35.62]
        max_prices = [max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def]
        min_prices = [min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, 33.21, 38.21, min_def, 35.82, 33.27, 31.13, min_def]
        for i in range(len(min_prices)):
            imbalance_message_interpreter.update(mid_prices[i], max_prices[i], min_prices[i])
            if i == 8:
                mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
                self.assertEqual(33.21, min_price)
                self.assertEqual(min_price, max_price)
            if i == 12:
                mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
                self.assertEqual(33.21, min_price)
                self.assertEqual(min_price, max_price)
            if i == 13:
                mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
                self.assertEqual(31.13, min_price)
                self.assertEqual(min_price, max_price)
            if i == 14:
                self.assertEqual((35.62, 31.13, 31.13), imbalance_message_interpreter.get_current_price())

    def test_forecast_max(self):
        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        mid_prices = [29.12, 29.12, 29.12, 29.12, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62]
        max_prices = [max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, 27.53, 26.12, max_def, 20.20, 24.10, 30.33, max_def]
        min_prices = [min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def]
        for i in range(len(min_prices)):
            imbalance_message_interpreter.update(mid_prices[i], max_prices[i], min_prices[i])
            if i == 8:
                mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
                self.assertEqual(27.53, max_price)
                self.assertEqual(max_price, min_price)
            if i == 12:
                mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
                self.assertEqual(27.53, max_price)
                self.assertEqual(max_price, min_price)
            if i == 13:
                mid_price, max_price, min_price = imbalance_message_interpreter.get_current_price()
                self.assertEqual(30.33, max_price)
                self.assertEqual(max_price, min_price)
            if i == 14:
                self.assertEqual((29.62, 30.33, 30.33), imbalance_message_interpreter.get_current_price())

    def test_forecast_real(self):
        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        mid_prices = [29.12, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62]
        max_prices = [38.21, 39.82, 45.96, 45.96, 45.96, 48.1, 51.85, 51.85, max_def, max_def, max_def, 48.1, 45.96, 45.96, 39.82]
        min_prices = [min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def, min_def]
        for i in range(len(min_prices)):
            imbalance_message_interpreter.update(mid_prices[i], max_prices[i], min_prices[i])
            if i == 0:
                self.assertEqual((29.12, 38.21, 38.21), imbalance_message_interpreter.get_current_price())
            if i == 5:
                self.assertEqual((29.62, 48.1, 48.1), imbalance_message_interpreter.get_current_price())
            if i == 7:
                self.assertEqual((29.62, 51.85, 51.85), imbalance_message_interpreter.get_current_price())
            if i == 10:
                self.assertEqual((29.62, 51.85, 51.85), imbalance_message_interpreter.get_current_price())
            if i == 14:
                self.assertEqual((29.62, 51.85, 51.85), imbalance_message_interpreter.get_current_price())

    def test_forecast_both(self):
        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        mid_prices = [29.12, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62]
        max_prices = [max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, 27.53, 26.12, max_def, 20.20, 24.10, 30.33, max_def]
        min_prices = [min_def, min_def, min_def, 29.63, min_def, min_def, min_def, min_def, min_def, 33.20, min_def, min_def, min_def, min_def, min_def]
        for i in range(len(min_prices)):
            imbalance_message_interpreter.update(mid_prices[i], max_prices[i], min_prices[i])
            if i == 3:
                self.assertEqual((29.62,  29.63,  29.63), imbalance_message_interpreter.get_current_price())
            if i == 8:
                self.assertEqual((29.62, 27.53, 29.63), imbalance_message_interpreter.get_current_price())
            if i == 12:
                self.assertEqual((29.62, 27.53, 29.63), imbalance_message_interpreter.get_current_price())
            if i == 13:
                self.assertEqual((29.62, 30.33, 29.63), imbalance_message_interpreter.get_current_price())

    def test_forecast_jeroen(self):
        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        imbalance_message_interpreter.update(29.12)
        imbalance_message_interpreter.update(29.12)
        imbalance_message_interpreter.update(29.12)
        self.assertEqual((29.12, 29.12, 29.12), imbalance_message_interpreter.get_current_price())

        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        imbalance_message_interpreter.update(29.12, new_min_price=50)
        imbalance_message_interpreter.update(29.62)
        self.assertEqual((29.62, 50, 50), imbalance_message_interpreter.get_current_price())

        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        imbalance_message_interpreter.update(29.12)
        imbalance_message_interpreter.update(29.12)
        imbalance_message_interpreter.update(29.12)
        self.assertEqual((29.12, 29.12, 29.12), imbalance_message_interpreter.get_current_price())

        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        imbalance_message_interpreter.update(29.12, new_min_price=50)
        imbalance_message_interpreter.update(29.62, new_max_price=45)
        self.assertEqual((29.62, 45, 50), imbalance_message_interpreter.get_current_price())

        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        imbalance_message_interpreter.update(29.12)
        imbalance_message_interpreter.update(29.12)
        imbalance_message_interpreter.update(29.12)
        self.assertEqual((29.12, 29.12, 29.12), imbalance_message_interpreter.get_current_price())

        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        imbalance_message_interpreter.update(29.12)
        imbalance_message_interpreter.update(29.62, new_max_price=45)
        self.assertEqual((29.62, 45, 45), imbalance_message_interpreter.get_current_price())

    def test_too_many_forecasts(self):
        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        mid_prices = [29.12, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62, 29.62]
        self.assertEqual(15, len(mid_prices))
        for new_mid_price in mid_prices:
            imbalance_message_interpreter.update(new_mid_price)
        self.assertRaises(OverflowError, imbalance_message_interpreter.update, 30.22)

    def test_real_fault(self):
        imbalance_message_interpreter = ImbalanceMessageInterpreter()
        mid_prices = list(reversed([31.21, 31.21, 31.21, 31.21, 31.21, 31.21, 31.21, 31.21, 31.21, 31.21, 31.21, 31.21, 31.21, 31.21,
                                    31.21]))
        max_prices = list(reversed([max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def, max_def,
                                    max_def, max_def, 31.14, 33.39]))
        min_prices = list(reversed([4.24, 0.23, 0.23, -8.26, -8.26, -8.26, -8.26, 0.23, 0.23, 0.23, 4.24,
                                    10.23, 17.01, 17.73, 17.73]))
        for i in range(len(min_prices)):
            imbalance_message_interpreter.update(mid_prices[i], max_prices[i], min_prices[i])
            if i == 2:
                self.assertEqual((31.21,  33.39,  17.01), imbalance_message_interpreter.get_current_price())
            if i == 14:
                self.assertEqual((31.21, 33.39, -8.26), imbalance_message_interpreter.get_current_price())
