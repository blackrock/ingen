//  Undo / Redo stack for ConfigModel snapshots.
//  Keeps at most MAX_HISTORY snapshots; newer pushes beyond that silently drop the oldest.
//
//  The stack transitions are pure functions exported alongside the hook, so the state machine is
//  unit-testable without a React renderer. The hook itself is a thin wrapper over them.

import { useState, useCallback } from 'react';

export const MAX_HISTORY = 50;

/**
 * Append a snapshot, evicting the oldest once the cap is reached.
 * @returns {object[]} the new past stack
 */
export function pushSnapshot(past, model, max = MAX_HISTORY) {
  return [...past.slice(-(max - 1)), model];
}

/**
 * Move one step back. Returns null when there is nothing to undo.
 * @returns {{ past: object[], future: object[], restored: object } | null}
 */
export function applyUndo(past, future, currentModel) {
  if (!past.length) return null;
  return {
    past: past.slice(0, -1),
    future: [currentModel, ...future],
    restored: past[past.length - 1],
  };
}

/**
 * Move one step forward. Returns null when there is nothing to redo.
 * @returns {{ past: object[], future: object[], restored: object } | null}
 */
export function applyRedo(past, future, currentModel) {
  if (!future.length) return null;
  return {
    past: [...past, currentModel],
    future: future.slice(1),
    restored: future[0],
  };
}

/**
 * Returns an undo/redo-aware wrapper for a model update function.
 *
 * Usage:
 *   const { pushHistory, undo, redo, canUndo, canRedo } = useModelHistory();
 *   // call pushHistory(model) BEFORE each mutation so the snapshot captures the pre-mutation state.
 */
export function useModelHistory() {
  const [past, setPast]     = useState([]);   // [...older, immediate-pre-mutation]
  const [future, setFuture] = useState([]);   // [immediate-post-undo, ...newer]

  const pushHistory = useCallback((model) => {
    setPast((prev) => pushSnapshot(prev, model));
    setFuture([]);    // new change clears the redo stack
  }, []);

  const undo = useCallback((currentModel, setModel) => {
    const next = applyUndo(past, future, currentModel);
    if (!next) return;
    setPast(next.past);
    setFuture(next.future);
    setModel(next.restored);
  }, [past, future]);

  const redo = useCallback((currentModel, setModel) => {
    const next = applyRedo(past, future, currentModel);
    if (!next) return;
    setPast(next.past);
    setFuture(next.future);
    setModel(next.restored);
  }, [past, future]);

  return {
    pushHistory,
    undo,
    redo,
    canUndo: past.length > 0,
    canRedo: future.length > 0,
  };
}
