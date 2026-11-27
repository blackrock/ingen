//  InGen Studio — ConfigContext (the document store)
//
//  Holds the single ConfigModel under edit and is the bridge between the UI and the data layer.
//  Responsibilities:
//    - load the model by id from ConfigService (mock adapter → localStorage)
//    - expose pure updaters that replace the model immutably
//    - derive the live YAML (real serializer) and validation issues with useMemo
//    - autosave (debounced) back through ConfigService → real persistence + Saved/Unsaved/Saving pill
//
//  This is the ONLY place that calls the service for config I/O, so switching between the mock and
//  HTTP adapters changes nothing here or in any consumer.

import { createContext, useContext, useEffect, useMemo, useRef, useState, useCallback } from 'react';

import { getServices } from '../services/index.js';
import { modelToYaml } from '../serializers/index.js';
import { validateConfigModel, upsertInterface } from '../models/configModel.js';
import { useModelHistory } from './useModelHistory.js';

/**
 * @typedef {Object} ConfigContextValue
 * @property {import('../models/types.js').ConfigModel | null} model
 * @property {string} status            'loading' | 'saved' | 'dirty' | 'saving' | 'error'
 * @property {string} yaml              live-serialized YAML of the current model
 * @property {import('../models/types.js').ConfigIssue[]} issues
 * @property {(updater: (m: any) => any) => void} updateModel
 * @property {(name: string, updater: (iface: any) => any) => void} updateInterface
 * @property {() => void} undo
 * @property {() => void} redo
 * @property {boolean} canUndo
 * @property {boolean} canRedo
 */

const ConfigContext = createContext(/** @type {ConfigContextValue} */ (null));

const SAVE_DEBOUNCE_MS = 600;

export function ConfigProvider({ configId, children }) {
  const [model, setModel] = useState(null);
  const [status, setStatus] = useState('loading');
  const saveTimer = useRef(null);
  const history = useModelHistory();
  // The last model reference that has been persisted. Drives the autosave decision (model !==
  // savedRef → there are unsaved edits) WITHOUT coupling it to `status`, which is what caused the
  // earlier data-loss race (a save resolving could cancel a pending save of a newer edit).
  const savedRef = useRef(null);
  // Always-current model reference, readable from inside an in-flight save's async closure so we
  // can tell whether a newer edit landed while we were saving.
  const modelRef = useRef(null);

  // Load the config. The provider is mounted with key={configId} (see ConfigWorkspace), so a
  // different config remounts this with fresh 'loading'/null state — no synchronous reset needed.
  useEffect(() => {
    let alive = true;
    getServices()
      .config.get(configId)
      .then((m) => {
        if (!alive) return;
        savedRef.current = m;
        modelRef.current = m;
        setModel(m);
        setStatus('saved');
      })
      .catch(() => { if (alive) setStatus('error'); });
    return () => { alive = false; };
  }, [configId]);

  // Keep modelRef in lockstep with the rendered model.
  useEffect(() => { modelRef.current = model; }, [model]);

  //  Apply an immutable update and mark dirty. Pushes a history snapshot BEFORE the mutation.
  //
  //  pushHistory is deliberately NOT called inside a setModel updater: React invokes updaters twice
  //  under StrictMode, which would record two snapshots per edit and make undo need two presses.
  //  modelRef is advanced synchronously here so several updateModel calls in one tick still chain
  //  off each other's result rather than a stale render value.
  const updateModel = useCallback((updater) => {
    const prev = modelRef.current;
    if (!prev) return;
    history.pushHistory(prev);
    const next = updater(prev);
    modelRef.current = next;
    setModel(next);
    setStatus('dirty');
  }, [history]);

  // Convenience for the common case of editing one interface.
  const updateInterface = useCallback((name, updater) => {
    updateModel((m) => {
      const current = m.interfacesByName[name];
      if (!current) return m;
      return upsertInterface(m, name, updater(current));
    });
  }, [updateModel]);

  // Debounced autosave (real persistence). Triggered by the MODEL changing away from the last
  // persisted reference — never by `status`. Each edit reschedules the debounce; an in-flight save
  // only flips the pill to 'saved' if no newer edit arrived meanwhile (otherwise the newer edit's
  // own effect run keeps the save chain going), so the latest edit is never silently dropped.
  useEffect(() => {
    if (!model || model === savedRef.current) return;
    clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(async () => {
      const toSave = model;
      setStatus('saving');
      try {
        await getServices().config.update(toSave);
        savedRef.current = toSave;
        // Only declare 'saved' if this is still the newest model; otherwise a pending save covers it.
        if (modelRef.current === toSave) setStatus('saved');
      } catch {
        setStatus('error');
      }
    }, SAVE_DEBOUNCE_MS);
    return () => clearTimeout(saveTimer.current);
  }, [model]);

  // Derived, recomputed only when the model changes.
  const yaml = useMemo(() => (model ? modelToYaml(model) : ''), [model]);
  const issues = useMemo(() => (model ? validateConfigModel(model) : []), [model]);

  // modelRef is advanced here too, so an edit made immediately after an undo branches from the
  // restored model rather than the one it replaced.
  const undo = useCallback(() => {
    history.undo(modelRef.current, (m) => { modelRef.current = m; setModel(m); setStatus('dirty'); });
  }, [history]);

  const redo = useCallback(() => {
    history.redo(modelRef.current, (m) => { modelRef.current = m; setModel(m); setStatus('dirty'); });
  }, [history]);

  // Flush the pending autosave immediately (e.g. triggered by Ctrl+S).
  const saveNow = useCallback(async () => {
    const m = modelRef.current;
    if (!m || m === savedRef.current) return;
    clearTimeout(saveTimer.current);
    setStatus('saving');
    try {
      await getServices().config.update(m);
      savedRef.current = m;
      if (modelRef.current === m) setStatus('saved');
    } catch {
      setStatus('error');
    }
  }, []);

  const value = useMemo(
    () => ({
      model, status, yaml, issues,
      updateModel, updateInterface,
      undo, redo, saveNow,
      canUndo: history.canUndo,
      canRedo: history.canRedo,
    }),
    [model, status, yaml, issues, updateModel, updateInterface, undo, redo, saveNow, history.canUndo, history.canRedo],
  );

  return <ConfigContext.Provider value={value}>{children}</ConfigContext.Provider>;
}

export function useConfig() {
  const ctx = useContext(ConfigContext);
  if (!ctx) throw new Error('useConfig must be used within a ConfigProvider');
  return ctx;
}
