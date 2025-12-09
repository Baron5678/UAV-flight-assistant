// src/map/MapView.jsx
// @ts-nocheck
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Polyline,
  useMapEvents,
  useMap,
} from "react-leaflet";
import L from "leaflet";

// same as before
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

function colorToIcon(color) {
  return L.divIcon({
    className: "custom-marker",
    html: `
      <svg width="20" height="20" viewBox="0 0 20 20" style="display:block">
        <circle cx="10" cy="10" r="7" stroke="white" stroke-width="2" fill="${color}" />
      </svg>
    `,
    iconAnchor: [10, 10],
    popupAnchor: [0, -10],
  });
}

function MapClickHandler({ onMapClick }) {
  useMapEvents({
    click: (e) => {
      if (!onMapClick) return;
      const { lat, lng } = e.latlng;
      onMapClick({ lat, lng });
    },
  });
  return null;
}

function WaypointMarker({ point, onDelete }) {
  const lat = Number(point.lat);
  const lng = Number(point.lng ?? point.lon);
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;

  let role = point.role ? String(point.role).toUpperCase() : null;
  if (!role && point.color) role = COLOR_TO_ROLE[point.color] || "REQUIRED";
  if (!role) role = "REQUIRED";

  const color = point.color || ROLE_TO_COLOR[role] || "blue";
  const icon = colorToIcon(color);

  return (
    <Marker position={[lat, lng]} icon={icon} eventHandlers={
        onDelete
          ? {
              dblclick: () => onDelete(point.id),   // << double-click delete
            }
          : undefined
      }>
      <Popup>
        <div>
          <div>ID: {point.id}</div>
          <div>Role: {role}</div>
          <div>
            ({lat.toFixed(6)}, {lng.toFixed(6)})
          </div>
        </div>
      </Popup>
    </Marker>
  );
}

// Separate layer for path so we can also fit bounds / show cost label
function PathLayer({ coords, cost }) {
  const map = useMap();
  if (!coords || coords.length < 2) return null;

  const polyline = L.polyline(coords);
  const bounds = polyline.getBounds();
  const center = bounds.getCenter();

  // zoom to path
  map.fitBounds(bounds, { padding: [30, 30] });

  // label icon for cost
  const labelIcon = L.divIcon({
    className: "path-label",
    html:
      typeof cost === "number"
        ? `Cost: ${cost.toFixed(2)}`
        : "Cost: n/a",
    iconSize: [80, 40],
    iconAnchor: [40, 12],
  });

  return (
    <>
      <Polyline positions={coords} weight={4} />
      <Marker position={center} icon={labelIcon} interactive={false} />
    </>
  );
}

function MapView({ waypoints = [], pathCoords = null, pathCost = null, onMapClick, onDeleteWaypoint }) {
  const center = [52.2297, 21.0122];

  return (
    <MapContainer
      center={center}
      zoom={12}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapClickHandler onMapClick={onMapClick} />

      {waypoints.map((p) => (
        <WaypointMarker key={p.id} point={p} onDelete={onDeleteWaypoint} />
      ))}

      {pathCoords && pathCoords.length >= 2 && (
        <PathLayer coords={pathCoords} cost={pathCost} />
      )}
    </MapContainer>
  );
}

export default MapView;
