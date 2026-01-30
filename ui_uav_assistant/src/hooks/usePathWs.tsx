import { useCallback, useMemo, useRef, useState } from "react";
import type { TracerApi } from "../cross/logs";
import type { MissionState } from "../uav_types/mission";
import type { LatLonTuple, PathRenderMode, Path } from "../uav_types/path";
import type { PathRequestDto } from "../api/path_http/dto";
import type { PathProgressEvent } from "../api/path_ws/dto";
import { startPathProgressWS } from "../api/path_ws/websocket_builder";

export interface UsePathsWSResult {
  path: Path | null;
  pathCoords: LatLonTuple[] | null;
  pathCost: number | null;

  hasPath: boolean;
  lastPathRequest: PathRequestDto | null;

  start: (requestBody: PathRequestDto, mode?: PathRenderMode) => void;
  cancel: () => void;
  clearPath: () => void;
}

export interface UsePathsWSArgs {
  mission: MissionState;
  tracer: TracerApi;
  onTrace?: (line: string) => void;
}

function unwrapPayload<T extends object>(msg: T): any {
  return (msg as any).payload ?? msg;
}

export function usePathsWS(args: UsePathsWSArgs): UsePathsWSResult {
  const [path, setPath] = useState<Path | null>(null);
  const [pathCoords, setPathCoords] = useState<LatLonTuple[] | null>(null);
  const [pathCost, setPathCost] = useState<number | null>(null);
  const [lastPathRequest, setLastPathRequest] = useState<PathRequestDto | null>(null);

  const wsRef = useRef<WebSocket | null>(null);

  const clearPath = useCallback(() => {
    setPath(null);
    setPathCoords(null);
    setPathCost(null);
  }, []);

  const cancel = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  const start = useCallback(
    (requestBody: PathRequestDto, mode: PathRenderMode = "EACH_GENERATION") => {
      if (!args.mission.id) {
        args.tracer.log("Start a mission first.");
        return;
      }
      if (requestBody.mission_id !== args.mission.id) {
        args.tracer.log("PathRequest mission_id mismatch.");
        return;
      }

      setLastPathRequest(requestBody);
      cancel();

      wsRef.current = startPathProgressWS({
        requestBody,

        onGeneration: (raw: PathProgressEvent) => {
          const msg = unwrapPayload(raw);
          if (msg.type === "generation") {
              if (!msg.is_feasible) {
                  setPathCoords(null);
                  setPathCost(null);
                  if (msg.message) args.onTrace?.(String(msg.message));
                  return;
              }
              setPathCost(msg.cost ?? null);
              console.log(msg.cost)
              setPathCoords((msg.waypoint_coords as LatLonTuple[]) ?? null);
              if (msg.message) args.onTrace?.(String(msg.message));
          } else {
              return;
          }
        },

        onFinal: (raw: PathProgressEvent) => {
          const msg = unwrapPayload(raw);
          if (msg.type === "final") {
              const generations =
                  (msg.generation as number | undefined) ?? requestBody.generations;
              const population_size = requestBody.population_size;
              const keepElitism = msg.keepElitism;
              const mutationProbability = msg.mutationProbability;
              const sigma0 = msg.sigma0;
              const seed= msg.seed;
              const kTournament = msg.kTournament;


              if(!msg.is_feasible){
                  setPath(null)
                  setPathCoords(null);
                  setPathCost(null);
                  if (msg.message) args.onTrace?.(String(msg.message));
                  wsRef.current = null;
                  return;
              }

              const finalPath: Path = {
                  waypoint_ids: (msg.waypoint_ids as number[]) ?? [],
                  waypoint_coords: (msg.waypoint_coords as LatLonTuple[]) ?? [],
                  cost: (msg.cost as number) ?? 0,
                  total_distance_m: (msg.total_distance_m as number) ?? 0,
                  generations,
                  population_size,
                  keepElitism,
                  kTournament,
                  mutationProbability,
                  sigma0,
                  seed,
                  algo: (msg.algo as any) ?? (requestBody.algo as any),
              };

              setPath(finalPath);
              setPathCost(finalPath.cost);
              setPathCoords(finalPath.waypoint_coords);

              args.onTrace?.(
                  msg.message ? String(msg.message) : `Final: best_cost=${finalPath.cost}`
              );
              wsRef.current = null;
          } else {
              return
          }

        },
          onDiagnostic: (raw: PathProgressEvent) => {
            const msg = unwrapPayload(raw);
            args.onTrace?.(JSON.stringify(msg));
            wsRef.current = null;
            },

        onError: (err: unknown) => {
          args.tracer.log("WebSocket error while generating path.");
          args.onTrace?.(String(err));
          wsRef.current = null;
        },
      });
    },
    [args.mission.id, args.tracer, args.onTrace, cancel]
  );

  return useMemo(
    () => ({
      path,
      pathCoords,
      pathCost,
      hasPath: !!path,
      lastPathRequest,
      start,
      cancel,
      clearPath,
    }),
    [path, pathCoords, pathCost, lastPathRequest, start, cancel, clearPath]
  );
}
