import { describe, expect, it } from "vitest";

import { queryKeys } from "./query-keys";

describe("queryKeys", () => {
  it("builds stable top-level keys", () => {
    expect(queryKeys.health).toEqual(["health"]);
    expect(queryKeys.workspaces.all).toEqual(["workspaces"]);
  });

  it("builds run keys with workspace and run ids", () => {
    expect(queryKeys.runs.list("ws-1")).toEqual(["runs", "ws-1"]);
    expect(queryKeys.runs.detail("ws-1", "run-9")).toEqual([
      "runs",
      "ws-1",
      "run-9",
    ]);
  });

  it("builds memory keys including optional params", () => {
    expect(queryKeys.memory.list("ws-1")).toEqual(["memory", "ws-1", undefined]);
    expect(queryKeys.memory.list("ws-1", { status: "active" })).toEqual([
      "memory",
      "ws-1",
      { status: "active" },
    ]);
    expect(queryKeys.memory.detail("ws-1", "mem-5")).toEqual([
      "memory",
      "ws-1",
      "mem-5",
    ]);
  });

  it("builds workspace-scoped integrity, drift, and theme keys", () => {
    expect(queryKeys.integrity.workspace("ws-1")).toEqual(["integrity", "ws-1"]);
    expect(queryKeys.drift.workspace("ws-1")).toEqual(["drift", "ws-1"]);
    expect(queryKeys.themes.workspace("ws-1")).toEqual(["themes", "ws-1"]);
  });
});
