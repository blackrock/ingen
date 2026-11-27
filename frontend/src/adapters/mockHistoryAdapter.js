//  Mock HistoryService — persists RunRecords in localStorage, namespaced per app. Real persistence
//  (survives reloads). A future HttpHistoryAdapter swaps the storage for the wrapper's runs endpoint.

import { HistoryService } from '../services/historyService.js';
import { STORAGE_NAMESPACE } from '../models/constants.js';

const KEY = `${STORAGE_NAMESPACE}:runs`;

function readAll() {
  if (typeof localStorage === 'undefined') return [];
  try {
    const raw = localStorage.getItem(KEY);
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
}

function writeAll(records) {
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem(KEY, JSON.stringify(records));
}

export class MockHistoryAdapter extends HistoryService {
  async list(configId) {
    return readAll()
      .filter((r) => r.configId === configId)
      .sort((a, b) => (a.startedAt < b.startedAt ? 1 : -1));
  }

  async get(runId) {
    return readAll().find((r) => r.runId === runId) ?? null;
  }

  async add(record) {
    const all = readAll();
    all.push(record);
    // Keep the store bounded (most recent 100 runs).
    writeAll(all.slice(-100));
  }

  async clear(configId) {
    writeAll(readAll().filter((r) => r.configId !== configId));
  }
}
