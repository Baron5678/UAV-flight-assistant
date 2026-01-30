import { make_request, ResponseUAV } from "../api/client/client";
import { buildCancelMissionRequest, buildFinishMissionRequest } from "../api/mission/request_builders";
import { buildStartMissionRequest } from "../api/mission/request_builders";
import { MissionState } from "../uav_types/mission";
import { AlgoSettings } from "../uav_types/algo";
import { Waypoint } from "../uav_types/waypoint";
import type { TracerApi } from "../cross/logs";
import { FinishMissionResponseDto, StartMissionResponseDto } from "../api/mission/dto";
import type { CancelMissionResponseDto } from "../api/mission/dto";
import {argon2Sync} from "node:crypto";

export interface CancelMissionHandlerArgs {
  mission: MissionState;
  tracer: TracerApi;
  clearPath: () => void;
}

export interface StartMissionHandlerArgs {
  waypoints: Waypoint[];
  settings: AlgoSettings;
  tracer: TracerApi;
  mission: MissionState;
  clearPath: () => void;
}

export interface FinishMissionHandlerArgs {
    mission: MissionState;
    settings: AlgoSettings;
    tracer: TracerApi;
    waypoint_ids: number[];
    total_distance_m: number;
    best_cost: number;
}

export function startMissionHandler(args :StartMissionHandlerArgs) {
  return async function startMission() {
    if (!args.waypoints.length) {
      args.tracer.log("Add waypoints first.");
      return;
    }

    const start = args.waypoints.find(w => w.role === "START");
    const end   = args.waypoints.find(w => w.role === "END");

    if (!start || !end) {
      args.tracer.log("START and END waypoints required.");
      return;
    }

    const dto = buildStartMissionRequest({
        startWaypointId: start.id,
        endWaypointId: end.id,
        waypointIds: args.waypoints.map(w => w.id),
        generations: args.settings.generations,
        populationSize: args.settings.populationSize,
        objectiveFunction: args.settings.objectiveFunction,
        keep_elitism: args.settings.keepElitism,
        mutation_probability: args.settings.mutationProbability,
        seed: args.settings.seed,
        sigma0: args.settings.sigma0,
        k_tournament: args.settings.kTournament,
        algo: args.settings.algo,
    });

    args.clearPath();

    console.log("REQUEST" + dto.objective)

    const res: ResponseUAV<StartMissionResponseDto> = await make_request("mission.start", dto);
    if (res.failed) {
      args.tracer.log(res.error);
      return;
    }

    args.mission.setId(res.body.mission_id);
    args.mission.setStatus("active");
    args.tracer.log(`Mission ${dto.name} started.`);
  };
}


export function finishMissionHandler(args: FinishMissionHandlerArgs) {
  return async function finishMission(): Promise<void> {
    if (!args.mission.id) {
      args.tracer.log("No active mission.");
      return;
    }

    if (!args.best_cost) {
      args.tracer.log("Generate a path first.");
      return;
    }

    const dto = buildFinishMissionRequest({
        missionId: args.mission.id,
        waypointIds: args.waypoint_ids,
        totalDistanceM: args.total_distance_m,
        bestCost: args.best_cost,
        generations: args.settings.generations,
        populationSize: args.settings.populationSize,
        algo: args.settings.algo,
        keep_elitism: args.settings.keepElitism,
        mutation_probability: args.settings.mutationProbability,
        seed: args.settings.seed,
        sigma0: args.settings.sigma0,
        k_tournament: args.settings.kTournament
    });

    const res: ResponseUAV<FinishMissionResponseDto> = await make_request("mission.finish", dto);

    if (res.failed) {
      args.tracer.log(res.error);
      return;
    }

    args.tracer.log(`Mission ${res.body.mission_id} finished.`);
    args.mission.setStatus("idle");
  };
}

export function cancelMissionHandler(args: CancelMissionHandlerArgs) {
  return async function cancelMission(): Promise<void> {
    if (!args.mission.id) {
      args.tracer.log("No active mission.");
      return;
    }

    const dto = buildCancelMissionRequest(args.mission.id);

    const res: ResponseUAV<CancelMissionResponseDto> =
      await make_request("mission.cancel", dto);

    if (res.failed) {
      args.tracer.log(res.error);
      return;
    }

    args.clearPath();
    args.tracer.clear();

    args.mission.setId(null);
    args.mission.setStatus("idle");

    args.tracer.log("Mission cancelled.");
  };
}