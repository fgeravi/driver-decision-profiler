"""Tests for the core driver decision profiler models."""

import pytest

from driver_decision_profiler.models import (
    DriverDecision,
    DriverRelationship,
    RaceContext,
    RacePhase,
    RacingLine,
    TrackSection,
    TrafficState,
    VehiclePosition,
)

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
def test_race_context_stores_teammate_following_conditions() -> None:
    context = RaceContext(
        traffic_state=TrafficState.FOLLOWING,
        race_phase=RacePhase.GREEN_FLAG,
        car_ahead_number=12,
        car_ahead_relationship=DriverRelationship.TEAMMATE,
        gap_seconds=0.35,
        closing_rate_mph=2.4,
        tire_age_laps=18,
    )

    assert context.traffic_state is TrafficState.FOLLOWING
    assert context.race_phase is RacePhase.GREEN_FLAG
    assert context.car_ahead_number == 12
    assert context.car_ahead_relationship is DriverRelationship.TEAMMATE
    assert context.gap_seconds == 0.35
    assert context.closing_rate_mph == 2.4
    assert context.tire_age_laps == 18


def test_race_context_allows_clear_track() -> None:
    context = RaceContext(
        traffic_state=TrafficState.CLEAR_TRACK,
        race_phase=RacePhase.GREEN_FLAG,
    )

    assert context.car_ahead_number is None
    assert context.car_ahead_relationship is DriverRelationship.NONE


def test_race_context_requires_car_number_for_relationship() -> None:
    with pytest.raises(
        ValueError,
        match="car_ahead_number is required",
    ):
        RaceContext(
            traffic_state=TrafficState.FOLLOWING,
            race_phase=RacePhase.GREEN_FLAG,
            car_ahead_relationship=DriverRelationship.TEAMMATE,
        )


def test_clear_track_rejects_car_ahead() -> None:
    with pytest.raises(
        ValueError,
        match="clear track context cannot include a car ahead",
    ):
        RaceContext(
            traffic_state=TrafficState.CLEAR_TRACK,
            race_phase=RacePhase.GREEN_FLAG,
            car_ahead_number=22,
            car_ahead_relationship=DriverRelationship.OPPONENT,
        )


def test_race_context_rejects_negative_gap() -> None:
    with pytest.raises(ValueError, match="gap_seconds cannot be negative"):
        RaceContext(
            traffic_state=TrafficState.FOLLOWING,
            race_phase=RacePhase.GREEN_FLAG,
            car_ahead_number=22,
            car_ahead_relationship=DriverRelationship.OPPONENT,
            gap_seconds=-0.2,
        )


def test_race_context_rejects_negative_tire_age() -> None:
    with pytest.raises(
        ValueError,
        match="tire_age_laps cannot be negative",
    ):
        RaceContext(
            traffic_state=TrafficState.CLEAR_TRACK,
            race_phase=RacePhase.GREEN_FLAG,
            tire_age_laps=-1,
        )


def test_driver_decision_can_store_race_context() -> None:
    context = RaceContext(
        traffic_state=TrafficState.FOLLOWING,
        race_phase=RacePhase.RESTART,
        car_ahead_number=12,
        car_ahead_relationship=DriverRelationship.TEAMMATE,
        gap_seconds=0.28,
    )

    decision = DriverDecision(
        lap_number=5,
        section=TrackSection("turn_1_entry", "Turn 1 Entry"),
        racing_line=RacingLine.LOW,
        position=VehiclePosition(150.0, 225.0),
        timestamp_seconds=52.4,
        context=context,
    )

    assert decision.context == context
    assert (
        decision.context.car_ahead_relationship
        is DriverRelationship.TEAMMATE
    )
