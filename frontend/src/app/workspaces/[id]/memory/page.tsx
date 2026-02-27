"use client";

import { useParams } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { AppShell } from "@/components/layout/sidebar";
import { MemoryLibrary } from "@/components/memory/memory-library";
import { ThemedMemoryLibrary } from "@/components/memory/themed-memory-library";
import { listMemories, listMemoryThemes } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { EmptyState } from "@/components/shared/empty-state";
import { Brain, Search, Layers, LayoutGrid } from "lucide-react";
import { useDebounce } from "@/hooks/use-debounce";
import { ExportButton } from "@/components/memory/export-button";
import { Button } from "@/components/ui/button";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";

export default function MemoryPage() {
  const { id } = useParams<{ id: string }>();
  const [q, setQ] = useState("");
  const [grouped, setGrouped] = useState(false);
  const debouncedQ = useDebounce(q, 300);

  const flatQuery = useQuery({
    queryKey: queryKeys.memory.list(id, { q: debouncedQ }),
    queryFn: () => listMemories(id, { q: debouncedQ }),
    enabled: !grouped,
  });

  const themeQuery = useQuery({
    queryKey: queryKeys.themes.workspace(id),
    queryFn: () => listMemoryThemes(id),
    enabled: grouped,
  });

  const isLoading = grouped ? themeQuery.isLoading : flatQuery.isLoading;
  const totalMemories = grouped
    ? themeQuery.data?.total_memories ?? 0
    : flatQuery.data?.total ?? 0;
  const hasData = grouped
    ? (themeQuery.data?.groups.length ?? 0) > 0
    : (flatQuery.data?.memories.length ?? 0) > 0;

  return (
    <AppShell>
      <div className="px-8 py-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-semibold text-foreground">Memory Library</h1>
            <p className="text-sm text-muted-foreground">
              {isLoading ? "Loading…" : `${totalMemories} memories`}
            </p>
          </div>
          <div className="flex items-center gap-3">
            <ExportButton workspaceId={id} />

            {/* Theme grouping toggle */}
            <Tooltip>
              <TooltipTrigger asChild>
                <Button
                  variant={grouped ? "default" : "ghost"}
                  size="icon"
                  aria-label="Toggle theme grouping"
                  onClick={() => setGrouped((g) => !g)}
                >
                  {grouped ? (
                    <Layers className="h-4 w-4" />
                  ) : (
                    <LayoutGrid className="h-4 w-4" />
                  )}
                </Button>
              </TooltipTrigger>
              <TooltipContent>
                {grouped ? "Switch to flat view" : "Group by theme (de-dup)"}
              </TooltipContent>
            </Tooltip>

            {!grouped && (
              <div className="relative w-64">
                <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted" />
                <Input
                  placeholder="Search memories…"
                  value={q}
                  onChange={(e) => setQ(e.target.value)}
                  className="pl-8"
                />
              </div>
            )}
          </div>
        </div>

        {isLoading ? (
          <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
            {[...Array(6)].map((_, i) => (
              <Skeleton key={i} className="h-32 w-full" />
            ))}
          </div>
        ) : !hasData ? (
          <EmptyState
            icon={Brain}
            title="No memories yet"
            description={
              q && !grouped
                ? `No memories match "${q}"`
                : "Import a trace to construct memories."
            }
          />
        ) : grouped ? (
          <ThemedMemoryLibrary
            workspaceId={id}
            groups={themeQuery.data!.groups}
          />
        ) : (
          <MemoryLibrary workspaceId={id} memories={flatQuery.data!.memories} />
        )}
      </div>
    </AppShell>
  );
}
