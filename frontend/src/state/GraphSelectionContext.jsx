//  InGen Studio — GraphSelectionContext
//
//  Bridges the inFlow sidebar (NavRail) and the canvas (InterfaceGraphEditor), which live in
//  different branches of the tree. The sidebar adds a node, then sets the selection here so the
//  canvas opens that node's config drawer. Mirrors ChatSessionContext.

import { createContext, useContext, useState, useMemo } from 'react';

const GraphSelectionContext = createContext(null);

export function GraphSelectionProvider({ children }) {
  const [selectedNodeId, setSelectedNodeId] = useState(null);
  const value = useMemo(() => ({ selectedNodeId, setSelectedNodeId }), [selectedNodeId]);
  return <GraphSelectionContext.Provider value={value}>{children}</GraphSelectionContext.Provider>;
}

export function useGraphSelection() {
  const ctx = useContext(GraphSelectionContext);
  if (!ctx) throw new Error('useGraphSelection must be used within a GraphSelectionProvider');
  return ctx;
}
