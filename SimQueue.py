import math

from Sim.CustomerDestination import CustomerDestination
from Sim.Customer import Customer
from Sim.Server import Server
from Sim.QueueEvent import QueueEvent
from Sim.ServerState import ServerState
from Sim.ServerEvent import ServerEvent
from collections import deque
import types

class SimQueue(CustomerDestination):
    """
    Queue class representing a generic queue that a customer waits in until they enter service
    """

    def __init__(self, id, assignDestination):
        """
        Constructor
        @param id: int or str - Unique identifier/descriptor of the queue
        @param assignDestination: function - Function that accepts a dictionary of objects
                                             as an argument and returns a single selected
                                             object.
        """

        # ensure that object is a valid SimulationStage/CustomerDestination
        super().__init__(id)

        if callable(assignDestination):
            if (type(assignDestination) is types.LambdaType) and not (assignDestination.__code__.co_argcount == 1 and
                 assignDestination.__code__.co_varnames[0] != 'self'):

                self._assignDestination = None
            else:
                self._assignDestination = assignDestination
        else:
            self._assignDestination = None

        self._buffer = deque()
        self._destination = {}
        self._nextEventTime = math.nan
        self._nextEventType = QueueEvent.SERVER_DOWN
        self._servers = {}
        self._assignServer = None


    def __repr__(self):
        return self.__str__()

    def __str__(self):
        msg = ''
        msg += f'{type(self)} object at {id(self)}\n'
        msg += f'\tIs a Queue with id: {self.id}\n'

        return msg

    @property
    def assignDestination(self):
        """
        Getter property for function that assigns customers to destinations

        @return: function
        """
        return self._assignDestination

    @property
    def destination(self):
        """
        Getter property for destination dictionary

        @return: dicitonary
        """
        return self._destination

    @property
    def nextEventTime(self):
        """
        Getter property for time next event will occur at queue

        @return: double
        """
        return self.getNextEventTime()

    @property
    def nextEventType(self):
        """
        Getter property for type of next event that will occur at queue

        @return: enum value
        """
        return self._nextEventType

    @property
    def servers(self):
        """
        Getter property for dictionary of servers at a queue

        @return: dictionary
        """
        return self._servers

    @property
    def assignServer(self):
        """
        Getter property for function that assigns server to customers waiting at a queue

        @return: function
        """
        return self._assignServer


    @assignServer.setter
    def assignServer(self, assignServer):

        if callable(assignServer):
            # assignServer is a valid function
            self._assignServer = assignServer

        else:

            # assignServer is not a function, so instance is not valid
            self._assignServer = None

            return

            # if we reached this point, we now have a valid assignServer function
            # need to test whether or not it requires arguments

        if self._assignServer.__code__.co_argcount == 1:
            # assignServer requires one argument, so it is valid
            self._assignServer = assignServer

        elif self._assignServer.__code__.co_argcount == 2 and \
                self._assignServer.__code__.co_varnames[0] == 'self':

            self._assignServer = assignServer

        else:
            # assignServer should require 1 argument, so it is invalid
            self._assignServer = None


    @assignDestination.setter
    def assignDestination(self, assignDestination):
        # validate that assignDestination is a function that takes a single argument.

        if callable(assignDestination):
            # assignDestination is a valid function
            self._assignDestination = assignDestination
        else:
            # assignDestination is not a function, so instance is not valid
            self._assignDestination = None
            return

        # if we reached this point, we now have a valid assignDestination function
        # need to test whether or not it requires arguments

        if self._assignDestination.__code__.co_argcount == 1:
            # assignDestination requires one argument, so it is valid
            self._assignDestination = assignDestination
        elif self._assignDestination.__code__.co_argcount == 2 and \
            self._assignDestination.__code__.co_varnames[0] == 'self':
            self._assignDestination = assignDestination
        else:
            # assignDestination should require 1 argument, so it is invalid
            self._assignDestination = None


    def acceptArrival(self, simtime, customer):
        """
        Accepts a Customer as long as: 1) the SimQueue has a valid state, and 2) the "customer"
        is actually a Customer instance
        @param customer: Customer
        @param simtime: double
        @return: boolean: True if the Customer is accepted, False otherwise
        """
        if isinstance(customer, Customer) and self.isValid():

            # adds customer to list of waiting customers
            self._buffer.append(customer)

            # logs customer arrival
            customer.logArrival(simtime, self.id)

            #tries to advance customer to service if possible
            self._advanceCustomers(simtime)

            return True

        else:
            return False

    def getNumCustomersWaiting(self):
        """
        gets the length of the waiting line
        @return: int
        """

        return len(self._buffer)

    def isValid(self):
        """
        Boolean function returning valid status of the SimQueue. To be valid, a
        SimQueue must have at least one CustomerDestination, at least one
        Server, and valid assignDestination and assignServer functions
        @return: boolean
        """

        if self._assignDestination is None:
            # assign destination function is invalid
            return False

        if self._assignServer is None:
            # assign server function is invalid
            return False

        if len(self._destination) == 0:
            # no customer destinations have been specified
            return False

        if len(self._servers) == 0:
            # no servers have been specified
            return False

        return True

    def addCustomerDestination(self, dest):
        """
        Adds a CustomerDestination into the list of possible destinations to which a
        Customer can be assigned on arrival
        @param dest: CustomerDestination - a new CustomerDestination
        @return: boolean
        """
        if isinstance(dest, CustomerDestination) and dest.id not in self._destination:

            self._destination[dest.id] = dest

            return True

        else:
            return False



    def addServer(self, server):
        """
         Adds a Server to which a Customer can be assigned on service entry
         @param server: Server - a new server
         @return: boolean
         """
        if isinstance(server, Server) and server.id not in self._servers:

            self._servers[server.id] = server

            return True

        else:
            return False


    def removeServer(self, id):
        """
        Removes a Server from the SimQueue after which the SimQueue will
        no longer assign Customers to that Server.
        @param destId: str or int - identifier (id) of Server to be removed
        @return: Server if existing or None if not found
        """
        if id in self._servers.keys():

            serv = self._servers.pop(id)

            return serv

        else:

            return None

    def removeCustomerDestination(self, destId):
        """
        Removes a CustomerDestination from the SimQueue after which the SimQueue will
        no longer route Customers to that CustomerDestination.
        @param destId: str or int - identifier (id) of CustomerDestination to be removed
        @return: CustomerDestination if existing or None if not found
        """
        if destId in self._destination.keys():

            dest = self._destination.pop(destId)
            return dest

        else:
            return None



    def getNextEventTime(self):
        """
        Returns the next event time for the SimQueue, which is the earliest
        nextEventTime for all of the SimQueue's Servers.
        @return: nextEventTime: float
        """
        if len(self._servers) >= 1:
            
            event = min([i._nextEventTime for i in self._servers.values()])

            return event

        else:

            return math.inf


    def getNextEventType(self):
        """
        Returns the next event type for the Queue.
        @return: QueueEvent
        """
        if len(self._servers) >= 1:

            for s in self.servers.values():

                if s._nextEventTime == min([i._nextEventTime for i in self._servers.values()]):

                    if s.nextEventType == ServerEvent.SERVICE_COMPLETION:

                        return QueueEvent.SERVICE_COMPLETION

                    elif s.nextEventType == ServerEvent.SERVER_UP:

                        return QueueEvent.SERVER_UP

                    elif s.nextEventType == ServerEvent.SERVER_DOWN:

                        return QueueEvent.SERVER_DOWN
        else:

            return None



    def processEvent(self, simtime):
        """
        Initiates the Queue's processing an event. If the event processed was a service
        completion, then processEvent returns a Customer instance. Otherwise it
        returns None.
        @param simtime:
        @return: Customer or None.
        """
        # The basic sequence
        # 1. verify validity, process event only if SimQueue is valid
        # 2. validate simtime, process event only if simtime <= nextEventTime
        # 3. identify server who is due to process event
        # 4. request that server process the event
        # 5. if a Customer object was returned, forward to next destination
        # 6. advance customers to service

        if not self.isValid():
            return None

        if len(self.servers) >= 1 and simtime == self.getNextEventTime():

            server = None

            for s in self.servers.values():

               if s._nextEventTime == self.getNextEventTime():

                    server = s


            if server._nextEventTime == self.getNextEventTime():

                cust = server.processEvent(simtime)

                if isinstance(cust, Customer):
                    dest = self.assignDestination(self._destination)
                    dest.acceptArrival(simtime, cust)



                self._advanceCustomers(simtime)
                return cust
        else:
            return None




    def getNumAvailableServers(self):
        """
        Returns the number of Servers that are currently avaialble to accept
        a Customer for service.
        @return: int
        """
        return len(self._getAvailableServers())



    def getNumBusyServers(self):
        """
        Returns the number of Servers that are currently busy serving
        Customers.
        @return: int
        """
        count = 0
        for i in self.servers.values():
            if i.status is ServerState.BUSY:
                count += 1
            else:
                count = count

        return count



    def _getAvailableServers(self):
        """
        Private method to return the available servers, streamlining operations related
        to advancing customers to service
        @return: list of Server
        """
        serv = {}
        for i in self.servers.keys():

            if self.servers[i].status is ServerState.AVAILABLE:

                serv[i] = self.servers[i]

        return serv


    def _advanceCustomers(self, time):
        """
        Private method to advance customers into service if possible. This method is used
        by acceptArrival and processEvent.
        @param simtime: float - current simulation time
        @return: boolean
        """

        ncust = min(self.getNumCustomersWaiting(), self.getNumAvailableServers())

        if ncust == 0:
            # there are either no waiting customers or no available servers
            return False

        # if we fall through to here, there is at least one available customer
        # and one available server

        for i in range(ncust):
            # we will advance ncust customers to service
            srvr = self._assignServer(self._getAvailableServers())

            # remove the customer from the buffer and advance to service with srvr
            cust = self._buffer.popleft()
            if not srvr.acceptCustomer(time, cust):
                # Server didn't accept customer, put the customer back at the
                # front of the line - this should never happen
                self._buffer.appendleft(cust)

        # there were customers to advance and servers to accept
        return True








