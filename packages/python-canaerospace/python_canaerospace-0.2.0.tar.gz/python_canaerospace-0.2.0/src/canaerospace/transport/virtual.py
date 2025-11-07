import can

from canaerospace.transport import canbus_config


def get_bus():
    return can.Bus(
        interface=canbus_config.get('interface'),
        channel=canbus_config.get('channel'),
        bitrate=canbus_config.get('bitrate'),
        receive_own_messages=True
    )
