"""Analytics for recorded driver racing-line decisions."""

from collections import Counter
from dataclasses import dataclass

from driver_decision_profiler.models import DriverDecision, RacingLine


@dataclass(frozen=True, slots=True)
class LinePreference:
    """Summary statistics for one racing-line classification."""

    racing_line: RacingLine
    decision_count: int
    percentage: float


@dataclass(frozen=True, slots=True)
class DriverProfile:
    """Aggregated racing-line preferences for a recorded session."""

    total_decisions: int
    preferences: tuple[LinePreference, ...]

    def preference_for(self, racing_line: RacingLine) -> LinePreference:
        """Return the preference statistics for a specific racing line."""
        for preference in self.preferences:
            if preference.racing_line is racing_line:
                return preference

        raise ValueError(f"No preference found for racing line: {racing_line}")


def build_driver_profile(
    decisions: list[DriverDecision],
) -> DriverProfile:
    """Build a driver profile from recorded racing-line decisions."""
    total_decisions = len(decisions)

    line_counts = Counter(
        decision.racing_line
        for decision in decisions
    )

    preferences = tuple(
        LinePreference(
            racing_line=racing_line,
            decision_count=line_counts[racing_line],
            percentage=(
                line_counts[racing_line] / total_decisions * 100
                if total_decisions
                else 0.0
            ),
        )
        for racing_line in RacingLine
    )

    return DriverProfile(
        total_decisions=total_decisions,
        preferences=preferences,
    )


def decisions_by_section(
    decisions: list[DriverDecision],
) -> dict[str, list[DriverDecision]]:
    """Group recorded decisions by track section identifier."""
    grouped: dict[str, list[DriverDecision]] = {}

    for decision in decisions:
        section_id = decision.section.section_id
        grouped.setdefault(section_id, []).append(decision)

    return grouped


def profiles_by_section(
    decisions: list[DriverDecision],
) -> dict[str, DriverProfile]:
    """Build a separate driver profile for each track section."""
    return {
        section_id: build_driver_profile(section_decisions)
        for section_id, section_decisions in decisions_by_section(
            decisions
        ).items()
    }
