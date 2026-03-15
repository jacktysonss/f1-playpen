#!/usr/bin/env python3
"""Generate sample ghost car data for testing without network access.

Creates a realistic-looking oval/circuit track with synthetic telemetry
for two drivers with slightly different lap times.
"""

import json
import math
import os
import random

random.seed(42)

NUM_POINTS = 500


def generate_track():
    """Generate a realistic F1-style track outline with straights and corners."""
    points_x = []
    points_y = []

    # Define a track shape using control segments
    # Bahrain-inspired: long straight, tight corners, flowing middle sector
    segments = [
        # (type, params)
        ("straight", {"length": 800, "angle": 0}),
        ("corner", {"radius": 120, "sweep": 90, "direction": 1}),
        ("straight", {"length": 200, "angle": 90}),
        ("corner", {"radius": 80, "sweep": 60, "direction": 1}),
        ("straight", {"length": 300, "angle": 150}),
        ("corner", {"radius": 100, "sweep": 90, "direction": -1}),
        ("straight", {"length": 250, "angle": 60}),
        ("corner", {"radius": 60, "sweep": 120, "direction": 1}),
        ("corner", {"radius": 150, "sweep": 60, "direction": -1}),
        ("straight", {"length": 400, "angle": 120}),
        ("corner", {"radius": 90, "sweep": 100, "direction": 1}),
        ("straight", {"length": 300, "angle": 220}),
        ("corner", {"radius": 70, "sweep": 80, "direction": 1}),
    ]

    x, y = 0.0, 0.0
    angle = 0.0  # degrees

    for seg_type, params in segments:
        if seg_type == "straight":
            length = params["length"]
            steps = max(5, int(length / 15))
            rad = math.radians(angle)
            for i in range(steps):
                x += (length / steps) * math.cos(rad)
                y += (length / steps) * math.sin(rad)
                points_x.append(round(x, 1))
                points_y.append(round(y, 1))
        else:
            radius = params["radius"]
            sweep = params["sweep"]
            direction = params["direction"]
            steps = max(8, int(sweep / 3))
            for i in range(steps):
                angle += (sweep / steps) * direction
                rad = math.radians(angle)
                x += (2 * math.pi * radius * (sweep / steps) / 360) * math.cos(rad)
                y += (2 * math.pi * radius * (sweep / steps) / 360) * math.sin(rad)
                points_x.append(round(x, 1))
                points_y.append(round(y, 1))

    # Close the track back to start with a sweeping return
    # Add points closing back to (0, 0)
    close_steps = 40
    start_x, start_y = points_x[0], points_y[0]
    end_x, end_y = points_x[-1], points_y[-1]
    for i in range(1, close_steps + 1):
        t = i / close_steps
        # Cubic ease for smooth closing
        t_smooth = t * t * (3 - 2 * t)
        cx = end_x + (start_x - end_x) * t_smooth
        cy = end_y + (start_y - end_y) * t_smooth
        # Add slight curve
        cx += math.sin(t * math.pi) * 200
        cy += math.sin(t * math.pi) * -100
        points_x.append(round(cx, 1))
        points_y.append(round(cy, 1))

    return points_x, points_y


