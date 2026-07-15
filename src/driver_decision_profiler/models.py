"""Core domain models for the driver decision profiler.

This module contains the shared data structures used throughout the project.
It intentionally has no dependency on Pygame, Pandas, or Matplotlib so the
models remain reusable and easy to test.
"""

from dataclasses import dataclass
from enum import Enum


class RacingLine(str, Enum):
    """Supported racing-line classifications."""

    HIGH = "high"
    MIDDLE = "middle"
    LOW = "low"

    def __str__(self) -> str:
        """Return a readable label for displays and reports."""
        return self.value.title()


class DriverRelationship(str, Enum):
    """Relationship between the profiled driver and the car ahead."""

    TEAMMATE = "teammate"
    OPPONENT = "opponent"
    NONE = "none"

    def __str__(self) -> str:
        return self.value.title()


class RacePhase(str, Enum):
    """Current phase of a race session."""

    GREEN_FLAG = "green_flag"
    RESTART = "restart"
    CAUTION = "caution"

    def __str__(self) -> str:
        return self.value.replace("_", " ").title()


class TrafficState(str, Enum):
    """Traffic situation surrounding the profiled vehicle."""

    CLEAR_TRACK = "clear_track"
    FOLLOWING = "following"
    SIDE_BY_SIDE = "side_by_side"

    def __str__(self) -> str:
        return self.value.replace("_", " ").title()


@dataclass(frozen=True, slots=True)
class VehiclePosition:
    """Represents a vehicle's two-dimensional position."""

    x: float
    y: float

    def __post_init__(self) -> None:
        if not isinstance(self.x, (int, float)):
            raise TypeError("x must be a numeric value")

        if not isinstance(self.y, (int, float)):
            raise TypeError("y must be a numeric value")


@dataclass(frozen=True, slots=True)
class TrackSection:
    """Identifies a named section of a racetrack."""

    section_id: str
    name: str

    def __post_init__(self) -> None:
        if not self.section_id.strip():
            raise ValueError("section_id cannot be empty")

        if not self.name.strip():
            raise ValueError("name cannot be empty")


@dataclass(frozen=True, slots=True)
class RaceContext:
    """Race conditions present when a driver decision is recorded."""

    traffic_state: TrafficState
    race_phase: RacePhase
    car_ahead_number: int | None = None
    car_ahead_relationship: DriverRelationship = DriverRelationship.NONE
    gap_seconds: float | None = None
    closing_rate_mph: float | None = None
    tire_age_laps: int = 0

    def __post_init__(self) -> None:
        if self.car_ahead_number is not None and self.car_ahead_number < 0:
            raise ValueError("car_ahead_number cannot be negative")

        if self.gap_seconds is not None and self.gap_seconds < 0:
            raise ValueError("gap_seconds cannot be negative")

        if self.tire_age_laps < 0:
            raise ValueError("tire_age_laps cannot be negative")

        if (
            self.car_ahead_relationship is not DriverRelationship.NONE
            and self.car_ahead_number is None
        ):
            raise ValueError(
                "car_ahead_number is required when a relationship is set"
            )

        if (
            self.traffic_state is TrafficState.CLEAR_TRACK
            and self.car_ahead_number is not None
        ):
            raise ValueError(
                "clear track context cannot include a car ahead"
            )


@dataclass(frozen=True, slots=True)
class DriverDecision:
    """A racing-line decision recorded at a specific track section."""

    lap_number: int
    section: TrackSection
    racing_line: RacingLine
    position: VehiclePosition
    timestamp_seconds: float
    context: RaceContext | None = None

    def __post_init__(self) -> None:
        if self.lap_number < 1:
            raise ValueError("lap_number must be at least 1")

        if self.timestamp_seconds < 0:
            raise ValueError("timestamp_seconds cannot be negative")
