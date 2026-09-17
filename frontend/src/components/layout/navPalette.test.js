import { test } from 'node:test';
import assert from 'node:assert';
import { buildPalette } from './navPalette.js';
import { PRE_PROCESSOR_ORDER } from '../../forms/schemas/preProcessorSchemas.js';
import { OUTPUT_TYPE_OPTIONS } from '../../forms/schemas/outputSchemas.js';

test('palette enumerates exactly the schema-supported types', () => {
  const groups = Object.fromEntries(buildPalette().map((g) => [g.group, g]));

  assert.deepEqual(
    groups.Sources.nodes.map((n) => n.subtype),
    ['file', 'mysql', 'api', 'json'],
  );
  assert.deepEqual(groups.Transforms.nodes.map((n) => n.subtype), PRE_PROCESSOR_ORDER);
  assert.deepEqual(groups.Output.nodes.map((n) => n.subtype), OUTPUT_TYPE_OPTIONS);
  assert.deepEqual(groups.Columns.nodes.map((n) => n.action), ['add_column']);
  assert.deepEqual(groups.Validations.nodes.map((n) => n.action), ['add_validation']);
});

test('every leaf is actionable — no dead info-only chips', () => {
  for (const g of buildPalette()) {
    for (const n of g.nodes) {
      assert.ok(n.subtype || n.action, `stale leaf in ${g.group}: ${n.label}`);
    }
  }
});
