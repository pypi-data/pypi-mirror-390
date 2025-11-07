from __future__ import annotations

import math

from hypothesis import given
from hypothesis import strategies as st

from canaerospace.datatypes import pack, unpack
from canaerospace.enums import DataType


@given(st.floats(width=32, allow_nan=False, allow_infinity=False))
def test_float_fuzzing(value: float):
    """Test that packing and unpacking a float returns the same value."""
    packed = pack(DataType.FLOAT, value)
    unpacked = unpack(DataType.FLOAT, packed)

    assert unpacked is not None
    assert len(unpacked) == 1
    assert math.isclose(unpacked[0], value, rel_tol=1e-6)


@given(st.integers(min_value=-2**31, max_value=2**31 - 1))
def test_long_fuzzing(value: int):
    """Test that packing and unpacking a LONG returns the same value."""
    packed = pack(DataType.LONG, value)
    unpacked = unpack(DataType.LONG, packed)

    assert unpacked is not None
    assert len(unpacked) == 1
    assert unpacked[0] == value


@given(st.integers(min_value=0, max_value=2**32 - 1))
def test_ulong_fuzzing(value: int):
    """Test that packing and unpacking a ULONG returns the same value."""
    packed = pack(DataType.ULONG, value)
    unpacked = unpack(DataType.ULONG, packed)

    assert unpacked is not None
    assert len(unpacked) == 1
    assert unpacked[0] == value


@given(st.integers(min_value=-2**15, max_value=2**15 - 1))
def test_short_fuzzing(value: int):
    """Test that packing and unpacking a SHORT returns the same value."""
    packed = pack(DataType.SHORT, value)
    unpacked = unpack(DataType.SHORT, packed)

    assert unpacked is not None
    assert len(unpacked) == 1
    assert unpacked[0] == value


@given(st.integers(min_value=0, max_value=2**16 - 1))
def test_ushort_fuzzing(value: int):
    """Test that packing and unpacking a USHORT returns the same value."""
    packed = pack(DataType.USHORT, value)
    unpacked = unpack(DataType.USHORT, packed)

    assert unpacked is not None
    assert len(unpacked) == 1
    assert unpacked[0] == value


@given(st.integers(min_value=-128, max_value=127))
def test_char_fuzzing(value: int):
    """Test that packing and unpacking a CHAR returns the same value."""
    packed = pack(DataType.CHAR, value)
    unpacked = unpack(DataType.CHAR, packed)

    assert unpacked is not None
    assert len(unpacked) == 1
    assert unpacked[0] == value


@given(st.integers(min_value=0, max_value=255))
def test_uchar_fuzzing(value: int):
    """Test that packing and unpacking a UCHAR returns the same value."""
    packed = pack(DataType.UCHAR, value)
    unpacked = unpack(DataType.UCHAR, packed)

    assert unpacked is not None
    assert len(unpacked) == 1
    assert unpacked[0] == value


@given(st.text(
    alphabet=st.characters(min_codepoint=0, max_codepoint=127),
    min_size=1, max_size=1))
def test_achar_fuzzing(value: str):
    """Test that packing and unpacking an ACHAR returns the same value."""
    packed = pack(DataType.ACHAR, value)
    unpacked = unpack(DataType.ACHAR, packed)

    assert unpacked is not None
    assert len(unpacked) == 1
    assert unpacked[0] == value


@given(st.tuples(
    st.integers(min_value=-128, max_value=127),
    st.integers(min_value=-128, max_value=127)))
def test_char2_fuzzing(values: tuple[int, int]):
    """Test that packing and unpacking a CHAR2 returns the same values."""
    packed = pack(DataType.CHAR2, *values)
    unpacked = unpack(DataType.CHAR2, packed)

    assert unpacked is not None
    assert len(unpacked) == 2
    assert unpacked == values


@given(st.tuples(
    st.integers(min_value=0, max_value=255),
    st.integers(min_value=0, max_value=255)))
