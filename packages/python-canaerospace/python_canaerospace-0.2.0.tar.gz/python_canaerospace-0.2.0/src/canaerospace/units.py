
import pint


class CANASUnitSystem:
    """
    A centralized unit system for the CANAS library using pint.
    This class encapsulates the UnitRegistry to avoid global state issues
    and provides a consistent set of units for the library.
    """

    def __init__(self):
        self._ureg = pint.UnitRegistry()
        self._build_unit_map()
        self._add_custom_definitions()

    def _build_unit_map(self):
        """Builds the map of standard, built-in unit strings to pint Quantity objects."""
        self._unit_map = {
            "norm": self._ureg.dimensionless,
            "gravity": self._ureg.meter / (self._ureg.second**2),
            "grams": self._ureg.gram,
            "degree": self._ureg.degree,
            "degree_per_second": self._ureg.degree / self._ureg.second,
            "meter_second_square": self._ureg.meter / (self._ureg.second**2),
            "meter_per_second": self._ureg.meter / self._ureg.second,
            "meter": self._ureg.meter,
            "hertz": self._ureg.hertz,
            "newton": self._ureg.newton,
            "newton_per_second": self._ureg.newton / self._ureg.second,
            "new_second_square": self._ureg.newton / (self._ureg.second ** 2),
            "kelvin": self._ureg.kelvin,
            "hpa": self._ureg.hectopascal,
            "temp": self._ureg.kelvin,
            "liter": self._ureg.liter,
            "liter_per_hour": self._ureg.liter / self._ureg.hour,
            "kilogram": self._ureg.kilogram,
            "volt": self._ureg.volt,
            "ampere": self._ureg.ampere
        }

    def _add_custom_definitions(self):
        """Adds custom or potentially missing unit definitions to the map."""
        try:
            # Check if 'mach' is already defined by trying to access it.
            mach_unit = self._ureg.mach
        except pint.errors.UndefinedUnitError:
            # If it's not defined, define it. This makes the system robust across
            # different versions of the pint library.
            self._ureg.define('mach = 343 * meter / second')
            mach_unit = self._ureg.mach

        self._unit_map['mach'] = mach_unit

    @property
    def registry(self) -> pint.UnitRegistry:
        """The encapsulated pint UnitRegistry instance."""
        return self._ureg

    @property
    def Q_(self):
        """Shortcut for creating a Quantity."""
        return self._ureg.Quantity

    @property
    def unit_map(self) -> dict[str, pint.Quantity]:
        """A map of string identifiers to unit objects."""
        return self._unit_map


# Create a singleton instance for the library to use.
# This provides the convenience of a global system without the risks of global state.
default_unit_system = CANASUnitSystem()

# Expose the key components for easy access throughout the library.
ureg = default_unit_system.registry
Q_ = default_unit_system.Q_
unit_map = default_unit_system.unit_map
