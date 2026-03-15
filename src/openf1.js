/**
 * OpenF1 API client
 * Docs: https://openf1.org/docs/
 * Base URL: https://api.openf1.org/v1/
 *
 * Free tier: no auth required, 3 req/s, 30 req/min
 * All historical data since 2023 season
 *
 * Set OPENF1_OFFLINE=1 to use bundled sample data (for offline/sandbox use).
 */

import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const BASE_URL = "https://api.openf1.org/v1";
const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, "..", "data");

const SAMPLE_FILES = {
  sessions: "sample-sessions.json",
  drivers: "sample-drivers.json",
  laps: "sample-laps.json",
  position: "sample-positions.json",
};

function isOffline() {
  return process.env.OPENF1_OFFLINE === "1";
}

/** Simple client-side filter: match all params as equality checks against data. */
function filterData(data, params) {
  if (Object.keys(params).length === 0) return data;
  return data.filter((item) =>
    Object.entries(params).every(([key, value]) => {
      // coerce numbers for comparison
      const itemVal = item[key];
      if (itemVal === undefined) return false;
      return String(itemVal) === String(value);
    })
  );
}

async function fetchSampleData(endpoint, params) {
  const filename = SAMPLE_FILES[endpoint];
  if (!filename) {
    console.warn(`[offline] No sample data for "${endpoint}", returning []`);
    return [];
  }
  const raw = await readFile(join(DATA_DIR, filename), "utf-8");
  const data = JSON.parse(raw);
  return filterData(data, params);
}

/**
 * Generic fetch wrapper for OpenF1 endpoints.
 * Accepts an endpoint name and optional query params object.
 * Supports comparison operators in param values (e.g. { speed: ">=315" }).
 * Falls back to sample data when OPENF1_OFFLINE=1.
 */
export async function fetchOpenF1(endpoint, params = {}) {
  if (isOffline()) {
    return fetchSampleData(endpoint, params);
  }

  const url = new URL(`${BASE_URL}/${endpoint}`);

  for (const [key, value] of Object.entries(params)) {
    url.searchParams.set(key, value);
  }

  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`OpenF1 ${endpoint} failed: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

// --- Endpoint helpers ---

/** Get sessions (race weekends). Filter by year, country_name, session_type, etc. */
export function getSessions(params = {}) {
  return fetchOpenF1("sessions", params);
}

/** Get drivers. Filter by session_key, driver_number, name_acronym, team_name, etc. */
export function getDrivers(params = {}) {
  return fetchOpenF1("drivers", params);
}

/** Get lap data. Filter by session_key, driver_number, lap_number, etc. */
export function getLaps(params = {}) {
  return fetchOpenF1("laps", params);
}

/** Get pit stop data. Filter by session_key, driver_number, pit_duration, etc. */
export function getPit(params = {}) {
  return fetchOpenF1("pit", params);
}

/** Get car telemetry (speed, RPM, throttle, brake, DRS, gear). High-frequency data. */
export function getCarData(params = {}) {
  return fetchOpenF1("car_data", params);
}

/** Get car location (x, y, z coordinates on track). High-frequency data. */
export function getLocation(params = {}) {
  return fetchOpenF1("location", params);
}

/** Get driver positions throughout a session. */
export function getPosition(params = {}) {
  return fetchOpenF1("position", params);
}

/** Get stint data (tyre compound, stint number, lap counts). */
export function getStints(params = {}) {
  return fetchOpenF1("stints", params);
}

/** Get weather data at the circuit. */
export function getWeather(params = {}) {
  return fetchOpenF1("weather", params);
}

/** Get team radio messages. */
export function getTeamRadio(params = {}) {
  return fetchOpenF1("team_radio", params);
}

/** Get race control messages (flags, penalties, track status). */
export function getRaceControl(params = {}) {
  return fetchOpenF1("race_control", params);
}

/** Get meetings (race weekend info). */
export function getMeetings(params = {}) {
  return fetchOpenF1("meetings", params);
}

/** Get interval data between drivers. */
export function getIntervals(params = {}) {
  return fetchOpenF1("intervals", params);
}

/** Get driver championship standings (race sessions only). */
export function getChampionshipDrivers(params = {}) {
  return fetchOpenF1("championship_drivers", params);
}

/** Get team/constructor championship standings (race sessions only). */
export function getChampionshipTeams(params = {}) {
  return fetchOpenF1("championship_teams", params);
}
