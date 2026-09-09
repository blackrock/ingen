//  InGen Studio — YAML deserializer (yamlToModel)
//
//  Parses an InGen YAML document into the normalized ConfigModel. Mirrors the resolution the
//  backend's MetaDataParser performs (top-level sources/interfaces/run_config), but keeps the
//  frontend's normalized maps + order arrays.
//
//  Extensibility: normalization runs through section normalizers so future per-section coercion
//  (e.g. defaulting dest_col_name, validating formatter shapes) slots in without rewriting the core.

import yaml from 'js-yaml';

import { createEmptyConfig } from '../models/configModel.js';

/** @typedef {import('../models/types.js').ConfigModel} ConfigModel */
/** @typedef {import('../models/types.js').RawConfig} RawConfig */

/** Error thrown when YAML is syntactically invalid or structurally unusable. */
export class YamlParseError extends Error {
  /** @param {string} message @param {{ line?: number, column?: number, cause?: unknown }} [info] */
  constructor(message, info = {}) {
    super(message);
    this.name = 'YamlParseError';
    this.line = info.line;
    this.column = info.column;
    this.cause = info.cause;
  }
}

/**
 * Parse raw YAML text into the backend document shape. Surfaces js-yaml position info.
 * @param {string} text
 * @returns {RawConfig}
 */
export function parseYaml(text) {
  let doc;
  try {
    doc = yaml.load(text);
  } catch (err) {
    const mark = err && err.mark ? err.mark : {};
    throw new YamlParseError(err?.reason || 'Failed to parse YAML', {
      line: mark.line,
      column: mark.column,
      cause: err,
    });
  }
  if (doc == null || typeof doc !== 'object' || Array.isArray(doc)) {
    throw new YamlParseError('Top-level YAML must be a mapping with sources/interfaces.');
  }
  return /** @type {RawConfig} */ (doc);
}

/**
 * Normalize a raw InGen document into a ConfigModel.
 * @param {RawConfig} raw
 * @param {{ id?: string, name?: string }} [meta]
 * @returns {ConfigModel}
 */
export function rawConfigToModel(raw, meta = {}) {
  const model = createEmptyConfig(meta);

  // run_config: keep only what the file declares so a file without one round-trips without one.
  // The backend's RunConfiguration resolves missing names to defaults.
  model.run_config = { ...(raw.run_config ?? {}) };

  // sources: list → { sourcesById, sourceOrder }, preserving order.
  const sources = Array.isArray(raw.sources) ? raw.sources : [];
  for (const [i, source] of sources.entries()) {
    // Fail loudly: the backend does source["id"] and raises on the same input; validateConfigModel
    // never sees entries dropped here, so silently skipping would hide the problem.
    if (!source || typeof source !== 'object' || !source.id) {
      throw new YamlParseError(`sources[${i}] is missing an "id".`);
    }
    model.sourcesById[source.id] = source;
    model.sourceOrder.push(source.id);
  }

  // interfaces: mapping → { interfacesByName, interfaceOrder }, preserving key order.
  const interfaces = raw.interfaces && typeof raw.interfaces === 'object' ? raw.interfaces : {};
  for (const name of Object.keys(interfaces)) {
    model.interfacesByName[name] = normalizeInterface(interfaces[name]);
    model.interfaceOrder.push(name);
  }

  return model;
}

/**
 * Coerce a raw interface into the normalized shape. In the backend YAML `sources` is already a
 * list of source-id strings, so it passes through; arrays default to [] so the editor never sees
 * undefined. This is the seam where future field-level normalization is added.
 */
function normalizeInterface(rawIface) {
  const iface = rawIface && typeof rawIface === 'object' ? rawIface : {};
  return {
    sources: Array.isArray(iface.sources) ? iface.sources : [],
    pre_processing: Array.isArray(iface.pre_processing) ? iface.pre_processing : [],
    columns: Array.isArray(iface.columns) ? iface.columns : [],
    post_processing: Array.isArray(iface.post_processing) ? iface.post_processing : [],
    ...(iface.validation_action ? { validation_action: iface.validation_action } : {}),
    output: iface.output && typeof iface.output === 'object' ? iface.output : {},
  };
}

/**
 * Convenience: YAML text → ConfigModel in one call.
 * @param {string} text
 * @param {{ id?: string, name?: string }} [meta]
 * @returns {ConfigModel}
 */
export function yamlToModel(text, meta = {}) {
  return rawConfigToModel(parseYaml(text), meta);
}
