from enum import Enum
import scipy
from scipy import stats
import numpy as np
class ServerEvent(Enum):
    SERVICE_COMPLETION = 0
    SERVER_DOWN = 1
    SERVER_UP = 2

