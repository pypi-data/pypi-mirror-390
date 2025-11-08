import contextlib

import pytest as _pytest
from pytest import fixture

from typhoon.utils import NoDuplicatesDict

from ..version import get_typhoontest_version

__version__ = get_typhoontest_version()


def parameter(values=None, table=None):
    if table is not None:
        params = _parse_table(table)
    elif values is not None:
        params = values
    else:
        raise ValueError("Neither value or table specified for parameter!")

    @fixture(scope="session", params=params)
    def parameter_fixture(request):
        return request.param

    return parameter_fixture


def check_if_internal_capture(signal):
    if isinstance(signal, str):
        if _capture is None:
            raise ValueError(
                "Signal given as a string but there is no past captured data available yet."
            )
        else:
            signal = _capture[signal]
    return signal


_capture = None
marks = NoDuplicatesDict()


class wont_raise:
    """Used as a context manager where we don't expect any exception do be raised.
    Pytest still does not provide this out-of-the-box because of disagreements on naming.
    See: https://github.com/pytest-dev/pytest/issues/1830
    """

    def __init__(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *excinfo):
        pass


def assert_td_list_approx(_list, list_ref, tol):
    if len(_list) != len(list_ref):
        raise AssertionError("Compared lists do not have same length.")
    for val, ref in zip(_list, list_ref):  # noqa: B905
        if not ref - tol <= val <= ref + tol:
            raise AssertionError(
                f"Value {val} is not equal to {ref} within tolerance {tol}."
            )


def process(item):
    # Sanitize
    item = item.strip().replace(" ", "_")
    with contextlib.suppress(ValueError):
        item = float(item)

    return item


def _parse_table(table):
    lines = table.splitlines()
    if len(lines) < 2:
        raise Exception("Table should have at least two lines, header and value.")

    header_items = None

    param_list = []

    for line in lines:
        items = [process(item) for item in line.split("|")]
        if items == [""]:
            continue
        if not header_items:
            header_items = items
        else:
            assert len(items) == len(header_items), (
                f"Table row ({items}) has more/less elements than table header ({header_items})."
            )
            # Contains one parameter row in dictionary form
            param_dict = {}
            for n, item in enumerate(items):
                param_dict[header_items[n]] = item

            param_attributes = {}

            param_id = param_dict.pop("id", None)
            if param_id:
                param_attributes["id"] = param_id

            marks_cell = param_dict.pop("marks", None)
            if marks_cell:
                marks = [
                    getattr(_pytest.mark, mark.strip())
                    for mark in marks_cell.split(";")
                ]
                param_attributes["marks"] = marks

            param = _pytest.param(param_dict, **param_attributes)
            param_list.append(param)

    return param_list
