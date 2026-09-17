//  InGen Studio — services barrel + locator
//
//  Components import `getServices()` and never touch adapters directly. The active backend mode is
//  read once from the Next env (NEXT_PUBLIC_ADAPTER_MODE), defaulting to mock. This is the seam that
//  makes the mock→FastAPI swap a one-line config change.

import { ADAPTER_MODE } from '../models/constants.js';
import { buildServices } from '../adapters/index.js';

export { ConfigService } from './configService.js';
export { CatalogService } from './catalogService.js';
export { ValidationService } from './validationService.js';
export { RunService } from './runService.js';
export { HistoryService } from './historyService.js';

/** Resolve the configured adapter mode from the build env, defaulting to mock. */
function resolveMode() {
  // Next inlines NEXT_PUBLIC_* at build time for client bundles; process.env also works in plain
  // Node test runs, so no guard is needed.
  return process.env.NEXT_PUBLIC_ADAPTER_MODE ?? ADAPTER_MODE.MOCK;
}

/** The active backend mode (one of ADAPTER_MODE.*). Lets the UI label real vs. simulated runs. */
export function getAdapterMode() {
  return resolveMode();
}

/** @type {import('../adapters/index.js').ServiceSet | null} */
let _services = null;

/**
 * Lazily construct and memoize the service set for the current mode.
 * @returns {import('../adapters/index.js').ServiceSet}
 */
export function getServices() {
  if (!_services) _services = buildServices(resolveMode());
  return _services;
}

/** Test/util hook: force a specific service set (e.g. inject fakes) or reset memoization. */
export function setServices(services) {
  _services = services;
}
