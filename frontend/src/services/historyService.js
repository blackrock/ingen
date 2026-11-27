//  InGen Studio — HistoryService interface
//
//  Persists completed RunRecords for the Execution History view. The mock adapter uses
//  localStorage; the HTTP adapter reads the wrapper's runs endpoint. Same signatures.

/** @typedef {import('./runService.js').RunRecord} RunRecord */

const NOT_IMPLEMENTED = 'HistoryService method not implemented by adapter';

export class HistoryService {
  /** @param {string} configId @returns {Promise<RunRecord[]>} newest first */
  async list(configId) { void configId; throw new Error(NOT_IMPLEMENTED); }

  /** @param {string} runId @returns {Promise<RunRecord|null>} */
  async get(runId) { void runId; throw new Error(NOT_IMPLEMENTED); }

  /** @param {RunRecord} record @returns {Promise<void>} */
  async add(record) { void record; throw new Error(NOT_IMPLEMENTED); }

  /** @param {string} configId @returns {Promise<void>} */
  async clear(configId) { void configId; throw new Error(NOT_IMPLEMENTED); }
}
