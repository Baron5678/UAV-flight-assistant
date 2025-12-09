// src/App.jsx
import "./style.css";
import "leaflet/dist/leaflet.css";
import { useState } from "react";        // <-- add this line
import MapView from "./map/MapView.jsx";
import { useWaypoints } from "./hooks/useWaypoints";
import { useMission } from "./hooks/useMissions";
import {usePaths, usePathsWS} from "./hooks/usePaths";
import {apiResetAll} from "./api/reset.js";

function buildPathRequest(missionId) {
  const algoSelect = document.getElementById("algo");
  const popInput = document.getElementById("pop");
  const genInput = document.getElementById("gen");
  const energyInput = document.getElementById("energy");
  const ratioInput = document.getElementById("ratio");

  return {
    mission_id: missionId,
    algo: algoSelect?.value || "GA",
    generations: Number(genInput?.value || 30),
    population_size: Number(popInput?.value || 20),
    drone : {
      battery_capacity_wh: Number(energyInput?.value || 100),
      wh_per_km: Number(ratioInput?.value || 10),
      reserve_ratio: 0.2,
    },
  };
}


function App() {
  // 1) Waypoints: points + click handling
  const { role, setRole, waypoints, handleMapClick, resetWaypoints, deleteWaypoint } = useWaypoints();
    let lastPathRequest =null  ;
  // 2) Mission: start/cancel/finish, based on waypoints
  const {
    missionId,
    missionStatus,
      setMissionStatus,
    startMission,
    finishMission,
    cancelMission,
      resetMission
  } = useMission(waypoints);

  // 3) Paths: path preview for a mission
  // const {
  //   pathCoords,
  //   pathCost,
  //   lastPathPreview,
  //   hasPath,
  //   generatePathPreview,
  //   clearPath,
  // } = usePaths(missionId);

   const {
    pathCoords,
    pathCost,
    lastPathPreview,
    hasPath,
    generatePathPreview, // now WS-based
    clearPath,
  } = usePathsWS(missionId);

    const [tracerLines, setTracerLines] = useState([]);
    const appendTracerLine = (line) => {
  setTracerLines((prev) => [...prev, line]);
    };

     const clearTracer = () => {
    setTracerLines([]);
  }

  const handleDeleteWaypoint = async (id) => {
    if (missionStatus === "active") {
      alert("Cancel mission before deleting waypoints.");
      return;
    }
    await deleteWaypoint(id);
  };

  const handleGeneratePathWithTrace = () => {
  if (!missionId) {
    alert("Start a mission first.");
    return;
  }

  const req = buildPathRequest(missionId);
lastPathRequest = req;
setTracerLines([]);
  appendTracerLine(
    `Mission ${missionId}: starting ${req.algo} path computation (${req.generations} generations, pop=${req.population_size})…`
  );

  generatePathPreview(req, {
    onTrace: appendTracerLine,
  });
};

  const handleResetApplication = async () => {
    try {
      await apiResetAll();
    } catch (err) {
      console.error(err);
      alert("Failed to reset backend: " + err.message);
    }
    resetWaypoints();
    resetMission();
    clearPath();
    setMissionStatus("idle");
  };

  const handleStartMission = async () => {
    clearPath();
    await startMission();
  };

  const handleCancelMission = async () => {
    await cancelMission();
    clearPath();
    setMissionStatus("idle");
    clearTracer()
  };

  const handleFinishMission = async () => {
    await finishMission(lastPathPreview, lastPathRequest);
    setMissionStatus("idle")
    // optionally clear path after finish:
    // clearPath();
      clearTracer();
  };

  return (
    <>
      <main className="layout">
        <section id="sidebar">
          <form>
            {/* Scouting options */}
            <fieldset className="groupbox">
              <legend>Scouting options</legend>
              <label htmlFor="role">Waypoint&apos;s type:</label>
              <select
                id="role"
                value={role}
                onChange={(e) => setRole(e.target.value.toUpperCase())}
              >
                <option value="REQUIRED">Required</option>
                <option value="START">Start</option>
                <option value="END">End</option>
                <option value="STATION">Station</option>
              </select>
            </fieldset>

            {/* Drone Settings */}
            <fieldset className="groupbox">
              <legend>Drone Settings</legend>
              <label htmlFor="energy">State of Charge:</label>
              <input id="energy" type="number" min="1" max="599" defaultValue="1" />
              <label htmlFor="ratio">Power per point:</label>
              <input id="ratio" type="number" min="1" max="599" defaultValue="1" />
            </fieldset>

            {/* GA Settings */}
            <fieldset className="groupbox">
              <legend>GA Settings</legend>
              <label htmlFor="pop">Population Size:</label>
              <input id="pop" type="number" min="1" max="200" defaultValue="1" />
              <label htmlFor="gen">Generations:</label>
              <input id="gen" type="number" min="1" max="599" defaultValue="1" />
              <label htmlFor="fit">Fitness criteria:</label>
              <select id="fit" defaultValue="Shortest Distance">
                <option>Shortest Distance</option>
              </select>
              <label htmlFor="algo">Algorithm:</label>
              <select id="algo" defaultValue="GA">
                <option value="GA">GA</option>
                <option value="ES">ES</option>
              </select>
              <label htmlFor="cost">Best Cost:</label>
              <input
                id="cost"
                type="number"
                min="1"
                max="599"
                defaultValue="1"
                disabled
              />
            </fieldset>
          </form>
            <section className="tracer-panel" aria-label="Computation tracer">
            <div className="tracer-header">Tracer</div>
            <div className="tracer-body">
              {tracerLines.length === 0 ? (
                <div className="tracer-placeholder">
                  Logs....
                </div>
              ) : (
                tracerLines.map((line, idx) => (
                  <div key={idx} className="tracer-line">
                    {line}
                  </div>
                ))
              )}
            </div>
          </section>
        </section>

        <div id="map">
          <MapView
            waypoints={waypoints}
            pathCoords={pathCoords}
            pathCost={pathCost}
            onMapClick={handleMapClick}
            onDeleteWaypoint={handleDeleteWaypoint}
          />
        </div>
      </main>

      <footer className="footer-actions">
        <button
          id="btn-start-mission"
          type="button"
          onClick={handleStartMission}
        >
          Start mission
        </button>

        <button
          id="btn-finish"
          type="button"
          onClick={handleFinishMission}
          disabled={missionStatus !== "active"}
        >
          Finish mission
        </button>

        <button
          id="btn-generate"
          type="button"
          onClick={handleGeneratePathWithTrace}
          disabled={missionStatus !== "active"}
        >
          Generate scouting path
        </button>

        <button
          id="btn-cancel"
          type="button"
          onClick={handleCancelMission}
            disabled={missionStatus !== "active"}
        >
          Cancel mission
        </button>

        <button
          id="btn-reset"
          type="button"
          onClick={handleResetApplication}
        >
          Reset application
        </button>
      </footer>

      <div className="stat" id="stats" />
    </>
  );
}

export default App;
