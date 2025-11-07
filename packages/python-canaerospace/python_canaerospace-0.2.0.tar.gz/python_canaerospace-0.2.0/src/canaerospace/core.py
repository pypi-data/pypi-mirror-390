from .enums import CANAeroMessageTypeID, MessageGroupID


class MessageGroup:
    @staticmethod
    def detect_message_group_id_from_id(msg_id: int) -> MessageGroupID:
        if (
                MessageGroup.range_inclusive(msg_id, *CANAeroMessageTypeID.EMERGENCY_EVENTS.value) or
                MessageGroup.range_inclusive(msg_id, *CANAeroMessageTypeID.USER_DEFINED_HIGH.value) or
                MessageGroup.range_inclusive(msg_id, *CANAeroMessageTypeID.NORMAL_OPERATION.value) or
                MessageGroup.range_inclusive(msg_id, *CANAeroMessageTypeID.USER_DEFINED_LOW.value) or
                MessageGroup.range_inclusive(
                    msg_id, *CANAeroMessageTypeID.DEBUG_SERVICE.value)
        ):
            return MessageGroupID.PARAMETER
        if (
            MessageGroup.range_inclusive(msg_id, *CANAeroMessageTypeID.NODE_SERVICE_HIGH.value) or
            MessageGroup.range_inclusive(
                msg_id, *CANAeroMessageTypeID.NODE_SERVICE_LOW.value)
        ):
            return MessageGroupID.SERVICE

        return MessageGroupID.WTF

    @staticmethod
    def range_inclusive(x: int, min_v: int, max_v: int) -> bool:
        return min_v <= x <= max_v

    @staticmethod
    def diff_u8(first: int, second: int) -> int:
        diff = first - second
        if diff <= -128:
            return 256 + diff
        elif diff >= 127:
            return diff - 256
        return diff
