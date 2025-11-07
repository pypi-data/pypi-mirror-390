from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pint.registry import Quantity

from .enums import DataType
from .identifier_distribution.aircraft_engine import get_aircraft_engine_parameters
from .identifier_distribution.electric_system_data import get_electric_system_data_parameters
from .identifier_distribution.flight_controls import get_flight_controls_parameters
from .identifier_distribution.flight_state import get_flight_state_data_parameters
from .identifier_distribution.hydraulic_system_data import get_hydraulic_system_data
from .identifier_distribution.landing_gear import get_landing_gear_system_data_parameters
from .identifier_distribution.misc_data import get_misc_data_parameters
from .identifier_distribution.navigation_data import get_navigation_data_parameters
from .identifier_distribution.power_transmission import get_power_transmission_parameters
from .utils import IdentifierDistributionConfiguration, identifier_distribution_configuration


@dataclass(frozen=True)  # Frozen makes the object instance immutable
class ParameterDef:
    name: str
    can_id: int
    data_type: DataType
    unit: Quantity


class IdentifierDirectory:
    """ Holds the identifier distribution. Either default or user-defined"""

    def __init__(self) -> None:
        self._by_name: dict[str, ParameterDef] = {}
        self._by_id: dict[int, ParameterDef] = {}

    def is_parameter_def_unique(self, param: ParameterDef) -> bool:
        return param.name not in self._by_name and param.can_id not in self._by_id

    def validate_parameter_def_or_raise(self, param: ParameterDef) -> None:
        if not self.is_parameter_def_unique(param):
            raise ValueError(f"Duplicate name {param.name} or CAN-ID {param.can_id} in directory")

    def add(self, param: ParameterDef) -> None:
        self.validate_parameter_def_or_raise(param)
        self._by_name[param.name] = param
        self._by_id[param.can_id] = param

    def by_name_safe(self, name: str) -> ParameterDef | None:
        return self._by_name.get(name, None)

    def by_id_safe(self, can_id: int) -> ParameterDef | None:
        return self._by_id.get(can_id, None)

    def by_name(self, name: str) -> ParameterDef | None:
        return self._by_name[name]

    def by_id(self, can_id: int) -> ParameterDef | None:
        return self._by_id[can_id]


def get_parameters_from_config(configuration: IdentifierDistributionConfiguration) -> list[dict[str, Any]]:
    parameters = []

    if configuration.FLIGHT_STATE:
        parameters += get_flight_state_data_parameters()

    if configuration.FLIGHT_CONTROLS:
        parameters += get_flight_controls_parameters()

    if configuration.AIRCRAFT_ENGINE:
        parameters += get_aircraft_engine_parameters()

    if configuration.POWER_TRANSMISSION:
        parameters += get_power_transmission_parameters()

    if configuration.HYDRAULIC_SYSTEMS:
        parameters += get_hydraulic_system_data()

    if configuration.ELECTRIC_SYSTEM:
        parameters += get_electric_system_data_parameters()

    if configuration.NAVIGATION_SYSTEM:
        parameters += get_navigation_data_parameters()

    if configuration.LANDING_GEAR:
        parameters += get_landing_gear_system_data_parameters()

    if configuration.MISCELLANEOUS:
        parameters += get_misc_data_parameters()

    return parameters


def default_directory(configuration: IdentifierDistributionConfiguration | None = None) -> IdentifierDirectory:
    directory = IdentifierDirectory()

    if configuration is None:
        configuration = identifier_distribution_configuration

    parameters = get_parameters_from_config(configuration)
    # Add all supported parameters
    for param in parameters:
        directory.add(ParameterDef(**param))

    return directory
