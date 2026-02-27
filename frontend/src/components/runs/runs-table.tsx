"use client";

import Link from "next/link";
import { type RunSummary } from "@/types/api";
import { StatusPill } from "@/components/shared/status-pill";
import { formatDate, formatDuration } from "@/lib/utils";

interface RunsTableProps {
  workspaceId: string;
  runs: RunSummary[];
}

export function RunsTable({ workspaceId, runs }: RunsTableProps) {
  return (
    <div className="overflow-x-auto rounded-lg border border-border">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-border bg-surface">
            <th className="px-4 py-2.5 text-left font-medium text-muted-foreground">
              Run ID
            </th>
            <th className="px-4 py-2.5 text-left font-medium text-muted-foreground">
              Outcome
            </th>
            <th className="px-4 py-2.5 text-left font-medium text-muted-foreground">
              Score
            </th>
            <th className="px-4 py-2.5 text-left font-medium text-muted-foreground">
              Started
            </th>
            <th className="px-4 py-2.5 text-left font-medium text-muted-foreground">
              Duration
            </th>
            <th className="px-4 py-2.5 text-left font-medium text-muted-foreground">
              Steps
            </th>
          </tr>
        </thead>
        <tbody>
          {runs.map((run, idx) => (
            <tr
              key={run.id}
              className={`border-b border-border last:border-0 hover:bg-surface-raised transition-colors ${
                idx % 2 === 0 ? "bg-bg" : "bg-surface"
              }`}
            >
              <td className="px-4 py-3">
                <Link
                  href={`/workspaces/${workspaceId}/runs/${run.id}`}
                  className="font-mono text-xs text-accent hover:underline"
                >
                  {run.external_id}
                </Link>
              </td>
              <td className="px-4 py-3">
                <StatusPill outcome={run.outcome} />
              </td>
              <td className="px-4 py-3 font-mono text-xs">
                {run.score !== null ? (
                  <span
                    className={
                      run.score >= 0.5 ? "text-success" : "text-danger"
                    }
                  >
                    {run.score.toFixed(2)}
                  </span>
                ) : (
                  <span className="text-muted">—</span>
                )}
              </td>
              <td className="px-4 py-3 text-xs text-muted-foreground">
                {formatDate(run.started_at)}
              </td>
              <td className="px-4 py-3 text-xs text-muted-foreground">
                {formatDuration(run.started_at, run.ended_at)}
              </td>
              <td className="px-4 py-3 text-xs text-muted-foreground">
                {run.step_count}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
