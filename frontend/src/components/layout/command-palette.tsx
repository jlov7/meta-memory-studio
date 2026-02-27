"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Command } from "cmdk";
import { useQuery } from "@tanstack/react-query";
import { Brain, Activity, Search } from "lucide-react";
import { listWorkspaces } from "@/lib/api";
import { queryKeys } from "@/lib/query-keys";

export function CommandPalette() {
  const [open, setOpen] = useState(false);
  const router = useRouter();

  const { data } = useQuery({
    queryKey: queryKeys.workspaces.all,
    queryFn: listWorkspaces,
    enabled: open,
  });

  const toggle = useCallback(() => setOpen((o) => !o), []);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.key === "/" && !["INPUT", "TEXTAREA"].includes((e.target as HTMLElement).tagName)) {
        e.preventDefault();
        toggle();
      }
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [toggle]);

  const navigate = (path: string) => {
    router.push(path);
    setOpen(false);
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-[20vh]">
      <div
        className="fixed inset-0 bg-black/60 backdrop-blur-sm"
        onClick={() => setOpen(false)}
      />
      <Command
        className="relative z-10 w-full max-w-xl overflow-hidden rounded-xl border border-border bg-surface shadow-2xl"
        shouldFilter={true}
      >
        <div className="flex items-center gap-2 border-b border-border px-3">
          <Search className="h-4 w-4 shrink-0 text-muted" />
          <Command.Input
            placeholder="Search workspaces, runs, memories…"
            className="h-11 w-full bg-transparent text-sm text-foreground placeholder:text-muted focus:outline-none"
          />
        </div>
        <Command.List className="max-h-72 overflow-y-auto p-1.5">
          <Command.Empty className="py-6 text-center text-sm text-muted-foreground">
            No results found.
          </Command.Empty>

          {data?.workspaces.map((ws) => (
            <Command.Group key={ws.id} heading={ws.name}>
              <Command.Item
                value={`${ws.name} runs`}
                onSelect={() => navigate(`/workspaces/${ws.id}`)}
                className="flex cursor-pointer items-center gap-2.5 rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:bg-surface-raised hover:text-foreground aria-selected:bg-surface-raised aria-selected:text-foreground"
              >
                <Activity className="h-3.5 w-3.5" />
                Runs — {ws.name}
              </Command.Item>
              <Command.Item
                value={`${ws.name} memory`}
                onSelect={() => navigate(`/workspaces/${ws.id}/memory`)}
                className="flex cursor-pointer items-center gap-2.5 rounded-md px-2 py-1.5 text-sm text-muted-foreground hover:bg-surface-raised hover:text-foreground aria-selected:bg-surface-raised aria-selected:text-foreground"
              >
                <Brain className="h-3.5 w-3.5" />
                Memory Library — {ws.name}
              </Command.Item>
            </Command.Group>
          ))}
        </Command.List>
        <div className="border-t border-border px-3 py-2 text-xs text-muted flex gap-3">
          <span><kbd className="font-mono">↑↓</kbd> navigate</span>
          <span><kbd className="font-mono">↵</kbd> select</span>
          <span><kbd className="font-mono">Esc</kbd> close</span>
        </div>
      </Command>
    </div>
  );
}
