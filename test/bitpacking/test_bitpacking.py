from typing import Tuple
from unittest.mock import MagicMock, call

import pytest

from randovania.bitpacking import bitpacking


@pytest.mark.parametrize("value", [
    10,
    65,
    0,
    1,
    2,
    134,
])
@pytest.mark.parametrize("limits", [
    (5, 20, 500),
    (3, 50, 150),
])
def test_encode_int_with_limits_round_trip(value: int,
                                           limits: Tuple[int, ...],
                                           ):
    # Run
    data = bitpacking._pack_encode_results(list(bitpacking.encode_int_with_limits(value, limits)))
    decoded = bitpacking.decode_int_with_limits(bitpacking.BitPackDecoder(data), limits)

    # Assert
    assert decoded == value


@pytest.fixture(
    params=[
        (5, (10,), [(5, 11)]),
        (50, (10,), [(50, 11)]),
        (5, (10, 100), [(5, 11)]),
        (50, (10, 100), [(10, 11), (40, 91)]),
        (5, (10, 100, 500), [(5, 11)]),
        (50, (10, 100, 500), [(10, 11), (40, 91)]),
        (500, (10, 100, 500), [(10, 11), (90, 91), (400, 401)]),
    ],
    name="limits_fixture")
def _limits_fixture(request):
    return request.param[0], request.param[1], request.param[2]


def test_encode_int_with_limits(limits_fixture):
    # Setup
    value, limits, encoded = limits_fixture

    # Run
    result = list(bitpacking.encode_int_with_limits(value, limits))

    # Assert
    assert result == encoded


def test_decode_int_with_limits(limits_fixture):
    # Setup
    value, limits, encoded = limits_fixture
    decoder = MagicMock()
    decoder.decode_single.side_effect = [part for part, _ in encoded]

    # Run
    result = bitpacking.decode_int_with_limits(decoder, limits)

    # Assert
    decoder.decode_single.assert_has_calls([
        call(limit)
        for _, limit in encoded
    ])
    assert result == value

