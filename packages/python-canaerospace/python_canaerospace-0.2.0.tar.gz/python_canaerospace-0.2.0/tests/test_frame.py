import pytest

from canaerospace.datatypes import PackingError
from canaerospace.directory import default_directory
from canaerospace.enums import ServiceCode
from canaerospace.frame import build, decode, encode


@pytest.fixture
def frame_data():
    """Provides a decoded frame and its encoded version for testing."""
    directory = default_directory()
    param = directory.by_name('static_pressure')
    decoded_message = build(
        can_id=param.can_id,
        node_id=1,
        data_type=param.data_type,
        service_code=int(ServiceCode.BSS.value),
        message_code=0x1A,
        values=(0.75,)
    )
    encoded_message = encode(decoded_message)
    return decoded_message, encoded_message


class TestFrame:
    def test_encode(self, frame_data):
        decoded, encoded = frame_data
        assert encode(decoded) == encoded

    def test_decode(self, frame_data):
        decoded, encoded = frame_data
        decoded_from_bytes = decode(decoded.can_id, encoded)
        assert decoded_from_bytes == decoded
        assert decoded_from_bytes.value() == 0.75

    def test_encode_decode_header_and_data(self, frame_data):
        decoded, encoded = frame_data
        assert len(encoded) == 8

        f2 = decode(decoded.can_id, encoded)
        assert f2.node_id == decoded.node_id
        assert f2.data_type == decoded.data_type
        assert f2.service_code == decoded.service_code
        assert f2.message_code == decoded.message_code
        assert f2.value() == 0.75

    def test_invalid_lengths(self, frame_data):
        decoded, _ = frame_data
        with pytest.raises(ValueError):
            decode(-1, b"\x00" * 7)  # Invalid data length

        with pytest.raises(PackingError):
            build(
                can_id=decoded.can_id,
                node_id=decoded.node_id,
                data_type=decoded.data_type,
                service_code=decoded.service_code,
                message_code=decoded.message_code,
                values=(1, 2, 3, 4, 5)  # Too many values
            )
