//  useDocTitle — sets document.title with an optional segment and the app suffix.
//  Example: useDocTitle('interface_1', 'My Pipeline') → "interface_1 — My Pipeline — InGen Studio"

import { useEffect } from 'react';

const SUFFIX = 'InGen Studio';

export function useDocTitle(...segments) {
  useEffect(() => {
    const parts = segments.filter(Boolean);
    document.title = parts.length > 0 ? `${parts.join(' — ')} — ${SUFFIX}` : SUFFIX;
  }, [segments.join('|')]);   // eslint-disable-line react-hooks/exhaustive-deps
}
