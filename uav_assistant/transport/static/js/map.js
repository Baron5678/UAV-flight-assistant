/** @type {typeof import('leaflet')} */
const L = window.L;
let id = 0;
let CURRENT_POINTS = [];
let NEXT_GUI_ID = 0;
let WAYPOINTS = [];
let ENDPOINTS = [];
let START_ID = null;
let END_ID = null;
let CURRENT_MISSION_ID = null;
let currentMissionId = null;
let lastPathPreview = null;
let last_point = null;

const map = L.map('map').setView([52.2297, 21.0122], 12);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  maxZoom: 19,
  attribution: '&copy; OpenStreetMap contributors'
}).addTo(map);

const colorToIcon = (color) => {
  return L.divIcon({
    className: "custom-marker",
    html: `<svg width="20" height="20" viewBox="0 0 20 20" style="display:block">
            <circle cx="10" cy="10" r="7" stroke="white" stroke-width="2" fill="${color}" />
          </svg>`,
    iconAnchor: [10, 10],
    popupAnchor: [0, -10]
  });
};

let markerLayer = L.layerGroup().addTo(map);
let pathLayer = L.layerGroup().addTo(map);

const ROLE_TO_COLOR = {
  REQUIRED: "red",
  START: "blue",
  END: "black",
  STATION: "green",
};

const COLOR_TO_ROLE = {
  red: "REQUIRED",
  blue: "START",
  black: "END",
  green: "STATION",
};
function esc(s) {
  return String(s).replace(/[&<>"']/g,
                            m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
}

function renderPoint(p) {
  const lat = Number(p.lat);
  const lng = Number(p.lng ?? p.lon);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;

  let role = p.role ? String(p.role).toUpperCase() : null;
  if (!role && p.color) {
    role = COLOR_TO_ROLE[p.color] || "REQUIRED";
  }
  if (!role) role = "REQUIRED";

  const color = p.color || ROLE_TO_COLOR[role] || "blue";
  const icon  = colorToIcon(color);

  const popupHtml =
    `ID: ${esc(p.id ?? "")}<br>` +
    `Role: ${esc(role)}<br>` +
    `(${lat.toFixed(6)}, ${lng.toFixed(6)})<br>` +
    `<button type="button" class="btn-delete" data-id="${p.id}">Delete</button>`;

  const m = L
    .marker([lat, lng], { icon, title: `ID ${p.id ?? ""}` })
    .bindPopup(popupHtml);

  m.on('popupopen', (e) => {
    const container = e.popup.getElement();
    if (!container) return;

    const btn = container.querySelector('.btn-delete');
    if (!btn) return;

    const id = Number(btn.getAttribute('data-id')); // backend waypoint id
    btn.onclick = () => deleteWaypoint(id);
  });

  markerLayer.addLayer(m);
  return m;
}


function renderPoints(points = []) {
  markerLayer.clearLayers();
  const markers = [];
  for (const p of points) {
    const m = renderPoint(p);
    if (m) markers.push(m);
  }
  if (markers.length) {
    const fg = L.featureGroup(markers);
    map.fitBounds(fg.getBounds().pad(0.1), { animate: false });
  }
  return markers;
}

function renderPath(coords, cost) {
  pathLayer.clearLayers();
  if (!coords || coords.length < 2) return;

  const line = L.polyline(coords, { weight: 4 });
  pathLayer.addLayer(line);
  const center = line.getBounds().getCenter();
  const label = L.marker(center, {
    icon: L.divIcon({
      className: 'path-label',
      html: `Cost: ${cost.toFixed(2)}`,
      iconSize: [80, 40],   // tweak as you like
      iconAnchor: [40, 12],
    })
  });

  pathLayer.addLayer(label);

  map.fitBounds(line.getBounds(), { padding: [30, 30] });
}
async function addWaypoint(lat, lon, role, name) {
  role = String(role).toUpperCase();
  console.log(role)
  const res = await fetch('/add_point', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ lat, lon, role, name })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Failed to add waypoint: " + (err.detail || res.statusText));
    return;
  }

  const point = await res.json();
  last_point = point;

  const guiId = NEXT_GUI_ID++;
  const dbId = point.id;

  // Cache for future mission & path
  WAYPOINTS.push({
    guiId,
    dbId,
    lat: point.lat,
    lng: point.lng,
    role: point.role,
    color: point.color,
    name: point.name,
  });

    if (role === "START") {
    if (START_ID !== null) {
      alert("START waypoint already set. Only one START is allowed.");
      return;
    }
    START_ID = dbId;
    console.log("START_ID:", START_ID);
  }

  if (role === "END") {
    if (END_ID !== null) {
      alert("END waypoint already set. Only one END is allowed.");
      return;
    }
    END_ID = dbId;
    console.log("END_ID:", END_ID);
  }

  renderPoint(point);
}

async function deleteWaypoint(waypointId) {
  if (currentMissionId) {
    alert("Cancel the current mission before deleting waypoints.");
    return;
  }

  const res = await fetch('/delete_point', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ waypoint_id: waypointId })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Failed to delete waypoint: " + (err.detail || res.statusText));
  }
  WAYPOINTS = WAYPOINTS.filter(wp => wp.dbId !== waypointId);

  if (START_ID === waypointId) {
    START_ID = null;
  }
  if (END_ID === waypointId) {
    END_ID = null;
  }

  markerLayer.clearLayers();
  renderPoints(
    WAYPOINTS.map(wp => ({
      id: wp.dbId,
      lat: wp.lat,
      lng: wp.lng,
      role: wp.role,
      color: wp.color,
      name: wp.name,
    }))
  );
}


