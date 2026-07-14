# Driver Decision Profiler

A Python-based motorsport simulation and analytics project that records how a driver selects different racing lines through defined track sections.

The system will classify vehicle position into high, middle, and low racing-line zones, record each decision, and generate a driver profile from the collected session data.

## Planned Features

- Interactive vehicle movement using Pygame
- Configurable high, middle, and low racing-line zones
- Detection of driver decisions at defined track sections
- Session data export to CSV or JSON
- Driver tendency and lane-preference summaries
- Charts and track-position heat maps
- Automated tests for zone classification and event recording

## Project Structure

```text
driver-decision-profiler/
├── data/                           Local input data
├── outputs/                        Generated reports and visualizations
├── src/
│   └── driver_decision_profiler/   Application source code
├── tests/                          Automated tests
├── README.md
└── requirements.txt
