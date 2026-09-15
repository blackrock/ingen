//  InGen Studio — RunContext
//
//  Scoped to the Run Console route. Owns the lifecycle of a (mock) execution so the console's child
//  panels — stage timeline, log stream, validation results — share one source of truth without prop
//  drilling. Calls RunService.simulate (streaming events) and, on completion, persists the record via
//  HistoryService. Reads the model from ConfigContext, so it stays in sync with the edited config.

import { createContext, useContext, useState, useRef, useCallback } from 'react';

import { getServices } from '../services/index.js';
import { makeId } from '../utils/id.js';
import { useConfig } from './ConfigContext.jsx';

const RunContext = createContext(null);

export function RunProvider({ children }) {
  const { model } = useConfig();
  const [status, setStatus] = useState('idle'); // idle | running | done
  const [events, setEvents] = useState([]);
  const [record, setRecord] = useState(null);
  const cancelRef = useRef(false);

  const start = useCallback(async (overrides = {}) => {
    if (!model || status === 'running') return;
    cancelRef.current = false;
    setStatus('running');
    setEvents([]);
    setRecord(null);

    const { run, history } = getServices();
    try {
      const result = await run.simulate(model, overrides, {
        onEvent: (e) => setEvents((prev) => [...prev, e]),
        isCancelled: () => cancelRef.current,
      });
      if (cancelRef.current) { setStatus('idle'); return; }
      setRecord(result);
      setStatus('done');
      // Persisting to history must not be able to reclassify a run that already succeeded — a
      // storage-quota failure here would otherwise be caught below and reported as a failed run.
      try {
        await history.add(result);
      } catch {
        /* history is a convenience surface; the run itself still succeeded */
      }
    } catch (err) {
      if (cancelRef.current) { setStatus('idle'); return; }
      // e.g. the HTTP wrapper is unreachable. Surface it as a failed run instead of hanging.
      const ts = new Date().toISOString();
      setRecord({
        runId: makeId('run_error'),
        configId: model.meta.id,
        configName: model.meta.name,
        status: 'failed',
        startedAt: ts,
        finishedAt: ts,
        durationMs: 0,
        stages: [],
        logs: [{ type: 'log', ts, level: 'error', message: `Run failed: ${err?.message ?? err}` }],
        validation: { results: [], summary: { passed: 0, failed: 0, warning: 0, total: 0 } },
        overrides,
      });
      setStatus('done');
    }
  }, [model, status]);

  const cancel = useCallback(() => { cancelRef.current = true; }, []);

  return (
    <RunContext.Provider value={{ status, events, record, start, cancel }}>
      {children}
    </RunContext.Provider>
  );
}

export function useRun() {
  const ctx = useContext(RunContext);
  if (!ctx) throw new Error('useRun must be used within a RunProvider');
  return ctx;
}
