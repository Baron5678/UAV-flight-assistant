import React, { useEffect, useMemo } from "react";
import { useForm } from "react-hook-form";

import type { WaypointRole } from "../uav_types/waypoint";
import type { Drone } from "../uav_types/drone";
import type {AlgoSettings, Objective} from "../uav_types/algo";
import { MissionStatus } from "../uav_types/mission";
import {RouteEnergyFailureResponse} from "../api/path_http/dto";

export interface SidebarProps {
  role: WaypointRole;
  setRole: (r: WaypointRole) => void;
  drone: Drone;
  setDrone: React.Dispatch<React.SetStateAction<Drone>>;
  algoSettings: AlgoSettings;
  setAlgoSettings: React.Dispatch<React.SetStateAction<AlgoSettings>>;
  streamGenerations: boolean;
  setStreamGenerations: (v: boolean) => void;
  bestCost: number | null;
  tracerLines: string[];
  missionStatus: MissionStatus;
  canFinish: boolean;
  onStartMission: () => void;
  onFinishMission: () => void;
  onGeneratePath: () => void;
  onCancelMission: () => void;
  onResetApplication: () => void;
}

type SidebarFormValues = {
  role: WaypointRole;
  batteryWh: Drone["batteryWh"];
  whPerKm: Drone["whPerKm"];
  populationSize: AlgoSettings["populationSize"];
  generations: AlgoSettings["generations"];
  algo: AlgoSettings["algo"];
  objectiveFunction: AlgoSettings["objectiveFunction"];
  streamGenerations: boolean;
};
const panelCls =
  "groupbox rounded-none border border-slate-600/70 bg-slate-900/60 shadow-none";

const legendCls =
  "px-2 text-[11px] font-semibold uppercase tracking-wider text-slate-200";

const labelCls = "text-[12px] font-medium text-slate-200";

const controlBase =
  "w-full rounded-none border border-slate-600/70 bg-slate-950/60 " +
  "px-3 py-2 text-sm text-slate-100 placeholder:text-slate-500 " +
  "focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-sky-500 " +
  "disabled:opacity-50 disabled:cursor-not-allowed";

const btnBase =
  "inline-flex w-full items-center justify-center rounded-none px-3 py-2 text-sm font-semibold " +
  "border border-slate-600/70 transition " +
  "disabled:opacity-50 disabled:cursor-not-allowed";

const btnPrimary = `${btnBase} bg-sky-600 text-white hover:bg-sky-500 active:bg-sky-700`;
const btnNeutral = `${btnBase} bg-slate-800 text-slate-100 hover:bg-slate-700 active:bg-slate-600`;
const btnDanger = `${btnBase} bg-rose-600 text-white hover:bg-rose-500 active:bg-rose-700`;

function applyDroneFormToState(
  v: Pick<SidebarFormValues, "batteryWh" | "whPerKm">,
  setDrone: React.Dispatch<React.SetStateAction<Drone>>
) {
  setDrone((d) => ({
    ...d,
    batteryWh: v.batteryWh,
    whPerKm: v.whPerKm,
  }));
}

function applyAlgoFormToState(
  v: Pick<SidebarFormValues, "populationSize" | "generations" | "algo" | "objectiveFunction">,
  setAlgoSettings: React.Dispatch<React.SetStateAction<AlgoSettings>>
) {
  setAlgoSettings((s) => ({
      ...s,
      populationSize: v.populationSize,
      generations: v.generations,
      objectiveFunction: v.objectiveFunction,
      algo: v.algo,
  }));
}

type DiagnosticProblem = {
  required_id: number;
  nearest_station_id: number;
  dist_required_to_station_m: number;
  max_leg_m: number;
  nearest_required_id?: number;
  dist_required_to_required_m?: number;
};

type DiagnosticMsg = {
  type: "diagnostic";
  feasible: boolean;
  max_leg_m: number;
  problems: DiagnosticProblem[];
};

type RouteValidationMsg = {
  type: "route_validation";
  feasible: false;
  objective: "ENERGY";
  failure: RouteEnergyFailureResponse;
};

function tryParseRouteValidation(line: string): RouteValidationMsg | null {
  try {
    const obj = JSON.parse(line);
    if (obj?.type !== "route_validation") return null;
    if (obj.feasible !== false) return null;
    if (obj.objective !== "ENERGY") return null;
    return obj as RouteValidationMsg;
  } catch {
    return null;
  }
}

function tryParseDiagnostic(line: string): DiagnosticMsg | null {
  const s = line.trim();
  if (!s.startsWith("{") || !s.includes(`"type"`)) return null;

  try {
    const obj = JSON.parse(s);
    if (obj?.type !== "diagnostic") return null;
    if (typeof obj.feasible !== "boolean") return null;
    if (typeof obj.max_leg_m !== "number") return null;
    if (!Array.isArray(obj.problems)) return null;
    return obj as DiagnosticMsg;
  } catch {
    return null;
  }
}

function Underlined(props: { children: React.ReactNode; className?: string }) {
  return (
    <span className={`underline underline-offset-2 decoration-rose-400 font-semibold ${props.className ?? ""}`}>
      {props.children}
    </span>
  );
}

