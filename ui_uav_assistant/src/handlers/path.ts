import type { MissionState} from "../uav_types/mission";
import type { TracerApi } from "../cross/logs";
import type {PathPreviewHttpResponse, PathResponseDto} from "../api/path_http/dto";
import type { PathState, Path } from "../uav_types/path";
import { buildGeneratePathRequest } from "../api/path_http/request_builders";
import { make_request, ResponseUAV } from "../api/client/client";
import {Drone} from "../uav_types/drone";
import {AlgoSettings} from "../uav_types/algo";

export interface GeneratePathHttpHandlerArgs {
  mission: MissionState;
  tracer: TracerApi;
  path: PathState;
  algoSettings: AlgoSettings
  drone: Drone;
}

export function generatePathHttpHandler(args: GeneratePathHttpHandlerArgs) {
  return async function generatePathHttp(): Promise<void> {
    if (!args.mission.id) {
      args.tracer.log("Start a mission first.");
      return;
    }

    const dto = buildGeneratePathRequest({
        missionId: args.mission.id,
        algo: args.algoSettings.algo,
        generations: args.algoSettings.generations,
        populationSize: args.algoSettings.populationSize,
        batteryWh: args.drone.batteryWh,
        whPerKm: args.drone.whPerKm,
        objectiveFunction: args.algoSettings.objectiveFunction,
        reserveRatio: args.drone.reserveRatio,
        seed: args.algoSettings.seed ?? null,
        mutationProbability: args.algoSettings.mutationProbability ?? null,
        keepElitism: args.algoSettings.keepElitism ?? null,
        kTournament: args.algoSettings.kTournament ?? null,
        sigma0: args.algoSettings.sigma0 ?? null,

    });
    console.log(dto)
    const res:ResponseUAV<PathPreviewHttpResponse> = await make_request("path.preview", dto);
    console.log(res)
    if (res.failed) {
      args.tracer.log(res.error);
      return;
    }

    if (res.body.type === "diagnostic") {
        args.tracer.log(JSON.stringify(res.body));
        args.path.setPath(null);
        return;
    }

    const path: Path = {
        waypoint_ids: res.body.waypoint_ids,
        waypoint_coords: res.body.waypoint_coords,
        cost: res.body.best_cost,
        total_distance_m: res.body.total_distance_m,
        generations: res.body.generations,
        population_size: res.body.population_size,
        keepElitism: res.body.keep_elitism,
        mutationProbability: res.body.mutation_probability,
        seed: res.body.seed,
        sigma0: res.body.sigma0,
        kTournament: res.body.k_tournament,
        algo: res.body.algo,
    };

    args.path.setPath(path);
    args.tracer.log(`Path preview ready. Cost=${path.cost ?? "n/a"}`);
  };
}
