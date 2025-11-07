from unittest.mock import Mock

import pytest

from canaerospace.enums import DataType, ServiceCode
from canaerospace.frame import CANASMessage, build
from canaerospace.services import NodeServiceHandler


@pytest.fixture
def service_handler_and_recorder():
    """Provides a NodeServiceHandler and a mock recorder for its callback."""
    recorder = Mock()
    handler = NodeServiceHandler(recorder, node_id=0x01)
    return handler, recorder


class TestService:
    def test_service_ids_roundtrip(self, service_handler_and_recorder):
        """IDS Service roundtrip test."""
        handler, recorder = service_handler_and_recorder
        handler.set_ids_info(hw_rev=1, sw_rev=1)

        request = build(
            can_id=0x01,
            node_id=0x01,
            data_type=DataType.NODATA,
            service_code=int(ServiceCode.IDS),
            message_code=0x01,
            values=()
        )

        # Act
        handler.on_request(request)

        # Assert
        recorder.assert_called_once()
        response: CANASMessage = recorder.call_args[0][0]

        assert response is not None
        assert response.node_id == 0x01
        assert response.can_id == 0x02  # Responses are always 1 more than the request
        assert response.data_type == DataType.UCHAR4
        assert response.service_code == int(ServiceCode.IDS)
        assert response.data == bytes([1, 1, 0, 0])

    def test_css_ack(self, service_handler_and_recorder):
        handler, recorder = service_handler_and_recorder
        request = build(
            can_id=0x02,
            node_id=0x01,
            data_type=DataType.NODATA,
            service_code=int(ServiceCode.CSS),
            message_code=2,
            values=()
        )

        handler.on_request(request)

        recorder.assert_called_once()
        response: CANASMessage = recorder.call_args[0][0]

        assert response is not None
        assert response.can_id == 0x03
        assert response.service_code == int(ServiceCode.CSS)
        assert response.message_code == 2

    def test_nss_and_nts(self, service_handler_and_recorder):
        handler, recorder = service_handler_and_recorder
        for service_code in [ServiceCode.NSS, ServiceCode.NIS]:
            recorder.reset_mock()  # Reset mock for each loop iteration
            req = build(
                can_id=0x01,
                node_id=0x01,
                data_type=DataType.NODATA,
                service_code=int(service_code),
                message_code=1,
                values=()
            )

            handler.on_request(req)

            recorder.assert_called_once()
            response: CANASMessage = recorder.call_args[0][0]

            assert response is not None
            assert response.node_id == 0x01
            assert response.can_id == 0x02
            assert response.service_code == int(service_code)
