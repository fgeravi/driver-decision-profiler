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
        """Return a readable label for display and exported reports."""
        return self.value.title()


@dataclass(frozen=True, slots=True)
class VehiclePosition:
    """Represents a vehicle's two-dimensional position at a point in time."""

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
class DriverDecision:
    """A racing-line decision recorded at a specific track section."""

    lap_number: int
    section: TrackSection
    racing_line: RacingLine
    position: VehiclePosition
    timestamp_seconds: float

    def __post_init__(self) -> None:
        if self.lap_number < 1:
            raise ValueError("lap_number must be at least 1")

        if self.timestamp_seconds < 0:
            raise ValueError("timestamp_seconds cannot be negative")
