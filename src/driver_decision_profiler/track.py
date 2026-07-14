"""Track geometry and racing-line zone classification."""

from dataclasses import dataclass

from driver_decision_profiler.models import RacingLine, TrackSection, VehiclePosition


@dataclass(frozen=True, slots=True)
class RectangularZone:
    """A rectangular region associated with a racing-line classification."""

    section: TrackSection
    racing_line: RacingLine
    left: float
    top: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width <= 0:
            raise ValueError("width must be greater than zero")

        if self.height <= 0:
            raise ValueError("height must be greater than zero")

    @property
    def right(self) -> float:
        """Return the right boundary of the zone."""
        return self.left + self.width

    @property
    def bottom(self) -> float:
        """Return the bottom boundary of the zone."""
        return self.top + self.height

    def contains(self, position: VehiclePosition) -> bool:
        """Return whether a vehicle position is inside the zone."""
        return (
            self.left <= position.x < self.right
            and self.top <= position.y < self.bottom
        )


@dataclass(frozen=True, slots=True)
class Track:
    """A collection of decision zones used to classify vehicle positions."""

    name: str
    zones: tuple[RectangularZone, ...]

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("track name cannot be empty")

        if not self.zones:
            raise ValueError("track must contain at least one zone")

    def classify_position(
        self,
        position: VehiclePosition,
        section_id: str,
    ) -> RacingLine | None:
        """Classify a vehicle position within a specific track section."""
        for zone in self.zones:
            if zone.section.section_id != section_id:
                continue

            if zone.contains(position):
                return zone.racing_line

        return None
