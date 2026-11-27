//  Tests for the mutating applyIntent ops: remove_column, remove_source, remove_transform,
//  add_transform and explain. These cover the edge cases most likely to corrupt a config.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { applyOp, applyOps } from './applyIntent.js';
import { createEmptyConfig, createEmptyInterface, upsertInterface, upsertSource } from './configModel.js';

const IFACE = 'iface_1';

function seededModel() {
  let m = createEmptyConfig({ id: 'cfg_t', name: 't' });
  m = upsertSource(m, { id: 'orders', type: 'file' });
  m = upsertInterface(m, IFACE, {
    ...createEmptyInterface(),
    sources: ['orders'],
    columns: [
      { src_col_name: 'id', dest_col_name: 'id' },
      { src_col_name: 'status', dest_col_name: 'status' },
    ],
    pre_processing: [{ type: 'not_equals_filter', cols: [{ col: 'status', val: ['CLOSED'] }] }],
    output: { type: 'excel', props: { path: 'out.xlsx' } },
  });
  return m;
}

// ── remove_column ────────────────────────────────────────────────────────────

test('remove_column removes an existing column by src_col_name', () => {
  const r = applyOp(seededModel(), IFACE, [], { op: 'remove_column', name: 'status' });
  assert.ok(r.changed);
  assert.equal(r.model.interfacesByName[IFACE].columns.length, 1);
  assert.equal(r.model.interfacesByName[IFACE].columns[0].src_col_name, 'id');
});

test('remove_column with unknown name suggests closest match', () => {
  const r = applyOp(seededModel(), IFACE, [], { op: 'remove_column', name: 'staus' });
  assert.equal(r.changed, false);
  assert.match(r.reply, /did you mean/i);
});

test('remove_column with no name returns error reply', () => {
  const r = applyOp(seededModel(), IFACE, [], { op: 'remove_column' });
  assert.equal(r.changed, false);
  assert.match(r.reply, /which column/i);
});

// ── remove_transform ─────────────────────────────────────────────────────────

test('remove_transform by type removes the first matching step', () => {
  const r = applyOp(seededModel(), IFACE, [], { op: 'remove_transform', type: 'not_equals_filter' });
  assert.ok(r.changed);
  assert.equal(r.model.interfacesByName[IFACE].pre_processing.length, 0);
});

test('remove_transform by index removes the correct step', () => {
  const r = applyOp(seededModel(), IFACE, [], { op: 'remove_transform', index: 0 });
  assert.ok(r.changed);
  assert.equal(r.model.interfacesByName[IFACE].pre_processing.length, 0);
});

test('remove_transform with bad type is a no-op', () => {
  const r = applyOp(seededModel(), IFACE, [], { op: 'remove_transform', type: 'nonexistent' });
  assert.equal(r.changed, false);
});

// ── add_transform ────────────────────────────────────────────────────────────

test('add_transform adds a valid transform type', () => {
  const r = applyOp(seededModel(), IFACE, [], { op: 'add_transform', type: 'merge' });
  assert.ok(r.changed);
  assert.equal(r.model.interfacesByName[IFACE].pre_processing.length, 2);
  assert.equal(r.model.interfacesByName[IFACE].pre_processing[1].type, 'merge');
});

test('add_transform rejects an invalid type', () => {
  const r = applyOp(seededModel(), IFACE, [], { op: 'add_transform', type: 'invalid_type' });
  assert.equal(r.changed, false);
  assert.match(r.reply, /can add these transforms/i);
});

// ── remove_source ────────────────────────────────────────────────────────────

test('remove_source removes from registry and ALL interface source lists', () => {
  const r = applyOp(seededModel(), IFACE, [], { op: 'remove_source', name: 'orders' });
  assert.ok(r.changed);
  assert.ok(!r.model.sourcesById.orders, 'source removed from registry');
  assert.deepEqual(r.model.interfacesByName[IFACE].sources, [], 'source removed from interface');
});

test('remove_source on non-existent source is a no-op', () => {
  const r = applyOp(seededModel(), IFACE, [], { op: 'remove_source', name: 'nonexistent' });
  assert.equal(r.changed, false);
  assert.match(r.reply, /doesn't exist/i);
});

// ── explain ──────────────────────────────────────────────────────────────────

test('explain returns pipeline summary without changing the model', () => {
  const m = seededModel();
  const r = applyOp(m, IFACE, [], { op: 'explain' });
  assert.equal(r.changed, false, 'explain should not mutate');
  assert.equal(r.model, m, 'same model reference');
  assert.match(r.reply, /sources.*orders/i);
  assert.match(r.reply, /columns mapped.*2/i);
  assert.match(r.reply, /output.*excel/i);
});

// ── Multi-op pipeline with new ops ───────────────────────────────────────────

test('multi-op: add transform then remove it in same batch', () => {
  const ops = [
    { op: 'add_transform', type: 'aggregate' },
    { op: 'remove_transform', type: 'aggregate' },
  ];
  const r = applyOps(seededModel(), IFACE, [], ops);
  assert.ok(r.changed);
  // Should end up with just the original filter, not the added+removed aggregate.
  assert.equal(r.model.interfacesByName[IFACE].pre_processing.length, 1);
  assert.equal(r.model.interfacesByName[IFACE].pre_processing[0].type, 'not_equals_filter');
});

test('multi-op: add column then remove it', () => {
  const ops = [
    { op: 'add_columns', cols: ['new_col'] },
    { op: 'remove_column', name: 'new_col' },
  ];
  const r = applyOps(seededModel(), IFACE, [], ops);
  assert.ok(r.changed);
  assert.equal(r.model.interfacesByName[IFACE].columns.length, 2, 'back to original 2');
});
