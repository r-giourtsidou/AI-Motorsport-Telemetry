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




# Check vehicle speed at each geometry group center

print("\nGeometry group centers and speeds:")

for center in group_centers:
    idx = np.argmin(np.abs(distance - center))


    print(f"Distance: {center:.0f} m | "
          f"Speed: {speed[idx]:.1f} km/h")


# Check net heading change around each geometry group center

window_distance = 100

print("\nNet heading change around geometry groups:")

for center in group_centers:

    mask = (
        (distance_geometry >= center - window_distance) 
        & (distance_geometry <= center + window_distance))

    net_heading_change = np.sum(smoothed_heading_change[mask])

    print(f"Distance: {center:.0f} m | "
          f"Net heading change: {net_heading_change:.3f} rad")
    




print("\nTotal heading change around geometry groups:")

total_heading_changes = []

print("\nTotal heading change around geometry groups:")

total_heading_changes = []

for center in group_centers:

    mask = (
        (distance_geometry >= center - window_distance)
        & (distance_geometry <= center + window_distance)
    )

    total_heading_change = np.sum(
        np.abs(smoothed_heading_change[mask])
    )

    total_heading_changes.append(total_heading_change)

    print(
        f"Distance: {center:.0f} m | "
        f"Total heading change: {total_heading_change:.3f} rad"
    )


turning_threshold = 0.4

filtered_group_centers = []
filtered_geometry_groups = []

for group, center, total_change in zip(
    geometry_groups,
    group_centers,
    total_heading_changes
):

    if total_change >= turning_threshold:
        filtered_group_centers.append(center)
        filtered_geometry_groups.append(group)


print("\nFiltered geometry groups:")

for center in filtered_group_centers:
    print(f"{center:.0f} m")

filtered_group_indices = []

for center in filtered_group_centers:

    idx = np.argmin(
        np.abs(distance_geometry - center)
    )

    filtered_group_indices.append(idx)






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




# Figure Filtered Geometry Regions on Track

plt.figure(figsize=(8, 8))

plt.plot(x, y)

plt.scatter(
    x_geometry[filtered_group_indices],
    y_geometry[filtered_group_indices],
    marker = "o",
    s = 100,
    label = "Filtered geometry groups"
)

plt.axis("equal")
plt.title("Filtered Geometry Regions on Track")
plt.legend()
plt.grid(True)

plt.show()


plt.plot(distance_geometry,
         turning_intensity,
         label="Turning intensity")

plt.scatter(distance_geometry[filtered_group_indices],
            turning_intensity[filtered_group_indices],
            marker="o",
            s=80,
            label="Filtered geometry centers")

plt.xlabel("Distance (m)")
plt.ylabel("Turning intensity (rad)")
plt.title("Filtered Geometry Centers vs Turning Intensity")
plt.grid(True)
plt.legend()

plt.show()







# Find the strongest geometry peak (anchor) inside each filtered region

filtered_region_anchors = []

for group in filtered_geometry_groups:

    candidate_indices = [
        np.argmin(np.abs(distance_geometry - d))
        for d in group
    ]

    


    strongest_position = np.argmax(
        turning_intensity[candidate_indices]
    )

    anchor_distance = group[strongest_position]

    filtered_region_anchors.append(anchor_distance)


print("\nFiltered region geometry anchors:")

for center, anchor in zip(
    filtered_group_centers,
    filtered_region_anchors
):
    print(
        f"Old center: {center:.0f} m | "
        f"Geometry anchor: {anchor:.0f} m"
    )







# Estimate start/end boundaries for each turning region

boundary_threshold = 0.01

region_boundaries = []

for group, anchor in zip(filtered_geometry_groups, filtered_region_anchors):

        first_idx = np.argmin(np.abs(distance_geometry - min(group)))

        last_idx = np.argmin(np.abs(distance_geometry - max(group)))


        # Search backwards for region start
        start_idx = first_idx

        while (start_idx > 0 and turning_intensity[start_idx - 1] >= boundary_threshold):

                 start_idx -= 1

        # Search forwards for region end 
        end_idx = last_idx

        while (end_idx < len(turning_intensity) - 1 and turning_intensity[end_idx + 1] >= boundary_threshold):

                 end_idx += 1

            
        region_boundaries.append((distance_geometry[start_idx],
                                      anchor,
                                      distance_geometry[end_idx]))


print("\nEstimated turning-region boundaries:")

for start, anchor, end in region_boundaries:

    print(f"Start: {start:.0f} m | "
          f"Anchor: {anchor:.0f} m | "
          f"End: {end:.0f} m" )





# Visualize detected turning-region boundaries

plt.figure(figsize=(12, 5))

plt.plot(distance_geometry,
         turning_intensity,
         label ="Turning intensity")

for start, anchor, end in region_boundaries:

    plt.axvspan(start,
                end,
                alpha=0.2)

    plt.axvline(anchor,
                linestyle="--",
                alpha=0.5)

plt.axhline(boundary_threshold,
            color="red",
            linestyle=":",
            label="Boundary threshold")


plt.xlabel("Distance (m)")
plt.ylabel("Turning intensity (rad)")
plt.title("Detected Turning Regions - Boundary Validation")
plt.grid(True)
plt.legend()

plt.show()




# Visualize turning - region boundaries on the track 

plt.figure(figsize=(9, 9))

plt.plot(x, y, color="lightgray", linewidth=2, label="Track")

for i, (start, anchor, end) in enumerate(region_boundaries, start=1):
    mask = ((distance_geometry >= start) & (distance_geometry <= end))

    plt.plot(x_geometry[mask],
             y_geometry[mask],
             linewidth=4,
             label=f"Region {i}")

plt.axis("equal")
plt.title("Detected Turning Regions - Monza")
plt.legend()
plt.grid(True)

plt.show()





# Speed profile with detected turning regions

plt.figure(figsize=(12, 5))

plt.plot(distance,
        speed,
        label="Vehicle speed")

for start, anchor, end in region_boundaries:

    plt.axvspan(start, end, alpha=0.2)

    plt.axvline(anchor, linestyle="--", alpha=0.5)


plt.xlabel("Distance (m)")
plt.ylabel("Speed (km/h)")
plt.title("Speed Profile with Detected Turning Regions")
plt.legend()
plt.grid(True)

plt.show()




     

    





