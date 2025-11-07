from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from enum import IntFlag
from typing import Protocol

from can import Message

CAN_MASK_STDID: int = 0x000007FF
CAN_MASK_EXTID: int = 0x1FFFFFFF


class CANFlag(IntFlag):
    EFF = 1 << 31  # Extended Frame Format
    RTR = 1 << 30  # Remote Transmission Request


@dataclass(frozen=True)
class CANFrame:
    id: int
    dlc: int
    _data: bytes

    @property
    def data(self):
        return self._data[: self.dlc]
        # return self._data

    @staticmethod
    def validate_dlc(dlc) -> bool:
        return 0 <= dlc <= 8

    @staticmethod
    def validate_data(data) -> bool:
        return len(data) == 8

    def __post_init__(self) -> None:
        if not self.validate_dlc(self.dlc):
            raise ValueError("Data Length Code must be between 0 and 8")

        if not self.validate_data(self.data):
            raise ValueError("Data must be 8 bytes long")

    def is_extended_id(self):
        return bool(self.id & CANFlag.EFF)

    def is_remote_transport_request(self):
        return bool(self.id & CANFlag.RTR)

    def get_dlc_data(self):
        return self.data[: self.dlc]

    @property
    def is_rtr(self):
        return False


@dataclass(frozen=True)
class CANFilterConfig:
    id: int
    mask: int


class CANSendFn(Protocol):
    def __call__(self, iface: int, frame: CANFrame) -> int:
        ...


class CANFilterFn(Protocol):
    def __call__(self, iface: int, filters: Iterable[CANFilterConfig]) -> int:
        ...


class BusAdapter(Protocol):
    def send(self, iface: int, frame: CANFrame) -> int: ...

    def set_filters(self, iface: int,
                    filters: Iterable[CANFilterConfig]) -> int: ...


""" Try to support python-can virtual"""
try:
    import can

    class PythonCANAdapter:

        def __init__(self,
                     buses: list[can.Bus] | None = None, *,
                     interface: str = 'virtual',
                     channel_prefix: str = 'vcan',
                     iface_count: int,
                     bitrate: int = 500_000) -> None:
            if buses is None:
                buses = [can.Bus(
                    interface=interface, channel=f'{channel_prefix}{i}',
                    bitrate=bitrate) for i in range(iface_count)]
            self._buses = buses

        def send(self, iface: int, frame: CANFrame) -> int:
            bus = self._buses[iface]
            is_ext = frame.is_extended_id()
            is_rtr = frame.is_remote_transport_request()
            msg = Message(
                # Force the id to be of a certain length
                arbitration_id=frame.id & (
                    CAN_MASK_EXTID if is_ext else CAN_MASK_STDID),
                is_extended_id=is_ext,
                is_remote_frame=is_rtr,
                data=frame.data,
                dlc=frame.dlc,
            )
            bus.send(msg)
            return 1

        def send_multiple(self, ifaces: list[int], frame: CANFrame) -> list[int]:
            results = []
            for int_index in ifaces:
                results.append(self.send(iface=int_index, frame=frame))
            return results

        def set_filters(self, iface: int, filters: Iterable[CANFilterConfig]) -> int:
            bus = self._buses[iface]
            can_filters = []
            for filtr in filters:
                extended = (filtr.id > CAN_MASK_STDID) or (
                    filtr.mask > CAN_MASK_STDID)
                can_filters.append({
                    "can_id": filtr.id,
                    "can_mask": filtr.mask,
                    "extended": extended,
                })
            bus.set_filters(can_filters)
            return 1

except Exception:
    PythonCANAdapter = None
