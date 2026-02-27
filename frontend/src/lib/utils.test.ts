import { afterEach, describe, expect, it, vi } from "vitest";

import {
  cn,
  formatDate,
  formatDateRelative,
  formatDelta,
  formatDuration,
  formatWeight,
  outcomeColor,
  parseContent,
} from "./utils";

afterEach(() => {
  vi.useRealTimers();
});

describe("utils", () => {
  it("merges classes with tailwind conflict resolution", () => {
    expect(cn("p-2", "p-4", "text-sm")).toBe("p-4 text-sm");
  });

  it("formats dates and handles missing/invalid values", () => {
    expect(formatDate("2024-01-02T03:04:05")).toBe("Jan 2, 2024 03:04");
    expect(formatDate(null)).toBe("—");
    expect(formatDate("not-a-date")).toBe("—");
  });

  it("formats relative dates and handles bad input", () => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date("2024-01-02T03:05:00Z"));
    expect(formatDateRelative("2024-01-02T03:04:00Z")).toBe("1 minute ago");
    expect(formatDateRelative(undefined)).toBe("—");
    expect(formatDateRelative("not-a-date")).toBe("—");
  });

  it("formats numeric display helpers", () => {
    expect(formatDelta(1.23456)).toBe("+1.235");
    expect(formatDelta(-0.0004)).toBe("-0.000");
    expect(formatWeight(2)).toBe("2.000");
  });

  it("formats durations in ms, s, and m/s buckets", () => {
    expect(formatDuration("2024-01-02T00:00:00.000", "2024-01-02T00:00:00.500")).toBe(
      "500ms"
    );
    expect(formatDuration("2024-01-02T00:00:00.000", "2024-01-02T00:00:01.200")).toBe(
      "1.2s"
    );
    expect(formatDuration("2024-01-02T00:00:00.000", "2024-01-02T00:02:05.000")).toBe(
      "2m 5s"
    );
    expect(formatDuration(null, "2024-01-02T00:02:05.000")).toBe("—");
  });

  it("parses JSON content or returns original string", () => {
    expect(parseContent('{"a":1}')).toEqual({ a: 1 });
    expect(parseContent("not-json")).toBe("not-json");
  });

  it("maps run outcomes to the expected color token", () => {
    expect(outcomeColor("SUCCESS")).toBe("text-success");
    expect(outcomeColor("error")).toBe("text-danger");
    expect(outcomeColor("skipped")).toBe("text-muted-foreground");
  });
});
