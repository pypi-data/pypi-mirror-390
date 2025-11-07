from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .constants import BROADCAST_NODE_ID, MAX_NODES
from .driver import BusAdapter
from .enums import CANAeroMessageTypeID, CANAeroServiceChannelID
from .frame import CANASMessage

# Use a TYPE_CHECKING block to import protocols for static analysis
# without creating a circular import at runtime.
if TYPE_CHECKING:
    from .protocols import (
        HookCallback,
        ParamCallback,
        ServicePollCallback,
        ServiceRequestCallback,
        ServiceResponseCallback,
    )


@dataclass
class TimestampedArg:
    timestamp_usec: int


@dataclass
class HookArgs(TimestampedArg):
    iface: int
    message: CANASMessage
    message_id: int
    redund_channel_id: int


@dataclass
class ParamCallbackArgs(TimestampedArg):
    message: CANASMessage
    argument: str
    message_id: int
    redund_channel_id: int


@dataclass
class ServicePollArgs(TimestampedArg):
    state: str


@dataclass
class ServiceRequestArgs(TimestampedArg):
    state: str
    message: CANASMessage
    service_channel: int


@dataclass
class ServiceResponseArgs(TimestampedArg):
    state: str
    message: CANASMessage


@dataclass
class ParamCacheEntry:
    timestamp_usec: int = 0
    message: CANASMessage | None = None


@dataclass
class ParamSubscription:
    message_id: int
    redund_count: int
    callback: ParamCallback | None
    callback_arg: Any | None
    redund_cache: list[ParamCacheEntry] = field(init=False)

    def __post_init__(self):
        self.redund_cache = [ParamCacheEntry()
                             for _ in range(self.redund_count)]


@dataclass
class ParamAdvertisement:
    message_id: int
    message_code: int = 0
    interlacing_next_iface: int = -1


@dataclass
class ServiceFrameHistoryEntry:
    node_id: int = 0
    ifaces_mask: int = 0xFF
    message_code: int = 0
    timestamp_usec: int = 0


@dataclass
class ServiceSubscription:
    service_code: int
    history_len: int
    pstate: Any | None
    callback_poll: ServicePollCallback | None
    callback_request: ServiceRequestCallback | None
    callback_response: ServiceResponseCallback | None
    history: list[ServiceFrameHistoryEntry] = field(init=False)

    def __post_init__(self):
        self.history = [ServiceFrameHistoryEntry()
                        for _ in range(self.history_len)]


TimestampFn = Callable[[], int]
SendFn = Callable[[], int]
FilterFn = Callable[[], int]


def service_channel_to_message_id(ch: int, is_request: bool) -> int:
    if (CANAeroServiceChannelID.SERVICE_CHANNEL_HIGH.value[0] <=
            ch <=
            CANAeroServiceChannelID.SERVICE_CHANNEL_HIGH.value[1]):
        base = CANAeroMessageTypeID.NODE_SERVICE_HIGH.value[0]
        offset = ch * 2
    elif (CANAeroServiceChannelID.SERVICE_CHANNEL_LOW.value[0] <=
          ch <= CANAeroServiceChannelID.SERVICE_CHANNEL_LOW.value[1]):
        base = CANAeroMessageTypeID.NODE_SERVICE_LOW.value[0]
        offset = (
            ch - CANAeroServiceChannelID.SERVICE_CHANNEL_LOW.value[0]) * 2
    else:
        raise ValueError("Invalid service channel")

    return base + (0 if is_request else 1) + offset


@dataclass
class CANAeroConfig:
    bus: BusAdapter
    timestamp: TimestampFn
    send_fn: SendFn
    filter_fn: FilterFn

    node_id: int
    filters: list

    hook: HookCallback | None = None
    iface_count: int = 1
    filters_per_iface: int = 0
    service_request_timeout_usec: int = 250_000
    service_poll_interval_usec: int = 10_000
    service_frame_hist_len: int = 4
    service_channel: int = 0
    repeat_timeout_usec: int = 1_000_000
    redundant_channel_id: int = 0

    def is_service_channel_valid(self):
        return (
            (CANAeroServiceChannelID.SERVICE_CHANNEL_HIGH.value[0] <=
             self.service_channel
             <= CANAeroServiceChannelID.SERVICE_CHANNEL_HIGH.value[1]) or
            CANAeroServiceChannelID.SERVICE_CHANNEL_LOW.value[
                0] <= self.service_channel <= CANAeroServiceChannelID.SERVICE_CHANNEL_LOW.value[1]
        )

    def _is_config_valid(self) -> bool:
        if not all([self.send_fn, self.timestamp]):
            return False
        if not (0 < self.iface_count <= MAX_NODES):
            return False
        if self.service_poll_interval_usec < 1 or self.service_request_timeout_usec < 1:
            return False
        if not self.filters and self.filters_per_iface > 0:
            return False
        return self.node_id == BROADCAST_NODE_ID
