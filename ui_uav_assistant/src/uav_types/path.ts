import type {Algo} from "./algo";
export type PathRenderMode = "FINAL_ONLY" | "EACH_GENERATION";

export type LatLonTuple = [number, number];
export interface Path {
    waypoint_ids: number[];
    waypoint_coords: LatLonTuple[];
    total_distance_m: number;
    cost: number;
    generations: number;
    population_size: number;
    algo: Algo;
    seed?: number | null;
    sigma0?: number | null;
    mutationProbability?: number | null;
    keepElitism?: number | null;
    kTournament?: number | null;
}

export interface PathState {
  setPath: (p: Path | null) => void;
}

