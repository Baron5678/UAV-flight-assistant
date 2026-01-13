import { useCallback, useMemo, useState } from "react";
import type { TracerApi } from "../cross/logs";

export interface UseTracerResult {
  lines: string[];
  log: (line: string) => void;
  clear: () => void;
  tracer: TracerApi;
}

export function useTracer(): UseTracerResult {
  const [lines, setLines] = useState<string[]>([]);

  const log = useCallback((line: string) => {
    setLines((prev) => [...prev, line]);
  }, []);

  const clear = useCallback(() => {
    setLines([]);
  }, []);
  const tracer = useMemo<TracerApi>(() => ({ log, clear }), [log]);

  return { lines, log, clear, tracer };
}
