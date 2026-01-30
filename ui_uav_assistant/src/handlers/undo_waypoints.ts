import { make_request } from "../api/client/client";
import {AddWaypointResponseDto} from "../api/waypoint/dto";

export type RestoreWaypointsResponseDto = {
  mission_id: number;
  path_id: number;
  waypoints: AddWaypointResponseDto[];
};

export async function getRestore(
  missionId: number
): Promise<RestoreWaypointsResponseDto> {
  const res = await make_request<RestoreWaypointsResponseDto, undefined>(
    "restore.get",
    undefined,
    { mission_id: missionId }
  );

  if (res.failed) {
    throw new Error(res.error);
  }

  return res.body;
}
