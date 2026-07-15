"""Driver decision event recording logic."""

from dataclasses import dataclass, field

from driver_decision_profiler.models import (
    DriverDecision,
    RaceContext,
    TrackSection,
    VehiclePosition,
)
from driver_decision_profiler.track import Track


@dataclass(slots=True)
class DecisionRecorder:
    """Records racing-line decisions while preventing duplicate events."""

    track: Track
    decisions: list[DriverDecision] = field(default_factory=list)
    _active_sections: set[str] = field(default_factory=set, init=False)

    def update(
        self,
        *,
        lap_number: int,
        section: TrackSection,
        position: VehiclePosition,
        timestamp_seconds: float,
        context: RaceContext | None = None,
    ) -> DriverDecision | None:
        """Record a decision when a vehicle first enters a section zone."""
        racing_line = self.track.classify_position(
            position=position,
            section_id=section.section_id,
        )

        if racing_line is None:
            self._active_sections.discard(section.section_id)
            return None

        if section.section_id in self._active_sections:
            return None

        decision = DriverDecision(
            lap_number=lap_number,
            section=section,
            racing_line=racing_line,
            position=position,
            timestamp_seconds=timestamp_seconds,
            context=context,
        )

        self.decisions.append(decision)
        self._active_sections.add(section.section_id)

        return decision

    def reset(self) -> None:
        """Clear all recorded decisions and active section state."""
        self.decisions.clear()
        self._active_sections.clear()

    def decisions_for_lap(self, lap_number: int) -> list[DriverDecision]:
        """Return all decisions recorded during a specific lap."""
        if lap_number < 1:
            raise ValueError("lap_number must be at least 1")

        return [
            decision
            for decision in self.decisions
            if decision.lap_number == lap_number
        ]
