import { useMemo, useState } from "react";
import {TracerApi} from "../cross/logs";
import type { MissionState } from "../uav_types/mission";
import { generatePathHttpHandler } from "../handlers/path";
import {Path} from "../uav_types/path";
import {AlgoSettings} from "../uav_types/algo";
import {Drone} from "../uav_types/drone";

export interface UsePathsHttpArgs {
  mission: MissionState;
  tracer: TracerApi;
  algoSettings: AlgoSettings;
  drone: Drone;
}

export interface UsePathsHttpResult {
  path: Path | null;
  hasPath: boolean;
  generatePathHttp: () => Promise<void>;
  clearPath: () => void;
}

export function usePathsHttp(args: UsePathsHttpArgs): UsePathsHttpResult {
  const [path, setPath] = useState<Path | null>(null);

  const pathState = useMemo(
    () => ({
      setPath
    }),
    []
  );

  const generatePathHttp = useMemo(
    () =>
      generatePathHttpHandler({
          mission: args.mission,
          tracer: args.tracer,
          path: pathState,
          algoSettings: args.algoSettings,
          drone: args.drone,
      }),
    [args.mission, args.tracer, args.drone, args.algoSettings, pathState]
  );

  function clearPath(): void {
    setPath(null);
  }

  return {
    path,
    hasPath: !!path,
    generatePathHttp,
    clearPath,
  };
}
