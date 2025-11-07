from __future__ import annotations

import struct

from .enums import DataType

# As per CANAS 1.7 Spec - Use Big Endian (BE) for wire-representation
BE = ">"


class PackingError(Exception):
    pass


def pack(data_type: DataType, *values: int | float | str) -> bytes:
    """Pack data into bytes, ensuring the result is exactly 4 bytes."""
    try:
        payload = b''
        match data_type:
            case DataType.NODATA:
                if values:
                    raise PackingError("NODATA should not have values")
                payload = b''

            case DataType.FLOAT:
                if len(values) != 1:
                    raise PackingError(
                        f"FLOAT requires exactly one value, got {len(values)}")
                payload = struct.pack(BE + "f", float(values[0]))

            case DataType.LONG | DataType.ULONG | DataType.MEMID | DataType.DOUBLEH | DataType.DOUBLEL:
                if len(values) != 1:
                    raise PackingError(
                        f"{data_type.name} requires exactly one value, got {len(values)}")
                fmt_map = {
                    DataType.LONG: "i",
                    DataType.ULONG: "I",
                    DataType.MEMID: "I",
                    DataType.DOUBLEH: "I",
                    DataType.DOUBLEL: "I",
                }
                payload = struct.pack(BE + fmt_map[data_type], int(values[0]))

            case DataType.SHORT | DataType.USHORT:
                if len(values) != 1:
                    raise PackingError(
                        f"{data_type.name} requires exactly one value, got {len(values)}")
                fmt = "h" if data_type == DataType.SHORT else "H"
                payload = struct.pack(BE + fmt, int(values[0]))

            case DataType.CHAR | DataType.UCHAR:
                if len(values) != 1:
                    raise PackingError(
                        f"{data_type.name} requires exactly one value, got {len(values)}")
                fmt = "b" if data_type == DataType.CHAR else "B"
                payload = struct.pack(BE + fmt, int(values[0]))

            case DataType.ACHAR:
                if len(values) == 1 and isinstance(values[0], str) and len(values[0]) == 1:
                    payload = values[0].encode('ascii')
                else:
                    raise PackingError(
                        "ACHAR requires a single one-character string")

            case DataType.CHAR2 | DataType.UCHAR2:
                if len(values) != 2:
                    raise PackingError(f"{data_type.name} requires two values")
                fmt = "bb" if data_type == DataType.CHAR2 else "BB"
                payload = struct.pack(BE + fmt, *[int(v) for v in values])

            case DataType.ACHAR2:
                if len(values) == 1 and isinstance(values[0], str) and len(values[0]) == 2:
                    payload = values[0].encode('ascii')
                elif len(values) == 2 and all(isinstance(v, str) and len(v) == 1 for v in values):
                    payload = "".join(values).encode('ascii')
                else:
                    raise PackingError(
                        "ACHAR2 requires a two-character string or two single characters")

            case DataType.CHAR4 | DataType.UCHAR4:
                if len(values) != 4:
                    raise PackingError(
                        f"{data_type.name} requires four values")
                fmt = "bbbb" if data_type == DataType.CHAR4 else "BBBB"
                payload = struct.pack(BE + fmt, *[int(v) for v in values])

            case DataType.ACHAR4:
                if len(values) == 1 and isinstance(values[0], str) and len(values[0]) == 4:
                    payload = values[0].encode('ascii')
                elif len(values) == 4 and all(isinstance(v, str) and len(v) == 1 for v in values):
                    payload = "".join(values).encode('ascii')
                else:
                    raise PackingError(
                        "ACHAR4 requires a four-character string or four single characters")

            case DataType.SHORT2 | DataType.USHORT2:
                if len(values) != 2:
                    raise PackingError(f"{data_type.name} requires two values")
                fmt = "hh" if data_type == DataType.SHORT2 else "HH"
                payload = struct.pack(BE + fmt, *[int(v) for v in values])

            case DataType.LONG2 | DataType.ULONG2:
                if len(values) != 2:
                    raise PackingError(f"{data_type.name} requires two values")
                fmt = "ii" if data_type == DataType.LONG2 else "II"
                payload = struct.pack(BE + fmt, *[int(v) for v in values])

            case DataType.CHAR3 | DataType.UCHAR3:
                if len(values) != 3:
                    raise PackingError(f"{data_type.name} requires three values")
                fmt = "bbb" if data_type == DataType.CHAR3 else "BBB"
                payload = struct.pack(BE + fmt, *[int(v) for v in values])

            case DataType.ACHAR3:
                if len(values) == 1 and isinstance(values[0], str) and len(values[0]) == 3:
                    payload = values[0].encode('ascii')
                elif len(values) == 3 and all(isinstance(v, str) and len(v) == 1 for v in values):
                    payload = "".join(values).encode('ascii')
                else:
                    raise PackingError(
                        "ACHAR3 requires a three-character string or three single characters")

            case DataType.SHORT3 | DataType.USHORT3:
                if len(values) != 3:
                    raise PackingError(f"{data_type.name} requires three values")
                fmt = "hhh" if data_type == DataType.SHORT3 else "HHH"
                payload = struct.pack(BE + fmt, *[int(v) for v in values])

            case DataType.SHORT4 | DataType.USHORT4:
                if len(values) != 4:
                    raise PackingError(f"{data_type.name} requires four values")
                fmt = "hhhh" if data_type == DataType.SHORT4 else "HHHH"
                payload = struct.pack(BE + fmt, *[int(v) for v in values])

            case _:
                raise PackingError(
                    f"Unsupported or reserved data type for packing: {data_type.name}")

        return payload

    except (struct.error, TypeError, ValueError, AttributeError, IndexError) as e:
        raise PackingError(
            f"Failed to pack {data_type.name} with values {values}: {e}") from e


