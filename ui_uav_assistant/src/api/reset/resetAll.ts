const API_BASE = "http://127.0.0.1:8000";

export async function apiResetAll(): Promise<void> {
  const res = await fetch(`${API_BASE}/reset_all`, {
    method: "POST",
  });

  if (!res.ok) {
    let message = res.statusText;

    try {
      const body = (await res.json()) as { detail?: string };
      if (body.detail) message = body.detail;
    } catch {
      /* ignore JSON parse errors */
    }

    throw new Error(message);
  }
}