def test_uchar2_fuzzing(values: tuple[int, int]):
    """Test that packing and unpacking a UCHAR2 returns the same values."""
    packed = pack(DataType.UCHAR2, *values)
    unpacked = unpack(DataType.UCHAR2, packed)

    assert unpacked is not None
    assert len(unpacked) == 2
    assert unpacked == values


@given(st.text(
    alphabet=st.characters(min_codepoint=0, max_codepoint=127),
    min_size=2, max_size=2))
def test_achar2_fuzzing(value: str):
    """Test that packing and unpacking an ACHAR2 returns the same value."""
    packed = pack(DataType.ACHAR2, value)
    unpacked = unpack(DataType.ACHAR2, packed)

    assert unpacked is not None
    assert len(unpacked) == 2
    assert "".join(unpacked) == value


@given(st.tuples(st.integers(min_value=-128, max_value=127),
                 st.integers(min_value=-128, max_value=127),
                 st.integers(min_value=-128, max_value=127)))
def test_char3_fuzzing(values: tuple[int, int, int]):
    """Test that packing and unpacking a CHAR3 returns the same values."""
    packed = pack(DataType.CHAR3, *values)
    unpacked = unpack(DataType.CHAR3, packed)

    assert unpacked is not None
    assert len(unpacked) == 3
    assert unpacked == values


@given(st.tuples(st.integers(min_value=0, max_value=255),
                 st.integers(min_value=0, max_value=255),
                 st.integers(min_value=0, max_value=255)))
def test_uchar3_fuzzing(values: tuple[int, int, int]):
    """Test that packing and unpacking a UCHAR3 returns the same values."""
    packed = pack(DataType.UCHAR3, *values)
    unpacked = unpack(DataType.UCHAR3, packed)

    assert unpacked is not None
    assert len(unpacked) == 3
    assert unpacked == values


@given(st.text(
    alphabet=st.characters(min_codepoint=0, max_codepoint=127),
    min_size=3, max_size=3))
def test_achar3_fuzzing(value: str):
    """Test that packing and unpacking an ACHAR3 returns the same value."""
    packed = pack(DataType.ACHAR3, value)
    unpacked = unpack(DataType.ACHAR3, packed)

    assert unpacked is not None
    assert len(unpacked) == 3
    assert "".join(unpacked) == value


@given(st.tuples(st.integers(min_value=-128, max_value=127),
                 st.integers(min_value=-128, max_value=127),
                 st.integers(min_value=-128, max_value=127),
                 st.integers(min_value=-128, max_value=127)))
def test_char4_fuzzing(values: tuple[int, int, int, int]):
    """Test that packing and unpacking a CHAR4 returns the same values."""
    packed = pack(DataType.CHAR4, *values)
    unpacked = unpack(DataType.CHAR4, packed)

    assert unpacked is not None
    assert len(unpacked) == 4
    assert unpacked == values


@given(st.tuples(st.integers(min_value=0, max_value=255),
                 st.integers(min_value=0, max_value=255),
                 st.integers(min_value=0, max_value=255),
                 st.integers(min_value=0, max_value=255)))
def test_uchar4_fuzzing(values: tuple[int, int, int, int]):
    """Test that packing and unpacking a UCHAR4 returns the same values."""
    packed = pack(DataType.UCHAR4, *values)
    unpacked = unpack(DataType.UCHAR4, packed)

    assert unpacked is not None
    assert len(unpacked) == 4
    assert unpacked == values


@given(st.text(
    alphabet=st.characters(min_codepoint=0, max_codepoint=127),
    min_size=4, max_size=4))
def test_achar4_fuzzing(value: str):
    """Test that packing and unpacking an ACHAR4 returns the same value."""
    packed = pack(DataType.ACHAR4, value)
    unpacked = unpack(DataType.ACHAR4, packed)

    assert unpacked is not None
    assert len(unpacked) == 4
    assert "".join(unpacked) == value


@given(st.tuples(
    st.integers(min_value=-2**15, max_value=2**15 - 1),
    st.integers(min_value=-2**15, max_value=2**15 - 1)))
