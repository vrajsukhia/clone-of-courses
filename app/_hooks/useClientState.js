"use client";

import { useCallback, useState } from "react";
import { DEFAULT_STATE, getClientState, saveClientState } from "../lib/clientState";

export function useClientState() {
  const [state, setState] = useState(() => getClientState());
  const isReady = typeof window !== "undefined";

  const updateState = useCallback((updater) => {
    setState((prev) => {
      const next = typeof updater === "function" ? updater(prev) : { ...prev, ...updater };
      saveClientState(next);
      return next;
    });
  }, []);

  return { state, updateState, isReady };
}
