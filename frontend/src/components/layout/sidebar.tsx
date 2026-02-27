"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useQuery } from "@tanstack/react-query";
import { Brain, Activity, Plus, Loader2 } from "lucide-react";
import { listWorkspaces, createWorkspace } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { useQueryClient } from "@tanstack/react-query";

export function Sidebar() {
  const pathname = usePathname();
  const qc = useQueryClient();

  const { data, isLoading } = useQuery({
    queryKey: queryKeys.workspaces.all,
    queryFn: listWorkspaces,
  });

  const handleCreate = async () => {
    const name = prompt("Workspace name:");
    if (!name) return;
    await createWorkspace(name);
    qc.invalidateQueries({ queryKey: queryKeys.workspaces.all });
  };

  return (
    <aside className="flex h-screen w-56 flex-col border-r border-border bg-surface">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-4 py-4 border-b border-border">
        <div className="flex h-7 w-7 items-center justify-center rounded-md bg-accent">
          <Brain className="h-4 w-4 text-white" />
        </div>
        <span className="text-sm font-semibold text-foreground">MetaMemory</span>
      </div>

      {/* Workspaces */}
      <div className="flex-1 overflow-y-auto px-2 py-3">
        <div className="mb-1 flex items-center justify-between px-2">
          <span className="text-xs font-medium text-muted uppercase tracking-wider">
            Workspaces
          </span>
          <button
            onClick={handleCreate}
            className="rounded p-0.5 text-muted hover:text-foreground transition-colors"
            title="New workspace"
          >
            <Plus className="h-3.5 w-3.5" />
          </button>
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-4">
            <Loader2 className="h-4 w-4 animate-spin text-muted" />
          </div>
        )}

        <nav className="space-y-0.5">
          {data?.workspaces.map((ws) => {
            const runsPath = `/workspaces/${ws.id}`;
            const memPath = `/workspaces/${ws.id}/memory`;
            const driftPath = `/workspaces/${ws.id}/drift`;
            const isActive =
              pathname.startsWith(runsPath) ||
              pathname.startsWith(memPath) ||
              pathname.startsWith(driftPath);

            return (
              <div key={ws.id}>
                <Link
                  href={runsPath}
                  className={cn(
                    "flex items-center gap-2 rounded-md px-2 py-1.5 text-sm transition-colors",
                    isActive
                      ? "bg-accent-muted text-accent"
                      : "text-muted-foreground hover:bg-surface-raised hover:text-foreground"
                  )}
                >
                  <Activity className="h-3.5 w-3.5 shrink-0" />
                  <span className="truncate">{ws.name}</span>
                </Link>
                {isActive && (
                  <div className="ml-7 mt-0.5 space-y-0.5">
                    <NavItem href={runsPath} label="Runs" exact={false} />
                    <NavItem href={memPath} label="Memory" exact />
                    <NavItem href={driftPath} label="Drift" exact />
                  </div>
                )}
              </div>
            );
          })}
        </nav>
      </div>

      {/* Footer hint */}
      <div className="border-t border-border px-4 py-3">
        <p className="text-xs text-muted">Press / to search</p>
      </div>
    </aside>
  );
}

function NavItem({
  href,
  label,
  exact,
}: {
  href: string;
  label: string;
  exact: boolean;
}) {
  const pathname = usePathname();
  const isActive = exact ? pathname === href : pathname.startsWith(href);

  return (
    <Link
      href={href}
      className={cn(
        "block rounded px-2 py-1 text-xs transition-colors",
        isActive
          ? "text-accent"
          : "text-muted-foreground hover:text-foreground"
      )}
    >
      {label}
    </Link>
  );
}

export function AppShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex h-screen overflow-hidden">
      <Sidebar />
      <main className="flex-1 overflow-y-auto bg-bg">{children}</main>
    </div>
  );
}

// Re-export Button for use in sidebar actions
export { Button };
