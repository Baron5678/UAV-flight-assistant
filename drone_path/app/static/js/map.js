/** @type {typeof import('leaflet')} */
const L = window.L;
let id = 0;
let CURRENT_POINTS = [];
let ENDPOINTS = []
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

const ROLE_BY_COLOR = {
  red: "REQUIRED",
  blue: "OPTIONAL",
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

  const role  = p.role ? String(p.role).toLowerCase() : (ROLE_BY_COLOR[p.color] ?? "optional");
  const color = p.color || ROLE_BY_COLOR[role] || "blue";
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

function renderPath(coords) {
  pathLayer.clearLayers();
  if (!coords || coords.length < 2) return;
  const line = L.polyline(coords, { weight: 4 });
  pathLayer.addLayer(line);
  map.fitBounds(line.getBounds(), { padding: [30, 30] })
}

async function addWaypoint(lat, lon, role, name) {
    role = String(role).toUpperCase()
    console.log(role)
    if (role === "OPTIONAL")
        ENDPOINTS.push(id)
    if(ENDPOINTS.length > 2){
        while (ENDPOINTS.length > 0) {
            ENDPOINTS.pop();
        }
    }
    const res = await fetch('/add_waypoint', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({id, lat, lon, role, name})
  });
    id++;
  const point = await res.json();
  last_point = point;
  renderPoint(point);
}

async function resetPoints() {
  await fetch('/reset_waypoint', { method: 'POST' });
  markerLayer.clearLayers();
  pathLayer.clearLayers();
  document.getElementById('stats').textContent = '';
  CURRENT_POINTS = [];
  ENDPOINTS = []
    id = 0;
}


async function fetchPoints() {
  const res = await fetch('/points');
  const data = await res.json();
  CURRENT_POINTS = data.points || [];
  renderPoints(CURRENT_POINTS);
  return CURRENT_POINTS;
}


async function scoutingPath() {
    let gens = document.getElementById("gen").value
    let pop_size = document.getElementById("pop").value
    let resp = await fetch('/path', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            start_id: ENDPOINTS[0],
            end_id: ENDPOINTS[1],
            generations: parseInt(gens),
            population_size: parseInt(pop_size)
        })
    });
    const data = await resp.json();
    renderPath(data.waypoint_coords);
    document.getElementById('cost').value = data.best_cost.toFixed(2);
}

map.on('click', async (e) => {
  const role = document.getElementById('role').value;
  await addWaypoint(e.latlng.lat, e.latlng.lng, role, "Default");
});

document.getElementById('btn-generate').addEventListener('click', scoutingPath);
document.getElementById('btn-reset').addEventListener('click', resetPoints);
