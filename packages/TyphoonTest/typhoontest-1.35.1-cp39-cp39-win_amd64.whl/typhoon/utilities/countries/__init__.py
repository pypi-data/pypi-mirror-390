#
# Utility functions regarding country codes and names
#
from __future__ import annotations

import re

from .countries_catalog import ALPHA2_CODE_TO_COUNTRY_NAME
from .exceptions import InvalidCountryAlpha2CodeError

ALPHA2_CODE_PATTERN = re.compile("^[A-Z]{2}$")


def get_country_by_alpha2_code(alpha2_code: str) -> str:
    """
    Return official country name based on provided ISO3166 alpha2 code.

    Args:
        alpha2_code(str): String as 2 uppercase characters.

    Raises:
        TypeError if provided alpha2 code is not a string.
        InvalidCountryAlpha2CodeError if provided alpha2 code is not in valid format.
        KeyError if there is no country defined for provided alpha2 code.
    """
    if not isinstance(alpha2_code, str):
        raise TypeError("Passed argument for alpha2_code must be a string.")
    alpha2_code_upper = alpha2_code.upper()
    if not ALPHA2_CODE_PATTERN.match(alpha2_code_upper):
        raise InvalidCountryAlpha2CodeError(alpha2_code)
    return ALPHA2_CODE_TO_COUNTRY_NAME[alpha2_code_upper]
