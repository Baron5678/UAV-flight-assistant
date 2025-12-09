// src/api/system.js
const API_BASE = "http://127.0.0.1:8000";

export async function apiResetAll() {
  const res = await fetch(`${API_BASE}/reset_all`, {
    method: "POST",
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || res.statusText);
  }
  return res.json();
}
