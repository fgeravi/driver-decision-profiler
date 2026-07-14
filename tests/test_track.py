"""Tests for track geometry and racing-line classification."""

import pytest

from driver_decision_profiler.models import (
    RacingLine,
    TrackSection,
    VehiclePosition,
)
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


def test_zone_calculates_boundaries(
    turn_one_section: TrackSection,
) -> None:
    zone = RectangularZone(
        section=turn_one_section,
        racing_line=RacingLine.HIGH,
        left=100,
        top=50,
        width=200,
        height=75,
    )

    assert zone.right == 300
    assert zone.bottom == 125


def test_zone_contains_position(
    turn_one_section: TrackSection,
) -> None:
    zone = RectangularZone(
        section=turn_one_section,
        racing_line=RacingLine.MIDDLE,
        left=100,
        top=150,
        width=200,
        height=50,
    )

    assert zone.contains(VehiclePosition(x=150, y=175))


def test_zone_excludes_position_outside_boundaries(
    turn_one_section: TrackSection,
) -> None:
    zone = RectangularZone(
        section=turn_one_section,
        racing_line=RacingLine.LOW,
        left=100,
        top=200,
        width=200,
        height=50,
    )

    assert not zone.contains(VehiclePosition(x=150, y=275))


def test_zone_rejects_invalid_width(
    turn_one_section: TrackSection,
) -> None:
    with pytest.raises(ValueError, match="width must be greater than zero"):
        RectangularZone(
            section=turn_one_section,
            racing_line=RacingLine.HIGH,
            left=100,
            top=100,
            width=0,
            height=50,
        )


def test_zone_rejects_invalid_height(
    turn_one_section: TrackSection,
) -> None:
    with pytest.raises(ValueError, match="height must be greater than zero"):
        RectangularZone(
            section=turn_one_section,
            racing_line=RacingLine.HIGH,
            left=100,
            top=100,
            width=200,
            height=-1,
        )


@pytest.mark.parametrize(
    ("position", "expected_line"),
    [
        (VehiclePosition(x=150, y=125), RacingLine.HIGH),
        (VehiclePosition(x=150, y=175), RacingLine.MIDDLE),
        (VehiclePosition(x=150, y=225), RacingLine.LOW),
    ],
)
def test_track_classifies_racing_line(
    sample_track: Track,
    position: VehiclePosition,
    expected_line: RacingLine,
) -> None:
    result = sample_track.classify_position(
        position=position,
        section_id="turn_1_entry",
    )

    assert result is expected_line


def test_track_returns_none_outside_all_zones(
    sample_track: Track,
) -> None:
    result = sample_track.classify_position(
        position=VehiclePosition(x=400, y=400),
        section_id="turn_1_entry",
    )

    assert result is None


def test_track_returns_none_for_unknown_section(
    sample_track: Track,
) -> None:
    result = sample_track.classify_position(
        position=VehiclePosition(x=150, y=125),
        section_id="turn_2_entry",
    )

    assert result is None


def test_track_requires_name(
    turn_one_section: TrackSection,
) -> None:
    zone = RectangularZone(
        section=turn_one_section,
        racing_line=RacingLine.HIGH,
        left=100,
        top=100,
        width=200,
        height=50,
    )

    with pytest.raises(ValueError, match="track name cannot be empty"):
        Track(name="   ", zones=(zone,))


def test_track_requires_at_least_one_zone() -> None:
    with pytest.raises(
        ValueError,
        match="track must contain at least one zone",
    ):
        Track(name="Empty Track", zones=())
