"use client";

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import type { ToolAnomalyOut } from "@/types/api";

interface ToolUsageChartProps {
  anomalies: ToolAnomalyOut[];
}

function barColor(score: number): string {
  if (score >= 4) return "#f87171"; // red-400
  if (score >= 3) return "#fb923c"; // orange-400
  return "#fbbf24"; // amber-400
}

export function ToolUsageChart({ anomalies }: ToolUsageChartProps) {
  const data = anomalies.map((a) => ({
    name: a.tool_name.length > 18 ? `${a.tool_name.slice(0, 18)}…` : a.tool_name,
    score: a.anomaly_score,
    expected: a.expected_freq,
    actual: a.actual_freq,
  }));

  return (
    <ResponsiveContainer width="100%" height={180}>
      <BarChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
        <XAxis
          dataKey="name"
          tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
        />
        <YAxis
          tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }}
          axisLine={false}
          tickLine={false}
          label={{
            value: "σ",
            position: "insideLeft",
            offset: 20,
            fill: "var(--color-muted-foreground)",
            fontSize: 11,
          }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "var(--color-surface-raised)",
            border: "1px solid var(--color-border)",
            borderRadius: "6px",
            fontSize: "12px",
            color: "var(--color-foreground)",
          }}
          formatter={(value, name) => {
            if (name === "score") return [(value as number).toFixed(2) + "σ", "Anomaly Score"];
            return [value, name];
          }}
          cursor={{ fill: "rgba(255,255,255,0.04)" }}
        />
        <Bar dataKey="score" radius={[3, 3, 0, 0]}>
          {data.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={barColor(entry.score)} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
