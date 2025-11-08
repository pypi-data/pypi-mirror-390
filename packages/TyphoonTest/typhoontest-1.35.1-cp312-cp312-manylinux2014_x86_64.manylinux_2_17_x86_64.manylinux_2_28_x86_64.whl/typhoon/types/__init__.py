import numpy as np
from ..version import get_typhoontest_version

__version__ = get_typhoontest_version()

# Used to typing check on several Typhoontest API functions
# Supports:
# Python datatypes:
#   - int
#   - float
# Numpy (2.2.3) datatypes:
#   - int8
#   - int16
#   - int32
#   - int64
#   - float16
#   - float32
#   - float64
_INT_TYPES = (int, np.integer)
_FLOAT_TYPES = (float, np.floating)
_NUMERIC_TYPES = _INT_TYPES + _FLOAT_TYPES
