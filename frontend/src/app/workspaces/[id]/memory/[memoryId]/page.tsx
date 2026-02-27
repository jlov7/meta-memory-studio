"use client";

import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import Link from "next/link";
import { ChevronLeft, Brain, Archive, Trash2 } from "lucide-react";
import { AppShell } from "@/components/layout/sidebar";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { WeightGraph } from "@/components/memory/weight-graph";
import { getMemory, deprecateMemory, forgetMemory } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { formatDate, formatDateRelative, formatWeight, formatDelta } from "@/lib/utils";
import { useRouter } from "next/navigation";

export default function MemoryDetailPage() {
  const { id: workspaceId, memoryId } = useParams<{ id: string; memoryId: string }>();
  const router = useRouter();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.memory.detail(workspaceId, memoryId),
    queryFn: () => getMemory(workspaceId, memoryId),
  });

  const { mutate: deprecate } = useMutation({
    mutationFn: () => deprecateMemory(workspaceId, memoryId),
    onSuccess: () => qc.invalidateQueries({ queryKey: queryKeys.memory.list(workspaceId) }),
  });

  const { mutate: forget } = useMutation({
    mutationFn: () => forgetMemory(workspaceId, memoryId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.memory.list(workspaceId) });
      router.push(`/workspaces/${workspaceId}/memory`);
    },
  });

  return (
    <AppShell>
      <div className="px-8 py-6">
        <Link
          href={`/workspaces/${workspaceId}/memory`}
          className="mb-4 inline-flex items-center gap-1 text-xs text-muted-foreground hover:text-foreground"
        >
          <ChevronLeft className="h-3.5 w-3.5" />
          Memory Library
        </Link>

        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-8 w-80" />
            <Skeleton className="h-4 w-48" />
          </div>
        ) : data ? (
          <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-1 flex-wrap">
                  <Brain className="h-5 w-5 text-accent shrink-0" />
                  <h1 className="text-xl font-semibold text-foreground">
                    {data.memory.title}
                  </h1>
                  <Badge variant="outline">{data.memory.memory_type}</Badge>
                  {data.memory.status !== "active" && (
                    <Badge variant="warning">{data.memory.status}</Badge>
                  )}
                </div>
                <p className="text-xs text-muted-foreground">
                  Created {formatDate(data.memory.created_at)} ·{" "}
                  Updated {formatDateRelative(data.memory.updated_at)} ·{" "}
                  Retrieved {data.retrieval_count}×
                </p>
              </div>
              <div className="flex items-center gap-2 ml-4 shrink-0">
                <Button variant="secondary" size="sm" onClick={() => deprecate()}>
                  <Archive className="h-3.5 w-3.5" />
                  Deprecate
                </Button>
                <Button
                  variant="danger"
                  size="sm"
                  onClick={() => {
                    if (confirm("Permanently forget this memory?")) forget();
                  }}
                >
                  <Trash2 className="h-3.5 w-3.5" />
                  Forget
                </Button>
              </div>
            </div>

            {/* Content + Weight */}
            <div className="grid grid-cols-3 gap-4">
              <div className="col-span-2 rounded-lg border border-border bg-surface p-4">
                <p className="mb-2 text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Content
                </p>
                <p className="text-sm text-foreground leading-relaxed">
                  {data.memory.content}
                </p>
              </div>
              <Card>
                <CardHeader>
                  <CardTitle>Current Weight</CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-3xl font-bold font-mono text-foreground">
                    {formatWeight(data.memory.current_weight)}
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Weight history graph */}
            {data.weight_history.length > 0 && (
              <div>
                <h2 className="mb-3 text-sm font-semibold text-foreground">
                  Weight Evolution
                </h2>
                <WeightGraph history={data.weight_history} />
              </div>
            )}

            {/* Contributions */}
            {data.contributions.length > 0 && (
              <div>
                <h2 className="mb-3 text-sm font-semibold text-foreground">
                  Contribution Events
                </h2>
                <div className="overflow-x-auto rounded-lg border border-border">
                  <table className="w-full text-xs">
                    <thead>
                      <tr className="border-b border-border bg-surface">
                        <th className="px-4 py-2 text-left font-medium text-muted-foreground">Baseline</th>
                        <th className="px-4 py-2 text-left font-medium text-muted-foreground">Guided</th>
                        <th className="px-4 py-2 text-left font-medium text-muted-foreground">Δ Score</th>
                        <th className="px-4 py-2 text-left font-medium text-muted-foreground">Measured</th>
                      </tr>
                    </thead>
                    <tbody>
                      {data.contributions.map((c) => (
                        <tr key={c.id} className="border-b border-border last:border-0">
                          <td className="px-4 py-2 font-mono">{c.baseline_score.toFixed(2)}</td>
                          <td className="px-4 py-2 font-mono">{c.guided_score.toFixed(2)}</td>
                          <td className={`px-4 py-2 font-mono font-semibold ${c.delta >= 0 ? "text-success" : "text-danger"}`}>
                            {formatDelta(c.delta)}
                          </td>
                          <td className="px-4 py-2 text-muted-foreground">{formatDateRelative(c.measured_at)}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        ) : (
          <p className="text-sm text-muted-foreground">Memory not found.</p>
        )}
      </div>
    </AppShell>
  );
}
