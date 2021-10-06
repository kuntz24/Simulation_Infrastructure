import math
from unittest import TestCase, main
from Sim.CustomerDestination import CustomerDestination
from Sim.SimulationStage import SimulationStage


class TestCustomerDestination(TestCase):
    def test_init(self):
        self.dest = CustomerDestination(1234)
        self.assertEqual(1234, self.dest.id)

        self.assertTrue(self.dest.processEvent(5) is None)
        self.assertTrue(math.isinf(self.dest.getNextEventTime()))
        self.assertFalse(self.dest.acceptArrival(100, 1234))
        self.assertTrue(math.isnan(self.dest.getNumCustomersWaiting()))

        self.assertTrue(isinstance(self.dest, SimulationStage))
        self.assertTrue(isinstance(self.dest, CustomerDestination))


if __name__ == '__main__':
    main(verbosity=2)

