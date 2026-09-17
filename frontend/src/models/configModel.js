//  InGen Studio — ConfigModel
//
//  Pure, framework-free helpers that create, mutate, normalize, and validate the normalized
//  ConfigModel. No React, no I/O. Every function is a pure transform (returns a new model) so it
//  can be driven by a reducer later and unit-tested in isolation.

import { CONFIG_MODEL_VERSION } from './constants.js';
import { makeId } from '../utils/id.js';

/** @typedef {import('./types.js').ConfigModel} ConfigModel */
/** @typedef {import('./types.js').Source} Source */
/** @typedef {import('./types.js').Interface} Interface */
/** @typedef {import('./types.js').ConfigIssue} ConfigIssue */

/**
 * Create an empty, valid ConfigModel.
 * @param {{id?: string, name?: string}} [opts]
 * @returns {ConfigModel}
 */
export function createEmptyConfig(opts = {}) {
  const now = new Date().toISOString();
  return {
    meta: {
      id: opts.id ?? makeId('cfg'),
      name: opts.name ?? 'Untitled config',
      version: CONFIG_MODEL_VERSION,
      createdAt: now,
      updatedAt: now,
    },
    run_config: {}, // only what the user/file declares; the backend's RunConfiguration resolves defaults
    sourcesById: {},
    sourceOrder: [],
    interfacesByName: {},
    interfaceOrder: [],
  };
}

/** Shallow-clone a model and stamp updatedAt. Internal helper for all mutators. */
function touch(model) {
  return {
    ...model,
    meta: { ...model.meta, updatedAt: new Date().toISOString() },
  };
}

// ───────────────────────── Sources ─────────────────────────

/**
 * Add or replace a source. The source's `id` is the map key and the order key.
 * @param {ConfigModel} model
 * @param {Source} source
 * @returns {ConfigModel}
 */
export function upsertSource(model, source) {
  if (!source?.id) throw new Error('Source requires an id');
  const next = touch(model);
  next.sourcesById = { ...model.sourcesById, [source.id]: source };
  next.sourceOrder = model.sourceOrder.includes(source.id)
    ? [...model.sourceOrder]
    : [...model.sourceOrder, source.id];
  return next;
}

/**
 * Remove a source by id (does not rewrite interfaces that still reference it — validation surfaces that).
 * @param {ConfigModel} model
 * @param {string} sourceId
 * @returns {ConfigModel}
 */
export function removeSource(model, sourceId) {
  const next = touch(model);
  next.sourcesById = { ...model.sourcesById };
  delete next.sourcesById[sourceId];
  next.sourceOrder = model.sourceOrder.filter((id) => id !== sourceId);
  return next;
}

// ───────────────────────── Interfaces ─────────────────────────

/** @returns {Interface} an empty interface skeleton. */
export function createEmptyInterface() {
  return { sources: [], pre_processing: [], columns: [], post_processing: [], output: {} };
}

/**
 * Add or replace an interface under `name`. Order is preserved/appended — interfaces run in YAML
 * declaration order.
 * @param {ConfigModel} model
 * @param {string} name
 * @param {Interface} iface
 * @returns {ConfigModel}
 */
export function upsertInterface(model, name, iface) {
  if (!name) throw new Error('Interface requires a name');
  const next = touch(model);
  next.interfacesByName = { ...model.interfacesByName, [name]: iface };
  next.interfaceOrder = model.interfaceOrder.includes(name)
    ? [...model.interfaceOrder]
    : [...model.interfaceOrder, name];
  return next;
}

/**
 * Remove an interface by name.
 * @param {ConfigModel} model
 * @param {string} name
 * @returns {ConfigModel}
 */
export function removeInterface(model, name) {
  const next = touch(model);
  next.interfacesByName = { ...model.interfacesByName };
  delete next.interfacesByName[name];
  next.interfaceOrder = model.interfaceOrder.filter((n) => n !== name);
  return next;
}

/**
 * Rename an interface (moves the key in interfacesByName + updates interfaceOrder).
 * @param {ConfigModel} model
 * @param {string} oldName
 * @param {string} newName
 * @returns {ConfigModel}
 */
export function renameInterface(model, oldName, newName) {
  if (!newName || oldName === newName) return model;
  if (model.interfacesByName[newName]) throw new Error(`Interface "${newName}" already exists`);
  const next = touch(model);
  const data = model.interfacesByName[oldName];
  next.interfacesByName = { ...model.interfacesByName, [newName]: data };
  delete next.interfacesByName[oldName];
  next.interfaceOrder = model.interfaceOrder.map((n) => (n === oldName ? newName : n));
  return next;
}

/**
 * Reorder interfaces. Pass the full new order (must be a permutation of existing names).
 * @param {ConfigModel} model
 * @param {string[]} newOrder
 * @returns {ConfigModel}
 */
export function reorderInterfaces(model, newOrder) {
  const known = new Set(model.interfaceOrder);
  const valid =
    newOrder.length === known.size &&
    new Set(newOrder).size === known.size && // reject repeats: ['a','a'] would silently drop 'b'
    newOrder.every((n) => known.has(n));
  if (!valid) throw new Error('reorderInterfaces requires a permutation of existing interface names');
  const next = touch(model);
  next.interfaceOrder = [...newOrder];
  return next;
}

// ───────────────────────── Validation (no execution) ─────────────────────────

/**
 * Cross-reference + structural checks that need no pipeline run. Mirrors the integrity rules the
 * backend relies on (resolved by MetaDataParser / SourceFactory).
 *
 * @param {ConfigModel} model
 * @returns {ConfigIssue[]}
 */
export function validateConfigModel(model) {
  /** @type {ConfigIssue[]} */
  const issues = [];

  if (model.interfaceOrder.length === 0) {
    issues.push({ level: 'warning', code: 'NO_INTERFACES', message: 'Config has no interfaces.' });
  }

  model.interfaceOrder.forEach((name) => {
    const iface = model.interfacesByName[name];
    const path = `interfacesByName.${name}`;

    // Every referenced source id must exist as a defined source.
    (iface.sources ?? []).forEach((sid, i) => {
      if (!model.sourcesById[sid]) {
        issues.push({
          level: 'error',
          code: 'UNKNOWN_SOURCE_REF',
          message: `Interface "${name}" references source "${sid}" which is not defined.`,
          path: `${path}.sources[${i}]`,
        });
      }
    });
  });

  return issues;
}

/** Convenience: true when there are no error-level issues. */
export function isConfigValid(model) {
  return validateConfigModel(model).every((i) => i.level !== 'error');
}
