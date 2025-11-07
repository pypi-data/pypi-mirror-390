import can
import pytest

from canaerospace import DataType
from canaerospace.frame import build, decode, encode


@pytest.fixture
def virtual_bus():
    """Provides a virtual CAN bus that receives its own messages."""
    bus = can.interface.Bus(
        channel='vcan0', interface='virtual', receive_own_messages=True)
    yield bus
    bus.shutdown()


class TestCANAeroFrameBus:
    def test_send_and_receive_frame(self, virtual_bus):
        msg = build(
            can_id=0x01,
            node_id=0xAF,
            service_code=0x01,
            message_code=0x01,
            data_type=DataType.FLOAT,
            values=(100.02,)
        )

        can_msg = can.Message(
            arbitration_id=msg.can_id,
            data=encode(msg),
            is_extended_id=False
        )

        virtual_bus.send(can_msg)

        received_msg = virtual_bus.recv(timeout=1.0)
        assert received_msg is not None, "No Message Received"

        rcvd_frame = decode(
            received_msg.arbitration_id, received_msg.data)
        assert rcvd_frame.can_id == 0x01
        assert rcvd_frame.node_id == 0xAF
        assert rcvd_frame.data_type == DataType.FLOAT
        assert rcvd_frame.value() == pytest.approx(100.02)

    def test_multiple_frames(self, virtual_bus):
        messages = [
            build(
                can_id=0x01,
                node_id=0xAF,
                service_code=0x01,
                message_code=0x01,
                data_type=DataType.FLOAT,
                values=(100.02,)
            ),
            build(
                can_id=0x02,
                node_id=0xBF,
                service_code=0xAA,
                message_code=0xBB,
                data_type=DataType.FLOAT,
                values=(2.0,)
            ),
            build(
                can_id=0x03,
                node_id=0xCF,
                service_code=0xCC,
                message_code=0xDD,
                data_type=DataType.FLOAT,
                values=(0.0,)
            )
        ]

        for msg in messages:
            can_msg = can.Message(arbitration_id=msg.can_id,
                                  data=encode(msg), is_extended_id=False)
            virtual_bus.send(can_msg)

        recvd_frames = []
        for _ in messages:
            can_msg = virtual_bus.recv(timeout=1.0)
            assert can_msg is not None, 'No Message Received'
            recvd_frames.append(decode(
                can_msg.arbitration_id, can_msg.data))

        assert len(messages) == len(recvd_frames)
        for sent, received in zip(messages, recvd_frames, strict=True):
            assert sent == received

    def test_no_message_timeout(self, virtual_bus):
        msg = virtual_bus.recv(timeout=0.01)
        assert msg is None, 'Message should not be received'
