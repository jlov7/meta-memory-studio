"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import Link from "next/link";
import { ChevronLeft, ShieldCheck } from "lucide-react";
import { AppShell } from "@/components/layout/sidebar";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { StatusPill } from "@/components/shared/status-pill";
import { Skeleton } from "@/components/ui/skeleton";
import { Timeline } from "@/components/runs/timeline";
import { ContributionCompare } from "@/components/runs/contribution-compare";
import { getRun } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { formatDate, formatDuration } from "@/lib/utils";

export default function RunDetailPage() {
  const { id: workspaceId, runId } = useParams<{ id: string; runId: string }>();

  const { data: run, isLoading } = useQuery({
    queryKey: queryKeys.runs.detail(workspaceId, runId),
    queryFn: () => getRun(workspaceId, runId),
  });

  return (
    <AppShell>
      <div className="px-8 py-6">
        {/* Back */}
        <Link
          href={`/workspaces/${workspaceId}`}
          className="mb-4 inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Runs
        </Link>

        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-8 w-64" />
            <Skeleton className="h-4 w-48" />
          </div>
        ) : run ? (
          <>
            {/* Header */}
            <div className="mb-6 flex items-start justify-between">
              <div>
                <div className="flex items-center gap-3 mb-1">
                  <h1 className="font-mono text-lg font-semibold text-foreground">
                    {run.external_id}
                  </h1>
                  <StatusPill outcome={run.outcome} />
                  {run.hash_valid && (
                    <Badge variant="success" className="gap-1">
                      <ShieldCheck className="h-3 w-3" />
                      VERIFIED
                    </Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  {formatDate(run.started_at)} ·{" "}
                  {formatDuration(run.started_at, run.ended_at)} ·{" "}
                  {run.step_count} steps
                </p>
              </div>
              {run.score !== null && (
                <div className="text-right">
                  <p className="text-xs text-muted-foreground">Score</p>
                  <p
                    className={`text-2xl font-bold ${
                      run.score >= 0.5 ? "text-success" : "text-danger"
                    }`}
                  >
                    {run.score.toFixed(2)}
                  </p>
                </div>
              )}
            </div>

            {/* Tabs */}
            <Tabs defaultValue="timeline">
              <TabsList>
                <TabsTrigger value="timeline">Timeline</TabsTrigger>
                <TabsTrigger value="compare">Contribution</TabsTrigger>
                <TabsTrigger value="raw">Raw Events</TabsTrigger>
              </TabsList>

              <TabsContent value="timeline">
                <Timeline steps={run.timeline} workspaceId={workspaceId} />
              </TabsContent>

              <TabsContent value="compare">
                <ContributionCompare workspaceId={workspaceId} run={run} />
              </TabsContent>

              <TabsContent value="raw">
                <div className="rounded-lg border border-border bg-surface font-mono text-xs overflow-auto max-h-[60vh] p-4">
                  {run.timeline.map((step) => (
                    <div key={step.id} className="py-1 border-b border-border-subtle last:border-0">
                      <span className="text-muted mr-3">{step.sequence}</span>
                      <span className="text-accent mr-3">{step.event_type}</span>
                      <span className="text-foreground-subtle break-all">{step.content}</span>
                    </div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </>
        ) : (
          <p className="text-sm text-muted-foreground">Run not found.</p>
        )}
      </div>
    </AppShell>
  );
}
