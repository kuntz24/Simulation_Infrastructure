import scipy
from scipy import stats
from Sim.Customer import Customer
from Sim.Distribution import Distribution
import math
from Sim.ServerEvent import ServerEvent
from Sim.ServerState import ServerState

class Server:
    """
    Server class represents any person, process, or machine that provides server for a
    SimQueue
    """
    # @classmethod
    # def isValidDistribution(cls, dist):
    #     """
    #     Helper function used to validate distributions (i.e. Distribution instance and valid)
    #     @param dist: Distribution
    #     @return: boolean
    #     """
    #     if isinstance(dist, Distribution) and dist.isValid:
    #         return True
    #     else:
    #         return False

    def __init__(self, id, simtime, downTimeDist, oosDist, svcTimeDist):
        """
        Server constructor.
        @param id: string or int - Unique identifer
        @param simtime: time at which the server begins work (i.e. is created)
        @param downTimeDist: Distribution used to generate elapsed time until the next OOS period.
        @param oosDist: Distribution used to generate the elapsed time for an OOS event
        @param svcTimeDist: Distribution used to generate service times
        """


        self._id = id
        self.downTimeDistribution = downTimeDist
        self.oosDistribution = oosDist
        self.serviceTimeDistribution = svcTimeDist

        # initialize remaining attibutes to ensure existence
        self._custInSvc = None
        self._nextDownTime = math.inf
        self._nextEventTime = math.inf
        self._nextEventType = ServerEvent.SERVER_DOWN
        self._availableSince = math.inf

        if self.status != ServerState.INVALID:
            self._setAvailable(simtime)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        msg = f'{type(self)} object at address {id(self)}\n'
        msg += f'\tId: {self.id}\n'
        msg += f'\tStatus: {self.status}\n'
        msg += f'\tnextEventType {self._nextEventType}\n'
        msg += f'\tnextEventTime {self._nextEventTime}\n'
        msg += f'\tnextDownTime {self._nextDownTime}\n'


        return msg

    @property
    def availableSince(self):
        """
        The most recent time at which the Server became available. Can be used
        to determine which Server should next be assigned a Customer.
        @return: float
        """
        return self._availableSince

    @property
    def custInSvc(self):
        """
        Name of customer currently being served, or None if no customer in service
        @return: name : string or none
        """
        return self._custInSvc.name

    @property
    def downTimeDistribution(self):
        # We don't want to offer access to the downTimeDistribution, so we'll
        # always return None here.
        return None

    @downTimeDistribution.setter
    def downTimeDistribution(self, downTimeDist):
        """
        Setter. Validates that downTimeDist is a valid Distribution instance.
        @param downTimeDist:
        @return: None
        """

        if Server.isValid(downTimeDist):
            self._downTimeDistribution = downTimeDist
        else:
            self._downTimeDistribution = None

    @property
    def id(self):
        """
        Server's identifier. Should be globally unique, but not enforced.
        @return: id : string or int
        """
        return self._id

    @property
    def isAvailable(self):
        """
        Boolean property indicating whether or not the Server is available to serve a Customer.
        @return: boolean
        """
        if self.status == ServerState.AVAILABLE:
            return True
        else:
            return False

    @property
    def isBusy(self):
        """
         Boolean property indicating whether or not the Server is currently serving a Customer.
         @return: boolean
         """
        if self.status == ServerState.BUSY:
            return True
        else:
            return False

    @property
    def nextEventTime(self):
        """
        Time at which the next event will occur for this Server
        @return: float
        """
        return self._nextEventTime

    @property
    def nextEventType(self):
        """
        The event type (i.e. SERVICE_COMPLETION, SERVER_UP, SERVER_DOWN) for the Server's
        next scheduled event.
        @return: ServerEvent
        """
        return self._nextEventType

    @property
    def oosDistribution(self):
        # We don't want to provide access to the oosDistribution, so we'll
        # always return None here.
        return None

    @oosDistribution.setter
    def oosDistribution(self, oosDist):
        """
        Setter. Validates that downTimeDist is a valid Distribution instance.
        @param downTimeDist:
        @return: None
        """

        if Server.isValid(oosDist):
            self._oosDistribution = oosDist
        else:
            self._oosDistribution = None

    @property
    def serviceTimeDistribution(self):
        # We don't want to provide access to the serviceTimeDistribution so
        # we'll always return None here.
        return None

    @serviceTimeDistribution.setter
    def serviceTimeDistribution(self, svcTimeDist):
        """
        Setter. Validates that serviceTimeDist is a valid Distribution instance.
        @param downTimeDist:
        @return: None
        """

        if Server.isValid(svcTimeDist):
            self._serviceTimeDistribution = svcTimeDist
        else:
            self._serviceTimeDistribution = None

    @property
    def status(self):
        """
        Indicates the current state/status of the Server: AVAILABLE, BUSY, OOS, PENDING_OOS
        @return: ServerState
        """
        for dist in [self._downTimeDistribution,
                     self._oosDistribution,
                     self._serviceTimeDistribution,
                     self.id]:

            if dist is None:

                 return ServerState.INVALID

        avail = True

        # check to see if Server is in service
        if isinstance(self._custInSvc, Customer):
            avail = False

        # check for Available: custInSvc = None, nextEventType == SERVER_DOWN ,
        # nextEventTime == nextDownTime
        if not avail:
            # Server might be busy, custInSvc is not None
            if self._nextEventType == ServerEvent.SERVICE_COMPLETION:


                return ServerState.BUSY
            else:
                # since custInSvc is not None, next event type MUST  be SERVICE_COMPLETION
                # if it's not, the Server is invalid
                return ServerState.INVALID
        else:
            # no customer in service
            if self._nextEventType == ServerEvent.SERVER_DOWN:
                # must be either AVAILABLE or PENDING_OOS
                if (self._nextDownTime == self._nextEventTime) or \
                        math.isinf(self._nextDownTime) and math.isinf(self._nextEventTime):

                    # Server, so must be available
                    return ServerState.AVAILABLE
                else:
                    # downtime <= eventtime, must be PENDING_OOS
                    return ServerState.PENDING_OOS
            elif self._nextEventType == ServerEvent.SERVER_UP and \
                    self._nextDownTime < self._nextEventTime:

                return ServerState.OOS
            else:
                # Server is invalid: can't be not in service with a next
                # event other than SERVER_UP OR SERVER_DOWN

                return ServerState.INVALID




    def isValid(dist):
        if isinstance(dist, Distribution) and dist.isValid:
            return True
        else:
            return False


    def _completeService(self, simtime):
        """
        Private method to perform service completion activities
        @param simtime: float - current simulation time
        @return: Customer - Customer for which service was completed
        """

        # first, ask customer to log service completion
        self._custInSvc.logServiceCompletion(simtime)

        # save customer for return
        cust = self._custInSvc
        self._custInSvc = None

        # determine transition
        if self._nextDownTime <= self._nextEventTime:
            # Server should have gone out of service before now
            # transition to pendingOOS
            self._setPendingOOS(simtime)
        else:
            # Server not yet scheduled to go OOS and transitions
            # to Available
            self._setAvailable(simtime)

        # return customer for forwarding to next destination
        return cust

    def _setAvailable(self, simtime):
        """
        Private method implementing transition action for moving Server
        to AVAILABLE state.
        @return: None
        """

        # if Server is OOS and returning to service, or is a newly
        # constructed Server, must calculate the next downtime
        if self.status == ServerState.OOS or math.isinf(self._nextDownTime):
            self._nextDownTime = simtime + self._downTimeDistribution.getEvent()

        # need to set the nextEventTime and nextEventType
        self._nextEventType = ServerEvent.SERVER_DOWN
        self._nextEventTime = self._nextDownTime

        # ensure that no customer is in service (which should already
        # be the case
        self._custInSvc = None

        # save the time at which the Server became available
        self._availableSince = simtime

    def _setBusy(self, simtime: float, cust: Customer):
        """
        Private method implementing transition action for moving Server
        from AVAILABLE to BUSY
        @param simtime: current simulation time
        @param cust: Customer to enter service
        @return: None
        """

        # move customer into service and calculate service completion time
        self._custInSvc = cust
        self._nextEventType = ServerEvent.SERVICE_COMPLETION
        self._nextEventTime = simtime + self._serviceTimeDistribution.getEvent()
        self._availableSince = math.inf

        # ensure customer logs service entry
        cust.logServiceEntry(simtime, self.id)

    def _setOOS(self, simtime: float):
        """
        Private method implementing the transition action to OOS
        @param simtime: float - current simulation time
        @return: None
        """
        # first, calculate the time at which the Server will return
        # to service
        self._nextEventTime = simtime + self._oosDistribution.getEvent()

        # set next event to return Server to Available
        self._nextEventType = ServerEvent.SERVER_UP

        self._availableSince = math.inf

    def _setPendingOOS(self, simtime):
        """
        Private method to implement setPendingOOS transition action
        @param simtime: float - current simulation time
        @return: None
        """
        # first, ensure that no Customer is in Service
        self._custInSvc = None


        self._nextEventType = ServerEvent.SERVER_DOWN

        self._availableSince = math.inf

    def acceptCustomer(self, simtime, cust):
        """
        Requests that a Customer be accepted for service.
        @param simTime: float - time at which service is requested
        @param cust: Customer - customer for which the service is performed.
        @return: boolean
        """

        # first, verify that server is available to accept a customer
        if self.status != ServerState.AVAILABLE:
            # server cannot accept a customer because it is not available
            return False

        # verify that the cust is a Customer instance
        if not isinstance(cust, Customer):
            # cannot accept cust into Service, it is not a Customer
            return False

        #Accept service request
        self._setBusy(simtime, cust)
        return True

    def getNextEventTime(self):
        """
        Returns the time at which Server's next event occurs.
        @return: float - nextEventTime
        """
        return self._nextEventTime

    def pauseService(self, nextDownTime):
        """
        Manually sets the nextDownTime. Server must be Available or Busy
        @param nextDownTime: float - time at which server will go OOS
        @return: boolean - True if change can be made, False otherwise
        """
        if self.status in {ServerState.AVAILABLE, ServerState.BUSY}:
            # OK to make change
            self._nextDownTime = nextDownTime
            return True
        else:
            return False

    def processEvent(self, simtime):
        """
        Called by a Queue to request the Server process its next event.
        @param simtime: float - Current simulation time
        @return: Customer or None
        """

        if self._nextEventTime > simtime:
            # it isn't yet time for the event, function was called prematurely
            # do not process the event - this should never happen.
            return None

        if self._nextEventType == ServerEvent.SERVICE_COMPLETION:
            # process the service completion
            return self._completeService(simtime)

        elif self._nextEventType == ServerEvent.SERVER_UP:
            # process the return to service
            self._setAvailable(simtime)

        elif self._nextEventType == ServerEvent.SERVER_DOWN:
            # process the transition to OOS
            self._setOOS(simtime)

        return None

    def resumeService(self, resumeTime):
        """
        Manually set's the next event time (i.e. resume time) when the server
        is OOS.
        @param resumeTime: float - time at which server will become available.
        @return: boolean - True if change can be made, False otherwise
        """
        if self.status == ServerState.OOS:
            self._nextEventTime = resumeTime
            return True
        else:
            return False

