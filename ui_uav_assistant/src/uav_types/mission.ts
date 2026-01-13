import {AlgoSettings} from "./algo";

export type MissionStatus = "idle" | "active";

export interface Mission {
    id: number;
    name: string;
    waypointIds: number[];
    startWaypointId: number;
    endWaypointId: number;
    status: MissionStatus;
    settings: AlgoSettings
}

export interface MissionState {
  id: number | null;
  setId: (id: number | null) => void;
  status: MissionStatus;
  setStatus: (s: MissionStatus) => void;
}
