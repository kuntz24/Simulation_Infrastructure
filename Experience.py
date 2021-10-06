import pandas as pd

import math

class Experience:
    """
    Represents an instance of a Customer's experience while progressing through a queue
    """

    def __init__(self, stageId, queueEntryTime):
        """
        Experience class constructor
        @param stageId: The current simulation stage that the Customer is recording an Experience at
        @param queueEntryTime: The time that a Customer enters the queue they are at
        """


        self._stageId = stageId
        self._queueEntryTime = queueEntryTime
        self._serverId = None
        self._serviceEntryTime = None
        self._serviceCompletionTime = None
        self._waitingTime = None
        self._systemTime = None



    def __repr__(self):
        return self.__str__()



    def __str__(self):

        msg = ""
        msg += f'{type(self)} object at {id(self)}\n'
        msg += f'has experience metrics:\n {self.makeRow()}'

        return msg



    @property
    def stageId(self):
        return self._stageId



    @property
    def queueEntryTime(self):
        return self._queueEntryTime



    @property
    def serverId(self):
        if self._serverId == None:
            return math.nan
        else:
            return self._serverId



    @property
    def serviceEntryTime(self):
        if self._serviceEntryTime == None:
            return math.nan
        else:
            return self._serviceEntryTime



    @property
    def serviceCompletionTime(self):
        if self._serviceCompletionTime == None:
            return math.nan
        else:
            return self._serviceCompletionTime



    @property
    def systemTime(self):
        if self._systemTime == None:
            return math.nan
        else:
            return self._systemTime



    @property
    def waitingTime(self):
        if self._waitingTime == None:
            return math.nan
        else:
            return self._waitingTime



    def logServiceEntry(self, serverId, serviceEntryTime):
        """
        Logs when a customer enters service at a queue

        @return: There is no return, the function simply updates a few variables
        """

        self._serverId = serverId

        self._serviceEntryTime = serviceEntryTime

        self._waitingTime = serviceEntryTime - self.queueEntryTime

    def logServiceCompletion(self, serviceCompletionTime):
        """
        Logs when a customer completes service at a queue

        @return: There is no return, the function simply updates a few variables
        """

        self._serviceCompletionTime = serviceCompletionTime

        self._systemTime = serviceCompletionTime - self.queueEntryTime


    def makeRow(self):
        """
        Creates a one-row pandas Dataframe that records all of the data for a Customer's experience in a single queue

        @return: pandas Dataframe
        """

        df = pd.DataFrame([[self.stageId, self.queueEntryTime, self.serverId,
                            self.serviceEntryTime, self.serviceCompletionTime,
                            self.waitingTime, self.systemTime]],
                          columns=['stageId', 'queueEntryTime', 'serverId',
                       'serviceEntryTime', 'serviceCompletionTime',
                       'waitingTime', 'systemTime'])

        return df


