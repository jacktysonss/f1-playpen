/**
 * OpenF1 API client
 * Docs: https://openf1.org/docs/
 * Base URL: https://api.openf1.org/v1/
 *
 * Free tier: no auth required, 3 req/s, 30 req/min
 * All historical data since 2023 season
 */

const BASE_URL = "https://api.openf1.org/v1";

/**
 * Generic fetch wrapper for OpenF1 endpoints.
 * Accepts an endpoint name and optional query params object.
 * Supports comparison operators in param values (e.g. { speed: ">=315" }).
 */
export async function fetchOpenF1(endpoint, params = {}) {
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
