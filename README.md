# f1-playpen

Apps, visualisations, and games built with [OpenF1 API](https://openf1.org) data.

## Quick Start

```bash
# No dependencies needed — uses native fetch (Node 18+)
node examples/list-drivers.js
node examples/lap-times.js
node examples/race-positions.js
```

## Project Structure

```
src/
  openf1.js        # API client with helpers for all endpoints
examples/
  list-drivers.js   # List drivers from a session
  lap-times.js      # Compare lap times between drivers
  race-positions.js # Track position changes through a race
```

## OpenF1 API Reference

**Base URL:** `https://api.openf1.org/v1/`

Free tier — no auth, no signup. 3 req/s, 30 req/min. Data from 2023 onwards.

### Available Endpoints

| Endpoint | Description |
|---|---|
| `sessions` | Race weekend sessions (Practice, Qualifying, Race) |
| `drivers` | Driver info (name, team, number, headshot URL) |
| `laps` | Lap times, sectors, speed traps |
| `pit` | Pit stop times and durations |
| `car_data` | Telemetry: speed, RPM, throttle, brake, DRS, gear |
| `location` | Car x/y/z coordinates on track |
| `position` | Race positions over time |
| `stints` | Tyre compounds and stint lengths |
| `weather` | Track temperature, air temp, humidity, wind, rain |
| `team_radio` | Team radio message URLs |
| `race_control` | Flags, penalties, track status messages |
| `intervals` | Gap to leader and gap to car ahead |
| `meetings` | Race weekend metadata |
| `championship_drivers` | Driver standings (race sessions only) |
| `championship_teams` | Constructor standings (race sessions only) |

### Query Examples

```
# All laps for Hamilton in a specific session
/v1/laps?session_key=9839&driver_number=44

# Pit stops under 2.3 seconds
/v1/pit?session_key=9877&stop_duration<2.3

# Car speeds over 315 km/h
/v1/car_data?driver_number=55&session_key=9159&speed>=315
```

## Ideas

- **Live dashboard** — positions, gaps, tyre strategy in real-time
- **Lap time visualiser** — overlay driver laps, highlight sectors
- **Track map** — plot car locations using x/y coordinates
- **Pit strategy game** — choose when to pit, which tyres, beat the AI
- **Weather impact analysis** — correlate rain/temp with lap times
- **Team radio explorer** — browse and play radio clips by session
- **Championship predictor** — simulate remaining races from standings
