from canaerospace.datatypes import DataType
from canaerospace.units import unit_map as units


#  @TODO Replace the norms unit with the correct unit per parameter
def get_hydraulic_system_data():
    """Hydraulic system data 5.5"""
    return [
        {"name": "hydraulic_system_1_pressure", "can_id": 800,
            "data_type": DataType.FLOAT, "unit": units.get("hpa")},
        {"name": "hydraulic_system_2_pressure", "can_id": 801,
            "data_type": DataType.FLOAT, "unit": units.get("hpa")},
        {"name": "hydraulic_system_3_pressure", "can_id": 802,
            "data_type": DataType.FLOAT, "unit": units.get("hpa")},
        {"name": "hydraulic_system_4_pressure", "can_id": 803,
            "data_type": DataType.FLOAT, "unit": units.get("hpa")},
        {"name": "hydraulic_system_5_pressure", "can_id": 804,
            "data_type": DataType.FLOAT, "unit": units.get("hpa")},
        {"name": "hydraulic_system_6_pressure", "can_id": 805,
            "data_type": DataType.FLOAT, "unit": units.get("hpa")},
        {"name": "hydraulic_system_7_pressure", "can_id": 806,
            "data_type": DataType.FLOAT, "unit": units.get("hpa")},
        {"name": "hydraulic_system_8_pressure", "can_id": 807,
            "data_type": DataType.FLOAT, "unit": units.get("hpa")},

        {"name": "hydraulic_system_1_fluid_temperature", "can_id": 808, "data_type": DataType.FLOAT,
         "unit": units.get("kelvin")},
        {"name": "hydraulic_system_2_fluid_temperature", "can_id": 809, "data_type": DataType.FLOAT,
         "unit": units.get("kelvin")},
        {"name": "hydraulic_system_3_fluid_temperature", "can_id": 810, "data_type": DataType.FLOAT,
         "unit": units.get("kelvin")},
        {"name": "hydraulic_system_4_fluid_temperature", "can_id": 811, "data_type": DataType.FLOAT,
         "unit": units.get("kelvin")},
        {"name": "hydraulic_system_5_fluid_temperature", "can_id": 812, "data_type": DataType.FLOAT,
         "unit": units.get("kelvin")},
        {"name": "hydraulic_system_6_fluid_temperature", "can_id": 813, "data_type": DataType.FLOAT,
         "unit": units.get("kelvin")},
        {"name": "hydraulic_system_7_fluid_temperature", "can_id": 814, "data_type": DataType.FLOAT,
         "unit": units.get("kelvin")},
        {"name": "hydraulic_system_8_fluid_temperature", "can_id": 815, "data_type": DataType.FLOAT,
         "unit": units.get("kelvin")},

        {"name": "hydraulic_system_1_fluid_quantity", "can_id": 816,
            "data_type": DataType.FLOAT, "unit": units.get("liter")},
        {"name": "hydraulic_system_2_fluid_quantity", "can_id": 817,
            "data_type": DataType.FLOAT, "unit": units.get("liter")},
        {"name": "hydraulic_system_3_fluid_quantity", "can_id": 818,
            "data_type": DataType.FLOAT, "unit": units.get("liter")},
        {"name": "hydraulic_system_4_fluid_quantity", "can_id": 819,
            "data_type": DataType.FLOAT, "unit": units.get("liter")},
        {"name": "hydraulic_system_5_fluid_quantity", "can_id": 820,
            "data_type": DataType.FLOAT, "unit": units.get("liter")},
        {"name": "hydraulic_system_6_fluid_quantity", "can_id": 821,
            "data_type": DataType.FLOAT, "unit": units.get("liter")},
        {"name": "hydraulic_system_7_fluid_quantity", "can_id": 822,
            "data_type": DataType.FLOAT, "unit": units.get("liter")},
        {"name": "hydraulic_system_8_fluid_quantity", "can_id": 823,
            "data_type": DataType.FLOAT, "unit": units.get("liter")},
    ]
