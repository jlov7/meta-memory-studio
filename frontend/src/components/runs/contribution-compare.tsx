"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Zap } from "lucide-react";
import { type RunDetail } from "@/types/api";
import { evolveWorkspace } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { Button } from "@/components/ui/button";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";

interface ContributionCompareProps {
  workspaceId: string;
  run: RunDetail;
}

export function ContributionCompare({ workspaceId, run }: ContributionCompareProps) {
  const qc = useQueryClient();

  const { mutate: evolve, isPending, data: evolveResult } = useMutation({
    mutationFn: () => evolveWorkspace(workspaceId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.memory.list(workspaceId) });
    },
  });

  const score = run.score;
  const isSuccess = run.outcome.toLowerCase() === "success";
  const isFail = run.outcome.toLowerCase() === "fail" || run.outcome.toLowerCase() === "failure";

  return (
    <div className="space-y-6">
      {/* Score comparison */}
      <div className="grid grid-cols-3 gap-4">
        <Card>
          <CardHeader>
            <CardTitle>Outcome</CardTitle>
          </CardHeader>
          <CardContent>
            <p
              className={`text-2xl font-bold ${
                isSuccess ? "text-success" : isFail ? "text-danger" : "text-muted-foreground"
              }`}
            >
              {run.outcome}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Score</CardTitle>
          </CardHeader>
          <CardContent>
            {score !== null ? (
              <p
                className={`text-2xl font-bold ${
                  score >= 0.5 ? "text-success" : "text-danger"
                }`}
              >
                {score.toFixed(2)}
              </p>
            ) : (
              <p className="text-muted">—</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Steps</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-foreground">{run.step_count}</p>
          </CardContent>
        </Card>
      </div>

      {/* Evolve */}
      <div className="rounded-lg border border-border bg-surface p-5">
        <div className="flex items-start justify-between">
          <div>
            <h3 className="text-sm font-semibold text-foreground mb-1">
              Contribution & Weight Update
            </h3>
            <p className="text-xs text-muted-foreground max-w-md">
              Compare runs in this workspace to measure how memories contributed
              to outcomes. Weight successful memories higher, penalize harmful ones.
            </p>
          </div>
          <Button
            onClick={() => evolve()}
            disabled={isPending}
            className="ml-4 shrink-0"
          >
            <Zap className="h-4 w-4" />
            {isPending ? "Running…" : "Evolve"}
          </Button>
        </div>

        {evolveResult && (
          <div className="mt-4 grid grid-cols-2 gap-3">
            <div className="rounded-md bg-surface-raised p-3">
              <p className="text-xs text-muted-foreground">Contributions</p>
              <p className="text-lg font-bold text-foreground">
                {evolveResult.contributions_created}
              </p>
            </div>
            <div className="rounded-md bg-surface-raised p-3">
              <p className="text-xs text-muted-foreground">Weight Updates</p>
              <p className="text-lg font-bold text-foreground">
                {evolveResult.weight_updates}
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
