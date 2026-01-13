import {Marker, Polyline, useMap} from "react-leaflet";
import React, {useEffect, useMemo} from "react";
import {LatLonTuple} from "../uav_types/path";
import L from "leaflet";

export function PathLayer(props: { coords: LatLonTuple[]; cost: number | null }) {
  const map = useMap();
  const { bounds, center } = useMemo(() => {
    const polyline = L.polyline(props.coords);
    const b = polyline.getBounds();
    return { bounds: b, center: b.getCenter() };
  }, [props.coords]);

  useEffect(() => {
    if (!props.coords || props.coords.length < 2) return;
    map.fitBounds(bounds, { padding: [30, 30] });
  }, [map, bounds, props.coords]);

  const labelIcon = useMemo(() => {
    const html =
      typeof props.cost === "number"
        ? `Cost: ${props.cost.toFixed(2)}`
        : "Cost: n/a";

    return L.divIcon({
      className: "path-label",
      html,
      iconSize: [108, 45],
      iconAnchor: [40, 12],
    });
  }, [props.cost]);

  return (
    <>
      <Polyline positions={props.coords} weight={4} />
      <Marker position={center} icon={labelIcon} interactive={false} />
    </>
  );
}