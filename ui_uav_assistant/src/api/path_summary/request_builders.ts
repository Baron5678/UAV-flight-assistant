import {PathSummaryPathParams} from "./dto";

export function buildPathSummaryRequest(args: { missionId: number }): PathSummaryPathParams {
  return { mission_id: args.missionId };
}
