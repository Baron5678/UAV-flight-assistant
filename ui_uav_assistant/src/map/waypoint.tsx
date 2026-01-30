import { Marker, Popup } from "react-leaflet";
import React, { useMemo } from "react";
import { Waypoint, WaypointRole, COLOR_TO_ROLE, ROLE_TO_COLOR } from "../uav_types/waypoint";
import L, {point} from "leaflet";
function normalizeRole(point: Waypoint): WaypointRole {
    const r = point.role ? String(point.role).toUpperCase() : "";
    if (r === "START" || r === "END" || r === "STATION" || r === "REQUIRED") {
        return r as WaypointRole;
    }
    if (point.color && COLOR_TO_ROLE[point.color]) return COLOR_TO_ROLE[point.color];
    return "REQUIRED";
}
function colorToIcon(color: string): L.DivIcon {
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
export function WaypointMarker(props: {
    point: Waypoint;
    onDelete?: (id: number) => void | Promise<void>;
}) {
    const lat = Number(props.point.lat);
    const lng = Number(props.point.lng);
    if (!Number.isFinite(lat) || !Number.isFinite(lng)) return null;
    const role = normalizeRole(props.point);
    const color = props.point.color ?? ROLE_TO_COLOR[role] ?? "blue";
    const icon = useMemo(() => colorToIcon(color), [color]);
    return (
        <Marker
            position={[lat, lng]}
            icon={icon}
            eventHandlers={
            props.onDelete
                ? {
                dblclick: () => {
                    const r = props.onDelete?.(props.point.id);
                    void Promise.resolve(r).catch((err) => {
                        console.error("WaypointMarker onDelete failed:", err);
                    });
                    },
                }
                : undefined
        }
        >
            <Popup>
                <div>
                    <div>ID: {props.point.id}</div>
                    <div>Role: {role}</div>
                    <div>
                        ({lat.toFixed(6)}, {lng.toFixed(6)})
                    </div>
                    <div>Wind speed: {props.point.wind_speed}</div>
                    <div>Wind direction: {props.point.wind_direction}</div>
                </div>
            </Popup>
        </Marker>
    );
}
