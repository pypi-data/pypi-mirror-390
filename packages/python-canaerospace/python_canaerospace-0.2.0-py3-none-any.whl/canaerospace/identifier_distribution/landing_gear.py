from canaerospace.datatypes import DataType
from canaerospace.units import unit_map as units


#  @TODO Replace the norms unit with the correct unit per parameter
def get_landing_gear_system_data_parameters():
    """Electric System data 5.8"""
    return [
        {
            "name": "gear_lever_switches",
            "can_id": 1175,
            "data_type": DataType.FLOAT,
            "unit": units.get('norm'),
        },
        {
            "name": "gear_lever_lights_wow_solenoid",
            "can_id": 1176,
            "data_type": DataType.FLOAT,
            "unit": units.get('norm'),
        },
        {
            "name": "landing_gear_1_tire_pressure",
            "can_id": 1177,
            "data_type": DataType.FLOAT,
            "unit": units.get("hPa"),
        },
        {
            "name": "landing_gear_2_tire_pressure",
            "can_id": 1178,
            "data_type": DataType.FLOAT,
            "unit": units.get("hPa"),
        },
        {
            "name": "landing_gear_3_tire_pressure",
            "can_id": 1179,
            "data_type": DataType.FLOAT,
            "unit": units.get("hPa"),
        },
        {
            "name": "landing_gear_4_tire_pressure",
            "can_id": 1180,
            "data_type": DataType.FLOAT,
            "unit": units.get("hPa"),
        },
        {
            "name": "landing_gear_1_brake_pad_thickness",
            "can_id": 1181,
            "data_type": DataType.FLOAT,
            "unit": units.get("mm"),
        },
        {
            "name": "landing_gear_2_brake_pad_thickness",
            "can_id": 1182,
            "data_type": DataType.FLOAT,
            "unit": units.get("mm"),
        },
        {
            "name": "landing_gear_3_brake_pad_thickness",
            "can_id": 1183,
            "data_type": DataType.FLOAT,
            "unit": units.get("mm"),
        },
        {
            "name": "landing_gear_4_brake_pad_thickness",
            "can_id": 1184,
            "data_type": DataType.FLOAT,
            "unit": units.get("mm"),
        },

    ]
