import { test } from 'node:test';
import assert from 'node:assert/strict';
import { applyOp, applyOps } from './applyIntent.js';
import { createEmptyConfig, createEmptyInterface, upsertInterface } from './configModel.js';

const IFACE = 'iface_1';
function baseModel() {
  return upsertInterface(createEmptyConfig({ id: 'cfg_t', name: 't' }), IFACE, createEmptyInterface());
}

test('add_columns adds new columns and skips duplicates', () => {
  const m1 = applyOp(baseModel(), IFACE, [], { op: 'add_columns', cols: ['a', 'b', 'a'] });
  assert.deepEqual(m1.model.interfacesByName[IFACE].columns.map((c) => c.src_col_name), ['a', 'b']);
  assert.ok(m1.changed);

  const m2 = applyOp(m1.model, IFACE, [], { op: 'add_columns', cols: ['a'] });
  assert.equal(m2.changed, false, 'already-present column is a no-op');
  assert.equal(m2.model.interfacesByName[IFACE].columns.length, 2);
});

test('rename_column sets dest on an existing column, or adds one', () => {
  const seeded = applyOp(baseModel(), IFACE, [], { op: 'add_columns', cols: ['region'] }).model;
  const renamed = applyOp(seeded, IFACE, [], { op: 'rename_column', from: 'region', to: 'market' });
  const col = renamed.model.interfacesByName[IFACE].columns[0];
  assert.equal(col.src_col_name, 'region');
  assert.equal(col.dest_col_name, 'market');
});

test('add_filter rejects an unknown column (no change)', () => {
  const r = applyOp(baseModel(), IFACE, ['status'], { op: 'add_filter', col: 'stats', val: 'x' });
  assert.equal(r.changed, false);
  assert.match(r.reply, /don't see a column/);
});

test('unknown / none op is a no-op', () => {
  const r = applyOp(baseModel(), IFACE, [], { op: 'frobnicate' });
  assert.equal(r.changed, false);
});

test('applyOps threads the model so later ops see earlier ones', () => {
  const ops = [
    { op: 'add_columns', cols: ['region', 'amount'] },
    { op: 'rename_column', from: 'region', to: 'market' },
    { op: 'set_output', type: 'excel' },
  ];
  const { model, changed } = applyOps(baseModel(), IFACE, [], ops);
  const it = model.interfacesByName[IFACE];
  assert.ok(changed);
  assert.equal(it.columns.find((c) => c.src_col_name === 'region').dest_col_name, 'market');
  assert.equal(it.output.type, 'excel');
});

test('set_output accepts every OUTPUT_TYPES value from constants (incl. splitted_file)', () => {
  const { model, changed } = applyOp(baseModel(), IFACE, [], { op: 'set_output', type: 'splitted_file' });
  assert.ok(changed);
  assert.equal(model.interfacesByName[IFACE].output.type, 'splitted_file');
});
