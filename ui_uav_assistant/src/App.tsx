import React, {useState} from "react";
import MapView from "./map/map";
import Sidebar from "./components/sidebar";
import { useUavAppController } from "./hooks/useUavAppController";
import {PageKey} from "./uav_types/base";
import SummaryPage from "./components/summary/plot";
import Summary from "./components/summary/summary";


function Page({ active, children }: { active: boolean; children: React.ReactNode }) {
    if (!active) return null;
  return <div className="h-full min-h-0" hidden={!active}>{children}</div>;
}

export default function App() {
    const vm = useUavAppController();
    let [page, setPage] = useState<PageKey>("DRONE_PLANNER")

  return (
      <>
          <header className="border-b border-slate-700 bg-slate-900 px-2">
              <button id="tab" content="Map" className={`px-4 py-2 text-sm font-medium border-b-2  
                      ${page === "DRONE_PLANNER" ? "border-blue-500 text-blue-400" : "border-transparent text-slate-200"}`}
                      onClick={() => {setPage("DRONE_PLANNER")}}
              >
                  Map
              </button>
              <button id="tab" content="Algorithm Summary" className={`px-4 py-2 color-white text-sm font-medium border-b-2  
                      ${page === "ALGO_SUMMARY" ? "border-blue-500 text-blue-400" : "border-transparent text-slate-200 "}`}
                      onClick={() => {setPage("ALGO_SUMMARY")}}
              >
                Summary
              </button>
          </header>
          <Page active={page === "DRONE_PLANNER"}>
              <main className="layout h-full">
                  <Sidebar
                      role={vm.role}
                      setRole={vm.setRole}
                      windSpeed={vm.windSpeed}
                      setWindSpeed={vm.setWindSpeed}
                      windDirection={vm.windDirection}
                      setWindDirection={vm.setWindDirection}
                      drone={vm.drone}
                      setDrone={vm.setDrone}
                      algoSettings={vm.algoSettings}
                      setAlgoSettings={vm.setAlgoSettings}
                      streamGenerations={vm.streamGenerations}
                      setStreamGenerations={vm.setStreamGenerations}
                      bestCost={vm.pathCost}
                      tracerLines={vm.tracerLines}
                      missionStatus={vm.missionStatus}
                      canFinish={vm.hasPath}
                      onStartMission={vm.onStartMission}
                      onFinishMission={vm.onFinishMission}
                      onGeneratePath={vm.onGeneratePath}
                      onCancelMission={vm.onCancelMission}
                      onResetApplication={vm.onResetApplication}
                      onRestoreWaypoints={vm.onRestoreWaypointsSafe}
                      onAddRandomWaypoints={vm.onAddRandomWaypointsSafe}
                  />
                  <div id="map">
                      <MapView
                          waypoints={vm.waypoints}
                          pathCoords={vm.pathCoords}
                          pathCost={vm.pathCost}
                          onMapClick={vm.onMapClick}
                          onDeleteWaypoint={vm.onDeleteWaypoint}
                      />
                  </div>
              </main>
          </Page>

          <Page active={page === "ALGO_SUMMARY"}>
             <Summary missionId={vm.missionId} algo={vm.algoSettings.algo} objective={vm.algoSettings.objectiveFunction}/>
          </Page>
      </>
  );
}
