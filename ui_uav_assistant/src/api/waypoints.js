const API_BASE = "http://127.0.0.1:8000";

export async function apiAddWaypoint({ lat, lon, role, name = "" }) {
  const res = await fetch(`${API_BASE}/add_point`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ lat, lon, role, name }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }

  return res.json();
}

export async function apiDeleteWaypoint(id) {
  const res = await fetch(`${API_BASE}/delete_point`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ waypoint_id: id }),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }

  return res.json(); // { ok: true }
}
