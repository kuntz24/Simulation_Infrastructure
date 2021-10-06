from unittest import TestCase, main
from Sim.SourcePopulation import SourcePopulation
from Sim.Distribution import Distribution

from Sim.Assigner import Assigner
from Sim.CustomerDestination import CustomerDestination
from Sim.SimulationStage import SimulationStage
from Sim.SimQueue import SimQueue
import numpy as np
import sys
import scipy
from scipy import stats


class TestSourcePopulation(TestCase):

    def setUp(self):
        dist = Distribution(scipy.stats.norm(10,5))


        # SourcePopulation generates the first arrival time on construction
        # so we have to set the random number before creating the source population

        np.random.seed(100)
        self.sp = SourcePopulation("Source1", dist, Assigner().assignInSequence)



    def test_init(self):
        # check a valid SourcePopulation instance
        self.assertTrue(isinstance(self.sp, SourcePopulation))
        self.assertTrue(isinstance(self.sp, SimulationStage))
        self.assertTrue(isinstance(self.sp._destination, dict))
        self.assertFalse(self.sp._arrivalTimeDistribution is None)
        self.assertFalse(self.sp._assignDestination is None)

        # now try  where the arrivalTimeDistribution is invalid
        dist = Distribution('nrml(100, 20)')
        sp = SourcePopulation("Source1", dist, Assigner().assignInSequence)
        self.assertTrue(sp._arrivalTimeDistribution is None)
        self.assertFalse(sp._assignDestination is None)

        # now try  where the assignDestination function is invalid
        dist = Distribution('scipy.stats.norm(100, 20)')

        # invalid assignDestination function, no arguments
        sp = SourcePopulation("Source1", dist, lambda: 5)

        self.assertFalse(sp._arrivalTimeDistribution is None)
        self.assertTrue(sp._assignDestination is None)

        # invalid assignDestination function, too many arguments
        sp = SourcePopulation("Source1", dist, lambda x, y: 5)

        self.assertFalse(sp._arrivalTimeDistribution is None)
        self.assertTrue(sp._assignDestination is None)

        # invalid assignDestination function, not callable
        sp = SourcePopulation("Source1", dist, 5)

        self.assertFalse(sp._arrivalTimeDistribution is None)
        self.assertTrue(sp._assignDestination is None)

    def test_isValid(self):
        # check SourcePopulation instance, invalid because it has no destinations
        self.assertFalse(self.sp.isValid())

        # now force it to be valid - make sure it has a destination
        dest = CustomerDestination('test_dest')
        self.sp._destination[dest.id] = dest
        self.assertTrue(self.sp.isValid())

        # now try  where the arrivalTimeDistribution is invalid
        dist = Distribution('nrml(100, 20)')
        sp = SourcePopulation("Source1", dist, Assigner().assignInSequence)
        sp._destination[dest.id] = dest
        self.assertFalse(sp.isValid())

        # now try  where the assignDestination function is invalid
        dist = Distribution('scipy.stats.norm(10, 5)')

        # invalid assignDestination function, no arguments
        sp = SourcePopulation("Source1", dist, lambda: 5)
        sp._destination[dest.id] = dest
        self.assertFalse(sp.isValid())

        # invalid assignDestination function, too many arguments
        sp = SourcePopulation("Source1", dist, lambda x, y: 5)
        sp._destination[dest.id] = dest
        self.assertFalse(sp.isValid())

        # invalid assignDestination function, not callable
        sp = SourcePopulation("Source1", dist, 5)
        sp._destination[dest.id] = dest
        self.assertFalse(sp.isValid())

    def test_getNextEventTime(self):
        # make sure the instance is valid, it needs a destination
        dest = CustomerDestination('test_dest')
        self.sp._destination[dest.id] = dest

        # reset seed and generate expected arrival time
        np.random.seed(100)
        expected = scipy.stats.norm(10,5).rvs()

        self.assertAlmostEqual(expected, self.sp.getNextEventTime())

    def test_addCustomerDestination(self):

        # check SourcePopulation instance, invalid because it has no destinations
        self.assertFalse(self.sp.isValid())

        # now force it to be valid - make sure it has a destination
        dest = CustomerDestination('test_dest')
        self.assertTrue(self.sp.addCustomerDestination(dest))
        self.assertTrue(self.sp.isValid())

        # now, try to add a non-CustomerDestination
        self.assertFalse(self.sp.addCustomerDestination(list()))
        self.assertTrue(self.sp.isValid())

        # now, try to add the SAME CustomerDestination
        self.assertFalse(self.sp.addCustomerDestination(dest))
        self.assertTrue(self.sp.isValid())

    def test_removeCustomerDestination(self):
        self.assertFalse(self.sp.isValid())

        # now force it to be valid - make sure it has a destination
        dest = CustomerDestination('test_dest')
        self.assertTrue(self.sp.addCustomerDestination(dest))
        self.assertTrue(self.sp.isValid())

        # try to delete a destination that doesn't exist
        self.assertTrue(self.sp.removeCustomerDestination("dummy") is None)

        # try a valid delete, SourcePopulation should still be valid
        self.assertTrue(self.sp.isValid())
        self.assertEqual('test_dest', self.sp.removeCustomerDestination('test_dest').id)

        # now SourcePopulation should have no destinations and should be invalid
        self.assertFalse(self.sp.isValid())

    def test_processEvent(self):
        # add a valid destination to the SourcePopulation
        dest = SimQueue('test_dest', Assigner().assignInSequence)
        self.assertTrue(self.sp.addCustomerDestination(dest))

        # save the random seed state
        rstate = np.random.get_state()

        # generate arrival times for validation
        np.random.seed(100)
        arrival_times = scipy.stats.norm(10,5).rvs(size = 10).cumsum()

        # reset the seed state
        np.random.set_state(rstate)

        for i in range(10):
            with self.subTest(i = i):
                self.assertAlmostEqual(arrival_times[i], self.sp.getNextEventTime())
                self.sp.processEvent(self.sp.getNextEventTime())

    def test_setArrivalTimeDistribution(self):
        # save the state, Distribution will have generated it's first RV
        rstate = np.random.get_state()

        # add a valid destination to the SourcePopulation
        dest = SimQueue('test_dest', Assigner().assignInSequence)
        self.sp.addCustomerDestination(dest)

        # set seed and generate expected results
        np.random.seed(100)
        expected = list(scipy.stats.norm(10,5).rvs(size = 10).cumsum())
        print(f'expected near line {sys._getframe().f_lineno}: {expected}')

        # reset state and generate test values
        np.random.set_state(rstate)
        actual = list()

        for i in range(10):
            with self.subTest(i=i):
                actual.append(self.sp.getNextEventTime())
                self.sp.processEvent(self.sp.getNextEventTime())
                self.assertAlmostEqual(expected[i], actual[i])

        # capture seed state
        rstate = np.random.get_state()
        temp = np.zeros(10)
        temp[1:10] = scipy.stats.norm(10,5).rvs(size = 9)
        expected = self.sp.getNextEventTime() + np.cumsum(temp)
        print(f'expected near line {sys._getframe().f_lineno}: {expected}')

        # restore the random state
        np.random.set_state(rstate)
        self.sp.setArrivalTimeDistribution(Distribution("scipy.stats.norm(10, 5)"))

        # reset state and generate test values
        np.random.set_state(rstate)
        actual = list()



        for i in range(10):
            with self.subTest(i=i):
                actual.append(self.sp.getNextEventTime())
                self.sp.processEvent(self.sp.getNextEventTime())
                self.assertAlmostEqual(expected[i], actual[i])


if __name__ == '__main__':
    main(verbosity=2)








