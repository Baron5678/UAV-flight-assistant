export const SERVER_URL: string = "http://127.0.0.1:8000"

export type Method = "GET" | "POST" | "HEAD"

export type RouteKey =
    | "mission.start"
    | "mission.finish"
    | "mission.cancel"
    | "path.preview"
    | "waypoint.add"
    | "waypoint.delete"
    | "summary.get"
    | "restore.get"
    | "waypoint.add_random"
    ;

export const ROUTES: Record<RouteKey, { method: Method; path: string }> = {
    "mission.start": { method: "POST", path: "/start_mission" },
    "mission.finish": { method: "POST", path: "/finish_mission" },
    "mission.cancel": { method: "POST", path: "/cancel_mission" },
    "path.preview": { method: "POST", path: "/path" },
    "waypoint.add": { method: "POST", path: "/add_point" },
    "waypoint.delete": { method: "POST", path: "/delete_point" },
    "summary.get": { method: "GET", path: "/path_summary/{mission_id}" },
    "restore.get" : { method: "GET", path: "/missions/{mission_id}/restore_waypoints"},
    "waypoint.add_random": { method: "POST", path: "/add_waypoints" },

};


export interface ResponseSuccessUAV<T> {
    failed: false
    http_status: number
    body: T
}

export interface ResponseErrorUAV {
    failed: true
    http_status: number
    error: string
}

export interface Url {
    method: 'GET' | 'POST' | 'DELETE'
    path: string
}