function renderDiagnostic(msg: DiagnosticMsg, key: React.Key) {
  return (
    <div
      key={key}
      className="whitespace-pre-wrap border border-amber-500/40 bg-amber-950/20 px-2 py-2"
    >
      <div className="text-amber-200 font-semibold">
        STATION REACHABILITY FAILED
      </div>

      {msg.problems.map((p, i) => (
        <div key={i} className="mt-1">
          Required <Underlined>{p.required_id}</Underlined> →
          Station <Underlined>{p.nearest_station_id}</Underlined>
          {"\n"}
          Distance:{" "}
          <Underlined>{p.dist_required_to_station_m.toFixed(1)}</Underlined> m
          {"\n"}
          Max leg: <Underlined>{p.max_leg_m.toFixed(1)}</Underlined> m
        </div>
      ))}
    </div>
  );
}


function renderRouteValidation(
  msg: RouteValidationMsg,
  key: React.Key
) {
  const f = msg.failure;

  return (
    <div
      key={key}
      className="whitespace-pre-wrap border border-red-500/40 bg-red-950/20 px-2 py-2"
    >
      <div className="text-red-200 font-semibold">
        ENERGY ROUTE INFEASIBLE
      </div>

      <div className="mt-1">
        From: <Underlined>{f.from_id}</Underlined> to{" "}
        <Underlined>{f.to_id}</Underlined>
        {"\n"}
        Distance: <Underlined>{f.dist_m.toFixed(1)}</Underlined> m
        {"\n"}
        SOC: <Underlined>{f.soc_wh.toFixed(1)}</Underlined> Wh
        {"\n"}
        Deficit:{" "}
        <Underlined>{f.deficit_m.toFixed(1)}</Underlined> m and{" "}
        <Underlined>{f.deficit_wh.toFixed(1)}</Underlined> Wh
        {"\n"}
        Needed: <Underlined>{f.needed_wh.toFixed(1)}</Underlined> Wh
      </div>
    </div>
  );
}


function renderTracerLine(line: string, key: React.Key) {
  const routeValidation = tryParseRouteValidation(line);
  if (routeValidation) {
    return renderRouteValidation(routeValidation, key);
  }

  const diagnostic = tryParseDiagnostic(line);
  if (diagnostic) {
    return renderDiagnostic(diagnostic, key);
  }

  return (
    <div key={key} className="whitespace-pre-wrap">
      {line}
    </div>
  );
}


