"""Interactive Pygame simulation for driver decision profiling."""

from dataclasses import dataclass

import pygame

from driver_decision_profiler.analytics import build_driver_profile
from driver_decision_profiler.models import (
    RacingLine,
    TrackSection,
    VehiclePosition,
)
from driver_decision_profiler.recorder import DecisionRecorder
from driver_decision_profiler.track import RectangularZone, Track


WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 650
FPS = 60

CAR_WIDTH = 42
CAR_HEIGHT = 24
CAR_SPEED = 260.0


@dataclass(slots=True)
class Vehicle:
    """Mutable vehicle state used by the interactive simulation."""

    x: float
    y: float
    speed: float = CAR_SPEED

    @property
    def position(self) -> VehiclePosition:
        """Return the current center position of the vehicle."""
        return VehiclePosition(
            x=self.x + CAR_WIDTH / 2,
            y=self.y + CAR_HEIGHT / 2,
        )

    @property
    def rectangle(self) -> pygame.Rect:
        """Return the vehicle's screen rectangle."""
        return pygame.Rect(
            round(self.x),
            round(self.y),
            CAR_WIDTH,
            CAR_HEIGHT,
        )

    def update(self, delta_seconds: float, keys: pygame.key.ScancodeWrapper) -> None:
        """Move the vehicle using the keyboard."""
        horizontal_direction = 0
        vertical_direction = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            horizontal_direction -= 1

        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            horizontal_direction += 1

        if keys[pygame.K_UP] or keys[pygame.K_w]:
            vertical_direction -= 1

        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            vertical_direction += 1

        movement = pygame.Vector2(
            horizontal_direction,
            vertical_direction,
        )

        if movement.length_squared() > 0:
            movement = movement.normalize()

        self.x += movement.x * self.speed * delta_seconds
        self.y += movement.y * self.speed * delta_seconds

        self.x = max(
            0,
            min(self.x, WINDOW_WIDTH - CAR_WIDTH),
        )
        self.y = max(
            0,
            min(self.y, WINDOW_HEIGHT - CAR_HEIGHT),
        )


def build_simulation_track() -> tuple[Track, TrackSection]:
    """Create one visible decision section with three racing-line zones."""
    section = TrackSection(
        section_id="turn_1_entry",
        name="Turn 1 Entry",
    )

    zones = (
        RectangularZone(
            section=section,
            racing_line=RacingLine.HIGH,
            left=300,
            top=130,
            width=360,
            height=90,
        ),
        RectangularZone(
            section=section,
            racing_line=RacingLine.MIDDLE,
            left=300,
            top=220,
            width=360,
            height=90,
        ),
        RectangularZone(
            section=section,
            racing_line=RacingLine.LOW,
            left=300,
            top=310,
            width=360,
            height=90,
        ),
    )

    return Track(name="Interactive Demo Oval", zones=zones), section


def draw_zone(
    screen: pygame.Surface,
    font: pygame.font.Font,
    zone: RectangularZone,
) -> None:
    """Draw one racing-line decision zone."""
    zone_rectangle = pygame.Rect(
        round(zone.left),
        round(zone.top),
        round(zone.width),
        round(zone.height),
    )

    pygame.draw.rect(
        screen,
        pygame.Color("gray25"),
        zone_rectangle,
        border_radius=6,
    )
    pygame.draw.rect(
        screen,
        pygame.Color("gray70"),
        zone_rectangle,
        width=2,
        border_radius=6,
    )

    label = font.render(
        f"{zone.racing_line} line",
        True,
        pygame.Color("white"),
    )

    screen.blit(
        label,
        (
            zone_rectangle.left + 14,
            zone_rectangle.centery - label.get_height() // 2,
        ),
    )


def draw_track(
    screen: pygame.Surface,
    font: pygame.font.Font,
    track: Track,
) -> None:
    """Draw the track area and decision zones."""
    pygame.draw.rect(
        screen,
        pygame.Color("darkgreen"),
        pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
    )

    track_surface = pygame.Rect(220, 80, 520, 390)

    pygame.draw.rect(
        screen,
        pygame.Color("gray15"),
        track_surface,
        border_radius=24,
    )
    pygame.draw.rect(
        screen,
        pygame.Color("white"),
        track_surface,
        width=3,
        border_radius=24,
    )

    for zone in track.zones:
        draw_zone(screen, font, zone)


