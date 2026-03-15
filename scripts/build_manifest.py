#!/usr/bin/env python3
"""Scan docs/data/ghost/ for JSON files and build a manifest.json for the UI."""

import json
import os

GHOST_DIR = os.path.join("docs", "data", "ghost")


def main():
    os.makedirs(GHOST_DIR, exist_ok=True)
    manifest = []

    for filename in sorted(os.listdir(GHOST_DIR)):
        if not filename.endswith(".json") or filename == "manifest.json":
            continue

        filepath = os.path.join(GHOST_DIR, filename)
        try:
            with open(filepath) as f:
                data = json.load(f)

            s = data.get("session", {})
            d1 = data.get("driver1", {})
            d2 = data.get("driver2", {})
            delta = abs(d1.get("lap_time", 0) - d2.get("lap_time", 0))

            manifest.append({
                "file": filename,
                "label": f"{s.get('year', '')} {s.get('event', '')} {s.get('session', '')} — {d1.get('code', '?')} vs {d2.get('code', '?')}",
                "meta": f"{s.get('circuit', '')} · Delta: {delta:.3f}s",
            })
        except (json.JSONDecodeError, KeyError):
            continue

    with open(os.path.join(GHOST_DIR, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"Manifest: {len(manifest)} comparison(s)")


if __name__ == "__main__":
    main()
