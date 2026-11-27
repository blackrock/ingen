//  Shared stage palette, constants, and source-consumer contract for the graph editor.

export const STAGE = {
  source: '#3b82f6',
  transform: '#f59e0b',
  columns: '#7853EC',
  post: '#ec4899',
  validation: '#10b981',
  output: '#ef4444',
};

// Pre-processors that pull in a SECONDARY source. Wiring a source node into one of these writes the
// named YAML field; `multi` types accept a list (union/melt), the rest a single id. `tag` labels the
// dashed feed edge so the relationship is legible on the canvas. Mirrors preProcessorSchemas.js.
export const SOURCE_CONSUMERS = {
  merge:             { param: 'source',          multi: false, tag: 'right' },
  outer_join:        { param: 'source',          multi: false, tag: 'right' },
  mask:              { param: 'masking_source',  multi: false, tag: 'mask' },
  not_equals_filter: { param: 'source',          multi: false, tag: 'exclude' },
  union:             { param: 'source',          multi: true,  tag: '∪' },
  melt:              { param: 'source',          multi: true,  tag: 'melt' },
};

/** Read a consumer's wired source ids as an array (handles single vs list params + stray scalars). */
export function wiredSources(step) {
  const spec = SOURCE_CONSUMERS[step?.type];
  if (!spec) return [];
  const v = step[spec.param];
  if (v == null || v === '') return [];
  return Array.isArray(v) ? v.filter(Boolean) : [v];
}

export const tr = (s, n = 28) => (s && s.length > n ? s.slice(0, n) + '…' : s);
export const SRC = 'src-';
export const PRE = 'pre-';

export const FLOW_STYLE  = { stroke: STAGE.columns, strokeWidth: 2 };
export const CONN_STYLE  = { stroke: STAGE.source, strokeWidth: 1.8, strokeDasharray: '5 4' };
