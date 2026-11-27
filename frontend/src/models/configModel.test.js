//  Unit tests for configModel pure functions — covers renameInterface, removeInterface,
//  removeSource, and edge cases that could break after Phases 2-5.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import {
  createEmptyConfig,
  createEmptyInterface,
  upsertSource,
  removeSource,
  upsertInterface,
  removeInterface,
  renameInterface,
  reorderInterfaces,
  validateConfigModel,
} from './configModel.js';

function base() {
  let m = createEmptyConfig({ id: 'test', name: 'Test' });
  m = upsertSource(m, { id: 'src1', type: 'file' });
  m = upsertSource(m, { id: 'src2', type: 'mysql' });
  m = upsertInterface(m, 'iface_a', { ...createEmptyInterface(), sources: ['src1'] });
  m = upsertInterface(m, 'iface_b', { ...createEmptyInterface(), sources: ['src1', 'src2'] });
  return m;
}

// ── renameInterface ──────────────────────────────────────────────────────────

test('renameInterface moves the key and updates interfaceOrder', () => {
  const m = renameInterface(base(), 'iface_a', 'renamed');
  assert.ok(!m.interfacesByName.iface_a, 'old name removed');
  assert.ok(m.interfacesByName.renamed, 'new name present');
  assert.deepEqual(m.interfaceOrder, ['renamed', 'iface_b']);
  assert.deepEqual(m.interfacesByName.renamed.sources, ['src1'], 'data preserved');
});

test('renameInterface to same name is a no-op', () => {
  const m = base();
  const same = renameInterface(m, 'iface_a', 'iface_a');
  assert.equal(same, m, 'returns same reference');
});

test('renameInterface with empty string is a no-op', () => {
  const m = base();
  const same = renameInterface(m, 'iface_a', '');
  assert.equal(same, m);
});

test('renameInterface throws on duplicate target name', () => {
  assert.throws(
    () => renameInterface(base(), 'iface_a', 'iface_b'),
    /already exists/,
  );
});

// ── removeInterface ──────────────────────────────────────────────────────────

test('removeInterface removes from map and order', () => {
  const m = removeInterface(base(), 'iface_a');
  assert.ok(!m.interfacesByName.iface_a);
  assert.deepEqual(m.interfaceOrder, ['iface_b']);
  assert.ok(m.interfacesByName.iface_b, 'other interface untouched');
});

test('removeInterface on non-existent name does not crash', () => {
  const m = removeInterface(base(), 'no_such');
  assert.deepEqual(m.interfaceOrder, ['iface_a', 'iface_b']);
});

// ── removeSource ─────────────────────────────────────────────────────────────

test('removeSource removes from registry but leaves interface references (validation catches)', () => {
  const m = removeSource(base(), 'src1');
  assert.ok(!m.sourcesById.src1);
  assert.deepEqual(m.sourceOrder, ['src2']);
  // Interface still references the now-missing source — validation should flag it.
  assert.deepEqual(m.interfacesByName.iface_a.sources, ['src1']);
});

// ── validateConfigModel ──────────────────────────────────────────────────────

test('validateConfigModel flags a missing source reference', () => {
  const m = removeSource(base(), 'src1');
  const issues = validateConfigModel(m);
  const srcIssues = issues.filter((i) => /src1/.test(i.message));
  assert.ok(srcIssues.length > 0, `expected a validation issue about src1, got: ${JSON.stringify(issues)}`);
});

test('validateConfigModel returns no errors for a valid model', () => {
  const issues = validateConfigModel(base());
  const errors = issues.filter((i) => i.level === 'error');
  assert.equal(errors.length, 0, `unexpected errors: ${JSON.stringify(errors)}`);
});

// ── reorderInterfaces ────────────────────────────────────────────────────────

test('reorderInterfaces changes order but preserves data', () => {
  const m = reorderInterfaces(base(), ['iface_b', 'iface_a']);
  assert.deepEqual(m.interfaceOrder, ['iface_b', 'iface_a']);
  assert.deepEqual(m.interfacesByName.iface_a.sources, ['src1']);
});

test('reorderInterfaces rejects invalid permutation', () => {
  assert.throws(() => reorderInterfaces(base(), ['iface_a']), /permutation/);
});

test('reorderInterfaces rejects repeated names (would silently drop an interface)', () => {
  assert.throws(() => reorderInterfaces(base(), ['iface_a', 'iface_a']), /permutation/);
});
