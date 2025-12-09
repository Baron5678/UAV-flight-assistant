async function handleJson(res) {
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}

/**
 * POST /start_mission
 * Body:
 * {
 *   name: "default_mission",
 *   start_waypoint_id,
 *   end_waypoint_id,
 *   waypoint_ids: number[],
 *   generations,
 *   population_size,
 *   algo: "GA" | "ES"
 * }
 * Returns: { mission_id, ... }
 */
export async function apiStartMission({
  name = "default_mission",
  startWaypointId,
  endWaypointId,
  waypointIds,
  generations,
  populationSize,
  algo,
}) {
  const res = await fetch("http://127.0.0.1:8000/start_mission", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      name,
      start_waypoint_id: startWaypointId,
      end_waypoint_id: endWaypointId,
      waypoint_ids: waypointIds,
      generations,
      population_size: populationSize,
      algo,
    }),
  });

  return handleJson(res); // expected { mission_id, ... }
}

/**
 * POST /finish_mission
 * Body: {
 *   mission_id,
 *   waypoint_ids,
 *   total_distance_m,
 *   best_cost,
 *   generations,
 *   population_size,
 *   algo
 * }
 * For now we’ll wire the signature; actual body will be filled when we
 * implement path/lastPathPreview.
 */
export async function apiFinishMission(body) {
  const res = await fetch("http://127.0.0.1:8000/finish_mission", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return handleJson(res); // e.g. { mission_id, path_id, cost }
}

/**
 * POST /cancel_mission
 * Body: { mission_id }
 */
export async function apiCancelMission(missionId) {
  const res = await fetch("http://127.0.0.1:8000/cancel_mission", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mission_id: missionId }),
  });
  return handleJson(res);
}