import pytest

from canaerospace.datatypes import PackingError, pack, unpack
from canaerospace.enums import DataType


class TestDatatypes:
    def test_pack_errors(self):
        with pytest.raises(PackingError):
            pack(DataType.RESVD, 123)

    def test_unpack_errors(self):
        with pytest.raises(PackingError):
            unpack(DataType.RESVD, b'\x00')

    def test_pack_unpack_symmetry(self):
        # These test cases use the exact byte lengths as defined by the spec,
        # without any padding.
        test_cases = [
            (DataType.FLOAT, (3.14,), b'\x40\x48\xf5\xc3'),
            (DataType.LONG, (-123456789,), b'\xf8\xa4\x32\xeb'),
            (DataType.ULONG, (123456789,), b'\x07\x5b\xcd\x15'),
            (DataType.SHORT, (-1234,), b'\xfb\x2e'),
            (DataType.USHORT, (1234,), b'\x04\xd2'),
            (DataType.CHAR, (-100,), b'\x9c'),
            (DataType.UCHAR, (100,), b'\x64'),
            (DataType.CHAR2, (-10, 20), b'\xf6\x14'),
            (DataType.UCHAR2, (10, 20), b'\x0a\x14'),
            (DataType.CHAR4, (-10, 20, -30, 40), b'\xf6\x14\xe2\x28'),
            (DataType.UCHAR4, (10, 20, 30, 40), b'\x0a\x14\x1e\x28'),
            (DataType.NODATA, (), b''),  # NODATA is 0 bytes
        ]

        for data_type, values, expected_bytes in test_cases:
            # Test packing
            packed = pack(data_type, *values)
            assert packed == expected_bytes

            # Test unpacking
            unpacked = unpack(data_type, packed)
            if data_type == DataType.FLOAT:
                assert unpacked is not None
                assert pytest.approx(unpacked[0], 0.01) == values[0]
            else:
                assert unpacked == values
