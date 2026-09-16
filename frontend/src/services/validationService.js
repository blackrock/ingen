//  InGen Studio — ValidationService interface
//
//  Produces validation results for a configured pipeline WITHOUT executing it. The mock derives
//  realistic pass/fail/warn outcomes from the column validations actually configured in the model;
//  the HTTP adapter returns real great_expectations results from the backend. Same shape.

/**
 * @typedef {Object} ValidationResult
 * @property {string} interface
 * @property {string} column
 * @property {string} expectation
 * @property {'blocker'|'critical'|'warning'} severity
 * @property {'passed'|'failed'|'warning'} status
 * @property {number} unexpectedCount
 */

/**
 * @typedef {Object} ValidationReport
 * @property {ValidationResult[]} results
 * @property {{ passed: number, failed: number, warning: number, total: number }} summary
 */

const NOT_IMPLEMENTED = 'ValidationService method not implemented by adapter';

export class ValidationService {
  /**
   * @param {import('../models/types.js').ConfigModel} model
   * @param {string[]} [interfaceNames] subset; defaults to all
   * @returns {Promise<ValidationReport>}
   */
  async evaluate(model, interfaceNames) { void model; void interfaceNames; throw new Error(NOT_IMPLEMENTED); }
}
