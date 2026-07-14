"""End-to-end demonstration of driver decision profiling."""

from driver_decision_profiler.analytics import (
    build_driver_profile,
    profiles_by_section,
)
from driver_decision_profiler.models import (
    RacingLine,
    TrackSection,
    VehiclePosition,
)
from driver_decision_profiler.recorder import DecisionRecorder
from driver_decision_profiler.track import RectangularZone, Track


def build_demo_track() -> tuple[Track, TrackSection, TrackSection]:
    """Create a small two-section oval-style track configuration."""
    turn_one = TrackSection(
        section_id="turn_1_entry",
        name="Turn 1 Entry",
    )
    turn_three = TrackSection(
        section_id="turn_3_entry",
        name="Turn 3 Entry",
    )

    zones = (
        RectangularZone(turn_one, RacingLine.HIGH, 100, 100, 200, 50),
        RectangularZone(turn_one, RacingLine.MIDDLE, 100, 150, 200, 50),
        RectangularZone(turn_one, RacingLine.LOW, 100, 200, 200, 50),
        RectangularZone(turn_three, RacingLine.HIGH, 500, 100, 200, 50),
        RectangularZone(turn_three, RacingLine.MIDDLE, 500, 150, 200, 50),
        RectangularZone(turn_three, RacingLine.LOW, 500, 200, 200, 50),
    )

    return Track(name="Demo Oval", zones=zones), turn_one, turn_three


def simulate_session(
    recorder: DecisionRecorder,
    turn_one: TrackSection,
    turn_three: TrackSection,
) -> None:
    """Feed simulated vehicle positions through the decision recorder."""
    simulated_laps = (
        (RacingLine.HIGH, RacingLine.MIDDLE),
        (RacingLine.HIGH, RacingLine.HIGH),
        (RacingLine.MIDDLE, RacingLine.LOW),
        (RacingLine.HIGH, RacingLine.MIDDLE),
        (RacingLine.LOW, RacingLine.HIGH),
        (RacingLine.HIGH, RacingLine.HIGH),
    )

    y_positions = {
        RacingLine.HIGH: 125.0,
        RacingLine.MIDDLE: 175.0,
        RacingLine.LOW: 225.0,
    }

    timestamp = 0.0

    for lap_number, (turn_one_line, turn_three_line) in enumerate(
        simulated_laps,
        start=1,
    ):
        recorder.update(
            lap_number=lap_number,
            section=turn_one,
            position=VehiclePosition(
                x=150.0,
                y=y_positions[turn_one_line],
            ),
            timestamp_seconds=timestamp,
        )
        timestamp += 4.0

        recorder.update(
            lap_number=lap_number,
            section=turn_one,
            position=VehiclePosition(x=350.0, y=300.0),
            timestamp_seconds=timestamp,
        )

        recorder.update(
            lap_number=lap_number,
            section=turn_three,
            position=VehiclePosition(
                x=550.0,
                y=y_positions[turn_three_line],
            ),
            timestamp_seconds=timestamp,
        )
        timestamp += 4.0

        recorder.update(
            lap_number=lap_number,
            section=turn_three,
            position=VehiclePosition(x=750.0, y=300.0),
            timestamp_seconds=timestamp,
        )


def print_profile(
    title: str,
    total_decisions: int,
    preferences: tuple,
) -> None:
    """Print a formatted driver profile."""
    print(f"\n{title}")
    print("=" * len(title))
    print(f"Total decisions: {total_decisions}")

    for preference in preferences:
        print(
            f"{str(preference.racing_line):<7} "
            f"{preference.decision_count:>2} decisions | "
            f"{preference.percentage:>5.1f}%"
        )


def main() -> None:
    """Run the complete simulated profiling workflow."""
    track, turn_one, turn_three = build_demo_track()
    recorder = DecisionRecorder(track=track)

    simulate_session(
        recorder=recorder,
        turn_one=turn_one,
        turn_three=turn_three,
    )

    overall_profile = build_driver_profile(recorder.decisions)

    print_profile(
        title="Overall Driver Profile",
        total_decisions=overall_profile.total_decisions,
        preferences=overall_profile.preferences,
    )

    section_profiles = profiles_by_section(recorder.decisions)

    for section in (turn_one, turn_three):
        profile = section_profiles[section.section_id]

        print_profile(
            title=section.name,
            total_decisions=profile.total_decisions,
            preferences=profile.preferences,
        )


if __name__ == "__main__":
    main()
