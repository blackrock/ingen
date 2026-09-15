//  InGen Studio — CatalogContext
//
//  Loads the static catalog once (via CatalogService) and shares it. The catalog drives palettes
//  and dropdowns — e.g. labelling the available output types and populating the schema-driven
//  form option lists.

import { createContext, useContext, useEffect, useState } from 'react';
import { getServices } from '../services/index.js';

/** @type {import('react').Context<{ catalog: any, loading: boolean }>} */
const CatalogContext = createContext({ catalog: null, loading: true });

export function CatalogProvider({ children }) {
  const [catalog, setCatalog] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let alive = true;
    getServices()
      .catalog.getCatalog()
      .then((c) => {
        if (!alive) return;
        setCatalog(c);
        setLoading(false);
      });
    return () => { alive = false; };
  }, []);

  return <CatalogContext.Provider value={{ catalog, loading }}>{children}</CatalogContext.Provider>;
}

export function useCatalog() {
  return useContext(CatalogContext);
}
