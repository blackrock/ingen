//  InGen Studio — ViewModeContext
//
//  Shared state for the active editor view mode (Graph / Chat). Lives above the
//  workspace so both the AppShell brand bar (where the switcher lives) and the editor/sidebar
//  (which render mode-specific content) can read and write the same value.

import { createContext, useContext, useState, useMemo } from 'react';

/**
 * @typedef {'graph' | 'chat'} ViewMode  (UI labels: graph = inFlow, chat = inChat)
 * @typedef {{ viewMode: ViewMode, setViewMode: (m: ViewMode) => void }} ViewModeContextValue
 */

const ViewModeContext = createContext(/** @type {ViewModeContextValue} */ (null));

export function ViewModeProvider({ children }) {
  const [viewMode, setViewMode] = useState('graph');
  const value = useMemo(() => ({ viewMode, setViewMode }), [viewMode]);
  return <ViewModeContext.Provider value={value}>{children}</ViewModeContext.Provider>;
}

export function useViewMode() {
  const ctx = useContext(ViewModeContext);
  if (!ctx) throw new Error('useViewMode must be used within a ViewModeProvider');
  return ctx;
}
