from __future__ import annotations

import time
from collections.abc import Callable, Iterable
from dataclasses import dataclass, field

from pint.registry import Quantity

from .enums import DataType, TransmissionInterval
from .frame import CANASMessage

"""
From CANAS 17 specification: 6.2 - Transmission Slot Concept
"With this transmission slot concept, either 100 parameters transmitted
 each 12.5ms or 8000 parameters transmitted once a second would
 generate 100% bus load. More likely, however, a combination of parameters in the various transmission
 slot groups from this table (A-G) will be used"
 https://files.stockflightsystems.com/_5_CANaerospace/canas_17.pdf
"""


@dataclass(frozen=True)
class TTSlot:
    """A transmission slot within a minor time frame"""
    phase: str  # 'A', 'B', etc
    index: int  # 0, 1, etc
    byte: int | None  # For multi-bytes messages
    param_name: str
    unit: Quantity
    can_id: int
    data_type: DataType

    @property
    def key(self) -> str:
        return f"{self.phase}_{self.index}_{self.byte or 0}"


@dataclass
class TTEntry:
    """Schedule entry mapping slot + interval"""
    slot: TTSlot
    interval: TransmissionInterval
    build_frame: Callable[[], CANASMessage | None]


@dataclass
class TTSchedule:
    """Holds TTEntries and provide lookup functionality"""
    entries: dict[str, TTEntry] = field(default_factory=dict)

    def register(self, entry: TTEntry) -> None:
        key = entry.slot.key
        if key in self.entries:
            raise ValueError(f"Slot {key} already registered")
        self.entries[key] = entry

    def items(self) -> Iterable[TTEntry]:
        return self.entries.values()


class TTScheduler:
    """clock agnostic scheduler"""

    def __init__(self, schedule: TTSchedule, send: Callable[[CANASMessage], None],
                 now: Callable[[], float] | None = None) -> None:
        self.schedule = schedule
        self.send = send
        self.now = now or time.monotonic
        self._next: dict[str, float] = {}
        for e in schedule.items():
            self._next[e.slot.key] = self.now()

    def poll(self) -> None:
        t = self.now()
        for key, entry in self.schedule.entries.items():
            due = self._next[key]
            if t >= due:
                frame = entry.build_frame()
                if frame is not None:
                    self.send(frame)
                period = int(entry.interval) / 1_000_000.0
                self._next[key] = due + period


"""
How to use
from canaerospace import directory
from
def build_pitch_frame() -> Optional[CANASMessage]:
    param = directory.by_name("pitch")
    val:float = your_sensor.read_pitch_deg()
    return build(
        can_id=param.can_id,
        node_id=param.node_id,
        data_type=param.data_type,
        service_code=service_code,
        message_code=param.message_code,
        values=val
    )


schedule = TTSchedule()
schedule.register(TTEntry(slot=TTSlot(), interval=TransmissionInterval.US_50MS, build_frame=build_pitch_frame))
scheduler = TTScheduler(schedule, send=transmit_function())

# then in the main loop
scheduler.poll()
"""
