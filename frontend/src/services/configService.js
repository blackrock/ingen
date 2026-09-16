//  InGen Studio — ConfigService interface
//
//  The adapter-agnostic contract for persisting and translating config documents. Both the
//  localStorage-backed MockConfigAdapter and the HttpConfigAdapter that calls the FastAPI wrapper
//  satisfy the SAME signatures. UI code depends only on this interface, so swapping adapters
//  touches nothing in the components.
//
//  Pattern: an abstract base class whose methods throw until an adapter overrides them. This gives
//  us a single place to document the contract and a runtime guard against unimplemented methods.

/** @typedef {import('../models/types.js').ConfigModel} ConfigModel */
/** @typedef {import('../models/types.js').ConfigIssue} ConfigIssue */

/**
 * Lightweight listing entry (no full body) for the configs landing page.
 * @typedef {Object} ConfigSummary
 * @property {string} id
 * @property {string} name
 * @property {string} updatedAt
 * @property {number} interfaceCount
 */

const NOT_IMPLEMENTED = 'ConfigService method not implemented by adapter';

export class ConfigService {
  /** @returns {Promise<ConfigSummary[]>} */
  async list() { throw new Error(NOT_IMPLEMENTED); }

  /** @param {string} id @returns {Promise<ConfigModel>} */
  async get(id) { void id; throw new Error(NOT_IMPLEMENTED); }

  /** @param {ConfigModel} model @returns {Promise<ConfigModel>} */
  async create(model) { void model; throw new Error(NOT_IMPLEMENTED); }

  /** @param {ConfigModel} model @returns {Promise<ConfigModel>} */
  async update(model) { void model; throw new Error(NOT_IMPLEMENTED); }

  /** @param {string} id @returns {Promise<void>} */
  async remove(id) { void id; throw new Error(NOT_IMPLEMENTED); }

  /** Schema/cross-reference validation without running the pipeline. @param {ConfigModel} model @returns {Promise<ConfigIssue[]>} */
  async validate(model) { void model; throw new Error(NOT_IMPLEMENTED); }

  /** Parse pasted YAML into a model. @param {string} yamlText @returns {Promise<ConfigModel>} */
  async importYaml(yamlText) { void yamlText; throw new Error(NOT_IMPLEMENTED); }

  /** Serialize a model to YAML text. @param {ConfigModel} model @returns {Promise<string>} */
  async exportYaml(model) { void model; throw new Error(NOT_IMPLEMENTED); }
}
