//  InGen Studio — Mock CatalogService adapter
//
//  Returns the static catalog assembled from the backend-derived registries in models/constants.js.
//  Real and final: these values match the backend today, so this adapter survives into production
//  unless the catalog is ever moved server-side.

import { CatalogService } from '../services/catalogService.js';
import {
  SOURCE_TYPES,
  FILE_TYPES,
  PRE_PROCESSOR_TYPES,
  POST_PROCESSOR_TYPES,
  FORMATTER_TYPES,
  VALIDATION_TYPES,
  VALIDATION_SEVERITIES,
  OUTPUT_TYPES,
  INTERPOLATORS,
} from '../models/constants.js';

/** @typedef {import('../services/catalogService.js').Catalog} Catalog */

export class MockCatalogAdapter extends CatalogService {
  /** @returns {Promise<Catalog>} */
  async getCatalog() {
    return {
      sourceTypes: Object.values(SOURCE_TYPES),
      fileTypes: Object.values(FILE_TYPES),
      preProcessors: Object.values(PRE_PROCESSOR_TYPES),
      postProcessors: Object.values(POST_PROCESSOR_TYPES),
      formatters: [...FORMATTER_TYPES],
      validations: { builtin: [...VALIDATION_TYPES.BUILTIN], custom: [...VALIDATION_TYPES.CUSTOM] },
      validationSeverities: Object.values(VALIDATION_SEVERITIES),
      outputTypes: Object.values(OUTPUT_TYPES),
      interpolators: { static: [...INTERPOLATORS.STATIC], runtime: [...INTERPOLATORS.RUNTIME] },
    };
  }
}
