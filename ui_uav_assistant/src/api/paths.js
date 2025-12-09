// src/api/paths.js
const API_BASE = "http://127.0.0.1:8000";

async function handleJson(res) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

/**
 * Call /path to generate an optimized path.
 *
 * Args:
 *   missionId        - current mission id
 *   generations      - GA/ES generations
 *   populationSize   - GA/ES population size
 *   algo             - "GA" or "ES"
 *   batteryWh        - drone battery capacity in Wh
 *   whPerKm          - energy per km in Wh/km
 */
export async function apiGeneratePath({
  missionId,
  generations,
  populationSize,
  algo,
  batteryWh,
  whPerKm,
}) {
  const res = await fetch("http://127.0.0.1:8000/path", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      mission_id: missionId,
      generations,
      population_size: populationSize,
      algo,
      drone: {
        battery_capacity_wh: batteryWh,
        wh_per_km: whPerKm,
        reserve_ratio: 0.2,
      },
    }),
  });

  // PathResponse:
  // { waypoint_ids, waypoint_coords, total_distance_m,
  //   best_cost, generations, population_size, algo }
  return handleJson(res);
}
