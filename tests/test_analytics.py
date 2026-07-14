"""Tests for driver decision analytics."""

import pytest

from driver_decision_profiler.analytics import (
    build_driver_profile,
    decisions_by_section,
    profiles_by_section,
)
from driver_decision_profiler.models import (
    DriverDecision,
    RacingLine,
    TrackSection,
    VehiclePosition,
)


@pytest.fixture
def turn_one_section() -> TrackSection:
    return TrackSection(
        section_id="turn_1_entry",
        name="Turn 1 Entry",
    )


@pytest.fixture
def turn_three_section() -> TrackSection:
    return TrackSection(
        section_id="turn_3_entry",
        name="Turn 3 Entry",
    )


def make_decision(
    *,
    lap_number: int,
    section: TrackSection,
    racing_line: RacingLine,
    timestamp_seconds: float,
) -> DriverDecision:
    """Create a reusable decision event for analytics tests."""
    return DriverDecision(
        lap_number=lap_number,
        section=section,
        racing_line=racing_line,
        position=VehiclePosition(x=150, y=150),
        timestamp_seconds=timestamp_seconds,
    )


def test_build_driver_profile_calculates_counts_and_percentages(
    turn_one_section: TrackSection,
) -> None:
    decisions = [
        make_decision(
            lap_number=1,
            section=turn_one_section,
            racing_line=RacingLine.HIGH,
            timestamp_seconds=5.0,
        ),
        make_decision(
            lap_number=2,
            section=turn_one_section,
            racing_line=RacingLine.HIGH,
            timestamp_seconds=15.0,
        ),
        make_decision(
            lap_number=3,
            section=turn_one_section,
            racing_line=RacingLine.MIDDLE,
            timestamp_seconds=25.0,
        ),
        make_decision(
            lap_number=4,
            section=turn_one_section,
            racing_line=RacingLine.LOW,
            timestamp_seconds=35.0,
        ),
    ]

    profile = build_driver_profile(decisions)

    assert profile.total_decisions == 4

    high = profile.preference_for(RacingLine.HIGH)
    middle = profile.preference_for(RacingLine.MIDDLE)
    low = profile.preference_for(RacingLine.LOW)

    assert high.decision_count == 2
    assert high.percentage == 50.0

    assert middle.decision_count == 1
    assert middle.percentage == 25.0

    assert low.decision_count == 1
    assert low.percentage == 25.0


def test_build_driver_profile_handles_empty_decisions() -> None:
    profile = build_driver_profile([])

    assert profile.total_decisions == 0

    for racing_line in RacingLine:
        preference = profile.preference_for(racing_line)

        assert preference.decision_count == 0
        assert preference.percentage == 0.0


def test_driver_profile_rejects_unknown_preference() -> None:
    profile = build_driver_profile([])

    with pytest.raises(
        ValueError,
        match="No preference found",
    ):
        profile.preference_for("outside")  # type: ignore[arg-type]


def test_decisions_by_section_groups_events(
    turn_one_section: TrackSection,
    turn_three_section: TrackSection,
) -> None:
    decisions = [
        make_decision(
            lap_number=1,
            section=turn_one_section,
            racing_line=RacingLine.HIGH,
            timestamp_seconds=5.0,
        ),
        make_decision(
            lap_number=1,
            section=turn_three_section,
            racing_line=RacingLine.LOW,
            timestamp_seconds=12.0,
        ),
        make_decision(
            lap_number=2,
            section=turn_one_section,
            racing_line=RacingLine.MIDDLE,
            timestamp_seconds=20.0,
        ),
    ]

    grouped = decisions_by_section(decisions)

    assert set(grouped) == {
        "turn_1_entry",
        "turn_3_entry",
    }
    assert len(grouped["turn_1_entry"]) == 2
    assert len(grouped["turn_3_entry"]) == 1


def test_profiles_by_section_builds_individual_profiles(
    turn_one_section: TrackSection,
    turn_three_section: TrackSection,
) -> None:
    decisions = [
        make_decision(
            lap_number=1,
            section=turn_one_section,
            racing_line=RacingLine.HIGH,
            timestamp_seconds=5.0,
        ),
        make_decision(
            lap_number=2,
            section=turn_one_section,
            racing_line=RacingLine.HIGH,
            timestamp_seconds=15.0,
        ),
        make_decision(
            lap_number=1,
            section=turn_three_section,
            racing_line=RacingLine.LOW,
            timestamp_seconds=22.0,
        ),
    ]

    profiles = profiles_by_section(decisions)

    turn_one_profile = profiles["turn_1_entry"]
    turn_three_profile = profiles["turn_3_entry"]

    assert turn_one_profile.total_decisions == 2
    assert (
        turn_one_profile
        .preference_for(RacingLine.HIGH)
        .percentage
        == 100.0
    )

    assert turn_three_profile.total_decisions == 1
    assert (
        turn_three_profile
        .preference_for(RacingLine.LOW)
        .percentage
        == 100.0
    )