async function resetPoints() {
  await fetch('/reset_all', { method: 'POST' });

  markerLayer.clearLayers();
  pathLayer.clearLayers();
  document.getElementById('stats').textContent = '';

  WAYPOINTS = [];
  START_ID = null;
  END_ID = null;
  CURRENT_MISSION_ID = null;
  NEXT_GUI_ID = 0;
  currentMissionId = null
}


async function fetchPoints() {
  const res = await fetch('/points');
  const data = await res.json();
  CURRENT_POINTS = data.points || [];
  renderPoints(CURRENT_POINTS);
  return CURRENT_POINTS;
}

async function startMission() {
  const generations = parseInt(document.getElementById('gen').value, 10);
  const populationSize = parseInt(document.getElementById('pop').value, 10);
  const algo = document.getElementById('algo').value;
  const waypoints_ids = WAYPOINTS.map(wp => wp.dbId);
  const res = await fetch('/start_mission', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        name: "default_mission",
        start_waypoint_id: START_ID,
        end_waypoint_id: END_ID,
        waypoint_ids: waypoints_ids,
        generations: generations,
        population_size: populationSize,
        algo: algo
    })
  });

  // name: str = "default_mission"
    //     start_waypoint_id: int = -1
    //     end_waypoint_id: int = -1
    //     waypoint_ids: List[int]
    //     generations: int = 0
    //     population_size: int = 0
    //     algo: str = "GA"//

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Failed to start mission: " + (err.detail || res.statusText));
    return;
  }

  const data = await res.json();
  currentMissionId = data.mission_id;

  lastPathPreview = null;
  document.getElementById('btn-finish').disabled = true;
}

async function scoutingPath() {
  if (!CURRENT_MISSION_ID) {
    alert("Start a mission first.");
    return;
  }

  const resp = await fetch('/path', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mission_id: CURRENT_MISSION_ID,
    }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    alert("Failed to generate path: " + (err.detail || resp.statusText));
    return;
  }

  const data = await resp.json();
  renderPath(data.waypoint_coords, data.cost);
  document.getElementById('cost').value = data.cost.toFixed(2);
}

async function generatePathPreview() {
  if (!currentMissionId) {
    alert("Start a mission first.");
    return;
  }

  const generations = parseInt(document.getElementById('gen').value, 10);
  const populationSize = parseInt(document.getElementById('pop').value, 10);
  const algo = document.getElementById('algo').value; // "GA" or "ES"
  const battery = document.getElementById('energy').value
  const ratio = document.getElementById('ratio').value

  const res = await fetch('/path', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      mission_id: currentMissionId,
      generations,
      population_size: populationSize,
      algo,
        drone: {
        "battery_capacity_wh": battery,
        "wh_per_km": ratio,
        "reserve_ratio": 0.2
        }
    })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Failed to generate path: " + (err.detail || res.statusText));
    return;
  }

  const data = await res.json(); // PathResponse
  // data: { waypoint_ids, waypoint_coords, total_distance_m, best_cost, generations, population_size, algo }
 console.log(data)
  lastPathPreview = data; // store full PathResponse

  // draw on map using your existing renderPath
  renderPath(data.waypoint_coords, data.best_cost);

  // enable Finish button
  document.getElementById('btn-finish').disabled = false;
}

async function finishMissionWithCurrentPath() {
  if (!currentMissionId) {
    alert("No active mission.");
    return;
  }
  if (!lastPathPreview) {
    alert("Generate a path first.");
    return;
  }

  const body = {
    mission_id: currentMissionId,
    waypoint_ids: lastPathPreview.waypoint_ids,
    total_distance_m: lastPathPreview.total_distance_m,
    best_cost: lastPathPreview.best_cost,
    generations: lastPathPreview.generations,
    population_size: lastPathPreview.population_size,
    algo: lastPathPreview.algo
  };

  const res = await fetch('/finish_mission', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Failed to finish mission: " + (err.detail || res.statusText));
    return;
  }

  const data = await res.json(); // e.g. { mission_id, path_id, cost }

  alert(`Mission ${data.mission_id} finished. Saved path ID: ${data.path_id}`);

  document.getElementById('btn-finish').disabled = true;

}

async function cancelCurrentMission() {
  if (!currentMissionId) {
    alert("No active mission.");
    return;
  }

  const res = await fetch('/cancel_mission', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ mission_id: currentMissionId })
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Failed to cancel mission: " + (err.detail || res.statusText));
    return;
  }

  currentMissionId = null;
  lastPathPreview = null;
  pathLayer.clearLayers();
  document.getElementById('btn-finish').disabled = true;
}


map.on('click', async (e) => {
  const role = document.getElementById('role').value;
  await addWaypoint(e.latlng.lat, e.latlng.lng, role, "Default");
});
document.getElementById('btn-generate').addEventListener('click', generatePathPreview);
//document.getElementById('btn-generate').addEventListener('click', scoutingPath);
document.getElementById('btn-reset').addEventListener('click', resetPoints);
document.getElementById('btn-cancel').addEventListener('click', cancelCurrentMission);
document.getElementById('btn-start-mission').addEventListener('click', startMission)
document.getElementById('btn-finish').addEventListener('click', finishMissionWithCurrentPath);

