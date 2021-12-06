import unittest
from helper_objects.cycle_counters.NaiveCycleCounter import NaiveCycleCounter


class TestNaiveCycleCounter(unittest.TestCase):

    def test_initialization(self):
        cycle_counter = NaiveCycleCounter(1000)
        self.assertEqual(0, cycle_counter.cycle_count)
        self.assertEqual(0, cycle_counter.old_cycle_count)
        self.assertEqual(1000, cycle_counter.max_kwh)

    def test_add_cycles(self):
        cycle_counter = NaiveCycleCounter(1000)
        self.assertEqual(0, cycle_counter.cycle_count)
        cycle_counter.add_cycle(1000)
        cycle_counter.add_cycle(-1000)
        self.assertEqual(1, cycle_counter.cycle_count)
        cycle_counter.add_cycle(1000)
        self.assertEqual(1.5, cycle_counter.cycle_count)

    def test_done_in_mean_time(self):
        cycle_counter = NaiveCycleCounter(1000)
        self.assertEqual(0, cycle_counter.old_cycle_count)
        cycle_counter.add_cycle(1000)
        cycle_counter.add_cycle(-1000)
        msg = cycle_counter.done_in_mean_time()
        self.assertEqual("Cycles in mean time: 1.0", msg)
        cycle_counter.add_cycle(1000)
        msg = cycle_counter.done_in_mean_time()
        self.assertEqual("Cycles in mean time: 0.5", msg)


if __name__ == '__main__':
    unittest.main()
