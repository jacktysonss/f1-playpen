/**
 * Example: List all drivers from a recent session
 * Run: node examples/list-drivers.js
 */
import { getSessions, getDrivers } from "../src/openf1.js";

// Get the most recent race session
const sessions = await getSessions({ year: 2024, session_type: "Race" });
const latestSession = sessions[sessions.length - 1];

console.log(`\n🏁 ${latestSession.session_name} — ${latestSession.meeting_name}`);
console.log(`   ${latestSession.country_name} | ${latestSession.date_start}\n`);

// Get all drivers from that session
const drivers = await getDrivers({ session_key: latestSession.session_key });

console.log("Driver".padEnd(25) + "Team".padEnd(25) + "#");
console.log("-".repeat(55));

for (const d of drivers) {
  const name = `${d.first_name} ${d.last_name}`;
  console.log(name.padEnd(25) + (d.team_name || "").padEnd(25) + d.driver_number);
}
