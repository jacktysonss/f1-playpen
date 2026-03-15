#!/usr/bin/env python3
"""Generate ghost-car comparison JSON from FastF1 telemetry data.

Usage:
    python scripts/generate_ghost_data.py [--year 2024] [--event Bahrain] \
        [--session Q] [--driver1 VER] [--driver2 NOR] [--out docs/data/ghost]

Outputs a JSON file that the ghost.html visualisation consumes.
"""

import argparse
import json
import math
import os
import sys

import fastf1
import numpy as np


def rotate(x, y, angle_deg):
    """Rotate x, y arrays by angle_deg (clockwise)."""
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    xr = x * cos_a + y * sin_a
    yr = -x * sin_a + y * cos_a
    return xr, yr


def downsample(arr, n):
    """Evenly downsample array to n points."""
    if len(arr) <= n:
        return arr
    idx = np.linspace(0, len(arr) - 1, n, dtype=int)
    return arr[idx]


def extract_driver_lap(session, driver_code, rotation):
    """Extract best lap telemetry for a driver, return dict."""
    driver_laps = session.laps.pick_drivers(driver_code)
    if driver_laps.empty:
        raise ValueError(f"No laps found for driver {driver_code}")

    fastest = driver_laps.pick_fastest()
    if fastest is None or (hasattr(fastest, "empty") and fastest.empty):
        raise ValueError(f"No valid fastest lap for {driver_code}")

    tel = fastest.get_telemetry()
    if tel.empty:
        raise ValueError(f"No telemetry for {driver_code}")

    # Get driver info
    driver_info = session.get_driver(driver_code)

    # Rotate coordinates to match track map orientation
    x, y = rotate(tel["X"].values.astype(float), tel["Y"].values.astype(float), rotation)

    # Convert Time to seconds from lap start
    time_s = tel["Time"].dt.total_seconds().values

    # Lap time in seconds
    lap_time = fastest["LapTime"].total_seconds()

    # Downsample to ~500 points for reasonable JSON size
    n = min(500, len(x))
    indices = np.linspace(0, len(x) - 1, n, dtype=int)

    return {
        "code": str(driver_info.get("Abbreviation", driver_code)),
        "full_name": str(driver_info.get("FullName", driver_code)),
        "number": int(driver_info.get("DriverNumber", 0)),
        "team": str(driver_info.get("TeamName", "")),
        "color": str(driver_info.get("TeamColor", "666666")),
        "lap_time": round(lap_time, 3),
        "telemetry": {
            "time": np.round(time_s[indices], 3).tolist(),
            "x": np.round(x[indices], 1).tolist(),
            "y": np.round(y[indices], 1).tolist(),
            "speed": tel["Speed"].values[indices].astype(float).round(1).tolist(),
            "throttle": tel["Throttle"].values[indices].astype(float).round(0).tolist(),
            "brake": [1 if b else 0 for b in tel["Brake"].values[indices]],
            "gear": tel["nGear"].values[indices].astype(int).tolist(),
            "drs": [int(d) if not np.isnan(d) else 0
                    for d in tel["DRS"].values[indices].astype(float)],
        },
    }


def extract_track(session, rotation):
    """Extract track outline from the fastest lap's position data."""
    fastest = session.laps.pick_fastest()
    pos = fastest.get_pos_data()
    x, y = rotate(pos["X"].values.astype(float), pos["Y"].values.astype(float), rotation)

    # Downsample track outline to ~300 points
    n = min(300, len(x))
    indices = np.linspace(0, len(x) - 1, n, dtype=int)
    tx = np.round(x[indices], 1).tolist()
    ty = np.round(y[indices], 1).tolist()
    # Close the loop so the track joins up smoothly
    tx.append(tx[0])
    ty.append(ty[0])
    return {"x": tx, "y": ty}


def extract_corners(session, rotation):
    """Extract corner positions and labels."""
    ci = session.get_circuit_info()
    corners = []
    for _, c in ci.corners.iterrows():
        cx, cy = rotate(
            np.array([float(c["X"])]),
            np.array([float(c["Y"])]),
            rotation,
        )
        corners.append({
            "number": int(c["Number"]),
            "letter": str(c.get("Letter", "")),
            "x": round(float(cx[0]), 1),
            "y": round(float(cy[0]), 1),
        })
    return corners


def main():
    parser = argparse.ArgumentParser(description="Generate ghost car comparison data")
    parser.add_argument("--year", type=int, default=2024)
    parser.add_argument("--event", default="Bahrain")
    parser.add_argument("--session", default="Q")
    parser.add_argument("--driver1", default="VER")
    parser.add_argument("--driver2", default="NOR")
    parser.add_argument("--out", default="docs/data/ghost",
                        help="Output directory for JSON files")
    args = parser.parse_args()

    # Enable cache
    cache_dir = os.path.join(os.path.dirname(__file__), "..", ".f1cache")
    os.makedirs(cache_dir, exist_ok=True)
    fastf1.Cache.enable_cache(cache_dir)

    print(f"Loading {args.year} {args.event} {args.session}...")
    session = fastf1.get_session(args.year, args.event, args.session)
    session.load(telemetry=True, laps=True, weather=False, messages=False)

    ci = session.get_circuit_info()
    rotation = float(ci.rotation)

    print(f"Extracting track outline...")
    track = extract_track(session, rotation)

    print(f"Extracting corners...")
    corners = extract_corners(session, rotation)

    print(f"Extracting {args.driver1} best lap...")
    d1 = extract_driver_lap(session, args.driver1, rotation)

    print(f"Extracting {args.driver2} best lap...")
    d2 = extract_driver_lap(session, args.driver2, rotation)

    result = {
        "session": {
            "year": args.year,
            "event": str(session.event["EventName"]),
            "session": args.session,
            "circuit": str(session.event["Location"]),
        },
        "track": track,
        "corners": corners,
        "driver1": d1,
        "driver2": d2,
    }

    # Write output
    os.makedirs(args.out, exist_ok=True)
    filename = f"{args.year}_{args.event}_{args.session}_{args.driver1}_vs_{args.driver2}.json"
    filepath = os.path.join(args.out, filename)

    with open(filepath, "w") as f:
        json.dump(result, f, separators=(",", ":"))

    size_kb = os.path.getsize(filepath) / 1024
    print(f"Written {filepath} ({size_kb:.0f} KB)")
    print(f"  {d1['code']}: {d1['lap_time']:.3f}s")
    print(f"  {d2['code']}: {d2['lap_time']:.3f}s")
    print(f"  Delta: {abs(d1['lap_time'] - d2['lap_time']):.3f}s")


if __name__ == "__main__":
    main()
