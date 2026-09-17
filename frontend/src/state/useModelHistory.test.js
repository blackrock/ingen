//  Tests for the undo/redo state machine that backs useModelHistory.
//
//  These exercise the REAL transitions exported from useModelHistory.js (pushSnapshot / applyUndo /
//  applyRedo) — the hook is a thin useState wrapper over them, so covering the transitions covers
//  the behaviour without needing a React renderer.

import { test } from 'node:test';
import assert from 'node:assert/strict';

import { pushSnapshot, applyUndo, applyRedo, MAX_HISTORY } from './useModelHistory.js';

/** Drive the real transitions through a tiny stateful harness, mirroring what the hook does. */
function createHistory(max = MAX_HISTORY) {
  let past = [];
  let future = [];

  return {
    get canUndo() { return past.length > 0; },
    get canRedo() { return future.length > 0; },
    get depth() { return past.length; },
    pushHistory(snapshot) {
      past = pushSnapshot(past, snapshot, max);
      future = [];  // new edit clears the redo stack
    },
    undo(current, apply) {
      const next = applyUndo(past, future, current);
      if (!next) return;
      ({ past, future } = next);
      apply(next.restored);
    },
    redo(current, apply) {
      const next = applyRedo(past, future, current);
      if (!next) return;
      ({ past, future } = next);
      apply(next.restored);
    },
  };
}

test('initial state: canUndo and canRedo are false', () => {
  const h = createHistory();
  assert.equal(h.canUndo, false);
  assert.equal(h.canRedo, false);
});

test('pushHistory enables undo', () => {
  const h = createHistory();
  h.pushHistory({ v: 1 });
  assert.equal(h.canUndo, true);
  assert.equal(h.canRedo, false);
});

test('undo restores the previous snapshot and enables redo', () => {
  const h = createHistory();
  h.pushHistory({ v: 1 });
  let restored = null;
  h.undo({ v: 2 }, (m) => { restored = m; });
  assert.deepEqual(restored, { v: 1 });
  assert.equal(h.canUndo, false);
  assert.equal(h.canRedo, true);
});

test('redo restores the undone state', () => {
  const h = createHistory();
  h.pushHistory({ v: 1 });
  h.undo({ v: 2 }, () => {});
  let restored = null;
  h.redo({ v: 1 }, (m) => { restored = m; });
  assert.deepEqual(restored, { v: 2 });
  assert.equal(h.canUndo, true);
  assert.equal(h.canRedo, false);
});

test('new edit after undo clears the redo stack', () => {
  const h = createHistory();
  h.pushHistory({ v: 1 });
  h.pushHistory({ v: 2 });
  h.undo({ v: 3 }, () => {});
  assert.equal(h.canRedo, true);
  h.pushHistory({ v: 4 }); // new edit
  assert.equal(h.canRedo, false, 'redo stack cleared after new edit');
});

test('history respects max size', () => {
  const h = createHistory(3);
  h.pushHistory({ v: 1 });
  h.pushHistory({ v: 2 });
  h.pushHistory({ v: 3 });
  h.pushHistory({ v: 4 }); // oldest (v:1) should be evicted
  let count = 0;
  while (h.canUndo) { h.undo({ v: 99 }, () => {}); count++; }
  assert.equal(count, 3, 'max 3 undos');
});

test('eviction drops the OLDEST snapshot, not the newest', () => {
  const h = createHistory(2);
  h.pushHistory({ v: 'oldest' });
  h.pushHistory({ v: 'middle' });
  h.pushHistory({ v: 'newest' });
  const seen = [];
  while (h.canUndo) h.undo({ v: 'cur' }, (m) => seen.push(m.v));
  assert.deepEqual(seen, ['newest', 'middle'], 'oldest evicted, order preserved');
});

test('undo with empty stack is a no-op', () => {
  const h = createHistory();
  let called = false;
  h.undo({ v: 1 }, () => { called = true; });
  assert.equal(called, false);
});

test('redo with empty stack is a no-op', () => {
  const h = createHistory();
  let called = false;
  h.redo({ v: 1 }, () => { called = true; });
  assert.equal(called, false);
});

test('multiple undo/redo cycles are consistent', () => {
  const h = createHistory();
  h.pushHistory({ v: 'a' });
  h.pushHistory({ v: 'b' });
  h.pushHistory({ v: 'c' });

  const states = [];

  // Current is 'd', undo back to 'c'
  h.undo({ v: 'd' }, (m) => states.push(m));
  assert.deepEqual(states[0], { v: 'c' });

  // Undo to 'b'
  h.undo({ v: 'c' }, (m) => states.push(m));
  assert.deepEqual(states[1], { v: 'b' });

  // Redo to 'c'
  h.redo({ v: 'b' }, (m) => states.push(m));
  assert.deepEqual(states[2], { v: 'c' });

  // Redo to 'd'
  h.redo({ v: 'c' }, (m) => states.push(m));
  assert.deepEqual(states[3], { v: 'd' });

  assert.equal(h.canRedo, false);
  assert.equal(h.canUndo, true);
});

test('transitions never mutate the arrays passed in', () => {
  const past = [{ v: 1 }];
  const future = [{ v: 2 }];
  applyUndo(past, future, { v: 3 });
  applyRedo(past, future, { v: 3 });
  pushSnapshot(past, { v: 4 });
  assert.deepEqual(past, [{ v: 1 }], 'past untouched');
  assert.deepEqual(future, [{ v: 2 }], 'future untouched');
});
