from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.parse import urlencode
from datetime import datetime, timedelta
from pathlib import Path

import json
import ssl
import time
import certifi
import numpy as np

# --------------------------------------------------
# Configuration
# --------------------------------------------------

BASE_URL = "https://api.openf1.org/v1"

# Already verified for Monza 2024 Race
SESSION_KEY = 9590
DRIVER_NUMBER = 44

# Already verified Hamilton fastest lap
LAP_NUMBER = 53
LAP_START = "2024-09-01T14:17:16.860000"
LAP_DURATION = 81.512

# Local cache so we do not repeatedly call OpenF1
CACHE_DIR = Path("data/openf1_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Updated SSL certificate bundle
SSL_CONTEXT = ssl.create_default_context(
    cafile=certifi.where()
)


# --------------------------------------------------
# OpenF1 request helper
# --------------------------------------------------

def fetch_openf1(endpoint, params, filters, cache_filename):

    cache_path = CACHE_DIR / cache_filename

    # If we already downloaded the data, use the local file
    if cache_path.exists():

        print(f"Loading cached data: {cache_filename}")

        with open(cache_path, "r", encoding="utf-8") as file:
            return json.load(file)

    query = urlencode(params)

    if filters:
        query += "&" + "&".join(filters)

    url = f"{BASE_URL}/{endpoint}?{query}"

    print(f"Downloading {endpoint} data...")

    # Maximum two attempts so we do not endlessly hit the API
    for attempt in range(2):

        try:

            with urlopen(
                url,
                context=SSL_CONTEXT
            ) as response:

                data = json.loads(
                    response.read().decode("utf-8")
                )

            # Save locally immediately
            with open(
                cache_path,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    data,
                    file,
                    indent=2
                )

            return data

        except HTTPError as error:

            if error.code == 429:

                retry_after = error.headers.get(
                    "Retry-After"
                )

                try:
                    wait_seconds = int(retry_after)
                except (TypeError, ValueError):
                    wait_seconds = 15

                if attempt == 0:

                    print(
                        "OpenF1 rate limit reached. "
                        f"Retrying once after {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)

                else:

                    raise RuntimeError(
                        "OpenF1 is still rate-limiting the request."
                    ) from error

            else:
                raise


# --------------------------------------------------
# Fastest lap time window
# --------------------------------------------------

lap_start = datetime.fromisoformat(
    LAP_START
)

lap_end = lap_start + timedelta(
    seconds=LAP_DURATION
)

# OpenF1 examples use ISO timestamps without
# the +00:00 timezone suffix in comparison filters
lap_start_str = lap_start.isoformat(
    timespec="milliseconds"
)

lap_end_str = lap_end.isoformat(
    timespec="milliseconds"
)


print("\nHamilton fastest lap:")
print("Lap number:", LAP_NUMBER)
print("Lap duration:", LAP_DURATION)

minutes = int(LAP_DURATION // 60)
seconds = LAP_DURATION % 60

print(
    f"Fastest lap time: "
    f"{minutes}:{seconds:06.3f}"
)

print("\nFastest lap time window:")
print("Start:", lap_start_str)
print("End:", lap_end_str)


# --------------------------------------------------
# Car telemetry
# --------------------------------------------------

car_data = fetch_openf1(
    endpoint="car_data",

    params={
        "session_key": SESSION_KEY,
        "driver_number": DRIVER_NUMBER
    },

    filters=[
        f"date>{lap_start_str}",
        f"date<{lap_end_str}"
    ],

    cache_filename="hamilton_monza_2024_fastest_lap_car_data.json"
)


print("\nCar telemetry:")
print("Number of samples:", len(car_data))

if car_data:

    print("\nFirst car-data sample:")
    print(car_data[0])

    print("\nLast car-data sample:")
    print(car_data[-1])


# Small pause before the second API request
# only relevant on the first execution
time.sleep(1)


# --------------------------------------------------
# Position data
# --------------------------------------------------

location_data = fetch_openf1(
    endpoint="location",

    params={
        "session_key": SESSION_KEY,
        "driver_number": DRIVER_NUMBER
    },

    filters=[
        f"date>{lap_start_str}",
        f"date<{lap_end_str}"
    ],

    cache_filename="hamilton_monza_2024_fastest_lap_location.json"
)


print("\nPosition data:")
print("Number of samples:", len(location_data))

if location_data:

    print("\nFirst location sample:")
    print(location_data[0])

    print("\nLast location sample:")
    print(location_data[-1])


print("\nOpenF1 fastest-lap data loaded successfully.")




# --------------------------------------------------
# Reconstruct distance from X/Y position data
# --------------------------------------------------

x = np.array([
    sample["x"]
    for sample in location_data
], dtype=float)

y = np.array([
    sample["y"]
    for sample in location_data
], dtype=float)


dx = np.diff(x)
dy = np.diff(y)


segment_distance = np.sqrt(
    dx**2 + dy**2
)


distance_raw = np.insert(
    np.cumsum(segment_distance),
    0,
    0.0
)


distance = distance_raw / 10.0

print("\nReconstructed distance in metres:")
print("First values:", distance[:5])
print("Final distance:", distance[-1], "m")


print("\nReconstructed raw distance:")
print("First values:", distance_raw[:5])
print("Final value:", distance_raw[-1])









# --------------------------------------------------
# Synchronize position data with car telemetry
# --------------------------------------------------

# Use the first position timestamp as common time reference
reference_time = datetime.fromisoformat(
    location_data[0]["date"]
)

location_times = np.array([
    (
        datetime.fromisoformat(sample["date"])
        - reference_time
    ).total_seconds()
    for sample in location_data
])


car_times = np.array([
    (
        datetime.fromisoformat(sample["date"])
        - reference_time
    ).total_seconds()
    for sample in car_data
])


# Interpolate geometry data at car telemetry timestamps

distance_sync = np.interp(
    car_times,
    location_times,
    distance
)

x_sync = np.interp(
    car_times,
    location_times,
    x
)

y_sync = np.interp(
    car_times,
    location_times,
    y
)


# Extract car telemetry channels

speed = np.array([
    sample["speed"]
    for sample in car_data
], dtype=float)

throttle = np.array([
    sample["throttle"]
    for sample in car_data
], dtype=float)

brake = np.array([
    sample["brake"]
    for sample in car_data
], dtype=float)


print("\nSynchronized telemetry:")
print("Distance samples:", len(distance_sync))
print("Speed samples:", len(speed))
print("X samples:", len(x_sync))
print("Y samples:", len(y_sync))

print("Final synchronized distance:", distance_sync[-1], "m")