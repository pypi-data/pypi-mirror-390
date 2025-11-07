from types import SimpleNamespace

import pytest

from canaerospace import DataType
from canaerospace.frame import build
from canaerospace.transmission import TTSchedule, TTScheduler
from canaerospace.transmission_slots import build_entries_for_builder


@pytest.fixture
def transmission_setup():
    """Sets up a test environment for the transmission scheduler."""
    state = SimpleNamespace(
        sent=[],
        time_now=0.0
    )

    def send(f):
        state.sent.append(f)

    def now():
        return state.time_now

    def frame_builder(can_id, **kwargs):
        return lambda: build(
            can_id=can_id,
            node_id=0x01,
            data_type=DataType.FLOAT,
            service_code=0x01,
            message_code=0x01,
            values=kwargs.get('values', (1.0,))
        )

    def tick_up_and_poll(scheduler, delta=0.01):
        state.time_now += delta
        scheduler.poll()

    def count_sent_by_can_id(can_id):
        return [f.can_id for f in state.sent].count(can_id)

    return SimpleNamespace(
        sent=state.sent,
        send=send,
        now=now,
        frame_builder=frame_builder,
        tick_up_and_poll=tick_up_and_poll,
        count_sent_by_can_id=count_sent_by_can_id
    )


class TestTransmission:
    def test_three_slots(self, transmission_setup):
        # Arrange
        setup = transmission_setup
        entries = build_entries_for_builder(setup.frame_builder)

        schedule = TTSchedule()
        schedule.register(entries[0])
        schedule.register(entries[9])
        schedule.register(entries[10])

        sched = TTScheduler(schedule=schedule, send=setup.send, now=setup.now)

        # Act & Assert
        setup.tick_up_and_poll(sched, delta=0.00)
        assert len(setup.sent) == 3

        # A simple send from t=0 should send all messages
        assert setup.count_sent_by_can_id(entries[0].slot.can_id) == 1
        assert setup.count_sent_by_can_id(entries[9].slot.can_id) == 1
        assert setup.count_sent_by_can_id(entries[10].slot.can_id) == 1

        # Tick up by 0.0125s, which should trigger the 0.0125s interval message
        setup.tick_up_and_poll(sched, delta=0.0125)
        assert setup.count_sent_by_can_id(entries[0].slot.can_id) == 2
        assert setup.count_sent_by_can_id(entries[9].slot.can_id) == 1
        assert setup.count_sent_by_can_id(entries[10].slot.can_id) == 1

        # Tick up by 0.09s, bringing total time over 0.1s, triggering all messages again
        setup.tick_up_and_poll(sched, delta=0.09)
        assert setup.count_sent_by_can_id(entries[0].slot.can_id) == 3
        assert setup.count_sent_by_can_id(entries[9].slot.can_id) == 2
        assert setup.count_sent_by_can_id(entries[10].slot.can_id) == 2

    def test_scheduler_rejects_double_registration(self):
        entries = build_entries_for_builder(lambda _: None)
        sch = TTSchedule()
        sch.register(entries[0])
        with pytest.raises(ValueError):
            sch.register(entries[0])
