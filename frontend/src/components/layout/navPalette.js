//  InGen Studio — inFlow palette config (pure, JSX-free so it is unit-testable under node --test).
//
//  Every leaf is actionable: a `subtype` leaf adds a node of that type; an `action` leaf runs a
//  named handler (columns/validations are singletons — append a row / open the existing drawer).
//  Icons are resolved in NavRail by subtype/action — keeping this module free of JSX.
//
//  Leaf shape: { subtype?, action?, label, color, draggable?, description?, hint?, writes? }
//  The lists are derived from the form schemas, so the menu never drifts from backend support.

import { PRE_PROCESSOR_SCHEMAS, PRE_PROCESSOR_ORDER } from '../../forms/schemas/preProcessorSchemas.js';
import { OUTPUT_SCHEMAS, OUTPUT_TYPE_OPTIONS } from '../../forms/schemas/outputSchemas.js';

const SOURCE_COLOR = '#3b82f6';
const TRANSFORM_COLOR = '#f59e0b';
const COLUMNS_COLOR = '#7853EC';
const VALIDATION_COLOR = '#10b981';
const OUTPUT_COLOR = '#ef4444';

// Source order mirrors how often you reach for each (file first); `file` fans out to its file_type
// variants inside the drawer rather than as separate leaves.
const SOURCE_ORDER = ['file', 'mysql', 'api', 'json'];
const SOURCE_LABELS = {
  file: 'File',
  mysql: 'Database (MySQL)',
  api: 'API',
  json: 'JSON payload',
};

export function buildPalette() {
  return [
    {
      group: 'Sources',
      note: 'A pipeline can read many sources; the first is the base input, the rest feed transforms.',
      nodes: SOURCE_ORDER.map((subtype) => ({
        subtype,
        label: SOURCE_LABELS[subtype],
        color: SOURCE_COLOR,
      })),
    },
    {
      group: 'Transforms',
      note: 'Merge, union, filter and reshape steps run in order on the base input.',
      nodes: PRE_PROCESSOR_ORDER.map((subtype) => {
        const s = PRE_PROCESSOR_SCHEMAS[subtype];
        return {
          subtype,
          label: s.label,
          color: TRANSFORM_COLOR,
          description: s.description,
          hint: s.hint,
          writes: (s.yamlFields || []).join(', '),
          draggable: true, // transforms also support drag-to-canvas
        };
      }),
    },
    {
      group: 'Columns',
      note: 'Columns map source fields to output fields. Add one, then edit the mapping in the drawer.',
      nodes: [{ action: 'add_column', label: 'Add column', color: COLUMNS_COLOR }],
    },
    {
      group: 'Validations',
      note: 'Optional great_expectations checks, attached per column. Opens the validations editor.',
      nodes: [{ action: 'add_validation', label: 'Add validation', color: VALIDATION_COLOR }],
    },
    {
      group: 'Output',
      note: 'One destination per interface. Use Splitted file or JSON writer for multi-shape output.',
      nodes: OUTPUT_TYPE_OPTIONS.map((subtype) => ({
        subtype,
        label: OUTPUT_SCHEMAS[subtype].label,
        color: OUTPUT_COLOR,
      })),
    },
  ];
}
