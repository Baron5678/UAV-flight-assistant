// components/summary/SummaryPlot.tsx
import React, { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

import type { PathSummaryData } from "../../uav_types/summary";
import {Algo} from "../../uav_types/algo";

export interface SummaryPlotProps {
  data: PathSummaryData[];
}

function metersToKm(meters: number){
    return (meters / 1000).toFixed(2);
}


export default function SummaryPlot({ data }: SummaryPlotProps) {
  const chartData = useMemo(() => {
    return [...data].sort((a, b) => a.generation - b.generation);
  }, [data]);

  return (
    <div className="border border-slate-700 bg-slate-900/60 p-4 ">
      <ResponsiveContainer width="100%" height={320}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis
            dataKey="gen"
            label={{ value: "Generation", position: "insideBottom", offset: -20 }}
          />

          <YAxis
            yAxisId="left"
            tickFormatter={metersToKm}
            label={{ value: "Fitness cost", angle: -90, position: "insideLeft"}}
          />

          <YAxis
            yAxisId="right"
            orientation="right"
            tickFormatter={metersToKm}
            label={{ value: "Distance (m)", angle: -90, position: "insideRight" }}
          />

          <Tooltip
           formatter={(value, name) => {
             if (name === "Distance (m)") {
                 return [`${metersToKm(value as number)} km`, "Distance"];
             }
             return [value, name];
           }}
          />
          <Legend
            verticalAlign="top"
            align="center"
            wrapperStyle={{ paddingBottom: 12 }}/>

          <Line
            yAxisId="left"
            type="monotone"
            dataKey="fitness_cost"
            name="Fitness cost"
            stroke="#3b82f6"
            strokeWidth={2}
            dot={false}
          />

          <Line
            yAxisId="right"
            type="monotone"
            dataKey="distance"
            name="Distance (m)"
            stroke="#f97316"
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
