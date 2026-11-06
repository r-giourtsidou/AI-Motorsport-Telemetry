"""Geometry-based turning-region detection for FastF1 lap telemetry.

This is a refactor of the existing Monza prototype, preserving its smoothing,
peak grouping, accumulated-heading filter, anchor selection and boundary logic.
It deliberately contains no API requests or plots.
"""

import numpy as np
from scipy.signal import find_peaks


def detect_turning_regions(
    telemetry,
    smoothing_window=7,
    peak_prominence=0.02,
    grouping_threshold=150,
    accumulation_half_window=100,
    turning_threshold=0.4,
    boundary_threshold=0.01):

    """Return turning-region boundaries plus geometry signals for plotting.

    Each region is a dict with start, center, anchor and end (lap distance, m).
    These are approximate turning-region estimates, not racing-line apexes.
    """
    distance = telemetry["Distance"].to_numpy(dtype=float)
    speed = telemetry["Speed"].to_numpy(dtype=float)
    x = telemetry["X"].to_numpy(dtype=float)
    y = telemetry["Y"].to_numpy(dtype=float)

    if len(distance) < 3:
        raise ValueError("At least three position samples are required.")
    if not np.all(np.diff(distance) >= 0):
        raise ValueError("Telemetry samples must be ordered by lap distance.")

    dx = np.diff(x)
    dy = np.diff(y)
    heading = np.unwrap(np.arctan2(dy, dx))
    heading_change = np.diff(heading)
    kernel = np.ones(smoothing_window) / smoothing_window
    smoothed_heading_change = np.convolve(heading_change, kernel, mode="same")
    distance_geometry = distance[2:]
    turning_intensity = np.abs(smoothed_heading_change)

    geometry_indices, _ = find_peaks(turning_intensity, prominence=peak_prominence)
    geometry_distances = distance_geometry[geometry_indices]

    # Group adjacent candidate peaks into broad turning regions.
    geometry_groups = []

    if len(geometry_distances):
        current_group = [geometry_distances[0]]

        for candidate_distance in geometry_distances[1:]:
            
            if candidate_distance - current_group[-1] <= grouping_threshold:
                current_group.append(candidate_distance)
            else:
                geometry_groups.append(current_group)
                current_group = [candidate_distance]
        geometry_groups.append(current_group)

    # Preserve group/center pairing while filtering by accumulated turning.
    regions = []
    for group in geometry_groups:
        center = float(np.mean(group))
        mask = ((distance_geometry >= center - accumulation_half_window)
            & (distance_geometry <= center + accumulation_half_window))
        
        total_heading_change = float(np.sum(turning_intensity[mask]))
        if total_heading_change < turning_threshold:
            continue

        candidate_indices = [int(np.argmin(np.abs(distance_geometry - candidate_distance)))
            for candidate_distance in group]
        strongest_position = int(np.argmax(turning_intensity[candidate_indices]))
        anchor = float(group[strongest_position])

        # Start from first/last grouped peaks so a chicane is not cut at
        # its strongest peak. Search outward to the threshold crossings.
        start_idx = candidate_indices[0]
        end_idx = candidate_indices[-1]

        while start_idx > 0 and turning_intensity[start_idx - 1] >= boundary_threshold:
            start_idx -= 1

        while (end_idx < len(turning_intensity) - 1
            and turning_intensity[end_idx + 1] >= boundary_threshold):
            end_idx += 1

        regions.append(
            {
                "start": float(distance_geometry[start_idx]),
                "center": center,
                "anchor": anchor,
                "end": float(distance_geometry[end_idx]),
                "total_heading_change": total_heading_change,
                "peaks": [float(value) for value in group]})

    return {
        "regions": regions,
        "distance": distance,
        "speed": speed,
        "x": x,
        "y": y,
        "distance_geometry": distance_geometry,
        "x_geometry": x[2:],
        "y_geometry": y[2:],
        "heading_change": heading_change,
        "smoothed_heading_change": smoothed_heading_change,
        "turning_intensity": turning_intensity,
        "geometry_distances": geometry_distances,
        "geometry_groups": geometry_groups,
        "boundary_threshold": boundary_threshold}
