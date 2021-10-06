import math


from Sim.SimulationStage import SimulationStage

from Sim.SystemExit import SystemExit


import numpy as np

class Simulation:

    """
    Represents an instance of a Simulation.
    Needs at least one source population and system exit to have meaning

    """
    def __init__(self, seedVal = None):
        """
        Simulation class constructor
        @param seedVal: seed value for random number generation

        """

        self._seedVal = np.random.seed(seedVal)
        self._customers = {}
        self._stages = {}
        self._simtime = 0
        self._trials = 0



    def __repr__(self):
        return self.__str__()

    def __str__(self):
        msg = ""
        msg += f'{type(self)} object at {id(self)}\n'
        msg += f'\tIs a simulation with this amount of stages: {self.numStages}\n'
        return msg


    def __iter__(self):
        """
        Returns an iterable so that a simulation object can be looped through

        @return: Customer iterable
        """
        for stage in self._stages.values():

            if isinstance(stage, SystemExit):

                for cust in stage:

                    yield cust



    @property
    def seed(self):

        return self._seedVal

    @property
    def numStages(self):
        return len(self._stages)

    @property
    def simtime(self):
        return self._simtime


    @seed.setter
    def seed(self, seed):
        self._seedVal = seed

    def addStage(self, stage):
        """
        Adds a stage to the simulation if the input is a valid stage

        @return: Bool
        """
        if isinstance(stage, SimulationStage):

            self._stages[stage.id] = stage
            return True
        else:
            return False

    def removeStage(self, stage):

        """
        Removes a stage from the simulation if the input is in the dictionary of stages

        @return: Bool
        """
        if stage in self._stages.keys():
            self._stages.pop(stage)
            return True
        else:
            return False

    def getSimulatedTime(self):

        """
        Gets the total time that the simulation ran for

        @return: double
        """
        return self.simtime

    def getTrialsCompleted(self):

        """
        Gets the total amount of loops that the simulation performed

        @return: double
        """
        return self._trials

    def run(self, maxTime = math.inf, maxEvents = 1000):

        """
        Performs the simulation with a specified maximum time or maximum amount of loops

        @return: None
        """

        complete = False

        while not complete:

            sorted_stages = sorted([stage for stage in self._stages.values()],
                                   key= lambda stg: stg.getNextEventTime())
            stage = sorted_stages[0]


            #sets the simulation time to the next event time
            self._simtime = stage.getNextEventTime()

            #processes the next event time
            stage.processEvent(self._simtime)

            #adds 1 to the number of events that have happened
            self._trials += 1

            #checks to see if the simulation should be complete and ends the loops if the if statement is executed
            if self._trials >= maxEvents or self._simtime >= maxTime:

                complete = True
