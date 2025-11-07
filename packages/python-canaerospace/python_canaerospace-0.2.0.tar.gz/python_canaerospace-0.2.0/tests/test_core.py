import pytest

from canaerospace.datatypes import PackingError, unpack
from canaerospace.driver import CANFlag, CANFrame
from canaerospace.enums import CANAeroMessageTypeID, DataType
from canaerospace.frame import build, encode
from tests.conftest import IFACE_COUNT, MY_NODE_ID


def make_message(msg_id, redund_chan_id, node_id, data_type: DataType, srv_code, msg_code, *payload):
    if redund_chan_id:
        msg_id |= (redund_chan_id << 16) | CANFlag.EFF.value

    return build(
        can_id=msg_id,
        node_id=node_id,
        data_type=data_type,
        service_code=srv_code,
        message_code=msg_code,
        values=payload)


class TestCore:
    def test_simple(self, mock_iface, generic_instance):
        inst = generic_instance
        # No post_init in the test fixture, so we do it manually
        inst.__post_init__()
        inst.update_timestamp(IFACE_COUNT - 1, None, 1)
        msg = make_message(123, 0, 90, DataType.NODATA, 0, 1)
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))

        with pytest.raises(ValueError):
            inst.update_timestamp(IFACE_COUNT, can_frame, 2)

        with pytest.raises(ValueError):
            inst.update_timestamp(-1, can_frame, 3)

        inst.update_timestamp(IFACE_COUNT, None, 2)
        inst.update_timestamp(-1, None, 3)

        for i in range(IFACE_COUNT):
            assert len(mock_iface.filters[i]) == 1
            assert mock_iface.filters[i][0].mask == CANFlag.RTR.value

    def test_data_validation(self, generic_instance):
        inst = generic_instance

        with pytest.raises(PackingError):
            make_message(123, 0, MY_NODE_ID, DataType.CHAR2, 0, 1, ord('a'))

        with pytest.raises(PackingError):
            make_message(123, 0, MY_NODE_ID, DataType.ACHAR, 0, 1, 'ab')

        with pytest.raises(PackingError):
            make_message(123, 0, MY_NODE_ID, DataType.RESVD_BEGIN_, 0, 1)

        msg = make_message(123, 0, MY_NODE_ID, DataType.FLOAT, 0, 1, 1.0)
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))
        inst.update_timestamp(0, can_frame, 1)

    def test_param_ignoring(self, mock_iface, generic_instance):
        inst = generic_instance
        msg = make_message(123, 0, MY_NODE_ID, DataType.ACHAR2, 0, 1, 'a', 'b')
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))
        inst.update_timestamp(0, can_frame, 1)
        mock_iface.param_callback.assert_not_called()
        mock_iface.hook_callback.assert_called_once()

    def test_param_reception(self, mock_iface, generic_instance):
        inst = generic_instance
        msg = make_message(123, 0, 90, DataType.ACHAR2, 0, 1, 'a', 'b')
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))

        with pytest.raises(ValueError):
            inst.param_subscribe(123, 0, mock_iface.param_callback)

        inst.param_subscribe(123, 8, mock_iface.param_callback)
        inst.update_timestamp(0, can_frame, 1)

        mock_iface.param_callback.assert_called_once()
        mock_iface.hook_callback.assert_called_once()

        cb_args = mock_iface.param_callback.call_args[0][0]
        assert cb_args.message.node_id == 90
        assert cb_args.message.service_code == 0
        assert cb_args.message.message_code == 1
        assert len(cb_args.message.data) == 4
        assert cb_args.message.data_type == DataType.ACHAR2
        assert cb_args.message.values() == ('a', 'b')

    def test_repeated_param_filtering(self, mock_iface, generic_instance):
        inst = generic_instance
        msg = make_message(123, 0, 90, DataType.ACHAR2, 0, 1, 'a', 'b')
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))
        inst.param_subscribe(123, 8, mock_iface.param_callback)

        inst.update_timestamp(0, can_frame, 1)
        assert mock_iface.param_callback.call_count == 1

        inst.update_timestamp(1, can_frame, 1)
        assert mock_iface.param_callback.call_count == 1

        mock_iface.timestamp = 60 * 1000 * 1000
        inst.update_timestamp(1, can_frame, mock_iface.timestamp)
        assert mock_iface.param_callback.call_count == 2
        assert mock_iface.hook_callback.call_count == 3

    def test_param_publication(self, mock_iface, generic_instance):
        inst = generic_instance
        inst.param_advertise(123, False)
        with pytest.raises(ValueError):
            inst.param_advertise(123, True)

        with pytest.raises(ValueError):
            inst.param_advertise(
                CANAeroMessageTypeID.NODE_SERVICE_LOW.value[0], False)

        mock_iface.send_returns = [0] * IFACE_COUNT
        with pytest.raises(RuntimeError):  # Expecting a driver error
            inst.param_publish(123, DataType.ACHAR2, ('a', 'b'), 34)

        mock_iface.send_counter = [0] * IFACE_COUNT
        mock_iface.send_dump = [None] * IFACE_COUNT
        mock_iface.drv_send.reset_mock()

        mock_iface.send_returns = [0, 1, 1]
        # This is the second call, so message_code should be 1
        inst.param_publish(123, DataType.ACHAR2, ('a', 'b'), 34)

        with pytest.raises(ValueError):
            inst.param_publish(124, DataType.ACHAR2, ('a', 'b'), 34)

        # The first call to param_publish incremented the message_code to 1
        reference = make_message(
            123, 0, MY_NODE_ID, DataType.ACHAR2, 34, 1, 'a', 'b')
        for i in range(IFACE_COUNT):
            assert mock_iface.send_counter[i] == 1
            sent_frame = mock_iface.send_dump[i]
            assert sent_frame.id == reference.can_id
            encoded_data = encode(reference)
            assert sent_frame.data == encoded_data
            assert sent_frame.dlc == len(encoded_data)

    def test_param_publication_with_interlacing(self, mock_iface, generic_instance):
        inst = generic_instance
        inst.param_advertise(123, True)

        mock_iface.send_returns = [1] * IFACE_COUNT

        inst.param_publish(123, DataType.ACHAR2, ('a', 'b'), 34)
        inst.param_publish(123, DataType.ACHAR2, ('a', 'b'), 34)
        inst.param_publish(123, DataType.ACHAR2, ('a', 'b'), 34)

        for i in range(IFACE_COUNT):
            assert mock_iface.send_counter[i] == 1
            reference = make_message(
                123, 0, MY_NODE_ID, DataType.ACHAR2, 34, i, 'a', 'b')
            sent_frame = mock_iface.send_dump[i]
            assert sent_frame.id == reference.can_id
            encoded_data = encode(reference)
            assert sent_frame.data == encoded_data
            assert sent_frame.dlc == len(encoded_data)

    def test_service_ignoring(self, mock_iface, generic_instance):
        inst = generic_instance
        msg = make_message(196, 2, MY_NODE_ID,
                           DataType.ULONG, 8, 1, 0xdeadface)
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))
        inst.update_timestamp(1, can_frame, 1)

        with pytest.raises(PackingError):
            make_message(196, 2, MY_NODE_ID, DataType.RESVD_BEGIN_, 8, 1)

        mock_iface.srv_poll_callback.assert_not_called()
        mock_iface.srv_request_callback.assert_not_called()
        mock_iface.srv_response_callback.assert_not_called()
        assert mock_iface.hook_callback.call_count == 1
        hook_args = mock_iface.hook_callback.call_args[0][0]
        assert unpack(hook_args.message.data_type,
                      hook_args.message.data)[0] == 0xdeadface

        inst.service_register(8, mock_iface.srv_poll_callback,
                              mock_iface.srv_request_callback, mock_iface.srv_response_callback)
        inst.service_register(9, mock_iface.srv_poll_callback,
                              mock_iface.srv_request_callback, mock_iface.srv_response_callback)
        inst.service_register(10, None, None, None)

        with pytest.raises(ValueError):
            inst.service_register(8, None, None, None)

        with pytest.raises(ValueError):
            inst.service_unregister(11)

        # Send a message for a service code that is NOT registered (e.g., 99)
        msg = make_message(196, 2, 1, DataType.UCHAR2, 99, 1, 0xca, 0xfe)
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))
        inst.update_timestamp(2, can_frame, 2)
        mock_iface.srv_poll_callback.assert_not_called()
        mock_iface.srv_request_callback.assert_not_called()
        mock_iface.srv_response_callback.assert_not_called()
        assert mock_iface.hook_callback.call_count == 2

        msg = make_message(2000, 2, MY_NODE_ID,
                           DataType.UCHAR2, 11, 1, 0xca, 0xfe)
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))
        inst.update_timestamp(2, can_frame, 2)
        mock_iface.srv_poll_callback.assert_not_called()
        mock_iface.srv_request_callback.assert_not_called()
        mock_iface.srv_response_callback.assert_not_called()
        assert mock_iface.hook_callback.call_count == 3

        inst.service_unregister(9)
        inst.service_unregister(8)
        inst.service_unregister(10)

    def test_service_poll(self, mock_iface, generic_instance):
        inst = generic_instance
        inst.service_register(8, mock_iface.srv_poll_callback,
                              mock_iface.srv_request_callback, mock_iface.srv_response_callback)
        inst.service_register(9, mock_iface.srv_poll_callback,
                              mock_iface.srv_request_callback, mock_iface.srv_response_callback)
        inst.service_register(10, None, None, None)

        inst.update_timestamp(0, None, 1)
        mock_iface.srv_poll_callback.assert_not_called()
        mock_iface.hook_callback.assert_not_called()

        inst.update_timestamp(-1, None, 1000000)
        assert mock_iface.srv_poll_callback.call_count == 2
        mock_iface.hook_callback.assert_not_called()

        msg = make_message(196, 2, MY_NODE_ID, DataType.NODATA, 48, 1)
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))
        with pytest.raises(ValueError):
            inst.update_timestamp(-1, can_frame, 2000000)

        with pytest.raises(ValueError):
            inst.update_timestamp(IFACE_COUNT, can_frame, 2000000)

        inst.update_timestamp(2, can_frame, 2000000)
        assert mock_iface.srv_poll_callback.call_count == 4
        assert mock_iface.hook_callback.call_count == 1

        inst.update_timestamp(-1, None, 2000001)
        assert mock_iface.srv_poll_callback.call_count == 4
        assert mock_iface.hook_callback.call_count == 1

        inst.update_timestamp(IFACE_COUNT, None, 3000000)
        assert mock_iface.srv_poll_callback.call_count == 6
        assert mock_iface.hook_callback.call_count == 1

        mock_iface.srv_request_callback.assert_not_called()
        mock_iface.srv_response_callback.assert_not_called()

    def test_service_reception(self, mock_iface, generic_instance):
        inst = generic_instance
        inst.service_register(
            8, None, mock_iface.srv_request_callback, mock_iface.srv_response_callback)

        msg = make_message(128, 2, MY_NODE_ID,
                           DataType.ULONG, 8, 1, 0xdeadface)
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))
        inst.update_timestamp(0, can_frame, 1)
        assert mock_iface.srv_request_callback.call_count == 1
        assert mock_iface.srv_response_callback.call_count == 0

        cb_args = mock_iface.srv_request_callback.call_args[0][0]
        assert cb_args.service_channel == 0
        assert cb_args.timestamp_usec == 1
        assert cb_args.message.values()[0] == 0xdeadface
        assert cb_args.message.data_type == DataType.ULONG
        assert cb_args.message.service_code == 8
        assert cb_args.message.node_id == MY_NODE_ID

        inst.config.service_channel = 101
        # This is a response, not a request, so the request callback should not be called again.
        msg = make_message(2003, 56, MY_NODE_ID + 1, DataType.NODATA, 8, 1)
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))
        inst.update_timestamp(0, can_frame, 2)
        assert mock_iface.srv_request_callback.call_count == 1
        assert mock_iface.srv_response_callback.call_count == 1

    def test_service_repetitions(self, mock_iface, generic_instance):
        inst = generic_instance
        inst.service_register(8, mock_iface.srv_poll_callback,
                              mock_iface.srv_request_callback, mock_iface.srv_response_callback)

        msg = make_message(196, 2, MY_NODE_ID,
                           DataType.ULONG, 8, 1, 0xdeadface)
        can_frame = CANFrame(id=msg.can_id, dlc=len(
            encode(msg)), _data=encode(msg))

        # First reception on interface 0
        inst.update_timestamp(0, can_frame, 1)
        assert mock_iface.srv_request_callback.call_count == 1
        assert mock_iface.hook_callback.call_count == 1

        # Same request on same interface, should be filtered
        inst.update_timestamp(0, can_frame, 10)
        assert mock_iface.srv_request_callback.call_count == 1
        assert mock_iface.hook_callback.call_count == 2

        # Same request on different interfaces, should be filtered
        inst.update_timestamp(1, can_frame, 20)
        inst.update_timestamp(2, can_frame, 30)
        assert mock_iface.srv_request_callback.call_count == 1
        assert mock_iface.hook_callback.call_count == 4

        # Re-transmission on an already-seen interface after timeout should be processed
        mock_iface.timestamp = 300000
        inst.update_timestamp(0, can_frame, mock_iface.timestamp)
        assert mock_iface.srv_request_callback.call_count == 2
        assert mock_iface.hook_callback.call_count == 5

    def test_service_state(self, generic_instance):
        inst = generic_instance

        state1 = object()
        state2 = object()
        state3 = 12345

        inst.service_register(8, None, None, None, pstate=state1)
        inst.service_register(9, None, None, None, pstate=state2)
        inst.service_register(10, None, None, None)

        assert inst.service_get_state(8) is state1
        assert inst.service_get_state(9) is state2

        inst.service_set_state(9, state3)
        assert inst.service_get_state(9) == state3

        inst.service_set_state(8, None)
        assert inst.service_get_state(8) is None

        with pytest.raises(ValueError):
            inst.service_get_state(88)

        with pytest.raises(ValueError):
            inst.service_set_state(88, None)

    def test_service_sending(self, mock_iface, generic_instance):
        inst = generic_instance
        inst.config.service_channel = 2

        msg = build(can_id=0, node_id=MY_NODE_ID + 1, data_type=DataType.ULONG,
                    service_code=8, message_code=123, values=(0xdeface11,))

        mock_iface.send_returns = [0, 1, 1]

        with pytest.raises(AttributeError):
            inst.service_send_request(None)

        inst.service_send_request(msg)

        reference = make_message(
            132, 0, msg.node_id, DataType.ULONG, 8, 123, 0xdeface11)
        for i in range(IFACE_COUNT):
            assert mock_iface.send_counter[i] == 1
            sent_frame = mock_iface.send_dump[i]
            assert sent_frame.id == reference.can_id
            encoded_data = encode(reference)
            assert sent_frame.data == encoded_data
            assert sent_frame.dlc == len(encoded_data)

        msg = build(can_id=0, node_id=MY_NODE_ID, data_type=DataType.ULONG,
                    service_code=8, message_code=123, values=(0xdeface11,))
        with pytest.raises(ValueError):
            inst.service_send_request(msg)

        with pytest.raises(ValueError):
            inst.service_send_response(
                msg, CANAeroMessageTypeID.NODE_SERVICE_LOW.value[0] - 1)

        msg = build(can_id=0, node_id=MY_NODE_ID + 1, data_type=DataType.ULONG,
                    service_code=8, message_code=123, values=(0xdeface11,))
        with pytest.raises(ValueError):
            inst.service_send_response(msg, 2)

        msg = build(can_id=0, node_id=MY_NODE_ID, data_type=DataType.ULONG,
                    service_code=8, message_code=123, values=(0xdeface11,))
        inst.service_send_response(msg, 2)

        reference = make_message(
            133, 0, msg.node_id, DataType.ULONG, 8, 123, 0xdeface11)
        for i in range(IFACE_COUNT):
            assert mock_iface.send_counter[i] == 2
            sent_frame = mock_iface.send_dump[i]
            assert sent_frame.id == reference.can_id
            encoded_data = encode(reference)
            assert sent_frame.data == encoded_data
            assert sent_frame.dlc == len(encoded_data)
