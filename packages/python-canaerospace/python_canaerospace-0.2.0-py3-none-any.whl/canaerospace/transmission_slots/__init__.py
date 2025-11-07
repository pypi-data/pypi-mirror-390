from canaerospace.directory import IdentifierDirectory, default_directory
from canaerospace.enums import TransmissionInterval
from canaerospace.transmission import TTEntry, TTSlot

us12_5ms = TransmissionInterval.US_12_5MS
us100ms = TransmissionInterval.US_100MS

param: IdentifierDirectory = default_directory()


_slots = [
    {"prefix": "A", "index": 0, "parameter": param.by_name(
        "body_long_accel"), "interval": us12_5ms},
    {"prefix": "A", "index": 1, "parameter": param.by_name(
        "body_lat_accel"), "interval": us12_5ms},
    {"prefix": "A", "index": 2, "parameter": param.by_name(
        "body_norm_accel"), "interval": us12_5ms},
    {"prefix": "A", "index": 3, "parameter": param.by_name(
        "body_pitch_rate"), "interval": us12_5ms},
    {"prefix": "A", "index": 4, "parameter": param.by_name(
        "body_roll_rate"), "interval": us12_5ms},
    {"prefix": "A", "index": 5, "parameter": param.by_name(
        "body_yaw_rate"), "interval": us12_5ms},
    {"prefix": "A", "index": 6, "parameter": param.by_name(
        "body_pitch_angle"), "interval": us12_5ms},
    {"prefix": "A", "index": 7, "parameter": param.by_name(
        "body_roll_angle"), "interval": us12_5ms},
    {"prefix": "A", "index": 8, "parameter": param.by_name(
        "heading_angle"), "interval": us12_5ms},
    {"prefix": "D", "index": 0, "byte": 0, "parameter": param.by_name(
        "altitude_rate"), "interval": us100ms},
    {"prefix": "D", "index": 0, "byte": 1, "parameter": param.by_name(
        "true_airspeed"), "interval": us100ms},
    {"prefix": "D", "index": 0, "byte": 2, "parameter": param.by_name(
        "calibrated_airspeed"), "interval": us100ms},
    {"prefix": "D", "index": 0, "byte": 3, "parameter": param.by_name(
        "baro_correction"), "interval": us100ms},
    {"prefix": "D", "index": 0, "byte": 4, "parameter": param.by_name(
        "baro_corrected_altitude"), "interval": us100ms},
    {"prefix": "D", "index": 0, "byte": 5, "parameter": param.by_name(
        "standard_altitude"), "interval": us100ms},
    #  @TODO Complete adding the slots from the documentation
]


def build_entries_for_builder(builder):
    entries = []
    for slot in _slots:
        tts = TTSlot(
            phase=slot["parameter"],
            index=slot['index'],
            byte=slot.get('byte', None),
            param_name=slot['parameter'].name,
            unit=slot['parameter'].unit,
            can_id=slot['parameter'].can_id,
            data_type=slot['parameter'].data_type
        )
        entry = TTEntry(slot=tts, interval=slot['interval'], build_frame=builder(
            slot['parameter'].can_id))
        entries.append(entry)
    return entries