def generate_corners(track_x, track_y):
    """Place corner markers at high-curvature points."""
    corners = []
    n = len(track_x)
    corner_num = 1

    for i in range(2, n - 2, max(1, n // 40)):
        # Approximate curvature
        dx1 = track_x[i] - track_x[i - 2]
        dy1 = track_y[i] - track_y[i - 2]
        dx2 = track_x[i + 2] - track_x[i]
        dy2 = track_y[i + 2] - track_y[i]
        cross = abs(dx1 * dy2 - dy1 * dx2)

        if cross > 800:
            # Offset label slightly from track
            corners.append({
                "number": corner_num,
                "letter": "",
                "x": round(track_x[i] + random.uniform(-30, 30), 1),
                "y": round(track_y[i] + random.uniform(-30, 30), 1),
            })
            corner_num += 1

    return corners[:15]  # cap at 15 corners


def interpolate_track(track_x, track_y, n_points):
    """Interpolate track to get n_points evenly spaced."""
    # Calculate cumulative distances
    dists = [0]
    for i in range(1, len(track_x)):
        dx = track_x[i] - track_x[i - 1]
        dy = track_y[i] - track_y[i - 1]
        dists.append(dists[-1] + math.sqrt(dx * dx + dy * dy))

    total = dists[-1]
    result_x = []
    result_y = []

    for j in range(n_points):
        target = (j / n_points) * total
        # Find surrounding indices
        for i in range(1, len(dists)):
            if dists[i] >= target:
                frac = (target - dists[i - 1]) / max(0.001, dists[i] - dists[i - 1])
                result_x.append(round(
                    track_x[i - 1] + (track_x[i] - track_x[i - 1]) * frac, 1
                ))
                result_y.append(round(
                    track_y[i - 1] + (track_y[i] - track_y[i - 1]) * frac, 1
                ))
                break

    return result_x, result_y


def generate_telemetry(track_x, track_y, lap_time, speed_offset=0):
    """Generate synthetic telemetry for a lap."""
    n = len(track_x)
    times = []
    speeds = []
    throttles = []
    brakes = []
    gears = []
    drs_vals = []

    # Calculate segment lengths
    seg_lengths = []
    for i in range(n):
        j = (i + 1) % n
        dx = track_x[j] - track_x[i]
        dy = track_y[j] - track_y[i]
        seg_lengths.append(math.sqrt(dx * dx + dy * dy))

    total_dist = sum(seg_lengths)

    # Calculate curvature at each point to determine speed
    curvatures = []
    for i in range(n):
        im2 = (i - 2) % n
        ip2 = (i + 2) % n
        dx1 = track_x[i] - track_x[im2]
        dy1 = track_y[i] - track_y[im2]
        dx2 = track_x[ip2] - track_x[i]
        dy2 = track_y[ip2] - track_y[i]
        cross = abs(dx1 * dy2 - dy1 * dx2)
        length = max(1, math.sqrt(dx1 * dx1 + dy1 * dy1) * math.sqrt(dx2 * dx2 + dy2 * dy2))
        curvatures.append(cross / length)

    # Smooth curvatures
    smoothed = curvatures[:]
    for _ in range(3):
        new_smooth = smoothed[:]
        for i in range(n):
            new_smooth[i] = sum(smoothed[(i + j) % n] for j in range(-3, 4)) / 7
        smoothed = new_smooth

    # Generate speed based on curvature (high curvature = slow)
    max_curv = max(smoothed) if smoothed else 1
    for i in range(n):
        curv_factor = smoothed[i] / max(0.001, max_curv)
        # Speed: 80-340 km/h based on curvature
        base_speed = 340 - curv_factor * 260
        speed = base_speed + speed_offset + random.uniform(-3, 3)
        speed = max(80, min(345, speed))
        speeds.append(round(speed, 1))

    # Generate time from speed and distance
    cumulative_time = 0
    for i in range(n):
        times.append(round(cumulative_time, 3))
        speed_ms = speeds[i] / 3.6
        dt = seg_lengths[i] / max(1, speed_ms) if i < len(seg_lengths) else 0
        cumulative_time += dt

    # Scale time to match target lap_time
    time_scale = lap_time / max(0.001, cumulative_time)
    times = [round(t * time_scale, 3) for t in times]

    # Generate throttle, brake, gear, DRS
    for i in range(n):
        speed = speeds[i]
        prev_speed = speeds[(i - 1) % n]

        # Throttle: high when accelerating or at high speed
        if speed > prev_speed + 1:
            throttle = min(100, 70 + speed / 10)
        elif speed < prev_speed - 5:
            throttle = max(0, speed / 10)
        else:
            throttle = min(100, 50 + speed / 8)
        throttles.append(round(throttle))

        # Brake: active when decelerating significantly
        braking = 1 if speed < prev_speed - 8 else 0
        brakes.append(braking)

        # Gear: 1-8 based on speed
        if speed < 100:
            gear = 2
        elif speed < 140:
            gear = 3
        elif speed < 180:
            gear = 4
        elif speed < 220:
            gear = 5
        elif speed < 260:
            gear = 6
        elif speed < 300:
            gear = 7
        else:
            gear = 8
        gears.append(gear)

        # DRS: active on straights above 300 km/h
        drs = 1 if speed > 290 and throttle > 90 else 0
        drs_vals.append(drs)

    return {
        "time": times,
        "x": [round(x, 1) for x in track_x],
        "y": [round(y, 1) for y in track_y],
        "speed": speeds,
        "throttle": throttles,
        "brake": brakes,
        "gear": gears,
        "drs": drs_vals,
    }


def main():
    print("Generating sample track...")
    raw_x, raw_y = generate_track()

    # Interpolate to get even spacing
    track_x, track_y = interpolate_track(raw_x, raw_y, NUM_POINTS)

    print("Generating corners...")
    corners = generate_corners(raw_x, raw_y)

    print("Generating Driver 1 telemetry (VER)...")
    d1_tel = generate_telemetry(track_x, track_y, lap_time=89.404)

    print("Generating Driver 2 telemetry (NOR)...")
    d2_tel = generate_telemetry(track_x, track_y, lap_time=89.685, speed_offset=-3)

    # Track outline (downsampled, closed loop)
    outline_x, outline_y = interpolate_track(raw_x, raw_y, 300)
    outline_x.append(outline_x[0])
    outline_y.append(outline_y[0])

    result = {
        "session": {
            "year": 2024,
            "event": "Bahrain Grand Prix",
            "session": "Q",
            "circuit": "Sakhir",
        },
        "track": {
            "x": outline_x,
            "y": outline_y,
        },
        "corners": corners,
        "driver1": {
            "code": "VER",
            "full_name": "Max Verstappen",
            "number": 1,
            "team": "Red Bull Racing",
            "color": "3671C6",
            "lap_time": 89.404,
            "telemetry": d1_tel,
        },
        "driver2": {
            "code": "NOR",
            "full_name": "Lando Norris",
            "number": 4,
            "team": "McLaren",
            "color": "FF8000",
            "lap_time": 89.685,
            "telemetry": d2_tel,
        },
    }

    out_dir = os.path.join("docs", "data", "ghost")
    os.makedirs(out_dir, exist_ok=True)
    filepath = os.path.join(out_dir, "2024_Bahrain_Q_VER_vs_NOR.json")

    with open(filepath, "w") as f:
        json.dump(result, f, separators=(",", ":"))

    size_kb = os.path.getsize(filepath) / 1024
    print(f"Written {filepath} ({size_kb:.0f} KB)")
    print(f"  VER: 89.404s")
    print(f"  NOR: 89.685s")
    print(f"  Delta: 0.281s")


if __name__ == "__main__":
    main()
