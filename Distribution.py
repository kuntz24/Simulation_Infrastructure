import scipy
from scipy import stats

class Distribution:
    """
    Represents an instance of a probability distribution for the purpose of
    generating random variates.
    """

    def __init__(self, RNG):
        """
        Distribution class constructor. Distribution is a "strategy" object that
        encapsulates a random number generating function. This provides for complete
        flexibility in creating Distribution objects. Any function can be used as a
        random number generator.

        @param RNG: function or lambda expression, or distribution specification.
                    If a distribution specification, it must represent a valid
                    np.random function call. For example, normal(100, 20) would
                    be valid as np.random.normal(100, 20) is a valid function call.
        """


        if self.isValid(RNG):

            self._RNG = RNG
        else:
            self._RNG = None

    def __repr__(self):
        return (self.__str__())

    def __str__(self):
        msg = ""
        msg += f'{type(self)} object at {id(self)}\n'
        msg += f'\tHas random number generating function: {self.RNG}\n'

        return msg

    @property
    def RNG(self):
        return self._RNG


    def isValid(self, RNG):
        """
        Boolean function that returns the state of the Distribution. If not valid,
        the Distribution will return None for getEvent calls.
        @return: boolean
        """
        try:

            if type(RNG) is str:

                if isinstance(eval(RNG), scipy.stats.rv_continuous):
                    return True
                elif isinstance(eval(RNG), scipy.stats.rv_discrete):
                    return True
                elif isinstance(eval(RNG), scipy.stats.distributions.rv_frozen):
                    return True
                else:
                    return False

            else:
                if isinstance(RNG, scipy.stats.rv_continuous):
                    return True
                elif isinstance(RNG, scipy.stats.rv_discrete):
                    return True
                elif isinstance(RNG, scipy.stats.distributions.rv_frozen):
                    return True
                else:
                    return False

        except (NameError, SyntaxError, AttributeError):

            return False



    def getEvent(self, count = 1):
        """
        Generates a random variate for the Distribution using the random number
        generating function provided at construction. Returns NaN if the Distribution
        is not valid

        @return: double
        """

        if self.isValid(self.RNG):

            if type(self.RNG) is str:


                rv = eval(self._RNG).rvs(size = count)

                return rv[0]

            else:
                rv = (self._RNG).rvs(size=count)

                return rv[0]

        else:
            return None

    @RNG.setter
    def RNG(self, dist_spec):

        # validate that dist_spec is a callable function
        if not callable(dist_spec):

            self._RNG = None
        # validate that dist_spec
        if dist_spec.__code__.co_argcount > 1 or \
                (dist_spec.__code__.co_argcount == 1 and
                 dist_spec.__code__.co_varnames[0] != 'self'):
            # RNG requires one or more arguments, so it is invalid
            self._RNG = None

        # if we get to this point, we can set the number generator to the setter input
        self._RNG = dist_spec



