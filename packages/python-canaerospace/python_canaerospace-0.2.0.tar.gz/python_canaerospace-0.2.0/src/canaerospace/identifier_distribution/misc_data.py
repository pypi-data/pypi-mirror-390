from canaerospace.datatypes import DataType
from canaerospace.units import unit_map as units


#  @TODO Replace the norms unit with the correct unit per parameter
def get_misc_data_parameters():
    """Misc Data 5.9"""
    return [
        # format of UTC is HHMMSS (2 bytes for hours, 2 bytes for min, 2 bytes for secs, 2 empty bytes
        {
            "name": "utc",
            "can_id": 1200,
            "data_type": DataType.FLOAT,
            "unit": units.get('norm'),
        },
        {
            "name": "cabin_pressure",
            "can_id": 1201,
            "data_type": DataType.FLOAT,
            "unit": units.get("hpa"),
        },
        {
            "name": "cabin_altitude",
            "can_id": 1202,
            "data_type": DataType.FLOAT,
            "unit": units.get("m"),
        },
        {
            "name": "cabin_temperature",
            "can_id": 1203,
            "data_type": DataType.FLOAT,
            "unit": units.get("temp"),
        },
        {
            "name": "longitudinal_center_of_gravity",
            "can_id": 1204,
            "data_type": DataType.FLOAT,
            "unit": units.get("% MAC", '% MAC'),
        },
        {
            "name": "lateral_center_of_gravity",
            "can_id": 1205,
            "data_type": DataType.FLOAT,
            "unit": units.get("% MAC", '% MAC'),
        },
        # format of Date is DDMMYYYY, 2 bytes for day, 2 bytes for month, 4 bytes for year.
        {
            "name": "date",
            "can_id": 1206,
            "data_type": DataType.FLOAT,
            "unit": units.get('norm'),
        },
    ]
