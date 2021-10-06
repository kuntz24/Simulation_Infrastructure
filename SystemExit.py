from Sim.CustomerDestination import CustomerDestination
from Sim.Customer import Customer

class SystemExit(CustomerDestination):

    """
    Represents a system exit object where the customer will be done with the queuing system

    """

    def __init__(self, id):

        # inherits id attribute from Customer Destination
        super().__init__(id)

        # customer will be added when accept arrival is called
        self._customers = {}



    def __repr__(self):

        return self.__str__()

    def __str__(self):
        msg = ""
        msg += f'{type(self)} object at {id(self)}\n'
        msg += f'\tIs a system exit with customer list: {self._customers}\n'

        return msg


    def __iter__(self):
        """
        iter special method that allows System Exit object to be looped through

        @return: iterable
        """

        return (i for i in self._customers.values())





    @property
    def customer(self):
        """
        Getter property for customer dictionary

        @return: dictionary
        """
        return self._customers



    def acceptArrival(self, simtime, customer):
        """
        Accepts a Customer and adds the customer to the customers dictionary. Customer,
        should have a unique identifier. If not, it will be rejected by the SystemExit
        which will return True if the Customer is admitted and False otherwise.
        @param customer: Customer
        @param simtime: double
        @return: boolean
        """

        if self.isValid():

            if not customer.name in self._customers.keys():

                self._customers[customer.name] = customer

                return True

            else:

                return False



    def getNumCustomersWaiting(self):
        """
        Returns the number of customers waiting which, for a SystemExit,
        must be 0.
        @return: 0
        """
        return 0

    def isValid(self):
        """
        Boolean indicating whether the SimulationStage is valid. By default, a "base"
        SystemExit is always valid (there may be future instances of specializations
        that are not automatically valid).
        @return: True
        """
        return True



    def arrivalTimeIterator(self):
        """
        Returns an iterable for accessing customers in arrival time sequence,
        rather than exit time sequence (the default sequence provided by __iter__)
        @return: iterable
        """

        return (c for c in sorted(self._customers.values(),
                                  key=lambda cust: cust.systemArrivalTime))







