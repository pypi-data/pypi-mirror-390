from __future__ import annotations

import math
import time
from dataclasses import dataclass


class CANASSwitchReasons:
    REASON_NONE = 0
    REASON_INIT = 1
    REASON_FOM = 2
    REASON_TIMEOUT = 3


@dataclass
class CANASGRRConfig:
    num_channels: int = 0
    fom_hysteresis: float = 0.0
    min_fom_switch_interval_usec: int = 0
    channel_timeout_usec: int = 0


@dataclass
class CANASGRRChannelState:
    fom: float = -float('inf')
    last_update_timestamp_usec: int = 0


class CANASGRRInstance:
    def __init__(self, config: CANASGRRConfig):
        if not self._is_config_ok(config):
            raise ValueError("Invalid config")
        self.config = config
        self.channels: list[CANASGRRChannelState] = [
            CANASGRRChannelState() for _ in range(config.num_channels)]
        self.active_channel = 0
        self.last_switch_timestamp_usec = 0

    def _is_config_ok(self, config: CANASGRRConfig) -> bool:
        return (config.num_channels > 0 and
                config.channel_timeout_usec > 0 and
                math.isfinite(config.fom_hysteresis) and config.fom_hysteresis >= 0.0 and
                (config.fom_hysteresis != 0.0 or config.min_fom_switch_interval_usec != 0))

    def get_active_channel(self) -> int:
        return self.active_channel

    def override_active_channel(self, redund_chan: int, timestamp: int | None = None):
        if not (0 <= redund_chan < self.config.num_channels):
            raise ValueError("Invalid channel index")
        self.active_channel = redund_chan
        if timestamp is None:
            timestamp = int(time.time() * 1e6)
        self.last_switch_timestamp_usec = timestamp

    def get_last_switch_timestamp(self) -> int:
        return self.last_switch_timestamp_usec

    def get_channel_state(self, redund_chan: int) -> tuple[float, int]:
        if not (0 <= redund_chan < self.config.num_channels):
            raise IndexError("Invalid channel index")
        state = self.channels[redund_chan]
        return state.fom, state.last_update_timestamp_usec

    def update(self, redund_chan: int, fom: float, timestamp: int) -> int:
        if not (0 <= redund_chan < self.config.num_channels):
            raise ValueError("Invalid channel index")
        if timestamp == 0:
            raise ValueError("Timestamp cannot be zero")

        if math.isnan(fom):
            fom = -float('inf')

        self.channels[redund_chan].fom = fom
        self.channels[redund_chan].last_update_timestamp_usec = timestamp

        updating_chan_state = self.channels[redund_chan]
        active_chan_state = self.channels[self.active_channel]

        reason = CANASSwitchReasons.REASON_NONE

        # Initial switch
        if self.last_switch_timestamp_usec == 0:
            reason = CANASSwitchReasons.REASON_INIT

        # By timeout
        if reason == CANASSwitchReasons.REASON_NONE and redund_chan != self.active_channel:
            time_threshold = active_chan_state.last_update_timestamp_usec + \
                self.config.channel_timeout_usec
            if timestamp > time_threshold:
                reason = CANASSwitchReasons.REASON_TIMEOUT

        # By figure of merit
        if reason == CANASSwitchReasons.REASON_NONE and redund_chan != self.active_channel:
            fom_threshold = active_chan_state.fom + self.config.fom_hysteresis
            fom_switch_dead_time = self.last_switch_timestamp_usec + \
                self.config.min_fom_switch_interval_usec

            if (updating_chan_state.fom > fom_threshold) and (timestamp >= fom_switch_dead_time):
                reason = CANASSwitchReasons.REASON_FOM

        if reason != CANASSwitchReasons.REASON_NONE:
            self.active_channel = redund_chan
            self.last_switch_timestamp_usec = timestamp

        return reason
