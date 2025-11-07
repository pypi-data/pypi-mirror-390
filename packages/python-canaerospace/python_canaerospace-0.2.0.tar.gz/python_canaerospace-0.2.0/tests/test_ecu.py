import pytest

from canaerospace import ECU, DataType
from canaerospace.directory import default_directory
from canaerospace.frame import build
from tests import FakeTransmitter


@pytest.fixture
def ecu_and_transmitter():
    transmitter = FakeTransmitter()
    ecu = ECU(
        node_id=4,
        directory=default_directory(),
        transmitter=transmitter
    )
    return ecu, transmitter


class TestECU:
    def test_register(self, ecu_and_transmitter):
        ecu, _ = ecu_and_transmitter
        assert len(ecu._params) == 0
        ecu.register("static_pressure")
        assert len(ecu._params) == 1

    def test_unregister(self, ecu_and_transmitter):
        ecu, _ = ecu_and_transmitter
        ecu.register("static_pressure")
        param = ecu.unregister("static_pressure")
        assert len(ecu._params) == 0
        assert param.name == 'static_pressure'

    def test_unregister_fake(self, ecu_and_transmitter):
        ecu, _ = ecu_and_transmitter
        ecu.register("static_pressure")
        param = ecu.unregister("pitch1")
        assert len(ecu._params) == 1
        assert param is None

    def test_set(self, ecu_and_transmitter):
        ecu, transmitter = ecu_and_transmitter
        ecu.register("static_pressure")
        assert len(transmitter.frames) == 0
        ecu.set("static_pressure", 0.69)
        assert len(transmitter.frames) == 1
        frame = transmitter.frames[0]
        assert frame.can_id == ecu._directory.by_name('static_pressure').can_id
        assert round(frame.value(),2) == 0.69

    def test_handle_receive_nofail(self, ecu_and_transmitter):
        ecu, _ = ecu_and_transmitter
        msg = build(
            can_id=999,
            node_id=1,
            data_type=DataType.FLOAT,
            service_code=0,
            message_code=0,
            values=(4.20,)
        )
        param = ecu.handle_receive(msg)
        assert param is None

    def test_handle_receive(self, ecu_and_transmitter):
        ecu, _ = ecu_and_transmitter
        ecu.register("static_pressure")
        real_param = ecu._directory.by_name('static_pressure')
        msg = build(
            can_id=real_param.can_id,
            node_id=1,
            data_type=real_param.data_type,
            service_code=99,
            message_code=99,
            values=(0.69,)
        )
        received_param = ecu.handle_receive(msg)
        assert received_param is not None
        assert received_param.service_code == 99
        assert received_param.message_code == 99
        assert round(msg.value(),2) == 0.69
