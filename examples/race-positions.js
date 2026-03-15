/**
 * Example: Show position changes throughout a race (text-based chart)
 * Run: node examples/race-positions.js
 */
import { getSessions, getDrivers, getPosition } from "../src/openf1.js";

// 2024 Bahrain GP
const sessions = await getSessions({
  year: 2024,
  country_name: "Bahrain",
  session_type: "Race",
});
const session = sessions[0];

const [drivers, positions] = await Promise.all([
  getDrivers({ session_key: session.session_key }),
  getPosition({ session_key: session.session_key }),
]);

// Map driver_number -> acronym
const acronyms = new Map(drivers.map((d) => [d.driver_number, d.name_acronym]));

// Get unique dates (snapshots) and sample every ~5 minutes
const snapshots = [...new Set(positions.map((p) => p.date))].sort();
const step = Math.max(1, Math.floor(snapshots.length / 15));
const sampled = snapshots.filter((_, i) => i % step === 0 || i === snapshots.length - 1);

console.log(`\n📊 Position chart — ${session.meeting_name} ${session.year}\n`);

for (const date of sampled) {
  const posAtTime = positions
    .filter((p) => p.date === date)
    .sort((a, b) => a.position - b.position);

  const time = new Date(date).toISOString().slice(11, 19);
  const line = posAtTime
    .slice(0, 10) // top 10
    .map((p) => acronyms.get(p.driver_number) || String(p.driver_number))
    .join(" ");

  console.log(`${time}  ${line}`);
}

console.log("\n(Showing top 10 positions at sampled intervals)");
