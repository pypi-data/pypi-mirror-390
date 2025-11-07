import pytest

from canaerospace.directory import IdentifierDirectory, default_directory
from canaerospace.enums import DataType
from canaerospace.identifier_distribution.aircraft_engine import get_aircraft_engine_parameters
from canaerospace.identifier_distribution.electric_system_data import get_electric_system_data_parameters
from canaerospace.identifier_distribution.flight_controls import get_flight_controls_parameters
from canaerospace.identifier_distribution.flight_state import get_flight_state_data_parameters
from canaerospace.identifier_distribution.hydraulic_system_data import get_hydraulic_system_data
from canaerospace.identifier_distribution.landing_gear import get_landing_gear_system_data_parameters
from canaerospace.identifier_distribution.misc_data import get_misc_data_parameters
from canaerospace.identifier_distribution.navigation_data import get_navigation_data_parameters
from canaerospace.identifier_distribution.power_transmission import get_power_transmission_parameters


@pytest.fixture
def default_dir() -> IdentifierDirectory:
    return default_directory()


class TestDirectory:
    def test_default_directory_contains_basic_params(self, default_dir):
        basic = ['static_pressure', 'port_side_angle_of_attack',
                 'starbord_side_angle_of_attack']
        for p in basic:
            param = default_dir.by_name(p)
            assert param is not None
            assert isinstance(param.can_id, int)
            assert param.data_type == DataType.FLOAT

    def test_default_directory_invalid_param(self, default_dir):
        assert default_dir.by_name_safe('i-do-not-exist') is None
        with pytest.raises(KeyError):
            default_dir.by_name('i-do-not-exist')

    def test_rejects_duplicate(self, default_dir):
        with pytest.raises(ValueError):
            default_dir.add(default_dir.by_name('static_pressure'))


@pytest.fixture
def sections_data():
    return {
        'sections': {
            '5.1': get_flight_state_data_parameters(),
            '5.2': get_flight_controls_parameters(),
            '5.3': get_aircraft_engine_parameters(),
            '5.4': get_power_transmission_parameters(),
            '5.5': get_hydraulic_system_data(),
            '5.6': get_electric_system_data_parameters(),
            '5.7': get_navigation_data_parameters(),
            '5.8': get_landing_gear_system_data_parameters(),
            '5.9': get_misc_data_parameters()
        },
        'expected': {
            '5.1': ['body_long_accel', 'body_lat_accel'],
            '5.2': ['roll_control_position', 'lateral_stick_trim_position_command'],
            '5.3': ['fuel_pump_1_flow_rate', 'fuel_tank_1_quantity'],
            '5.4': ['rotor_1_rpm', 'gearbox_1_oil_temperature'],
            '5.5': ['hydraulic_system_1_pressure', 'hydraulic_system_1_fluid_quantity'],
            '5.6': ['ac_system_1_voltage', 'dc_system_1_current', 'prop_9_iceguard_dc_current'],
            '5.7': [
                'active_nav_system_waypoint_latitude',
                'nav_waypoint_maximum_radar_height',
                'dme_2_distance',
                'true_heading'],
            '5.8': ['gear_lever_switches', 'landing_gear_3_brake_pad_thickness'],
            '5.9': ['utc', 'cabin_pressure']
        }
    }


class TestSectionDirectories:
    def test_sections(self, sections_data):
        """
        Automate the testing of either random samples, or eventually all if needed
        the parameters being present in the directory
        """
        sections = sections_data['sections']
        expected_data = sections_data['expected']
        for k in sections:
            expected = expected_data.get(k, None)
            assert expected is not None
            section_param_names = [p['name'] for p in sections[k]]
            for p_name in expected:
                assert p_name in section_param_names
