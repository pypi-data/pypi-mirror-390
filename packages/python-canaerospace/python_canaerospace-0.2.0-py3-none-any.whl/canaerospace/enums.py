from __future__ import annotations

from enum import Enum, IntEnum


class MessageType(IntEnum):
    EED = 0  # Emergency Event Data (0-127)
    NSH = 1  # High-Priority Node Service (128-199)
    UDH = 2  # High-Priority User-Defined Data (200-299)
    NOD = 3  # Normal Operation Data (300-1799)
    UDL = 4  # Low-Priority User-Defined (1800-1899)
    DSD = 5  # Debug Service Data (1900-1999)
    NSL = 6  # Low-Priority Node Service (2000-2031)


class DataType(IntEnum):
    NODATA = 0x00
    ERROR = 0x01
    FLOAT = 0x02
    LONG = 0x03
    ULONG = 0x04
    BLONG = 0x05
    SHORT = 0x06
    USHORT = 0x07
    BSHORT = 0x08
    CHAR = 0x09
    UCHAR = 0x0A
    BCHAR = 0x0B
    SHORT2 = 0x0C
    USHORT2 = 0x0D
    BSHORT2 = 0x0E
    CHAR4 = 0x0F
    UCHAR4 = 0x10
    BCHAR4 = 0x11
    CHAR2 = 0x12
    UCHAR2 = 0x13
    BCHAR2 = 0x14
    MEMID = 0x15
    CHKSUM = 0x16
    ACHAR = 0x17
    ACHAR2 = 0x18
    ACHAR4 = 0x19
    CHAR3 = 0x1A
    UCHAR3 = 0x1B
    BCHAR3 = 0x1C
    ACHAR3 = 0x1D
    DOUBLEH = 0x1E
    DOUBLEL = 0x1F
    RESVD = 0x20  # Codes 0x20-0x63 are reserved
    SHORT3 = 0x21
    USHORT3 = 0x22
    SHORT4 = 0x23
    USHORT4 = 0x24
    LONG2 = 0x25
    ULONG2 = 0x26
    RESVD_BEGIN_ = 0x64
    # Codes 0x64-0xFF are to be used in User-Defined DataTypes


class ServiceCode(IntEnum):
    IDS = 0  # Identification, response required
    NSS = 1  # Node Synchronisation
    DDS = 2  # Data Download, response required
    DUS = 3  # Data Upload, response required
    SCS = 4  # Simulation Control, response required
    TIS = 5  # Transmission Interval, response required
    FPS = 6  # Flash Programming, response required
    STS = 7  # State Transmission
    FSS = 8  # Filter Setting, response required
    TCS = 9  # Test Control, response required
    BSS = 10  # Baud Rate
    NIS = 11  # Node-ID Setting, response required
    MIS = 12  # Module Information, response required
    MCS = 13  # Module Configuration
    CSS = 14  # CAN-ID Setting
    DIS = 15  # CAN-ID Distributtion Setting
    XSS = 16  # 16~99 Reserved for future use
    UDF = 100  # 100-255 Reserved for User-defined services


class TransmissionInterval(IntEnum):
    US_12_5MS = 12_500
    US_25MS = 25_000
    US_50MS = 50_000
    US_100MS = 100_000
    US_200MS = 200_000
    US_500MS = 500_000
    US_1S = 1_000_000


class ErrorCode(IntEnum):
    OK = 0
    ARGUMENT = 1
    NOT_ENOUGH_MEMORY = 2
    DRIVER = 3
    NO_SUCH_ENTRY = 4
    ENTRY_EXISTS = 5
    BAD_DATA_TYPE = 6
    BAD_MESSAGE_ID = 7
    BAD_NODE_ID = 8
    BAD_REDUND_CHAN = 9
    BAD_SERVICE_CHAN = 19
    BAD_CAN_FRAME = 11
    QUOTA_EXCEEDED = 12
    LOGIC = 13


class NodeServiceCode(IntEnum):
    """CANAS Node Services codes"""
    pass


class CANAeroMessageTypeID(Enum):
    EMERGENCY_EVENTS = (0, 127)
    NODE_SERVICE_HIGH = (128, 199)
    USER_DEFINED_HIGH = (200, 299)
    NORMAL_OPERATION = (300, 1799)
    USER_DEFINED_LOW = (1800, 1899)
    DEBUG_SERVICE = (1900, 1999)
    NODE_SERVICE_LOW = (2000, 2031)


class MessageGroupID(Enum):
    WTF = 0
    PARAMETER = 1
    SERVICE = 2


class CANAeroServiceChannelID(Enum):
    SERVICE_CHANNEL_HIGH = (0, 35)
    SERVICE_CHANNEL_LOW = (100, 115)
