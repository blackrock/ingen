import { test } from 'node:test';
import assert from 'node:assert/strict';
import { parentPath } from './navPaths.js';

test('parentPath walks one level up the route hierarchy', () => {
  assert.equal(parentPath('/'), null);                                            // index has no up
  assert.equal(parentPath('/configs/cfg_1'), '/');                                // config → index
  assert.equal(parentPath('/configs/cfg_1/run'), '/configs/cfg_1');               // run → config
  assert.equal(parentPath('/configs/cfg_1/history'), '/configs/cfg_1');           // history → config
  assert.equal(parentPath('/configs/cfg_1/interfaces/iface_a'), '/configs/cfg_1'); // editor → config
  assert.equal(parentPath('/something/else'), '/');                               // unknown → home
  assert.equal(parentPath(null), null);
});
