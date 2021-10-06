import math
from unittest import TestCase, main
from Sim.SimulationStage import SimulationStage


class TestSimulationStage(TestCase):

    def test_init(self):
        self.stage = SimulationStage(1234)
        self.assertEqual(1234, self.stage.id)

        self.assertTrue(self.stage.processEvent(5) is None)
        self.assertTrue(math.isinf(self.stage.getNextEventTime()))

        self.stage = SimulationStage('Pre-check Verification')
        self.assertEqual('Pre-check Verification', self.stage.id)

        self.assertFalse(self.stage.isValid())



if __name__ == '__main__':
    main(verbosity=2)
