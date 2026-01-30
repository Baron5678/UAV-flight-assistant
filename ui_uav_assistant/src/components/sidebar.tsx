import React, {useEffect, useMemo, useState} from "react";
import { useForm } from "react-hook-form";
import type { WaypointRole } from "../uav_types/waypoint";
import type { Drone } from "../uav_types/drone";
import type {AlgoSettings, Objective} from "../uav_types/algo";
import { MissionStatus } from "../uav_types/mission";
import {OptimizerErrorResponse} from "../api/path_http/dto";
export interface SidebarProps {
    role: WaypointRole;
    setRole: (r: WaypointRole) => void;
    windSpeed: number
    setWindSpeed: (w: number) => void;
    windDirection: number
    setWindDirection: (w: number) => void;
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
    onRestoreWaypoints: (missionId: number) => Promise<void>;
    onAddRandomWaypoints: (size: number, seed: number) => void | Promise<void>;
}

type SidebarFormValues = {
    role: WaypointRole;
    windSpeed: number;
    windDirection: number;
    batteryWh: Drone["batteryWh"];
    whPerKm: Drone["whPerKm"];
    speed: Drone["speed"];
    populationSize: AlgoSettings["populationSize"];
    generations: AlgoSettings["generations"];
    algo: AlgoSettings["algo"];
    objectiveFunction: AlgoSettings["objectiveFunction"];
    mutationProbability: AlgoSettings["mutationProbability"];
    keepElitism: AlgoSettings["keepElitism"];
    kTournament: AlgoSettings["kTournament"];
    sigma0: AlgoSettings["sigma0"];
    seed: AlgoSettings["seed"];
    streamGenerations: boolean;
    randomWaypointCount: number;
    seedWaypoints: number | null;
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
    v: Pick<SidebarFormValues, "batteryWh" | "whPerKm" | "speed">,
    setDrone: React.Dispatch<React.SetStateAction<Drone>>
) {
    setDrone((d) => ({
        ...d,
        batteryWh: v.batteryWh,
        whPerKm: v.whPerKm,
        speed: v.speed
    }));
}
function applyAlgoFormToState(
    v: Pick<
        SidebarFormValues,
        | "populationSize"
        | "generations"
        | "algo"
        | "objectiveFunction"
        | "seed"
        | "mutationProbability"
        | "keepElitism"
        | "kTournament"
        | "sigma0"
    >,
    setAlgoSettings: React.Dispatch<React.SetStateAction<AlgoSettings>>
) {
    setAlgoSettings((s) => ({
        ...s,
        populationSize: v.populationSize,
        generations: v.generations,
        objectiveFunction: v.objectiveFunction,
        algo: v.algo,
        seed: v.seed ?? null,
        mutationProbability: v.mutationProbability ?? null,
        keepElitism: v.keepElitism ?? null,
        kTournament: v.kTournament ?? null,
        sigma0: v.sigma0 ?? null,

    }));
}
function Underlined(props: { children: React.ReactNode; className?: string }) {
    return (
        <span className={`underline underline-offset-2 decoration-rose-400 font-semibold ${props.className ?? ""}`}>
            {props.children}
        </span>
    );
}
function tryParseOptimizerError(line: string): OptimizerErrorResponse | null {
    const s = line.trim();
    if (!s.startsWith("{") || !s.includes(`"type"`)) return null;
    try {
        const obj = JSON.parse(s);
        if (obj?.type !== "diagnostic") return null;
        if (typeof obj.message !== "string") return null;
        return obj as OptimizerErrorResponse;
    } catch {
        return null;
    }
}
function renderOptimizerError(msg: OptimizerErrorResponse, key: React.Key) {
    return (
        <div
            key={key}
            className="whitespace-pre-wrap border border-red-500/40 bg-red-950/20 px-2 py-2"
        >
            <div className="text-red-200 font-semibold">OPTIMIZER ERROR</div>
            <div className="mt-1 text-slate-100">
                <Underlined className="decoration-sky-400">{msg.message}</Underlined>
            </div>
        </div>
    );
}
function renderTracerLine(line: string, key: React.Key) {
    const routeValidation = tryParseOptimizerError(line);
    if (routeValidation) {
        return renderOptimizerError(routeValidation, key);
    }
    return (
        <div key={key} className="whitespace-pre-wrap">
            {line}
        </div>
    );
}
export default function Sidebar(props: SidebarProps) {
    const missionActive = props.missionStatus === "active";
    const [restoreMissionId, setRestoreMissionId] = useState<string>("");
    const sideBarCls =
        "flex h-full flex-col gap-4 overflow-auto border-r border-slate-700 bg-slate-950 text-slate-100 p-4 " +
        "scrollbar-thin scrollbar-track-slate-900 scrollbar-thumb-slate-600 hover:scrollbar-thumb-slate-500";
    const defaultValues: SidebarFormValues = useMemo(
        () => ({
            role: props.role,
            windSpeed: props.windSpeed,
            windDirection: props.windDirection,
            batteryWh: Number(props.drone.batteryWh ?? 0),
            whPerKm: Number(props.drone.whPerKm ?? 0),
            speed: Number(props.drone.speed ?? 0),
            populationSize: Number(props.algoSettings.populationSize ?? 1),
            generations: Number(props.algoSettings.generations ?? 1),
            objectiveFunction: props.algoSettings.objectiveFunction ?? "DISTANCE",
            algo: props.algoSettings.algo,
            streamGenerations: props.streamGenerations,
            randomWaypointCount: 10,
            seedWaypoints: 42,
            mutationProbability: 0.1,
            keepElitism: 5,
            kTournament: 3,
            sigma0: 0.25,
            seed: 127,
        }),
        [props.role, props.windDirection, props.windSpeed, props.drone, props.algoSettings, props.streamGenerations]
    );
    const { register, watch, getValues } = useForm<SidebarFormValues>({
        defaultValues,
        mode: "onChange",
    });
    useEffect(() => {
        const sub = watch((v) => {
            if (!v) return;
            props.setRole(v.role ?? props.role);
            props.setWindSpeed(v.windSpeed ?? props.windSpeed);
            props.setWindDirection(v.windDirection ?? props.windDirection);
            applyDroneFormToState(
                {
                    batteryWh: v.batteryWh ?? props.drone.batteryWh,
                    whPerKm: v.whPerKm ?? props.drone.whPerKm,
                    speed: v.speed ?? props.drone.speed,
                },
                props.setDrone
            );
            if (v.objectiveFunction == null) return;
            if (
                typeof v.populationSize === "number" &&
                typeof v.generations === "number" &&
                v.algo
            ) {
                applyAlgoFormToState(
                    {
                        populationSize: v.populationSize,
                        generations: v.generations,
                        objectiveFunction: v.objectiveFunction,
                        algo: v.algo,
                        mutationProbability: v.mutationProbability ?? props.algoSettings.mutationProbability ?? 0.1,
                        keepElitism: v.keepElitism ?? props.algoSettings.keepElitism ?? 5,
                        kTournament: v.kTournament ?? props.algoSettings.kTournament ?? 3,
                        sigma0: v.sigma0 ?? props.algoSettings.sigma0 ?? 0.25,
                        seed: v.seed ?? props.algoSettings.seed ?? 127,
                    },
                    props.setAlgoSettings
                );
            }

            if (typeof v.streamGenerations === "boolean" && v.streamGenerations !== props.streamGenerations) {
                props.setStreamGenerations(v.streamGenerations);
            }
        });
        return () => sub.unsubscribe();
        }, [
            watch,
        props.role,
        props.setRole,
        props.windDirection,
        props.setWindDirection,
        props.windSpeed,
        props.setWindSpeed,
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
                    <label className={labelCls}>Wind speed:</label>
                    <input
                        type="number"
                        min={1}
                        max={10000}
                        className={controlBase}
                        {...register("windSpeed", { valueAsNumber: true, min: 1, max: 10000 })}
                    />
                    <label className={labelCls}>Wind direction:</label>
                    <input
                        type="number"
                        min={1}
                        max={10000}
                        className={controlBase}
                        {...register("windDirection", { valueAsNumber: true, min: 1, max: 10000 })}
                    />
                    <label className={labelCls}>Waypoint number:</label>
                    <input
                        type="number"
                        min={1}
                        max={10000}
                        className={controlBase}
                        {...register("randomWaypointCount", { valueAsNumber: true, min: 1, max: 10000 })}
                    />
                    <label className={labelCls}>Waypoint seed:</label>
                    <input
                        type="number"
                        min={1}
                        max={100}
                        className={controlBase}
                        {...register("seedWaypoints", { valueAsNumber: true, min: 1, max: 10000 })}
                    />
                    <button
                        type="button"
                        className={btnNeutral}
                        onClick={() => {
                            const n = Number(getValues("randomWaypointCount"));
                            const seed = Number(getValues("seedWaypoints"))
                            if (!Number.isFinite(n) || n < 1) {
                                alert("Waypoint number must be >= 1");
                                return;
                            }
                            void Promise.resolve(props.onAddRandomWaypoints(n, seed));
                        }}
                    >
                        Add random
                    </button>
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
                     <label htmlFor="speed" className={labelCls}>
                        Speed (m/s)
                    </label>
                    <input
                        id="speed"
                        type="number"
                        min={1}
                        max={5000}
                        className={controlBase}
                        {...register("speed", { valueAsNumber: true })}
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
                        <option value="BF">Exact</option>
                    </select>

                    <label htmlFor="objectiveFunction" className={labelCls}>
                        Objective
                    </label>
                    <select id="objectiveFunction" className={controlBase} {...register("objectiveFunction")}>
                        <option value="DISTANCE">Distance</option>
                        <option value="ENERGY">Battery</option>
                        <option value="WEATHER">Weather</option>
                    </select>
                    {/* Seed */}
                    <label htmlFor="seed" className={labelCls}>
                        Seed
                    </label>
                    <input
                        id="seed"
                        type="number"
                        min={0}
                        className={controlBase}
                        {...register("seed", {
                            setValueAs: (v) => (v === "" || v == null ? null : Number(v)),
                        })}
                    />
                    {/* GA parameters */}
                    <label htmlFor="mutationProbability" className={labelCls}>
                        Mutation probability
                    </label>
                    <input
                        id="mutationProbability"
                        type="number"
                        step="0.01"
                        min={0}
                        max={1}
                        className={controlBase}
                        {...register("mutationProbability", {
                            setValueAs: (v) => (v === "" || v == null ? null : Number(v)),
                        })}
                    />
                    <label htmlFor="keepElitism" className={labelCls}>
                        Keep elitism
                    </label>
                    <input
                        id="keepElitism"
                        type="number"
                        min={0}
                        className={controlBase}
                        {...register("keepElitism", {
                            setValueAs: (v) => (v === "" || v == null ? null : Number(v)),
                        })}
                    />
                    <label htmlFor="kTournament" className={labelCls}>
                        Tournament size (k)
                    </label>
                    <input
                        id="kTournament"
                        type="number"
                        min={2}
                        max={50}
                        className={controlBase}
                        {...register("kTournament", {
                            setValueAs: (v) => (v === "" || v == null ? null : Number(v)),
                        })}
                    />
                    {/* ES / CMA-ES parameter */}
                    <label htmlFor="sigma0" className={labelCls}>
                        Sigma₀
                    </label>
                    <input
                        id="sigma0"
                        type="number"
                        step="0.01"
                        min={0.001}
                        max={10}
                        className={controlBase}
                        {...register("sigma0", {
                            setValueAs: (v) => (v === "" || v == null ? null : Number(v)),
                        })}
                    />
                </fieldset>
                {/* Restore */}
                <fieldset className={panelCls}>
                    <legend className={legendCls}>Restore</legend>
                    <label htmlFor="restoreMissionId" className={labelCls}>
                        Mission ID
                    </label>
                    <div className="grid grid-cols-2 gap-2">
                        <input
                            id="restoreMissionId"
                            type="number"
                            min={1}
                            className={controlBase}
                            value={restoreMissionId}
                            onChange={(e) => setRestoreMissionId(e.target.value)}
                            placeholder="e.g. 12"
                        />
                        <button
                            type="button"
                            className={btnNeutral}
                            onClick={async () => {
                                const id = Number(restoreMissionId);
                                if (!Number.isFinite(id) || id <= 0) {
                                    alert("Enter a valid mission id.");
                                    return;
                                }
                                await props.onRestoreWaypoints(id);
                            }}
                        >
                            Restore waypoints
                        </button>
                    </div>
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
                            className={btnNeutral}
                        >
                            Generate path
                        </button>

                        <button
                            type="button"
                            onClick={props.onCancelMission}
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
