from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from .constants import ALL_IFACES, BROADCAST_NODE_ID, REDUND_CHAN_MULT
from .core import MessageGroup
from .driver import CAN_MASK_EXTID, CAN_MASK_STDID, CANFilterConfig, CANFlag, CANFrame
from .enums import DataType, MessageGroupID
from .frame import CANASMessage, build, decode, encode
from .types import (
    CANAeroConfig,
    HookArgs,
    ParamAdvertisement,
    ParamCallbackArgs,
    ParamSubscription,
    ServiceFrameHistoryEntry,
    ServicePollArgs,
    ServiceRequestArgs,
    ServiceResponseArgs,
    ServiceSubscription,
    service_channel_to_message_id,
)


@dataclass
class CANAerospaceInstance:
    config: CANAeroConfig

    last_service_ts: int = 0
    _service_subs: dict[int, ServiceSubscription] = field(default_factory=dict)
    _param_subs: dict[int, ParamSubscription] = field(default_factory=dict)
    _param_advs: dict[int, ParamAdvertisement] = field(default_factory=dict)

    def __post_init__(self):
        """
        Initializes the CANAerospace instance by setting up default
        filters on all interfaces to reject unsupported RTR frames.
        """
        rtr_filter = CANFilterConfig(id=0, mask=CANFlag.RTR.value)
        for i in range(self.config.iface_count):
            self.set_filters(i, [rtr_filter])

    def update_timestamp(self, iface: int, frame: CANFrame | None, timestamp: int):
        if frame is not None and not (0 <= iface < self.config.iface_count):
            raise ValueError("Invalid interface index")

        if frame is not None:
            try:
                if not (4 <= frame.dlc <= 8):
                    raise ValueError("Invalid DLC")
                if frame.is_rtr:
                    raise ValueError(
                        "RTR frames are not supported by the CANaerospace protocol")

                msg_id = frame.id & CAN_MASK_STDID
                redund_ch = 0
                if frame.is_extended_id:
                    redund_ch_raw = (
                        frame.id & CAN_MASK_EXTID) // REDUND_CHAN_MULT
                    if redund_ch_raw > 0xFF:
                        raise ValueError("Invalid redundancy channel ID")
                    redund_ch = int(redund_ch_raw)

                msg = decode(frame.id, frame.data)
                msg_group = MessageGroup.detect_message_group_id_from_id(
                    msg_id)

                if msg_group == MessageGroupID.WTF:
                    return

                self._issue_message_hook_callback(
                    iface, msg_id, msg, redund_ch, timestamp)

                if msg_group == MessageGroupID.PARAMETER:
                    sub = self._param_subs.get(msg_id)
                    if sub:
                        self._handle_received_param(
                            sub, msg_id, msg, redund_ch, timestamp)
                elif msg_group == MessageGroupID.SERVICE:
                    self._handle_service_message(iface, msg, timestamp, msg_id)

            except (ValueError, IndexError) as e:
                # Replace with proper logging
                print(f"Error processing frame: {e}")
                return

        self._poll_services(timestamp)

    def _handle_service_message(self, iface: int, msg: CANASMessage, timestamp: int, msg_id: int):
        is_request = (msg_id % 2 == 0)
        sub = self._service_subs.get(msg.service_code)
        if not sub:
            return

        if is_request:
            if not sub.callback_request:
                return

            # Request filtering
            history_entry = None
            for hist in sub.history:
                if hist.node_id == msg.node_id and hist.message_code == msg.message_code:
                    history_entry = hist
                    break

            if history_entry:
                if (timestamp - history_entry.timestamp_usec) < self.config.service_request_timeout_usec:
                    # Duplicate request within the timeout window. Filter it.
                    is_from_new_iface = not (
                        (1 << iface) & history_entry.ifaces_mask)
                    if is_from_new_iface:
                        history_entry.ifaces_mask |= (1 << iface)
                    return
                else:
                    # Timed out. Remove from history so it can be re-processed.
                    sub.history.remove(history_entry)

            # Process the request
            if len(sub.history) >= sub.history_len:
                sub.history.pop(0)
            sub.history.append(ServiceFrameHistoryEntry(node_id=msg.node_id, ifaces_mask=(
                1 << iface), message_code=msg.message_code, timestamp_usec=timestamp))

            args = ServiceRequestArgs(
                state=sub.pstate, message=msg, service_channel=self.config.service_channel, timestamp_usec=timestamp)
            sub.callback_request(args)
        else:  # Is response
            if sub.callback_response:
                args = ServiceResponseArgs(
                    state=sub.pstate, message=msg, timestamp_usec=timestamp)
                sub.callback_response(args)

    def _poll_services(self, timestamp: int):
        if timestamp - self.last_service_ts < self.config.service_poll_interval_usec:
            return

        self.last_service_ts = timestamp
        for sub in self._service_subs.values():
            if sub.callback_poll:
                args = ServicePollArgs(
                    state=sub.pstate,
                    timestamp_usec=timestamp
                )
                sub.callback_poll(args)

    def _handle_received_param(self,
                               sub: ParamSubscription,
                               msg_id: int, msg: CANASMessage,
                               redund_ch: int, timestamp: int):
        if not (0 <= redund_ch < sub.redund_count):
            return

        cache_entry = sub.redund_cache[redund_ch]

        if (
                cache_entry.timestamp_usec > 0
                and (timestamp - cache_entry.timestamp_usec) < self.config.repeat_timeout_usec
                and cache_entry.message
        ):
                msg_code_diff = MessageGroup.diff_u8(
                    msg.message_code, cache_entry.message.message_code)
                if msg_code_diff <= 0:
                    return

        cache_entry.message = msg
        cache_entry.timestamp_usec = timestamp

        if sub.callback:
            args = ParamCallbackArgs(
                message=msg,
                argument=sub.callback_arg,
                message_id=msg_id,
                redund_channel_id=redund_ch,
                timestamp_usec=timestamp
            )
            sub.callback(args)

    def send(self, iface: int, frame: CANFrame) -> int:
        return self.config.bus.send(iface, frame)

    def set_filters(self, iface: int, filters: list[CANFilterConfig]) -> int:
        return self.config.bus.set_filters(iface, filters)

    def _issue_message_hook_callback(self,
                                     iface: int,
                                     message_id: int,
                                     message: CANASMessage,
                                     redundant_channel: int,
                                     timestamp_usec: int):
        if self.config.hook is None:
            return

        args = HookArgs(iface=iface, message=message, message_id=message_id,
                        redund_channel_id=redundant_channel, timestamp_usec=timestamp_usec)
        self.config.hook(args)

    def param_subscribe(self,
                        msg_id: int,
                        redund_chan_count: int,
                        callback: Callable[[ParamCallbackArgs], None] | None,
                        callback_arg: Any | None = None):
        if MessageGroup.detect_message_group_id_from_id(msg_id) != MessageGroupID.PARAMETER:
            raise ValueError("Bad message ID for parameter subscription")
        if redund_chan_count < 1:
            raise ValueError("Redundancy channel count must be at least 1")
        if msg_id in self._param_subs:
            raise ValueError(f"Subscription for message ID {msg_id} already exists")

        sub = ParamSubscription(
            message_id=msg_id,
            redund_count=redund_chan_count,
            callback=callback,
            callback_arg=callback_arg
        )

        self._param_subs[msg_id] = sub

    def param_advertise(self, msg_id: int, interlaced: bool):
        if MessageGroup.detect_message_group_id_from_id(msg_id) != MessageGroupID.PARAMETER:
            raise ValueError("Bad message ID for parameter advertisement")
        if msg_id in self._param_advs:
            raise ValueError(f"Advertisement for message ID {msg_id} already exists")

        if self.config.iface_count < 2:
            interlaced = False

        adv = ParamAdvertisement(
            message_id=msg_id,
            interlacing_next_iface=0 if interlaced else ALL_IFACES
        )

        self._param_advs[msg_id] = adv

    def _generic_send(self, iface: int, msg_id: int, msg_group: MessageGroupID, message: CANASMessage):
        can_id = msg_id & CAN_MASK_STDID
        if msg_group == MessageGroupID.PARAMETER and self.config.redundant_channel_id > 0:
            can_id |= (self.config.redundant_channel_id *
                       REDUND_CHAN_MULT) | CANFlag.EFF.value

        encoded_data = encode(message)
        can_frame_to_send = CANFrame(
            id=can_id, dlc=len(encoded_data), _data=encoded_data)

        if iface == ALL_IFACES:
            sent_successfully = False
            for i in range(self.config.iface_count):
                send_result = self.send(i, can_frame_to_send)
                if send_result == 1:
                    sent_successfully = True
            if not sent_successfully:
                raise RuntimeError("Failed to send on any interface")
        else:
            send_result = self.send(iface, can_frame_to_send)
            if send_result != 1:
                raise RuntimeError(f"Failed to send on interface {iface}")

    def param_publish(self, msg_id: int, data_type: DataType, values: tuple[int | float, ...], service_code: int):
        if MessageGroup.detect_message_group_id_from_id(msg_id) != MessageGroupID.PARAMETER:
            raise ValueError("Bad message ID for parameter publication")

        adv = self._param_advs.get(msg_id)
        if adv is None:
            raise ValueError(f"Message ID {msg_id} is not advertised")

        iface = ALL_IFACES
        if adv.interlacing_next_iface != ALL_IFACES:
            iface = adv.interlacing_next_iface
            adv.interlacing_next_iface += 1
            if adv.interlacing_next_iface >= self.config.iface_count:
                adv.interlacing_next_iface = 0

        message = build(
            can_id=msg_id,
            node_id=self.config.node_id,
            data_type=data_type,
            service_code=service_code,
            message_code=adv.message_code,
            values=values
        )
        adv.message_code += 1

        self._generic_send(iface, msg_id, MessageGroupID.PARAMETER, message)

    def service_register(self,
                         service_code: int,
                         callback_poll: Callable[[ServicePollArgs], None] | None,
                         callback_request: Callable[[ServiceRequestArgs], None] | None,
                         callback_response: Callable[[ServiceResponseArgs], None] | None,
                         pstate: Any | None = None):
        if service_code in self._service_subs:
            raise ValueError(f"Service with code {service_code} is already registered")

        sub = ServiceSubscription(
            service_code=service_code,
            history_len=self.config.service_frame_hist_len,
            pstate=pstate,
            callback_poll=callback_poll,
            callback_request=callback_request,
            callback_response=callback_response
        )

        self._service_subs[service_code] = sub

    def service_unregister(self, service_code: int):
        if service_code not in self._service_subs:
            raise ValueError(f"Service with code {service_code} is not registered")
        del self._service_subs[service_code]

    def service_get_state(self, service_code: int) -> Any | None:
        sub = self._service_subs.get(service_code)
        if sub is None:
            raise ValueError(f"Service with code {service_code} is not registered")
        return sub.pstate

    def service_set_state(self, service_code: int, pstate: Any | None):
        sub = self._service_subs.get(service_code)
        if sub is None:
            raise ValueError(f"Service with code {service_code} is not registered")
        sub.pstate = pstate

    def service_send_request(self, message: CANASMessage):
        if message.node_id == self.config.node_id:
            raise ValueError("Self-addressed service requests are not allowed")

        msg_id = service_channel_to_message_id(
            self.config.service_channel, True)
        self._generic_send(ALL_IFACES, msg_id, MessageGroupID.SERVICE, message)

    def service_send_response(self, message: CANASMessage, service_channel: int):
        msg = message
        if msg.node_id == BROADCAST_NODE_ID:
            msg.node_id = self.config.node_id

        if msg.node_id != self.config.node_id:
            raise ValueError(
                "Usage of foreign Node ID in response is against specification.")

        msg_id = service_channel_to_message_id(service_channel, False)
        self._generic_send(ALL_IFACES, msg_id, MessageGroupID.SERVICE, msg)
