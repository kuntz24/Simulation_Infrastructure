import pandas as pd
import numpy as np
import math
import scipy
from scipy import stats
from Sim.Experience import Experience


class Customer:
    """
    Represents an instance of a Customer that has experiences in a queue

    """

    def __init__(self, name, simtime):
        """
        Customer class constructor
        @param name: name of the customer
        @param simtime: Time that customer arrives in a system
        """

        self._name = str(name)
        self._systemArrivalTime = simtime
        self._simtime = simtime


        self._experience = {}
        self._arrivalTime = None
        self._df_list = []
        self.totalWait = 0
        self.totalSys = 0


    def __repr__(self):

        return self.__str__()

    def __str__(self):
        msg = ""
        msg += f'{type(self)} object at {id(self)}\n'
        msg += f'\tIs a customer with name: {self.name}\n'

        return msg


    @property
    def systemArrivalTime(self):
        """
        Getter property for time customer arrives at system

        @return: double
        """

        return self._systemArrivalTime


    @property
    def name(self):
        """
        Getter property for name of customer

        @return: string
        """
        return self._name


    @name.setter
    def name(self, name):
        """
        Setter property for name of customer

        @return: None
        """

        self._name = name


    @property
    def totalSystemTime(self):
        """
        Getter property for total time customer is in system

        @return: double
        """

        if not math.isnan(self.exp.systemTime):

            return self.totalSys

        else:
            return math.nan



    @property
    def totalWaitTime(self):
        """
        Getter property for time customer has to wait in system

        @return: double
        """

        if not math.isnan(self.exp.waitingTime):
            return self.totalWait
        else:
            return math.nan




    def logArrival(self, simtime, stageId):
        """
        Creates an Experience object now that the customer has arrived at a queue
        Logs the arrival of the Customer

        @return: No return
        """

        # creates Experience object for this Customer
        self.exp = Experience(stageId, simtime)

        # adds Experiene to dictionary
        self._experience[self.exp.stageId] = self.exp




    def logServiceEntry(self, simtime, serverId):
        """
        Logs that the Customer has entered Service

        @return: No return
        """
        self.exp.logServiceEntry(serverId, simtime)

        if not math.isnan(self.exp.waitingTime):

            self.totalWait += self.exp.waitingTime

        else:
            self.totalWait = math.nan



    def logServiceCompletion(self, simtime):
        """
        Logs that the Customer has completed service, and creates the Dataframe from the Experience class becayse the data from that queue is complete

        @return: No return
        """
        self.exp.logServiceCompletion(simtime)

        self.single_df = self.exp.makeRow()

        self._df_list.append(self.single_df)

        if not math.isnan(self.exp.systemTime):

            self.totalSys += self.exp.systemTime

        else:

            self.totalSys = math.nan









    def getExperienceStatistics(self):
        """
        Returns the dataframe that the Experience class created for the Customer object

        @return: pandas Dataframe
        """

        if not math.isnan(self.exp.serviceCompletionTime):

            self.df = pd.concat(self._df_list)

        else:

            self.df = self.exp.makeRow()




        return self.df

    def getExperiences(self):
        """
        returns the experience dictionary that tracks all of a customers experiences

        @return: Dictionary
        """

        return self._experience




