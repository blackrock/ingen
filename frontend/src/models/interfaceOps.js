//  InGen Studio — pure interface operations
//
//  Immutable helpers that all six editor tabs share for add/update/remove/reorder on an interface's
//  list fields (sources, pre_processing, columns) and for nested column validations. Keeping these
//  pure + centralized means the editors carry no mutation logic and the behavior is testable in
//  isolation. They return a NEW interface; callers pass them to ConfigContext.updateInterface.

/** @typedef {import('./types.js').Interface} Interface */

function asArray(v) {
  return Array.isArray(v) ? v : [];
}

/** Append an item to a list field. */
export function listAdd(iface, field, item) {
  return { ...iface, [field]: [...asArray(iface[field]), item] };
}

/** Replace the item at index in a list field. */
export function listUpdate(iface, field, index, item) {
  const next = asArray(iface[field]).map((cur, i) => (i === index ? item : cur));
  return { ...iface, [field]: next };
}

/** Remove the item at index from a list field. */
export function listRemove(iface, field, index) {
  return { ...iface, [field]: asArray(iface[field]).filter((_, i) => i !== index) };
}

/** Move the item at index by `dir` (-1 up / +1 down). No-op at the ends. */
export function listMove(iface, field, index, dir) {
  const arr = [...asArray(iface[field])];
  const target = index + dir;
  if (target < 0 || target >= arr.length) return iface;
  [arr[index], arr[target]] = [arr[target], arr[index]];
  return { ...iface, [field]: arr };
}

/** Set a scalar/object field (e.g. output). */
export function setField(iface, field, value) {
  return { ...iface, [field]: value };
}

// ── Nested: column validations (columns[colIndex].validations[]) ──

function mapColumnValidations(iface, colIndex, fn) {
  const columns = asArray(iface.columns).map((col, i) => {
    if (i !== colIndex) return col;
    const validations = fn(asArray(col.validations));
    return { ...col, validations };
  });
  return { ...iface, columns };
}

export function colValAdd(iface, colIndex, item) {
  return mapColumnValidations(iface, colIndex, (vs) => [...vs, item]);
}

export function colValUpdate(iface, colIndex, valIndex, item) {
  return mapColumnValidations(iface, colIndex, (vs) => vs.map((v, i) => (i === valIndex ? item : v)));
}

export function colValRemove(iface, colIndex, valIndex) {
  return mapColumnValidations(iface, colIndex, (vs) => vs.filter((_, i) => i !== valIndex));
}
