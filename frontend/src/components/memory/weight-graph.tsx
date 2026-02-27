"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import { WeightUpdateOut } from "@/types/api";
import { formatDateRelative } from "@/lib/utils";

interface WeightGraphProps {
  history: WeightUpdateOut[];
}

export function WeightGraph({ history }: WeightGraphProps) {
  const data = history.map((w) => ({
    date: formatDateRelative(w.updated_at),
    weight: Number(w.new_weight.toFixed(3)),
    delta: w.delta,
  }));

  return (
    <div className="rounded-lg border border-border bg-surface p-4">
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data} margin={{ top: 4, right: 8, left: -16, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis
            dataKey="date"
            tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }}
            axisLine={{ stroke: "var(--color-border)" }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: "var(--color-muted-foreground)", fontSize: 11 }}
            axisLine={{ stroke: "var(--color-border)" }}
            tickLine={false}
            domain={["auto", "auto"]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: "var(--color-surface-raised)",
              border: "1px solid var(--color-border)",
              borderRadius: "6px",
              fontSize: "12px",
              color: "var(--color-foreground)",
            }}
            itemStyle={{ color: "var(--color-accent)" }}
            labelStyle={{ color: "var(--color-muted-foreground)", marginBottom: "4px" }}
            formatter={(value) => [(value as number).toFixed(3), "Weight"]}
          />
          <Line
            type="monotone"
            dataKey="weight"
            stroke="var(--color-accent)"
            strokeWidth={2}
            dot={{ r: 3, fill: "var(--color-accent)", strokeWidth: 0 }}
            activeDot={{ r: 5, fill: "var(--color-accent)", strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
