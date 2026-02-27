"use client";

import { useEffect } from "react";

type KeyCombo = string | string[];

interface Options {
  enabled?: boolean;
}

function matchesKey(event: KeyboardEvent, key: string): boolean {
  const parts = key.toLowerCase().split("+");
  const mainKey = parts[parts.length - 1];
  const needsCtrl = parts.includes("ctrl") || parts.includes("meta");
  const needsShift = parts.includes("shift");
  const needsAlt = parts.includes("alt");

  return (
    event.key.toLowerCase() === mainKey &&
    (!needsCtrl || event.ctrlKey || event.metaKey) &&
    (!needsShift || event.shiftKey) &&
    (!needsAlt || event.altKey)
  );
}

export function useKeyboardShortcut(
  keys: KeyCombo,
  callback: (event: KeyboardEvent) => void,
  options: Options = {}
) {
  const { enabled = true } = options;

  useEffect(() => {
    if (!enabled) return;

    const handler = (event: KeyboardEvent) => {
      const keyList = Array.isArray(keys) ? keys : [keys];
      if (keyList.some((k) => matchesKey(event, k))) {
        callback(event);
      }
    };

    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, [keys, callback, enabled]);
}
