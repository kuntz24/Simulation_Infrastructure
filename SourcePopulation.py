from Sim.Distribution import Distribution
from Sim.CustomerDestination import CustomerDestination
from Sim.SimulationStage import SimulationStage
import math
from Sim.Customer import Customer
from Sim.Assigner import Assigner
from inspect import signature
import types
import numpy as np
import scipy
from scipy import stats

class SourcePopulation(SimulationStage):
    """
    Represents a source population object that creates customer classes based on a probability distribution

    """
    def __init__(self, id, dist, assignDestination):
        """
        Source Population constructor
        :param id: simulation stage id
        :param dist: arrival time distribution
        :param assignDestination: function that assigns customer to their next destination

        """
        # inherits id attribute from simulation stage
        super().__init__(id)

        # checks to see if assignDestination is a valid function
        if callable(assignDestination):

            if (type(assignDestination) is types.LambdaType) and not (assignDestination.__code__.co_argcount == 1 and

                 assignDestination.__code__.co_varnames[0] != 'self'):

                self._assignDestination = None
            else:
                self._assignDestination = assignDestination
        else:
            self._assignDestination = None


        self._dist = dist


        if not dist.RNG is None:
            # sets arrival time distribution to the dist attribute
            self._arrivalTimeDistribution = dist
        else:
            self._arrivalTimeDistribution = None

        # destination dictionary will be filled when addDestination method is called
        self._destination = {}



        if not self._arrivalTimeDistribution is None:

            # getEvent() creates a random number
            self._nextArrivalTime = self._arrivalTimeDistribution.getEvent()
        else:
            self._nextArrivalTime = math.nan

        # used in Customer creation to increment customer names by 1 each time
        self.count = 1




    def __repr__(self):

        return self.__str__()



    def __str__(self):
        msg = ""
        msg += f'{type(self)} object at {id(self)}\n'
        msg += f'\tIs a source population with distribution: {self._dist}\n'

        return msg


    def addCustomerDestination(self, dest):

        """
        Adds a possible destination for the customer to go to next

        @return: Bool
        """

        if isinstance(dest, CustomerDestination) and dest.id not in self._destination:

            self._destination[dest.id] = dest

            return True

        else:
            return False



    def getNextEventTime(self):
        """
        Gets the next time that a customer will arrive

        @return: double
        """

        if not self.isValid():

            return math.nan

        return self._nextArrivalTime




    def isValid(self):

        """
        Insures that the source population instance is valid

        @return: Bool
        """


        if not self._dist.RNG is None and not self._destination == {} and not self._assignDestination == None:
                return True
        else:
                return False






    def processEvent(self, simtime):
        """
        Instructs the SourcePopulation to process its next event (i.e.
        generate a customer arrival). If the processEvent's nextEventTime
        is greater than the simtime, SourcePopulation will do nothing (it
        isn't yet time for the arrival and the call must have been made in error).
        Otherwise, SourcePopulation generates the Customer arrival and assigns
        the customer to a destination. If the Customer cannot be added to a
        destination, then the Customer will be returned, otherwise None will
        be returned.
        @param simtime: double - elapsed time since the beginning of the simulation.
        @return: Customer
        """

        if simtime < self._nextArrivalTime:

            self.cust = None

        else:
            # time to get busy:
            # 1. generate new customer
            # 2. determine which queue/stage to send the customer to
            # 3. update the next arrival time for the next arrival.

            # Generate a new customer:
            # 1. Assemble customer's name (really just a sequence number)
            # 2. Create the new instance
            name = f'{self.id}-{self.count}'
            self.cust = Customer(name, simtime)

            self.count += 1

            # decides where to send next customer
            stage = self._assignDestination(self._destination)

            # asks next stage to accept customer
            stage.acceptArrival(simtime, self.cust)

            # finds new arrival time
            self._nextArrivalTime = self._nextArrivalTime + self._arrivalTimeDistribution.getEvent()



        return None





    def removeCustomerDestination(self, destId):

        """
        Removes a customer destination if the inputs exists in the destination dictionary

        @return: the new destination dictionary
        """

        if destId not in self._destination:

            return None

        else:
            dest = self._destination.pop(destId)

            return dest

    def setArrivalTimeDistribution(self, dist):

        """
        Sets the arrivalTime Distribution based on the input if the input is a valid Distribution object

        @return: Customer iterable
        """
        if isinstance(dist, Distribution):

            self._dist = dist

        else:

            self._dist = None





    def setAssignDestination(self, assignDestination):

        """
        Sets the assignDestination function to the input if the input is valid

        @return: None
        """


        if len(signature(assignDestination).parameters) == 1:

            self._assignDestination = assignDestination


