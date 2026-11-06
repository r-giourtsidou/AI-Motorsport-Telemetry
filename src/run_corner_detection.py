
import fastf1
from corner_detection_core import detect_turning_regions

# Session configuration
YEAR = 2024
EVENT = "Monza"
SESSION_TYPE = "R"
DRIVER = "HAM"

# Load telemetry
session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
session.load()

fastest_lap = session.laps.pick_drivers(DRIVER).pick_fastest()
telemetry = fastest_lap.get_telemetry()

# Run geometry-based corner detection
result = detect_turning_regions(telemetry)
regions = result["regions"]

# Display results
print(f"\n=== {EVENT.upper()} {YEAR} | {DRIVER} ===")
print(f"Fastest lap: {fastest_lap['LapTime']}")
print(f"Detected turning regions: {len(regions)}\n")

print(f"{'Region':<10}{'Start (m)':>12}{'Anchor (m)':>14}{'End (m)':>12}")
print("-" * 48)

for i, region in enumerate(regions, start=1):
    print(
        f"{i:<10}"
        f"{region['start']:>12.0f}"
        f"{region['anchor']:>14.0f}"
        f"{region['end']:>12.0f}"
    )

print("\nNote: Boundaries and anchors are geometry-based estimates.")
