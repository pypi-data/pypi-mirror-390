import inspect
import logging
import sys
from collections.abc import Sequence

logger = logging.getLogger(__name__)


def generic_op(self, other, func):
    """Allows timedeltas to be summed/subtracted to everything that can be casted to self type"""

    try:
        other = self.__class__(other)
    except (TypeError, ValueError):
        return NotImplemented

    res = self.__class__(func(other))

    return res


class NoDuplicatesDict(dict):
    def __setitem__(self, key, value):
        if key in self:
            raise ValueError(f"The name {key} is already defined as a mark.")
        dict.__setitem__(self, key, value)


def _copy_signature(wrapper, wrapped):
    if sys.version_info.major < 3:
        # Not suported on Python 2.x
        pass
    else:
        wrapper.__signature__ = inspect.signature(wrapped)


def _recursive_map(seq, func):
    for item in seq:
        if isinstance(item, Sequence) and not isinstance(item, str):
            yield type(item)(recursive_map(item, func))
        else:
            yield func(item)


def recursive_map(item, func):
    if isinstance(item, Sequence) and not isinstance(item, str):
        return tuple(_recursive_map(item, func))
    else:
        return func(item)


def parse_to_tuple(item):
    """If is a single value instead of tuple, create a tuple with the same value"""

    try:
        item0 = item[0]
        item1 = item[1]
    except (TypeError, IndexError):  # not a tuple/list, single value
        item0 = item
        item1 = item
    return (item0, item1)


def validate_range(item, reference=None, type_cast=None, limit=False):
    """Converts single numbers to tuple, cast them to same type as reference
    if provided and adjust limits to the reference limits."""

    item = parse_to_tuple(item)
    item0 = item[0]
    item1 = item[1]

    if reference is not None:
        if type_cast is None:
            type_cast = reference[0].__class__

        if not isinstance(item0, type_cast):
            try:
                item0 = type_cast(item0)
                item1 = type_cast(item1)
            except Exception as ex:
                raise TypeError(
                    f"Arguments {item} couldn't be converted to type {type_cast}"
                ) from ex

    range_consistent = item0 <= item1

    if not range_consistent:
        msg = (
            f"Lower value is greater than the upper value for item '{item}'."
            "Range is nonexistent."
        )
        raise ValueError(msg)

    if reference is not None and limit:
        minimum = reference[0]
        maximum = reference[-1]

        # item0 = item0 if item0 >= minimum else minimum
        # item1 = item1 if item1 <= maximum else maximum
        if item0 < minimum:
            logger.warning(
                f"Desired time [{item0}] is anterior to earliest signal time. Using earlist signal time [{minimum}]"
            )
            item0 = minimum
        if item1 > maximum:
            logger.warning(
                f"Desired time [{item1}] is later to latest signal time. Using latest signal time [{maximum}]"
            )
            item1 = maximum

    return item0, item1


def gcd(a, b):
    """returns the greatest common denominator of a and b"""
    while b:
        a, b = b, a % b
    return a


class AliasTuple(tuple):
    def __new__(cls, value, alias=None):
        return tuple.__new__(cls, value)

    def __init__(self, value, alias=None):
        self.original_str = str(value)
        self.alias = alias

    def _str_representation_alias(self):
        if self.alias is None:
            return self.original_str
        else:
            return f"{self.alias} [{self.original_str}]"

    def __str__(self):
        return self._str_representation_alias()

    def __repr__(self):
        return self._str_representation_alias()


def sizeof_fmt(num):
    sign = "-" if num < 0 else ""
    num = abs(num)

    # Minimum allowed decimal before jumping to lower unit
    min_decimal = 0.01

    if num == 0:
        return "0.00"
    elif num >= min_decimal:
        for unit in ["", "k", "M"]:
            if abs(num) < 1000.0:
                return f"{sign}{num:.2f}{unit}"
            num /= 1000.0
        return "{}{:.2f}{}".format(sign, num, "G")
    else:
        num *= 1000.0
        for unit in ["m", "u"]:
            if abs(num) > min_decimal:
                return f"{sign}{num:.2f}{unit}"
            num *= 1000.0
        return "{}{:.2f}{}".format(sign, num, "n")
