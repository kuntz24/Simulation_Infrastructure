from enum import Enum

class QueueEvent(Enum):
        """
        Enumeration describing the valid Queue events:
        - SERVICE_COMPLETION
        - SERVER_DOWN
        - SERVER_UP
        """

        SERVICE_COMPLETION = 0
        SERVER_DOWN = 1
        SERVER_UP = 2
