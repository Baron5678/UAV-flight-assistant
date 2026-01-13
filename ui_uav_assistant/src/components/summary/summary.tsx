import React, { useEffect, useMemo, useState } from "react";

import {ExportZipButtonAsButton} from "./export";
import SummaryPlot from "./plot";
import SummaryStatsTable from "./stats";

import type {
  PathSummaryData,
  PathSummaryStats,
} from "../../uav_types/summary";


import { getSummary } from "../../handlers/summary";
import {PathSummaryResponseDto} from "../../api/path_summary/dto";
import {Algo, Objective} from "../../uav_types/algo";

export interface SummaryProps {
  missionId: number | null;
  algo: Algo
    objective: Objective
}


export default function Summary({ missionId, algo, objective }: SummaryProps) {
  const [paths, setPaths] = useState<PathSummaryData[]>([]);
  const [stats, setStats] = useState<PathSummaryStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (missionId == null) {
      setPaths([]);
      setStats(null);
      return;
    }

    let cancelled = false;

    async function load() {
      setLoading(true);
      setError(null);

      try {
        const resp: PathSummaryResponseDto = await getSummary(missionId ?? -1);
        if (cancelled) return;
        console.log(resp)
        setPaths(resp.paths);
        setStats(resp.stats ?? null);
      } catch (e: any) {
        if (!cancelled) {
          setError(e?.message ?? String(e));
          setPaths([]);
          setStats(null);
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }

    load().then();

    return () => {
      cancelled = true;
    };
  }, [missionId]);

  const plotData = useMemo(() => {
    return paths.map((p) => ({
      ...p,
      gen: p.generation,
      fitness_cost: p.cost,
      distance: p.total_distance_m,
    }));
  }, [paths]);

  return (
    <main className="h-full min-h-0 p-3 bg-slate-900">
        <h1 className="text-slate-300 p-2">{algo == "ES" ? "Evolutionary Strategy" : "Genetic Algorithm"}
            ({objective == "ENERGY" ? "Battery" : "Distance"})</h1>
      {missionId == null && (
        <div className="rounded-lg border border-slate-700 bg-slate-900/60 p-3 text-sm text-slate-300">
          No active mission. Start a mission to view summary.
        </div>
      )}


      {loading && (
        <div className="text-sm text-slate-400">Loading summary…</div>
      )}

      {error && (
        <div className="rounded-lg border border-red-700 bg-red-950/40 p-3 text-sm text-red-200">
          Failed to load summary: {error}
        </div>
      )}
        <ExportZipButtonAsButton />
      {!loading && !error && missionId != null && (
        <div className="grid grid-rows-[auto,1fr] gap-3 min-h-0">
          <div className="grid grid-cols-1 gap-3 lg:grid-cols-2 min-h-0">
            <SummaryPlot data={plotData as any} />
            <SummaryStatsTable stats={stats} />
          </div>
          <div className="rounded-lg border border-slate-700 bg-slate-900/60 p-3 text-sm text-slate-300">
            Table component pending (next step).
          </div>
        </div>
      )}
    </main>
  );
}
