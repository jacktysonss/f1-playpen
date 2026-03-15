/**
 * Example: Compare lap times for two drivers in a race
 * Run: node examples/lap-times.js
 */
import { getSessions, getLaps } from "../src/openf1.js";

const DRIVER_A = 1;   // Verstappen
const DRIVER_B = 44;  // Hamilton

// Get a specific race — 2024 Bahrain GP
const sessions = await getSessions({
  year: 2024,
  country_name: "Bahrain",
  session_type: "Race",
});
const session = sessions[0];

console.log(`\n🏎️  Lap time comparison — ${session.meeting_name} ${session.year}`);
console.log(`   Drivers: #${DRIVER_A} vs #${DRIVER_B}\n`);

const [lapsA, lapsB] = await Promise.all([
  getLaps({ session_key: session.session_key, driver_number: DRIVER_A }),
  getLaps({ session_key: session.session_key, driver_number: DRIVER_B }),
]);

// Build a map for easy comparison
const timesB = new Map(lapsB.map((l) => [l.lap_number, l.lap_duration]));

console.log("Lap".padStart(4) + `  #${DRIVER_A}`.padStart(10) + `  #${DRIVER_B}`.padStart(10) + "  Delta".padStart(10));
console.log("-".repeat(36));

for (const lap of lapsA) {
  const tA = lap.lap_duration;
  const tB = timesB.get(lap.lap_number);
  if (tA == null || tB == null) continue;

  const delta = (tA - tB).toFixed(3);
  const sign = delta > 0 ? "+" : "";
  console.log(
    String(lap.lap_number).padStart(4) +
    tA.toFixed(3).padStart(10) +
    tB.toFixed(3).padStart(10) +
    `${sign}${delta}`.padStart(10)
  );
}
