//  InGen Studio — CatalogService interface
//
//  Serves the component palettes (source types, pre/post-processors, formatters, validations,
//  writers, interpolators). These are static and derived from the backend registries, so the
//  catalog adapter returns them straight from src/models/constants.js in both mock and http mode.

/**
 * @typedef {Object} Catalog
 * @property {string[]} sourceTypes
 * @property {string[]} fileTypes
 * @property {string[]} preProcessors
 * @property {string[]} postProcessors
 * @property {string[]} formatters
 * @property {{ builtin: string[], custom: string[] }} validations
 * @property {string[]} validationSeverities
 * @property {string[]} outputTypes
 * @property {{ static: string[], runtime: string[] }} interpolators
 */

const NOT_IMPLEMENTED = 'CatalogService method not implemented by adapter';

export class CatalogService {
  /** @returns {Promise<Catalog>} the full catalog in one call. */
  async getCatalog() { throw new Error(NOT_IMPLEMENTED); }
}
