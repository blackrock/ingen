//  InGen Studio — HTTP HistoryService adapter
//
//  Run history is owned by the backend: a run is persisted by POST /api/runs at execution time, so
//  `add` is a no-op here (avoids double-writing). `list`/`get` read from the wrapper. `clear` has no
//  backend endpoint in scope and is a no-op (history is server-authoritative in HTTP mode).

import { HistoryService } from '../services/historyService.js';

export class HttpHistoryAdapter extends HistoryService {
  constructor(client) {
    super();
    this.client = client;
  }

  async list(configId) {
    return this.client.get(`/api/runs/history?config_id=${encodeURIComponent(configId)}`);
  }

  async get(runId) {
    return this.client.get(`/api/runs/${encodeURIComponent(runId)}`);
  }

  async add() {
    // No-op: the backend already persisted the run during POST /api/runs.
  }

  async clear() {
    // No-op: no delete endpoint in scope; history is backend-owned in HTTP mode.
  }
}
