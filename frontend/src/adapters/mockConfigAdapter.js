//  InGen Studio — Mock ConfigService adapter
//
//  Implements the ConfigService contract against the browser's localStorage. This is REAL
//  persistence: configs created/edited here survive reloads. YAML import/export delegate to the
//  real serializers, and validation to the pure model validator — so the only thing "mock" about
//  this adapter is the storage backend. Swapping it for HttpConfigAdapter, which calls the FastAPI
//  wrapper, requires no change to callers.

import { ConfigService } from '../services/configService.js';
import { STORAGE_NAMESPACE } from '../models/constants.js';
import { validateConfigModel } from '../models/configModel.js';
import { modelToYaml, yamlToModel } from '../serializers/index.js';

/** @typedef {import('../models/types.js').ConfigModel} ConfigModel */
/** @typedef {import('../services/configService.js').ConfigSummary} ConfigSummary */

const STORE_KEY = `${STORAGE_NAMESPACE}:configs`;

/** Read the full id→ConfigModel map from localStorage (tolerant of missing/corrupt data). */
function readStore() {
  if (typeof localStorage === 'undefined') return {};
  try {
    const raw = localStorage.getItem(STORE_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

/** Persist the full id→ConfigModel map. */
function writeStore(store) {
  if (typeof localStorage === 'undefined') return;
  localStorage.setItem(STORE_KEY, JSON.stringify(store));
}

/** Deep clone so callers can't mutate persisted state by reference. */
function clone(value) {
  return JSON.parse(JSON.stringify(value));
}

export class MockConfigAdapter extends ConfigService {
  /** @returns {Promise<ConfigSummary[]>} */
  async list() {
    const store = readStore();
    return Object.values(store)
      .map((m) => ({
        id: m.meta.id,
        name: m.meta.name,
        updatedAt: m.meta.updatedAt,
        interfaceCount: m.interfaceOrder?.length ?? 0,
      }))
      .sort((a, b) => (a.updatedAt < b.updatedAt ? 1 : -1));
  }

  /** @param {string} id @returns {Promise<ConfigModel>} */
  async get(id) {
    const store = readStore();
    const model = store[id];
    if (!model) throw new Error(`Config "${id}" not found`);
    return clone(model);
  }

  /** @param {ConfigModel} model @returns {Promise<ConfigModel>} */
  async create(model) {
    const store = readStore();
    if (store[model.meta.id]) throw new Error(`Config "${model.meta.id}" already exists`);
    store[model.meta.id] = clone(model);
    writeStore(store);
    return clone(model);
  }

  /** @param {ConfigModel} model @returns {Promise<ConfigModel>} */
  async update(model) {
    const store = readStore();
    store[model.meta.id] = clone(model);
    writeStore(store);
    return clone(model);
  }

  /** @param {string} id @returns {Promise<void>} */
  async remove(id) {
    const store = readStore();
    delete store[id];
    writeStore(store);
  }

  /** @param {ConfigModel} model */
  async validate(model) {
    return validateConfigModel(model);
  }

  /** @param {string} yamlText @returns {Promise<ConfigModel>} */
  async importYaml(yamlText) {
    return yamlToModel(yamlText);
  }

  /** @param {ConfigModel} model @returns {Promise<string>} */
  async exportYaml(model) {
    return modelToYaml(model);
  }
}
