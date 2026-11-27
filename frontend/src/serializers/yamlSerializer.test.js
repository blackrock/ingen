//  Tests for the YAML serializer / deserializer round-trip.
//
//  Run with: `node --test` (frontend is "type": "module", so the built-in runner imports the ESM
//  source directly — no extra test dependency). These pin the serializer's two contracts: (1) it is
//  the inverse of the deserializer for a normalized model (round-trip is lossless + idempotent), and
//  (2) it is deterministic — stable key order, empty sections dropped.

import test from 'node:test';
import assert from 'node:assert/strict';

import { modelToYaml, modelToRawConfig } from './yamlSerializer.js';
import { yamlToModel, rawConfigToModel } from './yamlDeserializer.js';

const SAMPLE_YAML = `sources:
  - id: positions
    type: file
    file_path: /data/pos.csv
  - id: prices
    type: mysql
interfaces:
  daily:
    sources:
      - positions
      - prices
    pre_processing:
      - type: merge
    columns:
      - src_col_name: qty
        dest_col_name: quantity
    output:
      type: delimited_file
      props:
        path: /out/daily.csv
run_config:
  writer: InterfaceWriter
`;

test('round-trip yaml -> model -> yaml -> model is lossless', () => {
  const model1 = yamlToModel(SAMPLE_YAML);
  const yaml1 = modelToYaml(model1);
  const model2 = yamlToModel(yaml1);

  // The normalized document content must survive a full round-trip.
  assert.deepEqual(model2.sourcesById, model1.sourcesById);
  assert.deepEqual(model2.sourceOrder, model1.sourceOrder);
  assert.deepEqual(model2.interfacesByName, model1.interfacesByName);
  assert.deepEqual(model2.interfaceOrder, model1.interfaceOrder);
  assert.deepEqual(model2.run_config, model1.run_config);
});

test('serialization is idempotent (deterministic output)', () => {
  const model = yamlToModel(SAMPLE_YAML);
  const a = modelToYaml(model);
  const b = modelToYaml(yamlToModel(a));
  assert.equal(a, b);
});

test('source and interface declaration order is preserved', () => {
  const model = yamlToModel(SAMPLE_YAML);
  assert.deepEqual(model.sourceOrder, ['positions', 'prices']);
  const raw = modelToRawConfig(model);
  // sources are emitted as an ordered list in declaration order.
  assert.deepEqual(raw.sources.map((s) => s.id), ['positions', 'prices']);
  // interface body sections follow the fixed INTERFACE_SECTIONS order.
  const keys = Object.keys(raw.interfaces.daily);
  assert.deepEqual(keys, ['sources', 'pre_processing', 'columns', 'output']);
});

test('top-level key order is sources -> interfaces -> run_config', () => {
  const model = yamlToModel(SAMPLE_YAML);
  assert.deepEqual(Object.keys(modelToRawConfig(model)), ['sources', 'interfaces', 'run_config']);
});

test('empty sections are dropped from the emitted document', () => {
  const raw = {
    interfaces: { a: { sources: ['s'], pre_processing: [], columns: [], post_processing: [], output: {} } },
    sources: [{ id: 's', type: 'file' }],
  };
  const model = rawConfigToModel(raw);
  const out = modelToRawConfig(model);
  // Only the non-empty `sources` section remains on the interface body.
  assert.deepEqual(Object.keys(out.interfaces.a), ['sources']);
  assert.ok(!('pre_processing' in out.interfaces.a));
  assert.ok(!('output' in out.interfaces.a));
});

test('deserializer rejects non-mapping documents', () => {
  assert.throws(() => yamlToModel('- 1\n- 2\n'), /mapping/);
});
