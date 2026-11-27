//  InGen Studio — YAML serializer (modelToYaml)
//
//  Converts the normalized ConfigModel into the exact YAML document InGen consumes.
//  Real (not stubbed) output via js-yaml. Determinism is the contract: stable key order,
//  unlimited line width, no anchors — so the live preview and diffs are reproducible.
//
//  Extensibility: the interface body is emitted by looping the ordered key list
//  INTERFACE_SECTION_ORDER. Supporting a new section later = add one string. Sources / columns /
//  output currently pass through structurally (they are already plain YAML-shaped objects in the
//  model), which is why the skeleton round-trips losslessly without yet modelling every leaf field.

import yaml from 'js-yaml';

/** @typedef {import('../models/types.js').ConfigModel} ConfigModel */
/** @typedef {import('../models/types.js').RawConfig} RawConfig */
/** @typedef {import('../models/types.js').Interface} Interface */

/** js-yaml dump options chosen for deterministic, InGen-friendly output. */
const DUMP_OPTIONS = Object.freeze({
  indent: 2,
  lineWidth: -1, // never wrap — keep long paths/queries on one line
  noRefs: true, // never emit YAML anchors/aliases
  quotingType: '"',
  // NOTE: sortKeys is intentionally NOT set — we control order by building ordered objects,
  // which preserves InGen's conventional section order instead of forcing alphabetical.
});

/** Drop keys whose values are empty ({}/[]/undefined/null) so the YAML stays clean. */
function isEmpty(value) {
  if (value == null) return true;
  if (Array.isArray(value)) return value.length === 0;
  if (typeof value === 'object') return Object.keys(value).length === 0;
  return false;
}

// Order of sections in an emitted interface body, matching the order InGen's own sample configs
// use so generated YAML reads the same as hand-written YAML. Empty sections are dropped.
const INTERFACE_SECTION_ORDER = [
  'sources', 'pre_processing', 'columns', 'post_processing', 'validation_action', 'output',
];

/** Build the ordered plain object for a single interface, omitting empty sections. */
function interfaceToObject(iface) {
  const obj = {};
  for (const key of INTERFACE_SECTION_ORDER) {
    if (!isEmpty(iface[key])) obj[key] = iface[key];
  }
  return obj;
}

/**
 * Denormalize a ConfigModel into the raw InGen document shape.
 * Top-level key order: sources → interfaces → run_config.
 * @param {ConfigModel} model
 * @returns {RawConfig}
 */
export function modelToRawConfig(model) {
  /** @type {RawConfig} */
  const raw = {};

  // sources: ordered list of full definitions.
  const sources = model.sourceOrder.map((id) => model.sourcesById[id]).filter(Boolean);
  if (!isEmpty(sources)) raw.sources = sources;

  // interfaces: mapping keyed by name, preserving declaration order.
  const interfaces = {};
  for (const name of model.interfaceOrder) {
    const iface = model.interfacesByName[name];
    if (iface) interfaces[name] = interfaceToObject(iface);
  }
  if (!isEmpty(interfaces)) raw.interfaces = interfaces;

  // run_config: only emit when it differs from being absent (keep it simple — always emit if present).
  if (!isEmpty(model.run_config)) raw.run_config = { ...model.run_config };

  return raw;
}

/**
 * Serialize a ConfigModel to a YAML string.
 * @param {ConfigModel} model
 * @returns {string}
 */
export function modelToYaml(model) {
  const raw = modelToRawConfig(model);
  return yaml.dump(raw, DUMP_OPTIONS);
}

export { DUMP_OPTIONS };
