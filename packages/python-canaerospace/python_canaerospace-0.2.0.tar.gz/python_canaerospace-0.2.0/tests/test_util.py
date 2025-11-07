from canaerospace.constants import DUMP_BUF_LEN
from canaerospace.driver import CANFlag
from canaerospace.enums import DataType
from canaerospace.frame import build


class TestDump:
    def test_can_frame_buf_space(self) -> None:
        """
        This test mirrors the C++ test 'DumpTest, CanFrameBufSpace'.
        It checks if the string representation of a CANASMessage fits within
        the expected buffer length.
        """
        can_id = 1234
        redund_chan_id = 255
        if redund_chan_id:
            can_id |= (redund_chan_id << 16) | CANFlag.EFF.value

        msg = build(
            can_id=can_id,
            node_id=0,
            data_type=DataType.ACHAR,
            service_code=0,
            message_code=0,
            values=('a',)
        )

        dump_str = str(msg)
        assert len(dump_str) < DUMP_BUF_LEN

    def test_message_buf_space(self) -> None:
        """
        This test mirrors the C++ test 'DumpTest, MessageBufSpace'.
        It checks if the string representation of a CANASMessage fits within
        the expected buffer length.
        """
        msg = build(
            can_id=0x4D2,
            node_id=42,
            data_type=DataType.UCHAR4,
            service_code=1,
            message_code=2,
            values=(0xde, 0xad, 0xbe, 0xef)
        )

        dump_str = str(msg)
        assert len(dump_str) < DUMP_BUF_LEN
