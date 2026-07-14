"""Tests for the core driver decision profiler models."""

import pytest

from driver_decision_profiler.models import (
    DriverDecision,
    RacingLine,
    TrackSection,
    VehiclePosition,
)


def test_racing_line_string_format() -> None:
    assert str(RacingLine.HIGH) == "High"
    assert str(RacingLine.MIDDLE) == "Middle"
    assert str(RacingLine.LOW) == "Low"


def test_vehicle_position_accepts_numeric_coordinates() -> None:
    position = VehiclePosition(x=125.5, y=240)

    assert position.x == 125.5
    assert position.y == 240


def test_vehicle_position_rejects_non_numeric_coordinates() -> None:
    with pytest.raises(TypeError, match="x must be a numeric value"):
        VehiclePosition(x="left", y=200)  # type: ignore[arg-type]


def test_track_section_requires_identifier() -> None:
    with pytest.raises(ValueError, match="section_id cannot be empty"):
        TrackSection(section_id="   ", name="Turn 1 Entry")


def test_track_section_requires_name() -> None:
    with pytest.raises(ValueError, match="name cannot be empty"):
        TrackSection(section_id="turn_1_entry", name="   ")


def test_driver_decision_stores_valid_event_data() -> None:
    section = TrackSection(
        section_id="turn_1_entry",
        name="Turn 1 Entry",
    )
    position = VehiclePosition(x=350.0, y=125.0)

    decision = DriverDecision(
        lap_number=2,
        section=section,
        racing_line=RacingLine.HIGH,
        position=position,
        timestamp_seconds=18.7,
    )

    assert decision.lap_number == 2
    assert decision.section == section
    assert decision.racing_line is RacingLine.HIGH
    assert decision.position == position
    assert decision.timestamp_seconds == 18.7


def test_driver_decision_rejects_invalid_lap_number() -> None:
    with pytest.raises(ValueError, match="lap_number must be at least 1"):
        DriverDecision(
            lap_number=0,
            section=TrackSection("turn_1_entry", "Turn 1 Entry"),
            racing_line=RacingLine.MIDDLE,
            position=VehiclePosition(300.0, 160.0),
            timestamp_seconds=4.5,
        )


def test_driver_decision_rejects_negative_timestamp() -> None:
    with pytest.raises(
        ValueError,
        match="timestamp_seconds cannot be negative",
    ):
        DriverDecision(
            lap_number=1,
            section=TrackSection("turn_1_entry", "Turn 1 Entry"),
            racing_line=RacingLine.LOW,
            position=VehiclePosition(300.0, 210.0),
            timestamp_seconds=-1.0,
        )
