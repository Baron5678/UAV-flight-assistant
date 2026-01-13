import type { PathSummaryResponseDto } from "../api/path_summary/dto";
import { make_request } from "../api/client/client";

export async function getSummary(
  missionId: number
): Promise<PathSummaryResponseDto> {
  const res = await make_request<PathSummaryResponseDto, undefined>(
    "summary.get",
    undefined,
    { mission_id: missionId }
  );

  if (res.failed) {
    throw new Error(res.error);
  }

  return res.body;
}

