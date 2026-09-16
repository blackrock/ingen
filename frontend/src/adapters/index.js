//  InGen Studio — adapter selection (the one swap point)
//
//  `buildServices(mode)` returns the concrete service set for a given backend mode. Two sets
//  exist: `mock` (localStorage, no server required) and `http` (the FastAPI wrapper). Both
//  implement the same service interfaces, so callers work unchanged against either.

import { ADAPTER_MODE } from '../models/constants.js';
import { MockConfigAdapter } from './mockConfigAdapter.js';
import { MockCatalogAdapter } from './mockCatalogAdapter.js';
import { MockValidationAdapter } from './mockValidationAdapter.js';
import { MockRunAdapter } from './mockRunAdapter.js';
import { MockHistoryAdapter } from './mockHistoryAdapter.js';
import { HttpClient } from './httpClient.js';
import { HttpConfigAdapter } from './httpConfigAdapter.js';
import { HttpValidationAdapter } from './httpValidationAdapter.js';
import { HttpRunAdapter } from './httpRunAdapter.js';
import { HttpHistoryAdapter } from './httpHistoryAdapter.js';
import { MockChatAdapter } from './mockChatAdapter.js';
import { HttpChatAdapter } from './httpChatAdapter.js';

/**
 * @typedef {Object} ServiceSet
 * @property {import('../services/configService.js').ConfigService} config
 * @property {import('../services/catalogService.js').CatalogService} catalog
 * @property {import('../services/validationService.js').ValidationService} validation
 * @property {import('../services/runService.js').RunService} run
 * @property {import('../services/historyService.js').HistoryService} history
 * @property {{ interpret: Function, warmup: Function }} chat
 */

/**
 * @param {string} [mode] one of ADAPTER_MODE.*; defaults to MOCK.
 * @returns {ServiceSet}
 */
export function buildServices(mode = ADAPTER_MODE.MOCK) {
  switch (mode) {
    case ADAPTER_MODE.MOCK: {
      const validation = new MockValidationAdapter();
      return {
        config: new MockConfigAdapter(),
        catalog: new MockCatalogAdapter(),
        validation,
        run: new MockRunAdapter(validation), // run reuses the same validation service
        history: new MockHistoryAdapter(),
        chat: new MockChatAdapter(),
      };
    }
    case ADAPTER_MODE.HTTP: {
      // Base URL of the FastAPI wrapper; configurable via NEXT_PUBLIC_API_BASE_URL.
      const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
      const client = new HttpClient(baseUrl);
      return {
        config: new HttpConfigAdapter(client), // CRUD via localStorage; validate → backend
        catalog: new MockCatalogAdapter(),     // catalog is static (backend-derived constants)
        validation: new HttpValidationAdapter(client),
        run: new HttpRunAdapter(client),
        history: new HttpHistoryAdapter(client),
        chat: new HttpChatAdapter(client),
      };
    }
    default:
      throw new Error(`Unknown adapter mode "${mode}"`);
  }
}
