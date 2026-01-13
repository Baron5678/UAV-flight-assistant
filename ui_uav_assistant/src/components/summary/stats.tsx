// components/summary/SummaryStatsTable.tsx
import React, { useMemo } from "react";
import type { PathSummaryStats } from "../../uav_types/summary";

export interface SummaryStatsTableProps {
  stats: PathSummaryStats | null;
}

function fmtNum(x: number, digits: number = 2): string {
  if (!Number.isFinite(x)) return "—";
  return x.toFixed(digits);
}

function fmtMeters(m: number): string {
  if (!Number.isFinite(m)) return "—";
  if (m >= 1000) return `${(m / 1000).toFixed(2)} km`;
  return `${m.toFixed(0)} m`;
}

function fmtPct(p: number): string {
  if (!Number.isFinite(p)) return "—";
  return `${p.toFixed(2)}%`;
}

type Row = { label: string; value: string };

export default function SummaryStatsTable({ stats }: SummaryStatsTableProps) {
  const groups = useMemo(() => {
    if (!stats) return [];

    const costRows: Row[] = [
      { label: "Best cost", value: fmtNum(stats.best_cost, 2) },
      { label: "First cost", value: fmtNum(stats.first_cost, 2) },
      { label: "Min cost", value: fmtNum(stats.min_cost, 2) },
      { label: "Max cost", value: fmtNum(stats.max_cost, 2) },
      { label: "Avg cost", value: fmtNum(stats.avg_cost, 2) },
    ];

    const distRows: Row[] = [
      { label: "Min distance", value: fmtMeters(stats.min_total_distance_m) },
      { label: "Max distance", value: fmtMeters(stats.max_total_distance_m) },
      { label: "Avg distance", value: fmtMeters(stats.avg_total_distance_m) },
    ];

    const gaRows: Row[] = [
      { label: "Improvement (abs)", value: fmtNum(stats.improvement_abs, 2) },
      { label: "Improvement (%)", value: fmtPct(stats.improvement_pct * 100) },
      { label: "Improving generations", value: String(stats.improving_generations) },
      {
        label: "Last improvement generation",
        value: stats.last_improvement_generation == null ? "—" : String(stats.last_improvement_generation),
      },
      { label: "Max stagnation (generations)", value: String(stats.max_stagnation_generations) },
    ];

    return [
      { title: "Cost", rows: costRows },
      { title: "Distance", rows: distRows },
      { title: "GA progress", rows: gaRows },
    ];
  }, [stats]);

  if (!stats) {
    return (
      <div className="rounded-lg border border-slate-700 bg-slate-900/60 p-3 text-sm text-slate-300">
        No statistics available.
      </div>
    );
  }

  return (
    <div className="rounded-lg border border-slate-700 bg-slate-900/60 p-3">
      <div className="grid gap-4">
        {groups.map((g) => (
          <div key={g.title}>
            <div className="mb-2 text-sm font-semibold text-slate-200">{g.title}</div>

            <div className="overflow-hidden rounded-md border border-slate-800">
              <table className="w-full border-collapse text-sm">
                <tbody>
                  {g.rows.map((r) => (
                    <tr key={r.label} className="border-b border-slate-800 last:border-b-0">
                      <td className="px-3 py-2 text-slate-300">{r.label}</td>
                      <td className="px-3 py-2 text-right font-semibold text-slate-100">{r.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
