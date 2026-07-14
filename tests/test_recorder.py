"""Tests for driver decision recording."""

import pytest

from driver_decision_profiler.models import (
    RacingLine,
    TrackSection,
    VehiclePosition,
)
from driver_decision_profiler.recorder import DecisionRecorder
from driver_decision_profiler.track import RectangularZone, Track


@pytest.fixture
def turn_one_section() -> TrackSection:
    return TrackSection(
        section_id="turn_1_entry",
        name="Turn 1 Entry",
    )


@pytest.fixture
def sample_track(turn_one_section: TrackSection) -> Track:
    return Track(
        name="Test Oval",
        zones=(
            RectangularZone(
                section=turn_one_section,
                racing_line=RacingLine.HIGH,
                left=100,
                top=100,
                width=200,
                height=50,
            ),
            RectangularZone(
                section=turn_one_section,
                racing_line=RacingLine.MIDDLE,
                left=100,
                top=150,
                width=200,
                height=50,
            ),
            RectangularZone(
                section=turn_one_section,
                racing_line=RacingLine.LOW,
                left=100,
                top=200,
                width=200,
                height=50,
            ),
        ),
    )


@pytest.fixture
def recorder(sample_track: Track) -> DecisionRecorder:
    return DecisionRecorder(track=sample_track)


def test_recorder_records_first_zone_entry(
    recorder: DecisionRecorder,
    turn_one_section: TrackSection,
) -> None:
    decision = recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=VehiclePosition(x=150, y=125),
        timestamp_seconds=5.2,
    )

    assert decision is not None
    assert decision.racing_line is RacingLine.HIGH
    assert len(recorder.decisions) == 1


def test_recorder_does_not_record_outside_zone(
    recorder: DecisionRecorder,
    turn_one_section: TrackSection,
) -> None:
    decision = recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=VehiclePosition(x=400, y=400),
        timestamp_seconds=5.2,
    )

    assert decision is None
    assert recorder.decisions == []


def test_recorder_prevents_duplicate_event_while_zone_is_active(
    recorder: DecisionRecorder,
    turn_one_section: TrackSection,
) -> None:
    first = recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=VehiclePosition(x=150, y=125),
        timestamp_seconds=5.2,
    )
    second = recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=VehiclePosition(x=170, y=130),
        timestamp_seconds=5.4,
    )

    assert first is not None
    assert second is None
    assert len(recorder.decisions) == 1


def test_recorder_allows_new_event_after_vehicle_exits_zone(
    recorder: DecisionRecorder,
    turn_one_section: TrackSection,
) -> None:
    recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=VehiclePosition(x=150, y=125),
        timestamp_seconds=5.2,
    )

    recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=VehiclePosition(x=400, y=400),
        timestamp_seconds=6.0,
    )

    decision = recorder.update(
        lap_number=2,
        section=turn_one_section,
        position=VehiclePosition(x=150, y=225),
        timestamp_seconds=12.3,
    )

    assert decision is not None
    assert decision.lap_number == 2
    assert decision.racing_line is RacingLine.LOW
    assert len(recorder.decisions) == 2


def test_recorder_keeps_original_entry_position(
    recorder: DecisionRecorder,
    turn_one_section: TrackSection,
) -> None:
    entry_position = VehiclePosition(x=150, y=175)

    decision = recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=entry_position,
        timestamp_seconds=7.8,
    )

    assert decision is not None
    assert decision.position == entry_position
    assert decision.timestamp_seconds == 7.8


def test_decisions_for_lap_filters_recorded_events(
    recorder: DecisionRecorder,
    turn_one_section: TrackSection,
) -> None:
    recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=VehiclePosition(x=150, y=125),
        timestamp_seconds=5.2,
    )
    recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=VehiclePosition(x=400, y=400),
        timestamp_seconds=6.0,
    )
    recorder.update(
        lap_number=2,
        section=turn_one_section,
        position=VehiclePosition(x=150, y=175),
        timestamp_seconds=12.1,
    )

    lap_two_decisions = recorder.decisions_for_lap(2)

    assert len(lap_two_decisions) == 1
    assert lap_two_decisions[0].lap_number == 2
    assert lap_two_decisions[0].racing_line is RacingLine.MIDDLE


def test_decisions_for_lap_rejects_invalid_lap_number(
    recorder: DecisionRecorder,
) -> None:
    with pytest.raises(ValueError, match="lap_number must be at least 1"):
        recorder.decisions_for_lap(0)


def test_reset_clears_decisions_and_active_state(
    recorder: DecisionRecorder,
    turn_one_section: TrackSection,
) -> None:
    recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=VehiclePosition(x=150, y=125),
        timestamp_seconds=5.2,
    )

    recorder.reset()

    assert recorder.decisions == []

    new_decision = recorder.update(
        lap_number=1,
        section=turn_one_section,
        position=VehiclePosition(x=150, y=175),
        timestamp_seconds=8.0,
    )

    assert new_decision is not None
    assert new_decision.racing_line is RacingLine.MIDDLE
