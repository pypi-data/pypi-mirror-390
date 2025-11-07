from hypothesis import given
from hypothesis import strategies as st

from canaerospace.units import default_unit_system


# Fuzzing test for the unit system
@given(unit_key=st.sampled_from(list(default_unit_system.unit_map.keys())),
       value=st.floats(allow_nan=False, allow_infinity=False))
def test_unit_fuzzing(unit_key, value) -> None:
    """
    This test uses hypothesis to fuzz the unit system.
    It randomly selects a unit from the unit_map and a random float value,
    then creates a pint Quantity and verifies that the units are correctly applied.
    """
    # Arrange
    unit = default_unit_system.unit_map[unit_key]
    Q_ = default_unit_system.Q_

    # Act
    quantity = Q_(value, unit)

    # Assert
    assert quantity.magnitude == value
    assert quantity.units == unit
