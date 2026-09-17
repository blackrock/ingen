//  Per-source column cache (from file uploads). Kept OUT of the config model so it never leaks into
//  the serialized YAML — the serializer dumps source objects verbatim. Uses localStorage so column
//  names survive tab close and reload (previously sessionStorage caused silent autocomplete loss).

const KEY = (sid) => `ingen:cols:${sid}`;

export function setColumns(sourceId, columns) {
  try { localStorage.setItem(KEY(sourceId), JSON.stringify(columns || [])); } catch { /* ignore */ }
}

export function getColumns(sourceId) {
  try { return JSON.parse(localStorage.getItem(KEY(sourceId))) || []; } catch { return []; }
}

/** Union of columns across a list of source ids (deduped, order-preserving). */
export function columnsForSources(sourceIds = []) {
  const seen = new Set();
  const out = [];
  for (const sid of sourceIds) for (const c of getColumns(sid)) if (!seen.has(c)) { seen.add(c); out.push(c); }
  return out;
}
