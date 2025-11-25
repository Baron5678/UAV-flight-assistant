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

  // Normalize role to UPPERCASE string
  let role = p.role ? String(p.role).toUpperCase() : null;
  if (!role && p.color) {
    role = COLOR_TO_ROLE[p.color] || "REQUIRED";
  }
  if (!role) role = "REQUIRED";

  const color = p.color || ROLE_TO_COLOR[role] || "blue";
  const icon  = colorToIcon(color);

  const m = L
    .marker([lat, lng], { icon, title: `ID ${p.id ?? ""}` })
    .bindPopup(
      `ID: ${esc(p.id ?? "")}<br>` +
      `Role: ${esc(role)}<br>` +
      `(${lat.toFixed(6)}, ${lng.toFixed(6)})`
    );

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
    body: JSON.stringify({ lat, lon, role, name })  // WaypointRequest
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    alert("Failed to add waypoint: " + (err.detail || res.statusText));
    return;
  }

  const point = await res.json(); // WaypointResponse: { id, lat, lng, role, color, name }
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
}


async function fetchPoints() {
  const res = await fetch('/points');
  const data = await res.json();
  CURRENT_POINTS = data.points || [];
  renderPoints(CURRENT_POINTS);
  return CURRENT_POINTS;
}

async function startMission() {
  if (WAYPOINTS.length < 2) {
    alert("Add at least two waypoints before starting a mission.");
    return;
  }


  const gens = parseInt(document.getElementById("gen").value, 10);
  const popSize = parseInt(document.getElementById("pop").value, 10);
  const algo = document.getElementById("algo").value; // "GA" or "ES"
    const startId = START_ID;
  const endId = END_ID;
  const waypointIds = WAYPOINTS.map(p => p.dbId);

  const resp = await fetch('/start_mission', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      name: "Mission #1",
      start_waypoint_id: startId,
      end_waypoint_id: endId,
      waypoint_ids: waypointIds,
      generations: gens,
      population_size: popSize,
      algo: algo,
    }),
  });

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    alert("Failed to start mission: " + (err.detail || resp.statusText));
    return;
  }

  const data = await resp.json();
  CURRENT_MISSION_ID = data.mission_id;
  alert("Mission started with id: " + CURRENT_MISSION_ID);
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

map.on('click', async (e) => {
  const role = document.getElementById('role').value;
  await addWaypoint(e.latlng.lat, e.latlng.lng, role, "Default");
});

document.getElementById('btn-generate').addEventListener('click', scoutingPath);
document.getElementById('btn-reset').addEventListener('click', resetPoints);
document.getElementById('btn-start-mission').addEventListener('click', startMission)
