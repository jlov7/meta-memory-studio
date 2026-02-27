"use client";

import { useParams } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/sidebar";
import { RunsTable } from "@/components/runs/runs-table";
import { listRuns } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { Activity } from "lucide-react";

export default function WorkspacePage() {
  const { id } = useParams<{ id: string }>();

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.runs.list(id),
    queryFn: () => listRuns(id),
  });

  return (
    <AppShell>
      <div className="px-8 py-6">
        <div className="mb-6">
          <h1 className="text-xl font-semibold text-foreground">Runs</h1>
          <p className="text-sm text-muted-foreground">
            {data ? `${data.total} runs` : "Loading…"}
          </p>
        </div>

        {isLoading ? (
          <div className="space-y-2">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-12 w-full" />
            ))}
          </div>
        ) : !data?.runs.length ? (
          <EmptyState
            icon={Activity}
            title="No runs yet"
            description="Import a trace file to see your agent runs here."
          />
        ) : (
          <RunsTable workspaceId={id} runs={data.runs} />
        )}
      </div>
    </AppShell>
  );
}
