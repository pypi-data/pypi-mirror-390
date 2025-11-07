# mypy: disable-error-code="arg-type"

import numpy

from ...client import _parse_data_types


def test_parse_data_types():
    # null case
    assert _parse_data_types(None) == []

    # list vs. non-list case
    expected = ["float64"]
    assert _parse_data_types(expected) == expected
    assert _parse_data_types(expected[0]) == expected

    # equivalent data types
    expected = ["int32", "float64"]
    assert _parse_data_types(expected) == expected
    assert _parse_data_types([numpy.int32, numpy.float64]) == expected
    assert _parse_data_types([numpy.dtype("int32"), numpy.dtype("float64")]) == expected