def unpack(data_type: DataType, data: bytes) -> tuple[int | float, ...]:
    try:
        match data_type:
            case DataType.NODATA:
                return ()
            case DataType.FLOAT:
                return struct.unpack(BE + "f", data[:4])
            case DataType.LONG:
                return (struct.unpack(BE + "i", data[:4])[0],)
            case DataType.ULONG | DataType.MEMID:
                return (struct.unpack(BE + "I", data[:4])[0],)
            case DataType.SHORT:
                return (struct.unpack(BE + "h", data[:2])[0],)
            case DataType.USHORT:
                return (struct.unpack(BE + "H", data[:2])[0],)
            case DataType.CHAR:
                return (struct.unpack(BE + "b", data[:1])[0],)
            case DataType.UCHAR:
                return (struct.unpack(BE + "B", data[:1])[0],)
            case DataType.ACHAR:
                return (data[:1].decode('ascii'),)
            case DataType.CHAR2:
                return struct.unpack(BE + "bb", data[:2])
            case DataType.UCHAR2:
                return struct.unpack(BE + "BB", data[:2])
            case DataType.ACHAR2:
                return tuple(data[:2].decode('ascii'))
            case DataType.CHAR4:
                return struct.unpack(BE + "bbbb", data[:4])
            case DataType.UCHAR4:
                return struct.unpack(BE + "BBBB", data[:4])
            case DataType.ACHAR4:
                return tuple(data[:4].decode('ascii'))
            case DataType.DOUBLEH | DataType.DOUBLEL:
                return (struct.unpack(BE + "I", data[:4])[0],)
            case DataType.SHORT2:
                return struct.unpack(BE + "hh", data[:4])
            case DataType.USHORT2:
                return struct.unpack(BE + "HH", data[:4])
            case DataType.LONG2:
                return struct.unpack(BE + "ii", data[:8])
            case DataType.ULONG2:
                return struct.unpack(BE + "II", data[:8])
            case DataType.CHAR3:
                return struct.unpack(BE + "bbb", data[:3])
            case DataType.UCHAR3:
                return struct.unpack(BE + "BBB", data[:3])
            case DataType.ACHAR3:
                return tuple(data[:3].decode('ascii'))
            case DataType.SHORT3:
                return struct.unpack(BE + "hhh", data[:6])
            case DataType.USHORT3:
                return struct.unpack(BE + "HHH", data[:6])
            case DataType.SHORT4:
                return struct.unpack(BE + "hhhh", data[:8])
            case DataType.USHORT4:
                return struct.unpack(BE + "HHHH", data[:8])
            case _:
                raise PackingError(
                    f"Unsupported or reserved data type for unpacking: {data_type.name}")
    except (struct.error, UnicodeDecodeError) as e:
        raise PackingError(
            f"Failed to unpack {data_type} from data {data}: {e}") from e
