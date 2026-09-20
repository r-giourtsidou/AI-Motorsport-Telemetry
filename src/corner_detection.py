import fastf1
import matplotlib.pyplot as plt
import numpy as np

from scipy.signal import find_peaks

YEAR = 2024
EVENT = "Monza"
SESSION_TYPE = "R"
DRIVER = "HAM"

# Load session 
session = fastf1.get_session(YEAR, EVENT, SESSION_TYPE)
session.load()
print("Session loaded succesfully.")

# Get telemetry
driver_laps = session.laps.pick_drivers(DRIVER)
fastest_lap = driver_laps.pick_fastest()
telemetry = fastest_lap.get_telemetry()
print(f"\n{DRIVER} fastest lap:")
print(fastest_lap["LapTime"])
print(telemetry[["X", "Y", "Speed"]].head())

distance = telemetry["Distance"].to_numpy()
speed = telemetry["Speed"].to_numpy()
corner_indices, _ = find_peaks(-speed, prominence = 20)



print("Detected corner candidates")
print(corner_indices)
print("Number of candidates:", len(corner_indices))


# Figure 1
plt.figure(figsize=(12, 5))

plt.plot(distance,
         speed,
         label = "Speed")


plt.scatter(distance[corner_indices],
            speed[corner_indices],
            label = "Corner candidates")


plt.xlabel("Distance (m)")
plt.ylabel("Speed (km/h)")
plt.title("Corner Detection - Speed Minima")
plt.grid(True)
plt.legend()

plt.show()



x = telemetry["X"].to_numpy()
y = telemetry["Y"].to_numpy()


# Figure 2
plt.figure(figsize = (10, 8))

plt.plot(x, y)

plt.scatter(
            x[corner_indices],
            y[corner_indices],
            label = "Corner candidates")


plt.title("Detected Corner Candidates - Monza")
plt.axis("equal")
plt.grid(True)
plt.legend()

plt.show()



# Track geometry


dx = np.diff(x)
dy = np.diff(y)

heading = np.arctan2(dy, dx)
heading = np.unwrap(heading)

heading_change = np.diff(heading)

# Smooth heading change
window_size = 7
kernel = np.ones(window_size) / window_size


smoothed_heading_change = np.convolve(
    heading_change,
    kernel,
    mode = "same")


# Distance array corresponding to heading_change
distance_geometry = distance[2:]

# Turning intensity
turning_intensity = np.abs(smoothed_heading_change)


# Detect geometry-based corner candidates
geometry_indices, _ = find_peaks(
    turning_intensity,
    prominence=0.02)


# Convert candidate indices to lap distances 
geometry_distances = distance_geometry[geometry_indices]

print("\nDetected geometry candidates")
print(geometry_indices)
print("Number of geometry candidates:", len(geometry_indices))


for idx in geometry_indices:
    print(
        f"Distance: {distance_geometry[idx]:.0f} m | "
        f"Turning intensity: {turning_intensity[idx]:.3f}"
    )

# Distance between consecutive geometry candidates
candidate_gaps = np.diff(geometry_distances)

print("\nDistance between consecutive geometry candidates:")

for i, gap in enumerate(candidate_gaps):
    print(f"{geometry_distances[i]:.0f} m -> "
          f"{geometry_distances[i + 1]:.0f} m | "
          f"Gap: {gap:.0f} m")

# Group nearby geometry peaks into turning regions
# 150 m chosen from the observed separation between candidate gaps
grouping_threshold = 150

geometry_groups = []
current_group = [geometry_distances[0]]

for i in range(1, len(geometry_distances)):

    gap = geometry_distances[i] - geometry_distances[i - 1]

    if gap <= grouping_threshold:
        current_group.append(geometry_distances[i])

    else:
        geometry_groups.append(current_group)
        current_group = [geometry_distances[i]]


# Add the final group
geometry_groups.append(current_group)

print("\nGeometry groups:")

for group in geometry_groups:
    print([round(value) for value in group])



# Representative distance for each geometry group
group_centers = []

for group in geometry_groups:
    center = np.mean(group)
    group_centers.append(center)

group_center_indices = []

for center in group_centers:
    idx = np.argmin(np.abs(distance_geometry - center))
    group_center_indices.append(idx)


# Geometry coordinates corresponding to heading_change
x_geometry = x[2:]
y_geometry = y[2:]






# Figure Heading Change vs Distance
plt.figure(figsize=(12, 5))
plt.plot(distance_geometry, heading_change)
plt.xlabel("Distance (m)")
plt.ylabel("Heading change (rad)")
plt.title("Track Geometry - Heading Change vs Distance")
plt.grid(True)

plt.plot(distance_geometry,
         smoothed_heading_change,
         label = "Smoothed heading change")

plt.legend()

plt.show()




# Figure Turning Intensity vs Distance
plt.figure(figsize=(12, 5))

plt.plot(distance_geometry,
         turning_intensity)


plt.xlabel("Distance (m)")
plt.ylabel("Turning Intensity (rad)")
plt.title("Track Geometry - Turning Intensity vs Distance")
plt.grid(True)

plt.show()


# Figure Geometry - Based Corner Candidates
plt.figure(figsize=(12, 5))

plt.plot(distance_geometry,
         turning_intensity,
         label="Turning intensity")

plt.scatter(distance_geometry[geometry_indices],
            turning_intensity[geometry_indices],
            marker="x",
            s=70,
            label="Geometry candidates")

plt.xlabel("Distance (m)")
plt.ylabel("Turning intensity (rad)")
plt.title("Geometry - Based Corner Candidates")
plt.grid(True)
plt.legend()

plt.show()


# Figure Geometry - Based Corner Candidates on Track
plt.figure(figsize=(8, 8))

plt.plot(x, y)

plt.scatter(x_geometry[geometry_indices],
            y_geometry[geometry_indices],
            marker="x",
            s=80,
            label="Geometry candidates")

plt.axis("equal")
plt.title("Geometry - Based Corner Candidates on Track")
plt.legend()
plt.grid(True)

plt.show()


# Figure Grouped Geometry Regions on Track
plt.figure(figsize=(8, 8 ))

plt.plot(x, y)

plt.scatter(
    x_geometry[group_center_indices],
    y_geometry[group_center_indices],
    marker = "o",
    s=100,
    label="Geometry groups")

plt.axis("equal")
plt.title("Grouped Geometry Regions on Track")
plt.legend()
plt.grid(True)

plt.show()