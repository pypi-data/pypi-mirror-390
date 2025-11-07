from __future__ import annotations

from dataclasses import dataclass

from .datatypes import pack, unpack
from .enums import DataType


@dataclass(frozen=True)
class CANASMessage:
    can_id: int
    node_id: int
    data_type: DataType
    service_code: int
    message_code: int
    data: bytes  # Exactly 4 bytes!
    timestamp: int | None = 0
    channel: str | None = ''
    is_rx: bool | None = False

    def __post_init__(self):
        if self.data_type == DataType.NODATA:
            return
        if len(self.data) > 4:
            raise ValueError("Data must be at most 4 bytes long")

    def __str__(self):
        return (f"id=0x{self.can_id:08X} nid={self.node_id} dt={self.data_type.name} sc={self.service_code} "
                f"mc={self.message_code} data=0x{self.data.hex()}")

    def values(self) -> tuple[int | float, ...]:
        return unpack(self.data_type, self.data)

    def value(self):
        return self.values()[0]


def encode(msg: CANASMessage) -> bytes:
    """
    Message bytes breakdown
    [0..3] header: Node-ID, DataType, ServiceCode, MessageCode
    [4..7] data packet
    """
    return bytes([
        msg.node_id,
        int(msg.data_type) & 0xFF,
        msg.service_code & 0xFF,
        msg.message_code & 0xFF,
    ]) + msg.data


def decode(can_id: int, raw8: bytes) -> CANASMessage:
    if len(raw8) != 8:
        raise ValueError("CAN data should be exactly 8 bytes")

    node_id, raw_type, service_code, message_code = raw8[0:4]
    data_type = DataType(raw_type)
    data = raw8[4:8]

    return CANASMessage(can_id, node_id, data_type, service_code, message_code, data)


def build(can_id: int, node_id: int, data_type: DataType, service_code: int, message_code: int,
          values: tuple[int | float | str, ...]) -> CANASMessage:
    payload = pack(data_type, *values).ljust(4, b'\x00')
    return CANASMessage(can_id, node_id, data_type, service_code, message_code, payload)