def test_short2_fuzzing(values: tuple[int, int]):
    """Test that packing and unpacking a SHORT2 returns the same values."""
    packed = pack(DataType.SHORT2, *values)
    unpacked = unpack(DataType.SHORT2, packed)

    assert unpacked is not None
    assert len(unpacked) == 2
    assert unpacked == values


@given(st.tuples(
    st.integers(min_value=0, max_value=2**16 - 1),
    st.integers(min_value=0, max_value=2**16 - 1)))
def test_ushort2_fuzzing(values: tuple[int, int]):
    """Test that packing and unpacking a USHORT2 returns the same values."""
    packed = pack(DataType.USHORT2, *values)
    unpacked = unpack(DataType.USHORT2, packed)

    assert unpacked is not None
    assert len(unpacked) == 2
    assert unpacked == values


@given(st.tuples(
    st.integers(min_value=-2**15, max_value=2**15 - 1),
    st.integers(min_value=-2**15, max_value=2**15 - 1),
    st.integers(min_value=-2**15, max_value=2**15 - 1)))
def test_short3_fuzzing(values: tuple[int, int, int]):
    """Test that packing and unpacking a SHORT3 returns the same values."""
    packed = pack(DataType.SHORT3, *values)
    unpacked = unpack(DataType.SHORT3, packed)

    assert unpacked is not None
    assert len(unpacked) == 3
    assert unpacked == values


@given(st.tuples(
    st.integers(min_value=0, max_value=2**16 - 1),
    st.integers(min_value=0, max_value=2**16 - 1),
    st.integers(min_value=0, max_value=2**16 - 1)))
def test_ushort3_fuzzing(values: tuple[int, int, int]):
    """Test that packing and unpacking a USHORT3 returns the same values."""
    packed = pack(DataType.USHORT3, *values)
    unpacked = unpack(DataType.USHORT3, packed)

    assert unpacked is not None
    assert len(unpacked) == 3
    assert unpacked == values


@given(st.tuples(
    st.integers(min_value=-2**15, max_value=2**15 - 1),
    st.integers(min_value=-2**15, max_value=2**15 - 1),
    st.integers(min_value=-2**15, max_value=2**15 - 1),
    st.integers(min_value=-2**15, max_value=2**15 - 1)))
def test_short4_fuzzing(values: tuple[int, int, int, int]):
    """Test that packing and unpacking a SHORT4 returns the same values."""
    packed = pack(DataType.SHORT4, *values)
    unpacked = unpack(DataType.SHORT4, packed)

    assert unpacked is not None
    assert len(unpacked) == 4
    assert unpacked == values


@given(st.tuples(
    st.integers(min_value=0, max_value=2**16 - 1),
    st.integers(min_value=0, max_value=2**16 - 1),
    st.integers(min_value=0, max_value=2**16 - 1),
    st.integers(min_value=0, max_value=2**16 - 1)))
def test_ushort4_fuzzing(values: tuple[int, int, int, int]):
    """Test that packing and unpacking a USHORT4 returns the same values."""
    packed = pack(DataType.USHORT4, *values)
    unpacked = unpack(DataType.USHORT4, packed)

    assert unpacked is not None
    assert len(unpacked) == 4
    assert unpacked == values


@given(st.tuples(
    st.integers(min_value=-2**31, max_value=2**31 - 1),
    st.integers(min_value=-2**31, max_value=2**31 - 1)))
def test_long2_fuzzing(values: tuple[int, int]):
    """Test that packing and unpacking a LONG2 returns the same values."""
    packed = pack(DataType.LONG2, *values)
    unpacked = unpack(DataType.LONG2, packed)

    assert unpacked is not None
    assert len(unpacked) == 2
    assert unpacked == values


@given(st.tuples(
    st.integers(min_value=0, max_value=2**32 - 1),
    st.integers(min_value=0, max_value=2**32 - 1)))
def test_ulong2_fuzzing(values: tuple[int, int]):
    """Test that packing and unpacking a ULONG2 returns the same values."""
    packed = pack(DataType.ULONG2, *values)
    unpacked = unpack(DataType.ULONG2, packed)

    assert unpacked is not None
    assert len(unpacked) == 2
    assert unpacked == values