export default function Sidebar(props: SidebarProps) {
  const missionActive = props.missionStatus === "active";

  const sideBarCls =
    "flex h-full flex-col gap-4 overflow-auto border-r border-slate-700 bg-slate-950 text-slate-100 p-4 " +
    "scrollbar-thin scrollbar-track-slate-900 scrollbar-thumb-slate-600 hover:scrollbar-thumb-slate-500";

  const defaultValues: SidebarFormValues = useMemo(
    () => ({
        role: props.role,
        batteryWh: Number(props.drone.batteryWh ?? 0),
        whPerKm: Number(props.drone.whPerKm ?? 0),
        populationSize: Number(props.algoSettings.populationSize ?? 1),
        generations: Number(props.algoSettings.generations ?? 1),
        objectiveFunction: props.algoSettings.objectiveFunction ?? "DISTANCE",
        algo: props.algoSettings.algo,
        streamGenerations: props.streamGenerations,
    }),
    [props.role, props.drone, props.algoSettings, props.streamGenerations]
  );

  const { register, watch, reset } = useForm<SidebarFormValues>({
    defaultValues,
    mode: "onChange",
  });

  useEffect(() => {
    reset(defaultValues);
  }, [defaultValues, reset]);

  useEffect(() => {
    const sub = watch((v) => {
      if (!v) return;
      if (v.role && v.role !== props.role) {
        props.setRole(v.role);
      }
      if (
        typeof v.batteryWh === "number" &&
        typeof v.whPerKm === "number" &&
        (v.batteryWh !== props.drone.batteryWh || v.whPerKm !== props.drone.whPerKm)
      ) {
        applyDroneFormToState({ batteryWh: v.batteryWh, whPerKm: v.whPerKm }, props.setDrone);
      }
      if (v.objectiveFunction == null) return;
      if (
        typeof v.populationSize === "number" &&
        typeof v.generations === "number" &&
            v.algo &&
           (v.populationSize !== props.algoSettings.populationSize ||
            v.generations !== props.algoSettings.generations ||
            v.algo !== props.algoSettings.algo ||
            v.objectiveFunction !== props.algoSettings.objectiveFunction)
      ) {
        applyAlgoFormToState(
          { populationSize: v.populationSize, generations: v.generations, objectiveFunction: v.objectiveFunction, algo: v.algo },
          props.setAlgoSettings
        );
      }

      // Streaming toggle
      if (typeof v.streamGenerations === "boolean" && v.streamGenerations !== props.streamGenerations) {
        props.setStreamGenerations(v.streamGenerations);
      }
    });

    return () => sub.unsubscribe();
  }, [
    watch,
    props.role,
    props.setRole,
    props.drone,
    props.setDrone,
    props.algoSettings,
    props.setAlgoSettings,
    props.streamGenerations,
    props.setStreamGenerations,
  ]);

  return (
    <section id="sidebar" className={sideBarCls}>
      <form onSubmit={(e) => e.preventDefault()} className="flex flex-col gap-4">
        {/* Mission Setup */}
        <fieldset className={panelCls}>
          <legend className={legendCls}>Mission Setup</legend>

          <label htmlFor="role" className={labelCls}>
            Waypoint role
          </label>
          <select id="role" className={controlBase} {...register("role")}>
            <option value="REQUIRED">Required</option>
            <option value="START">Start</option>
            <option value="END">End</option>
            <option value="STATION">Station</option>
          </select>
        </fieldset>
          <fieldset className={panelCls}>
          <legend className={legendCls}>Drone Energy Model</legend>

          <label htmlFor="batteryWh" className={labelCls}>
            Battery capacity (Wh)
          </label>
          <input
            id="batteryWh"
            type="number"
            min={100}
            max={20000}
            className={controlBase}
            {...register("batteryWh", { valueAsNumber: true })}
          />

          <label htmlFor="whPerKm" className={labelCls}>
            Consumption (Wh/km)
          </label>
          <input
            id="whPerKm"
            type="number"
            min={1}
            max={5000}
            className={controlBase}
            {...register("whPerKm", { valueAsNumber: true })}
          />
        </fieldset>
          <fieldset className={panelCls}>
          <legend className={legendCls}>Solver Settings</legend>
          <label htmlFor="populationSize" className={labelCls}>
            Population size
          </label>
          <input
            id="populationSize"
            type="number"
            min={1}
            max={2000}
            className={controlBase}
            {...register("populationSize", { valueAsNumber: true })}
          />

          <label htmlFor="generations" className={labelCls}>
            Generations
          </label>
          <input
            id="generations"
            type="number"
            min={1}
            max={20000}
            className={controlBase}
            {...register("generations", { valueAsNumber: true })}
          />

          <label htmlFor="algo" className={labelCls}>
            Algorithm
          </label>
          <select id="algo" className={controlBase} {...register("algo")}>
            <option value="GA">Genetic Algorithm (GA)</option>
            <option value="ES">Evolution Strategy (ES)</option>
          </select>

          <label htmlFor="objectiveFunction" className={labelCls}>
            Objective
          </label>
          <select id="objectiveFunction" className={controlBase} {...register("objectiveFunction")}>
            <option value="DISTANCE">Distance</option>
            <option value="ENERGY">Battery</option>
            <option value="WEATHER">Weather</option>
          </select>
        </fieldset>

        {/* Execution */}
        <fieldset className={`${panelCls} actions-groupbox`}>
          <legend className={legendCls}>Execution</legend>

          <div className="col-span-full flex items-center gap-3 border border-slate-600/70 bg-slate-950/40 px-3 py-2">
            <input
              id="toggle-stream-generations"
              type="checkbox"
              className="h-4 w-4 rounded-none border-slate-500 text-sky-500 focus:ring-sky-500"
              {...register("streamGenerations")}
            />
            <label htmlFor="toggle-stream-generations" className="select-none text-sm text-slate-100">
              Stream generations (WebSocket)
            </label>
          </div>

          <div className="actions-grid col-span-full grid grid-cols-2 gap-2">
            <button type="button" onClick={props.onStartMission} className={btnPrimary}>
              Start mission
            </button>

            <button
              type="button"
              onClick={props.onFinishMission}
              disabled={!missionActive || !props.canFinish}
              className={btnNeutral}
            >
              Finish mission
            </button>

            <button
              type="button"
              onClick={props.onGeneratePath}
              disabled={!missionActive}
              className={btnNeutral}
            >
              Generate path
            </button>

            <button
              type="button"
              onClick={props.onCancelMission}
              disabled={!missionActive}
              className={btnNeutral}
            >
              Cancel mission
            </button>

            <button type="button" onClick={props.onResetApplication} className={`${btnDanger} col-span-2`}>
              Reset application
            </button>
          </div>
        </fieldset>
      </form>

      <section
        className="flex min-h-[30vh] max-h-[40vh] flex-col overflow-hidden border border-slate-600/70 bg-black/80"
        aria-label="Computation tracer"
      >
        <div className="border-b border-white/10 px-3 py-2 text-[11px] font-semibold uppercase tracking-wider text-slate-200">
          Tracer
        </div>

        <div className="flex-1 overflow-y-auto px-3 py-2 font-mono text-xs leading-5 text-slate-200 scrollbar-thin scrollbar-track-black scrollbar-thumb-slate-700">
          {props.tracerLines.length === 0 ? (
            <div className="text-slate-400">Logs…</div>
          ) : (
            props.tracerLines.map((line, idx) => renderTracerLine(line, idx)))}
        </div>
      </section>
    </section>
  );
}
