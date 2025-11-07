import pytest

from canaerospace.generic_redundancy_resolver import CANASGRRConfig as GrrConfig
from canaerospace.generic_redundancy_resolver import CANASGRRInstance as Grr
from canaerospace.generic_redundancy_resolver import CANASSwitchReasons


@pytest.fixture
def grr_instance():
    cfg = GrrConfig()
    cfg.channel_timeout_usec = 20000
    cfg.fom_hysteresis = 0.2
    cfg.min_fom_switch_interval_usec = 500000
    cfg.num_channels = 3
    return Grr(config=cfg)


class TestGrr:
    def test_initialization_and_first_update(self, grr_instance):
        grr = grr_instance
        # Initial state
        assert grr.get_active_channel() == 0
        assert grr.get_last_switch_timestamp() == 0

        # First update should always be REASON_INIT
        assert grr.update(0, 1.0, 100) == CANASSwitchReasons.REASON_INIT
        assert grr.get_active_channel() == 0
        assert grr.get_last_switch_timestamp() == 100

    def test_no_switch_scenarios(self, grr_instance):
        grr = grr_instance
        grr.update(0, 1.0, 100)  # Initial update

        # Scenario 1: Update the currently active channel
        assert grr.update(0, 1.0, 200) == CANASSwitchReasons.REASON_NONE

        # Scenario 2: FOM not better enough to overcome hysteresis
        assert grr.update(1, 1.1, 300) == CANASSwitchReasons.REASON_NONE

        # Scenario 3: FOM is better, but min_fom_switch_interval has not passed
        grr.update(1, 1.3, 200)  # This won't switch
        assert grr.get_active_channel() == 0
        assert grr.update(1, 1.3, 200) == CANASSwitchReasons.REASON_NONE

    def test_fom_switch(self, grr_instance):
        grr = grr_instance
        grr.update(0, 1.0, 100)  # Initial update

        # Keep channel 0 alive so it doesn't time out
        grr.update(0, 1.0, 500100)

        # Perform a valid FOM switch
        # last_switch_timestamp is 100. Current time is 500200. 500200 >= 100 + 500000 is TRUE
        # new FOM 1.3 > old FOM 1.0 + hysteresis 0.2 is TRUE
        assert grr.update(
            1, 1.3, 500200) == CANASSwitchReasons.REASON_FOM
        assert grr.get_active_channel() == 1
        assert grr.get_last_switch_timestamp() == 500200

    def test_timeout_switch(self, grr_instance):
        grr = grr_instance
        grr.update(0, 1.0, 100)  # Initial update, active channel is 0

        # Active channel (0) was last updated at 100. It will time out at 100 + 20000 = 20100.
        # Update a different channel after the timeout period.
        # A switch should occur even though the new channel has a worse FOM.
        assert grr.update(
            1, 0.5, 30000) == CANASSwitchReasons.REASON_TIMEOUT
        assert grr.get_active_channel() == 1
        assert grr.get_last_switch_timestamp() == 30000

    def test_manual_override(self, grr_instance):
        grr = grr_instance
        grr.update(0, 1.0, 100)      # Channel 0 is now active, FOM=1.0
        # Channel 1 has a great FOM, but not switched due to min_interval
        grr.update(1, 99.0, 200)

        # Override to channel 2, which has no updates and a FOM of -inf
        grr.override_active_channel(2, 300)
        assert grr.get_active_channel() == 2
        assert grr.get_last_switch_timestamp() == 300

        # An update to another channel with a better FOM should NOT cause a switch
        # because the override is in effect and the timeout has not been reached.
        # Active channel (2) has last_update_timestamp_usec=0. Timeout is 20000.
        # Current timestamp is 400, which is less than 20000.
        assert grr.update(0, 1.0, 400) == CANASSwitchReasons.REASON_NONE
        assert grr.get_active_channel() == 2

        # Now, let the overridden channel (2) time out.
        # Its last update was never (timestamp 0). It will time out at 0 + 20000 = 20000.
        # This update to channel 0 happens at 20001, after the timeout.
        # The resolver should switch to the updating channel (0), NOT the best FOM channel (1).
        assert grr.update(
            0, 1.0, 20001) == CANASSwitchReasons.REASON_TIMEOUT
        assert grr.get_active_channel() == 0

    def test_forced_channel_initialization(self, grr_instance):
        grr = grr_instance
        grr.override_active_channel(2, 100)
        assert grr.get_active_channel() == 2
        # After an override, the system is no longer in the initial state.
        # An update to the active channel should result in REASON_NONE.
        assert grr.update(2, 0.0, 200) == CANASSwitchReasons.REASON_NONE
        assert grr.get_active_channel() == 2

    def test_validation(self, grr_instance):
        grr = grr_instance
        with pytest.raises(IndexError):
            grr.get_channel_state(3)

        grr.get_channel_state(0)
        grr.get_channel_state(2)

        with pytest.raises(ValueError):
            grr.override_active_channel(3)

        with pytest.raises(ValueError):
            grr.update(3, 0.0, 1)

        with pytest.raises(ValueError):
            grr.update(1, 0.0, 0)
