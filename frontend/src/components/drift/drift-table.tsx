"use client";

import Link from "next/link";
import type { ToolAnomalyOut } from "@/types/api";

interface DriftTableProps {
  anomalies: ToolAnomalyOut[];
  workspaceId: string;
}

function SeverityBadge({ score }: { score: number }) {
  if (score >= 4) {
    return (
      <span className="rounded-full bg-red-500/15 px-2 py-0.5 text-xs font-medium text-red-400">
        Critical
      </span>
    );
  }
  if (score >= 3) {
    return (
      <span className="rounded-full bg-orange-500/15 px-2 py-0.5 text-xs font-medium text-orange-400">
        High
      </span>
    );
  }
  return (
    <span className="rounded-full bg-amber-500/15 px-2 py-0.5 text-xs font-medium text-amber-400">
      Medium
    </span>
  );
}

export function DriftTable({ anomalies, workspaceId }: DriftTableProps) {
  if (anomalies.length === 0) {
    return (
      <div className="flex h-32 flex-col items-center justify-center gap-2 text-muted-foreground">
        <p className="text-sm">No anomalies detected — tool usage looks stable.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border text-left text-xs text-muted-foreground uppercase tracking-wide">
            <th className="px-4 py-2 font-medium">Tool</th>
            <th className="px-4 py-2 font-medium">Severity</th>
            <th className="px-4 py-2 font-medium tabular-nums">Expected</th>
            <th className="px-4 py-2 font-medium tabular-nums">Actual</th>
            <th className="px-4 py-2 font-medium tabular-nums">σ Score</th>
            <th className="px-4 py-2 font-medium">Affected Runs</th>
          </tr>
        </thead>
        <tbody>
          {anomalies.map((anomaly) => (
            <tr
              key={anomaly.tool_name}
              className="border-b border-border/50 last:border-0 hover:bg-surface-raised/50"
            >
              <td className="px-4 py-3 font-mono text-xs text-foreground">
                {anomaly.tool_name}
              </td>
              <td className="px-4 py-3">
                <SeverityBadge score={anomaly.anomaly_score} />
              </td>
              <td className="px-4 py-3 tabular-nums text-muted-foreground">
                {anomaly.expected_freq.toFixed(2)}
              </td>
              <td className="px-4 py-3 tabular-nums text-foreground">
                {anomaly.actual_freq.toFixed(0)}
              </td>
              <td className="px-4 py-3 tabular-nums text-amber-400 font-medium">
                {anomaly.anomaly_score.toFixed(2)}σ
              </td>
              <td className="px-4 py-3">
                <div className="flex flex-wrap gap-1">
                  {anomaly.runs_affected.map((runId) => (
                    <Link
                      key={runId}
                      href={`/workspaces/${workspaceId}/runs/${runId}`}
                      className="rounded bg-surface-raised px-1.5 py-0.5 font-mono text-xs text-accent hover:underline"
                    >
                      {runId.slice(0, 8)}
                    </Link>
                  ))}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
