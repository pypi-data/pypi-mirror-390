# When a message needs to be sent to everyone, it needs to be sent to node 0
BROADCAST_NODE_ID: int = 0
MAX_NODES: int = 255
IFACE_COUNT_MAX: int = 8
DUMP_BUF_LEN: int = 100

# Multiplier for encoding the redundancy channel ID into the extended CAN ID
REDUND_CHAN_MULT = 65536

# Sentinel value to indicate that a message should be sent on all interfaces
ALL_IFACES = -1
