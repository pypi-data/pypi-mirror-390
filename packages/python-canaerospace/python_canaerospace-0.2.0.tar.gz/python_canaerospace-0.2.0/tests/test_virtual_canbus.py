from collections.abc import Generator

import can
import pytest

from canaerospace import CANASMessage
from canaerospace.directory import IdentifierDirectory, ParameterDef, default_directory
from canaerospace.enums import ServiceCode
from canaerospace.frame import build, decode, encode
from canaerospace.transport.virtual import get_bus


@pytest.fixture
def virtual_bus() -> Generator:
    bus = get_bus()
    yield bus
    bus.shutdown()


@pytest.fixture
def test_frame() -> CANASMessage:
    d: IdentifierDirectory = default_directory()
    param: ParameterDef = d.by_name('static_pressure')
    return build(
        can_id=param.can_id,
        node_id=0x01,
        data_type=param.data_type,
        service_code=int(ServiceCode.BSS.value),
        message_code=0x01,
        values=(0.64,)
    )


class TestVirtualCanbus:
    def test_send_and_receive_frame(self, virtual_bus, test_frame):
        # Create a python-can message
        encoded_msg = encode(test_frame)
        msg_to_send = can.Message(
            arbitration_id=test_frame.can_id,
            data=encoded_msg,
            is_extended_id=False,
            dlc=8
        )

        virtual_bus.send(msg_to_send)
        received_msg = virtual_bus.recv(timeout=1)

        assert received_msg is not None
        decoded_msg = decode(received_msg.arbitration_id, received_msg.data)
        assert decoded_msg == test_frame
