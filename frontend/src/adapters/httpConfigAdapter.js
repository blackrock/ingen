//  InGen Studio — HTTP ConfigService adapter
//
//  Config CRUD has no backend endpoint in scope, so persistence (list/get/create/update/remove) and
//  YAML import/export are inherited unchanged from the localStorage-backed MockConfigAdapter. Only
//  `validate` is routed to the FastAPI wrapper (POST /api/configs/validate), which performs the same
//  schema/cross-reference checks server-side. Same ConfigService interface, so callers don't change.

import { MockConfigAdapter } from './mockConfigAdapter.js';
import { modelToYaml } from '../serializers/index.js';

export class HttpConfigAdapter extends MockConfigAdapter {
  constructor(client) {
    super();
    this.client = client;
  }

  /** @param {import('../models/types.js').ConfigModel} model */
  async validate(model) {
    const yaml = modelToYaml(model);
    const res = await this.client.post('/api/configs/validate', { yaml });
    return res.issues ?? [];
  }
}
