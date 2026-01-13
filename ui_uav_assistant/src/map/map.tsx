import React from "react";
import {
  MapContainer,
  TileLayer,
  useMapEvents,
} from "react-leaflet";
import type { LeafletMouseEvent } from "leaflet";
import type { Waypoint } from "../uav_types/waypoint";
import type {LatLonTuple} from "../uav_types/path";
import { WaypointMarker } from "./waypoint";
import { PathLayer } from "./path";

type MapClick = { lat: number; lng: number };

function MapClickHandler(props: { onMapClick?: (p: MapClick) => void | Promise<void> }) {
  useMapEvents({
    click: (e: LeafletMouseEvent) => {
      if (!props.onMapClick) return;
      const r = props.onMapClick({ lat: e.latlng.lat, lng: e.latlng.lng });
      void Promise.resolve(r).catch((err) => {
        console.error("Map onMapClick failed:", err);
      });
    },
  });
  return null;
}

export interface MapViewProps {
  waypoints?: Waypoint[];
  pathCoords?: LatLonTuple[] | null;
  pathCost?: number | null;
  onMapClick?: (p: MapClick) => void;
  onDeleteWaypoint?: (id: number) => void;
}

export default function Map({
  waypoints = [],
  pathCoords = null,
  pathCost = null,
  onMapClick,
  onDeleteWaypoint,
}: MapViewProps) {
  const center: LatLonTuple = [52.2297, 21.0122];

  return (
    <MapContainer center={center} zoom={12} style={{ height: "100%", width: "100%" }}>
      <TileLayer
        attribution="&copy; OpenStreetMap contributors"
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <MapClickHandler onMapClick={onMapClick} />

      {waypoints.map((p) => (
        <WaypointMarker key={p.id} point={p} onDelete={onDeleteWaypoint} />
      ))}

      {pathCoords && pathCoords.length >= 2 && (
        <PathLayer coords={pathCoords} cost={pathCost ?? null} />
      )}
    </MapContainer>
  );
}
