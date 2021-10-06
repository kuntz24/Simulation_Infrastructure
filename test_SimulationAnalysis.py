from unittest import TestCase, main
from Sim.Simulation import Simulation
from Sim.SimulationAnalysis import SimulationAnalysis
from Sim.SourcePopulation import SourcePopulation
from Sim.SystemExit import SystemExit
from Sim.SimQueue import SimQueue
from Sim.Assigner import Assigner
from Sim.Distribution import Distribution
from Sim.Customer import Customer
from Sim.Server import Server
import numpy as np
import pandas as pd
import shelve


class TestSimulation(TestCase):
    def setUp(self) -> None:
        self.gen_setup = False
        self.sim = Simulation(100)

        rstate = np.random.get_state()

        self.assigner = Assigner()
        self.dist = {}
        self.dist['ar'] = Distribution("exponential(180)")
        self.dist['dt'] = Distribution("triangular(14400, 14400, 18000)")
        self.dist['oos'] = Distribution("triangular(300, 600, 1200)")
        # 144 second service time corresponds to 25 service completions per hour
        self.dist['st'] = Distribution("exponential(144)")

        np.random.set_state(rstate)

        self.stages = {}

        # define 2 valid system exits
        for i in range(2):
            self.stages[f'SE{i}'] = SystemExit(f'SE{i}')

        # define 2 valid source populations - destinations not yet assigned
        for i in range(2):
            # 180 second average inter-arrival time corresponds to 20 arrivals per hour
            self.stages[f'SP{i}'] = SourcePopulation(f'SP{i}',
                                                     self.dist['ar'],
                                                     self.assigner.assignToShortest)
            self.stages[f'SP{i}'].addCustomerDestination(self.stages[f'SE{i}'])
            # print(f"SP{i} arrival: {self.stages[f'SP{i}'].getNextEventTime()}")

        rstate = np.random.get_state()

        # define 4 valid queues (alternating system exits)
        for i in range(5):
            tqueue = SimQueue(f'Q{i}', self.assigner.assignInSequence)
            self.stages[f'Q{i}'] = tqueue

            server = self.server = Server(f'Server{i}',
                                          0,
                                          self.dist['dt'],
                                          self.dist['oos'],
                                          self.dist['st']
                                          )
            tqueue.addServer(server)
            tqueue.addCustomerDestination(self.stages[f'SE{i % 2}'])
            tqueue.assignServer = self.assigner.assignByAvailableTime

        np.random.set_state(rstate)

    def test_init(self):
        self.assertEqual(0, self.sim.getTrialsCompleted())
        # analysis1 = SimulationAnalysis(self.sim)
        # self.assertFalse(analysis1.isValid)

        # now, setup up and run a valid simulation
        self.sim.addStage(self.stages['SP0'])
        self.sim.addStage(self.stages['SE0'])
        self.assertTrue(self.stages['SP0'].isValid())
        # self.stages['SP0'].addCustomerDestination(self.stages['SE0'])

        # obtain the seed as of end of setup
        rstate = np.random.get_state()
        stage = self.stages['SP0']

        # initialize the first arrival
        iatimes = [stage.getNextEventTime(), ]

        # generate the next 9 events (the first is already in the SourcePopulation)
        iatimes.extend([stage._arrivalTimeDistribution.getEvent() for i in range(9)])
        artimes = np.cumsum(np.array(iatimes))

        # total sim time
        total_sim_time = sum(iatimes)

        # reset random seed after generating expected results in preparation for run
        np.random.set_state(rstate)

        self.sim.run(maxEvents=10)
        # need to account for the source populations' initial arrival times
        # self.dist['ar'].getEvent()
        # self.dist['ar'].getEvent()

        self.assertEqual(total_sim_time, self.sim.simtime)
        self.assertEqual(total_sim_time, self.sim.getSimulatedTime())
        self.assertEqual(10, self.sim.getTrialsCompleted())

        i = 0
        for cust in self.sim:
            with self.subTest(i=i):
                self.assertAlmostEqual(artimes[i], cust.systemArrivalTime)
            i += 1

        # now, recreate a simulation analysis and test validity
        analysis2 = SimulationAnalysis(self.sim)
        self.assertTrue(analysis2.isValid())

        # uncomment for debugging
        # for cust in self.sim:
        #     print(cust)

    def test_analyzeSystemPerformance(self):
        # setup and run the sim
        self.sim.addStage(self.stages['SP0'])
        self.sim.addStage(self.stages['SE0'])
        self.assertTrue(self.stages['SE0'], SystemExit)

        # remove default system exit from source population and set up
        # single server queue for sim
        self.stages['SP0'].removeCustomerDestination('SE0')
        self.stages['SP0'].addCustomerDestination(self.stages['Q0'])
        self.stages['Q0'].addCustomerDestination(self.stages['SE0'])

        self.sim.addStage(self.stages['Q0'])

        # obtain the seed as of end of setup
        rstate = np.random.get_state()
        stage = self.stages['SP0']

        # initialize the first arrival
        iatimes = [stage.getNextEventTime(), ]

        # generate the next 9 events (the first is already in the SourcePopulation)
        iatimes.extend([stage._arrivalTimeDistribution.getEvent() for i in range(9)])
        artimes = np.cumsum(np.array(iatimes))

        # total sim time
        total_sim_time = sum(iatimes)

        # reset random seed after generating expected results in preparation for run
        np.random.set_state(rstate)

        self.sim.run(maxEvents=500)

        df = pd.DataFrame()

        for cust in self.sim:
            if len(df) == 0:
                df = cust.getExperienceStatistics()
                df['name'] = cust.name
            else:
                custdf = cust.getExperienceStatistics()
                custdf['name'] = cust.name
                df = df.append(custdf)

        if self.gen_setup:
            with shelve.open('run2metrics.shelve') as metrics:
                metrics['mean_wait_time'] = df['waitingTime'].mean() / 60
                metrics['mean_system_time'] = np.mean(df['systemTime'])
                # metrics['mean_system_time'] = np.mean(df['serviceCompletionTime'] -
                #                                       df['serviceEntryTime'])
                metrics['max_wait_time'] = df['waitingTime'].max() / 60
                metrics['max_system_time'] = np.max(df['serviceCompletionTime'] -
                                                    df['queueEntryTime'])

                metrics['tot_wait_time'] = df['waitingTime'].sum()
                metrics['tot_system_time'] = np.sum(df['serviceCompletionTime'] -
                                                    df['queueEntryTime'])
                metrics['simevents'] = self.sim.getTrialsCompleted()
                metrics['simtime'] = self.sim.getSimulatedTime()
                metrics['90%_wait_time'] = df['waitingTime'].quantile(0.90, interpolation='higher')
                metrics['90%_system_time'] = df['systemTime'].quantile(0.90, interpolation='higher')

                # uncomment for debugging
                # for k, v in metrics.items():
                #     print(f'{k}: {v}')

                metrics.close()

        actmetrics = {}
        actmetrics['mean_wait_time'] = df['waitingTime'].mean() / 60
        actmetrics['mean_system_time'] = np.mean(df['serviceCompletionTime'] -
                                                  df['queueEntryTime'])
        actmetrics['max_wait_time'] = df['waitingTime'].max()
        actmetrics['max_system_time'] = np.max(df['serviceCompletionTime'] -
                                                  df['queueEntryTime'])
        actmetrics['tot_wait_time'] = df['waitingTime'].sum()
        actmetrics['tot_system_time'] = np.sum(df['serviceCompletionTime'] -
                                                df['queueEntryTime'])
        actmetrics['simevents'] = self.sim.getTrialsCompleted()
        actmetrics['simtime'] = self.sim.getSimulatedTime()

        # Verify summary metrics
        with shelve.open('run2metrics.shelve') as metrics:

            self.assertAlmostEqual(metrics['mean_wait_time'],
                                   df['waitingTime'].mean() / 60)
            self.assertAlmostEqual(metrics['mean_system_time'],
                                   np.mean(df['serviceCompletionTime'] -
                                           df['queueEntryTime']))
            self.assertAlmostEqual(metrics['max_wait_time'],
                                   df['waitingTime'].max() / 60)
            self.assertAlmostEqual(metrics['max_system_time'],
                                   np.max(df['serviceCompletionTime'] -
                                           df['queueEntryTime']))
            self.assertAlmostEqual(metrics['tot_wait_time'],
                                   df['waitingTime'].sum())
            self.assertAlmostEqual(metrics['tot_system_time'],
                                   np.sum(df['serviceCompletionTime'] -
                                          df['queueEntryTime']))
            self.assertAlmostEqual(metrics['simevents'],
                                   self.sim.getTrialsCompleted())
            self.assertAlmostEqual(metrics['simtime'],
                                   self.sim.getSimulatedTime())

            keys = list(metrics.keys())
            for key in keys:
                if key in actmetrics:
                    print(f'metric[{key}]: expected={metrics[key]},  actual={actmetrics[key]}')

            metrics.close()

        # check column details (via customer experience statistics)
        if self.gen_setup:
            df.to_pickle("run2expdf.pickle")

        expdf: pd.DataFrame = pd.read_pickle("run2expdf.pickle")
        colnames = expdf.columns

        # uncomment for debugging
        # print()
        # print(df.head())
        # print(df.tail())
        # print()

        for c in colnames:
            with self.subTest(column=c):
                self.assertEqual(len(expdf[c]), len(df[c]))

                if any(expdf[c] != df[c]):
                    # there is at least one difference
                    for i in range(len(expdf[c])):
                        with self.subTest(i=i):
                            self.assertAlmostEqual(expdf[c], df[c])

        analysis = SimulationAnalysis(self.sim)
        results = analysis.analyzeSystemPerformance()
        self.assertTrue(analysis.isValid())

        # uncomment for debugging
        # print()
        # print("Simulation Analysis:")
        # for k, v in analysis.analyzeSystemPerformance().items():
        #     print(f'{k}: {v}')
        #
        # print()

        # verify the analysis values
        with shelve.open('run2metrics.shelve') as metrics:
            self.assertAlmostEqual(metrics['mean_wait_time'],
                                   results['AvgWaitTime']/60)
            self.assertAlmostEqual(metrics['mean_system_time'],
                                   results['AvgSystemTime'])
            self.assertAlmostEqual(metrics['max_wait_time'],
                                   results['MaxWaitTime']/60)
            self.assertAlmostEqual(metrics['max_system_time'],
                                   results['MaxSystemTime'])
            self.assertEqual(len(df), results['NumCustomers'])
            self.assertAlmostEqual(metrics['90%_wait_time'],
                                   results['90%WaitTime'])
            self.assertAlmostEqual(metrics['90%_system_time'],
                                   results['90%SystemTime'])

        # compare it to itself, all differences should be zero
        diffs = analysis.comparePerformance(self.sim)
        for v in diffs.values():
            self.assertAlmostEqual(0, v)


if __name__ == '__main__':
    main(verbosity=2)
