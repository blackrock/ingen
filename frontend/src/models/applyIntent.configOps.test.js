import { test } from 'node:test';
import assert from 'node:assert/strict';
import { applyOp } from './applyIntent.js';
import { createEmptyConfig, createEmptyInterface, upsertInterface } from './configModel.js';

const IFACE = 'iface_1';
const base = () => upsertInterface(createEmptyConfig({ id: 'cfg_t', name: 't' }), IFACE, createEmptyInterface());
const iface = (r) => r.model.interfacesByName[IFACE];

test('add_source merges fields, and updates an existing source without re-validating type', () => {
  const r1 = applyOp(base(), IFACE, [], { op: 'add_source', name: 'f', type: 'file', fields: { delimiter: '|', id: 'x', type: 'api' } });
  assert.deepEqual(Object.keys(r1.model.sourcesById.f).slice(0, 2), ['id', 'type']);
  assert.equal(r1.model.sourcesById.f.type, 'file', 'fields cannot override identity');
  assert.equal(r1.model.sourcesById.f.delimiter, '|');

  const r2 = applyOp(r1.model, IFACE, [], { op: 'add_source', name: 'f', type: 'file|mysql', fields: { skip_header_size: 1 } });
  assert.ok(r2.changed);
  assert.equal(r2.model.sourcesById.f.delimiter, '|', 'existing fields kept');
  assert.equal(r2.model.sourcesById.f.skip_header_size, 1);
  assert.deepEqual(iface(r2).sources, ['f'], 'not added to the interface twice');
});

test('add_formatter attaches to an existing column by src or dest, or creates a derived column', () => {
  const seeded = applyOp(base(), IFACE, [], { op: 'rename_column', from: 'start_date', to: 'START DATE' }).model;
  const byDest = applyOp(seeded, IFACE, [], { op: 'add_formatter', col: 'START DATE', type: 'date', format: { src: '%Y-%m-%d', des: '%m/%d/%y' } });
  assert.deepEqual(iface(byDest).columns[0].formatters, [{ type: 'date', format: { src: '%Y-%m-%d', des: '%m/%d/%y' } }]);

  const derived = applyOp(byDest.model, IFACE, [], { op: 'add_formatter', col: 'a+b', type: 'concat', format: { columns: ['a', 'b'], separator: '_' } });
  assert.equal(iface(derived).columns[1].src_col_name, 'a+b');
  assert.equal(iface(derived).columns[1].formatters[0].type, 'concat');

  const bad = applyOp(base(), IFACE, [], { op: 'add_formatter', col: 'x', type: 'not_a_formatter' });
  assert.equal(bad.changed, false);
});

test('add_transform keeps config with type first; set_output merges props and drops unknown header types', () => {
  const t = applyOp(base(), IFACE, [], { op: 'add_transform', type: 'aggregate', config: { type: 'union', groupby: { cols: ['k'] } } });
  const step = iface(t).pre_processing[0];
  assert.equal(Object.keys(step)[0], 'type');
  assert.equal(step.type, 'aggregate');
  assert.deepEqual(step.groupby, { cols: ['k'] });

  const o = applyOp(base(), IFACE, [], { op: 'set_output', type: 'delimited_file', props: { path: 'o.csv', delimiter: ',', header: { type: 'none' } } });
  assert.deepEqual(iface(o).output, { type: 'delimited_file', props: { path: 'o.csv', delimiter: ',' } });

  const h = applyOp(base(), IFACE, [], { op: 'set_output', type: 'delimited_file', props: { header: { type: 'delimited_result_header' } } });
  assert.equal(iface(h).output.props.header.type, 'delimited_result_header');
});

test('add_columns leaves dest_col_name unset (ingen defaults it to src)', () => {
  const r = applyOp(base(), IFACE, [], { op: 'add_columns', cols: ['name'] });
  assert.deepEqual(iface(r).columns, [{ src_col_name: 'name' }]);
});
