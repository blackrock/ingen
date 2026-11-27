//  InGen Studio — RunService interface
//
//  Executes a pipeline. `simulate` streams events (logs + stage transitions) through a handler and
//  resolves with the final RunRecord. The mock adapter fabricates that stream locally; the HTTP
//  adapter POSTs to the wrapper's /api/runs and replays the returned record through the same
//  handler. Both implement this signature, so the Run Console never changes.

/**
 * @typedef {Object} RunEvent
 * @property {'log'|'stage'} type
 * @property {string} ts                 ISO timestamp
 * @property {string} [interface]
 * @property {string} [stage]            read | pre_process | format | validate | write
 * @property {'info'|'warn'|'error'} [level]   for log events
 * @property {string} [message]          for log events
 * @property {'running'|'ok'|'warning'|'failed'|'skipped'} [status]  for stage events
 */

/**
 * @typedef {Object} RunStage
 * @property {string} interface
 * @property {string} stage
 * @property {'ok'|'warning'|'failed'|'skipped'} status
 */

/**
 * @typedef {Object} RunRecord
 * @property {string} runId
 * @property {string} configId
 * @property {string} configName
 * @property {'success'|'partial'|'failed'} status
 * @property {string} startedAt
 * @property {string} finishedAt
 * @property {number} durationMs
 * @property {RunStage[]} stages
 * @property {RunEvent[]} logs
 * @property {import('./validationService.js').ValidationReport} validation
 * @property {Object} overrides           runtime overrides used (run_date, interfaces, params…)
 */

const NOT_IMPLEMENTED = 'RunService method not implemented by adapter';

export class RunService {
  /**
   * @param {import('../models/types.js').ConfigModel} model
   * @param {Object} overrides
   * @param {{ onEvent?: (e: RunEvent) => void, isCancelled?: () => boolean }} [handlers]
   * @returns {Promise<RunRecord>}
   */
  async simulate(model, overrides, handlers) { void model; void overrides; void handlers; throw new Error(NOT_IMPLEMENTED); }
}