def draw_vehicle(screen: pygame.Surface, vehicle: Vehicle) -> None:
    """Draw the simulated race car."""
    rectangle = vehicle.rectangle

    pygame.draw.rect(
        screen,
        pygame.Color("red"),
        rectangle,
        border_radius=5,
    )
    pygame.draw.rect(
        screen,
        pygame.Color("white"),
        rectangle,
        width=2,
        border_radius=5,
    )

    pygame.draw.rect(
        screen,
        pygame.Color("black"),
        pygame.Rect(
            rectangle.centerx - 5,
            rectangle.top + 5,
            10,
            rectangle.height - 10,
        ),
    )


def draw_profile(
    screen: pygame.Surface,
    title_font: pygame.font.Font,
    body_font: pygame.font.Font,
    recorder: DecisionRecorder,
    current_line: RacingLine | None,
) -> None:
    """Draw the live driver profile and session information."""
    panel = pygame.Rect(760, 80, 220, 390)

    pygame.draw.rect(
        screen,
        pygame.Color("gray10"),
        panel,
        border_radius=12,
    )
    pygame.draw.rect(
        screen,
        pygame.Color("gray65"),
        panel,
        width=2,
        border_radius=12,
    )

    title = title_font.render(
        "Driver Profile",
        True,
        pygame.Color("white"),
    )
    screen.blit(title, (panel.left + 18, panel.top + 18))

    profile = build_driver_profile(recorder.decisions)

    current_text = (
        str(current_line)
        if current_line is not None
        else "Outside zone"
    )

    lines = [
        f"Current: {current_text}",
        f"Decisions: {profile.total_decisions}",
        "",
    ]

    for preference in profile.preferences:
        lines.append(
            f"{str(preference.racing_line):<6} "
            f"{preference.decision_count:>2}  "
            f"{preference.percentage:>5.1f}%"
        )

    lines.extend(
        [
            "",
            "Controls:",
            "Arrow keys / WASD",
            "",
            "R: Reset profile",
            "Esc: Quit",
        ]
    )

    y_position = panel.top + 70

    for line in lines:
        rendered_line = body_font.render(
            line,
            True,
            pygame.Color("white"),
        )
        screen.blit(
            rendered_line,
            (panel.left + 18, y_position),
        )
        y_position += 28


def run_simulation() -> None:
    """Run the interactive driver decision simulation."""
    pygame.init()

    screen = pygame.display.set_mode(
        (WINDOW_WIDTH, WINDOW_HEIGHT)
    )
    pygame.display.set_caption("Driver Decision Profiler")

    clock = pygame.time.Clock()
    title_font = pygame.font.Font(None, 34)
    body_font = pygame.font.Font(None, 25)

    track, section = build_simulation_track()
    recorder = DecisionRecorder(track=track)

    vehicle = Vehicle(
        x=90.0,
        y=250.0,
    )

    lap_number = 1
    running = True
    session_start_seconds = pygame.time.get_ticks() / 1000.0

    while running:
        delta_seconds = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_r:
                    recorder.reset()
                    lap_number = 1
                    vehicle.x = 90.0
                    vehicle.y = 250.0
                    session_start_seconds = (
                        pygame.time.get_ticks() / 1000.0
                    )

        keys = pygame.key.get_pressed()
        vehicle.update(delta_seconds, keys)

        elapsed_seconds = (
            pygame.time.get_ticks() / 1000.0
            - session_start_seconds
        )

        current_line = track.classify_position(
            position=vehicle.position,
            section_id=section.section_id,
        )

        decision = recorder.update(
            lap_number=lap_number,
            section=section,
            position=vehicle.position,
            timestamp_seconds=elapsed_seconds,
        )

        if decision is not None:
            lap_number += 1
            print(
                f"Recorded lap {decision.lap_number}: "
                f"{decision.racing_line} line at "
                f"{decision.timestamp_seconds:.2f} seconds"
            )

        draw_track(screen, body_font, track)
        draw_vehicle(screen, vehicle)
        draw_profile(
            screen,
            title_font,
            body_font,
            recorder,
            current_line,
        )

        instruction = body_font.render(
            "Enter a zone, leave it completely, then enter again "
            "to record another decision.",
            True,
            pygame.Color("white"),
        )
        screen.blit(instruction, (30, 570))

        pygame.display.flip()

    pygame.quit()


def main() -> None:
    """Application entry point."""
    run_simulation()


if __name__ == "__main__":
    main()
