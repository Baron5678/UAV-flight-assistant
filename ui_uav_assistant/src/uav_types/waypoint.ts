export type WaypointRole = "START" | "END" | "REQUIRED" | "STATION";
export interface Waypoint {
  id: number;
  role: WaypointRole;
  lat: number;
  lng: number;
  color?: string;
}
export interface WaypointState {
  add: (wp: Waypoint) => void;
  remove: (id: number) => void;
}

export const ROLE_TO_COLOR: Record<WaypointRole, string> = {
  REQUIRED: "red",
  START: "blue",
  END: "black",
  STATION: "green",
};

export const COLOR_TO_ROLE: Record<string, WaypointRole> = {
  red: "REQUIRED",
  blue: "START",
  black: "END",
  green: "STATION",
};