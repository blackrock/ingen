//  Tests for YAML import flow — covers edge cases that could break the Import YAML feature.
//  Ensures yamlToModel correctly handles meta overrides, malformed input, and round-trip integrity.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import { yamlToModel } from './yamlDeserializer.js';
import { modelToYaml } from './yamlSerializer.js';

const VALID_YAML = `sources:
  - id: sales
    type: file
    file_path: /data/sales.csv
interfaces:
  report:
    sources:
      - sales
    columns:
      - src_col_name: amount
        dest_col_name: total
    output:
      type: excel
      props:
        path: /out/report.xlsx
`;

test('yamlToModel with meta overrides sets custom id and name', () => {
  const m = yamlToModel(VALID_YAML, { id: 'custom_id', name: 'My Pipeline' });
  assert.equal(m.meta.id, 'custom_id');
  assert.equal(m.meta.name, 'My Pipeline');
  assert.deepEqual(m.sourceOrder, ['sales']);
  assert.deepEqual(m.interfaceOrder, ['report']);
});

test('yamlToModel without meta overrides generates defaults', () => {
  const m = yamlToModel(VALID_YAML);
  assert.ok(m.meta.id, 'should have a generated id');
  assert.ok(m.meta.name, 'should have a default name');
});

test('yamlToModel preserves interface data through import', () => {
  const m = yamlToModel(VALID_YAML, { id: 'imp', name: 'Imported' });
  const iface = m.interfacesByName.report;
  assert.deepEqual(iface.sources, ['sales']);
  assert.equal(iface.columns.length, 1);
  assert.equal(iface.columns[0].src_col_name, 'amount');
  assert.equal(iface.columns[0].dest_col_name, 'total');
  assert.equal(iface.output.type, 'excel');
});

test('imported model round-trips cleanly back to YAML', () => {
  const m1 = yamlToModel(VALID_YAML, { id: 'rt', name: 'RT Test' });
  const yaml1 = modelToYaml(m1);
  const m2 = yamlToModel(yaml1);
  assert.deepEqual(m2.sourcesById, m1.sourcesById);
  assert.deepEqual(m2.interfacesByName, m1.interfacesByName);
});

test('yamlToModel throws on completely invalid YAML', () => {
  assert.throws(() => yamlToModel('{{{{not yaml'), /error|invalid|mapping/i);
});

test('yamlToModel throws on non-mapping (array) document', () => {
  assert.throws(() => yamlToModel('- item1\n- item2\n'), /mapping/);
});

test('yamlToModel handles YAML with no sources gracefully', () => {
  const noSources = `interfaces:
  empty:
    columns: []
`;
  const m = yamlToModel(noSources, { id: 'ns', name: 'No Sources' });
  assert.deepEqual(m.sourceOrder, []);
  assert.deepEqual(m.interfaceOrder, ['empty']);
});

test('yamlToModel handles YAML with no interfaces gracefully', () => {
  const noIfaces = `sources:
  - id: s1
    type: api
`;
  const m = yamlToModel(noIfaces, { id: 'ni', name: 'No Interfaces' });
  assert.deepEqual(m.sourceOrder, ['s1']);
  assert.deepEqual(m.interfaceOrder, []);
});

test('yamlToModel throws on a source without an id instead of dropping it', () => {
  const bad = VALID_YAML.replace('- id: sales', '- name: sales');
  assert.throws(() => yamlToModel(bad), /sources\[0\] is missing an "id"/);
});

test('a file without run_config round-trips without one', () => {
  const m = yamlToModel(VALID_YAML);
  assert.deepEqual(m.run_config, {});
  assert.ok(!/run_config/.test(modelToYaml(m)), 'run_config must not be invented on export');
});
