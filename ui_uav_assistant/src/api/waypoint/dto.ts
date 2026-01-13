import { WaypointRole } from '../../uav_types/waypoint';
export interface AddWaypointRequestDto {
  lat: number;
  lon: number;
  role: WaypointRole;
  name: string;
}

export interface AddWaypointResponseDto {
  id: number;
  lat: number;
  lng: number;
  role: WaypointRole;
  name: string;
}

export interface DeleteWaypointRequestDto {
  waypoint_id: number;
}

export interface DeleteWaypointResponseDto {
  ok: boolean;
}
