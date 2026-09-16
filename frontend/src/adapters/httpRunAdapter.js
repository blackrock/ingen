//  InGen Studio — HTTP RunService adapter
//
//  Serializes the model with the SAME serializer the editor uses, POSTs the YAML to the wrapper
//  (which runs `python -m ingen` and returns a structured RunRecord), then replays the record's
//  logs and stages through `onEvent` so the live console panels (timeline, log stream) populate
//  exactly as they do in mock mode. Returns the identical RunRecord shape — components don't change.

import { RunService } from '../services/runService.js';
import { modelToYaml } from '../serializers/index.js';
import { makeId } from '../utils/id.js';

export class HttpRunAdapter extends RunService {
  constructor(client) {
    super();
    this.client = client;
  }

  async simulate(model, overrides = {}, handlers = {}) {
    const { onEvent, isCancelled } = handlers;
    const yaml = modelToYaml(model);

    if (isCancelled?.()) {
      return this._cancelledRecord(model, overrides);
    }

    const record = await this.client.post('/api/runs', {
      yaml,
      configId: model.meta.id,
      configName: model.meta.name,
      run_date: overrides.run_date ?? null,
      interfaces: overrides.interfaces ?? null,
      query_params: overrides.query_params ?? null,
      override_params: overrides.override_params ?? null,
    });

    // Replay backend results as a stream so the UI behaves identically to mock mode.
    if (onEvent) {
      (record.logs ?? []).forEach((e) => onEvent(e));
      (record.stages ?? []).forEach((s) =>
        onEvent({ type: 'stage', ts: record.startedAt, interface: s.interface, stage: s.stage, status: s.status }));
    }
    return record;
  }

  _cancelledRecord(model, overrides) {
    const ts = new Date().toISOString();
    return {
      runId: makeId('run_cancelled'),
      configId: model.meta.id,
      configName: model.meta.name,
      status: 'failed',
      startedAt: ts,
      finishedAt: ts,
      durationMs: 0,
      stages: [],
      logs: [{ type: 'log', ts, level: 'warn', message: 'Run cancelled before submission.' }],
      validation: { results: [], summary: { passed: 0, failed: 0, warning: 0, total: 0 } },
      overrides,
    };
  }
}
