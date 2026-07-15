"""Demonstrate race-context driver decision profiling."""

from driver_decision_profiler.analytics import (
    build_driver_profile,
    profile_by_context,
)
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


def create_decision(
    *,
    lap_number: int,
    racing_line: RacingLine,
    context: RaceContext,
) -> DriverDecision:
    """Create one simulated contextual driver decision."""
    return DriverDecision(
        lap_number=lap_number,
        section=TrackSection(
            section_id="turn_1_entry",
            name="Turn 1 Entry",
        ),
        racing_line=racing_line,
        position=VehiclePosition(x=150.0, y=150.0),
        timestamp_seconds=lap_number * 30.0,
        context=context,
    )


def print_profile(title: str, profile: object) -> None:
    """Print a formatted profile to the terminal."""
    print(f"\n{title}")
    print("=" * len(title))
    print(f"Total decisions: {profile.total_decisions}")

    for preference in profile.preferences:
        print(
            f"{str(preference.racing_line):<7} "
            f"{preference.decision_count:>2} | "
            f"{preference.percentage:>5.1f}%"
        )


def main() -> None:
    """Run the contextual profiling demonstration."""
    teammate_context = RaceContext(
        traffic_state=TrafficState.FOLLOWING,
        race_phase=RacePhase.GREEN_FLAG,
        car_ahead_number=12,
        car_ahead_relationship=DriverRelationship.TEAMMATE,
        gap_seconds=0.32,
        closing_rate_mph=2.1,
        tire_age_laps=14,
    )

    opponent_context = RaceContext(
        traffic_state=TrafficState.FOLLOWING,
        race_phase=RacePhase.GREEN_FLAG,
        car_ahead_number=5,
        car_ahead_relationship=DriverRelationship.OPPONENT,
        gap_seconds=0.41,
        closing_rate_mph=3.0,
        tire_age_laps=14,
    )

    clear_track_context = RaceContext(
        traffic_state=TrafficState.CLEAR_TRACK,
        race_phase=RacePhase.GREEN_FLAG,
        tire_age_laps=8,
    )

    decisions = [
        create_decision(
            lap_number=1,
            racing_line=RacingLine.LOW,
            context=teammate_context,
        ),
        create_decision(
            lap_number=2,
            racing_line=RacingLine.LOW,
            context=teammate_context,
        ),
        create_decision(
            lap_number=3,
            racing_line=RacingLine.MIDDLE,
            context=teammate_context,
        ),
        create_decision(
            lap_number=4,
            racing_line=RacingLine.LOW,
            context=teammate_context,
        ),
        create_decision(
            lap_number=5,
            racing_line=RacingLine.HIGH,
            context=opponent_context,
        ),
        create_decision(
            lap_number=6,
            racing_line=RacingLine.HIGH,
            context=opponent_context,
        ),
        create_decision(
            lap_number=7,
            racing_line=RacingLine.MIDDLE,
            context=opponent_context,
        ),
        create_decision(
            lap_number=8,
            racing_line=RacingLine.HIGH,
            context=clear_track_context,
        ),
        create_decision(
            lap_number=9,
            racing_line=RacingLine.MIDDLE,
            context=clear_track_context,
        ),
    ]

    print_profile(
        "Overall Driver Profile",
        build_driver_profile(decisions),
    )

    print_profile(
        "Following a Teammate",
        profile_by_context(
            decisions,
            relationship=DriverRelationship.TEAMMATE,
            traffic_state=TrafficState.FOLLOWING,
        ),
    )

    print_profile(
        "Following an Opponent",
        profile_by_context(
            decisions,
            relationship=DriverRelationship.OPPONENT,
            traffic_state=TrafficState.FOLLOWING,
        ),
    )

    print_profile(
        "Clear Track",
        profile_by_context(
            decisions,
            traffic_state=TrafficState.CLEAR_TRACK,
        ),
    )

    print_profile(
        "Close Behind Teammate",
        profile_by_context(
            decisions,
            relationship=DriverRelationship.TEAMMATE,
            maximum_gap_seconds=0.5,
        ),
    )


if __name__ == "__main__":
    main()
