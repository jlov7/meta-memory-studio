"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Activity, AlertTriangle } from "lucide-react";
import { getDrift } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { DriftTable } from "@/components/drift/drift-table";
import { ToolUsageChart } from "@/components/drift/tool-usage-chart";

export default function DriftPage() {
  const { id: workspaceId } = useParams<{ id: string }>();

  const { data, isLoading, error } = useQuery({
    queryKey: queryKeys.drift.workspace(workspaceId),
    queryFn: () => getDrift(workspaceId),
  });

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        <div className="h-8 w-48 rounded bg-surface-raised animate-pulse" />
        <div className="h-48 rounded bg-surface-raised animate-pulse" />
        <div className="h-64 rounded bg-surface-raised animate-pulse" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex h-64 flex-col items-center justify-center gap-3 text-muted-foreground">
        <AlertTriangle className="h-8 w-8 text-red-400" />
        <p className="text-sm">Failed to load drift report.</p>
      </div>
    );
  }

  const anomalyCount = data?.anomalies.length ?? 0;
  const totalRuns = data?.total_runs ?? 0;

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-xl font-semibold text-foreground flex items-center gap-2">
          <Activity className="h-5 w-5 text-accent" />
          Drift Detection
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Tool usage anomalies across {totalRuns} run{totalRuns !== 1 ? "s" : ""} — flags tools
          with usage &gt;2σ above baseline.
        </p>
      </div>

      {/* Summary pills */}
      <div className="flex gap-4">
        <div className="rounded-lg border border-border bg-surface px-4 py-3">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">Total Runs</p>
          <p className="mt-1 text-2xl font-semibold text-foreground tabular-nums">{totalRuns}</p>
        </div>
        <div className="rounded-lg border border-border bg-surface px-4 py-3">
          <p className="text-xs text-muted-foreground uppercase tracking-wide">Anomalies</p>
          <p
            className={`mt-1 text-2xl font-semibold tabular-nums ${
              anomalyCount > 0 ? "text-amber-400" : "text-green-400"
            }`}
          >
            {anomalyCount}
          </p>
        </div>
      </div>

      {/* Chart */}
      {data && data.anomalies.length > 0 && (
        <div className="rounded-lg border border-border bg-surface p-4">
          <h2 className="mb-3 text-sm font-medium text-foreground">Anomaly Scores</h2>
          <ToolUsageChart anomalies={data.anomalies} />
        </div>
      )}

      {/* Table */}
      <div className="rounded-lg border border-border bg-surface">
        <div className="border-b border-border px-4 py-3">
          <h2 className="text-sm font-medium text-foreground">Tool Anomalies</h2>
        </div>
        <DriftTable anomalies={data?.anomalies ?? []} workspaceId={workspaceId} />
      </div>
    </div>
  );
}
