//  Field descriptors for each pre-processor type (corrected against ingen/pre_processor source).
//  `source`/`masking_source` selects resolve their options from ctx.sources (sibling source ids).

const MERGE_TYPES = ['inner', 'left', 'right', 'outer'];

export const PRE_PROCESSOR_SCHEMAS = {
  merge: {
    label: 'Merge',
    description: 'Join two DataFrames on matching key columns, like a SQL JOIN. The base input is the left side; the wired source is the right.',
    hint: 'Use when you need to combine data from two sources by a shared key (e.g. account id).',
    yamlFields: ['source', 'left_key', 'right_key', 'merge_type'],
    schema: [
      { key: 'source', label: 'Right source', kind: 'select', optionsFrom: 'sources' },
      { key: 'left_key', label: 'Left key', kind: 'text' },
      { key: 'right_key', label: 'Right key', kind: 'text' },
      { key: 'merge_type', label: 'Merge type', kind: 'select', options: MERGE_TYPES },
    ],
  },
  outer_join: {
    label: 'Outer join',
    description: 'Full outer join between two DataFrames — keeps all rows from both sides, filling NaN for non-matching keys.',
    hint: 'Use when you need every row from both sources, even if no match exists.',
    yamlFields: ['source', 'left_key', 'right_key'],
    schema: [
      { key: 'source', label: 'Right source', kind: 'select', optionsFrom: 'sources' },
      { key: 'left_key', label: 'Left key', kind: 'text' },
      { key: 'right_key', label: 'Right key', kind: 'text' },
    ],
  },
  union: {
    label: 'Union',
    description: 'Vertically concatenate (stack) multiple DataFrames. All sources must share compatible columns.',
    hint: 'Use to combine rows from multiple sources with the same structure (e.g. daily files).',
    yamlFields: ['source'],
    schema: [{ key: 'source', label: 'Sources', kind: 'tags', help: 'source ids to concatenate' }],
  },
  aggregate: {
    label: 'Aggregate',
    description: 'Group rows by one or more columns and compute an aggregate (sum, count, min, max, mean) on another column.',
    hint: 'Use to summarize data — e.g. total amount per account.',
    yamlFields: ['groupby.cols', 'agg.operation', 'agg.col'],
    schema: [
      { key: 'groupby', label: 'Group by', kind: 'group', fields: [
        { key: 'cols', label: 'Columns', kind: 'tags' },
      ] },
      { key: 'agg', label: 'Aggregation', kind: 'group', fields: [
        { key: 'operation', label: 'Operation', kind: 'select', options: ['sum', 'count', 'min', 'max', 'mean'] },
        { key: 'col', label: 'Column', kind: 'text' },
      ] },
    ],
  },
  mask: {
    label: 'Mask',
    description: 'Filter the base DataFrame by checking membership against a column in another source (masking source).',
    hint: 'Use to keep only rows whose key appears in a reference/lookup table.',
    yamlFields: ['on_col', 'masking_source', 'masking_col'],
    schema: [
      { key: 'on_col', label: 'On column', kind: 'text' },
      { key: 'masking_source', label: 'Masking source', kind: 'select', optionsFrom: 'sources' },
      { key: 'masking_col', label: 'Masking column', kind: 'text' },
    ],
  },
  melt: {
    label: 'Melt',
    description: 'Unpivot (melt) wide-format columns into key-value rows. Turns multiple columns into a single "variable" + "value" pair.',
    hint: 'Use when you have data spread across many columns that should be in rows (e.g. monthly columns → month + value).',
    yamlFields: ['key_column', 'value_column', 'include_keys', 'source'],
    schema: [
      { key: 'key_column', label: 'Key column', kind: 'text' },
      { key: 'value_column', label: 'Value column', kind: 'text' },
      { key: 'include_keys', label: 'Include keys', kind: 'tags' },
      { key: 'source', label: 'Source', kind: 'tags' },
    ],
  },
  filter: {
    label: 'Filter',
    description: 'Keep rows matching conditions on column values. Conditions can be combined with AND / OR logic.',
    hint: 'Use to remove unwanted rows — e.g. keep only status = "ACTIVE".',
    yamlFields: ['operator', 'cols'],
    schema: [
      { key: 'operator', label: 'Operator', kind: 'select', options: ['and', 'or'] },
      { key: 'cols', label: 'Conditions', kind: 'json', rows: 4, help: '[{ "col": "name", "val": ["x"] }]' },
    ],
  },
  not_equals_filter: {
    label: 'Not-equals filter',
    description: 'Exclude rows where a column matches specific values. Optionally cross-references against another source.',
    hint: 'Use to drop rows — e.g. exclude status = "CLOSED" or "CANCELLED".',
    yamlFields: ['source', 'cols'],
    schema: [
      { key: 'source', label: 'Source (optional)', kind: 'select', optionsFrom: 'sources' },
      { key: 'cols', label: 'Exclusions', kind: 'json', rows: 4, help: '[{ "col": "status", "val": ["CLOSED"] }]' },
    ],
  },
  drop_duplicates: {
    label: 'Drop duplicates',
    description: 'Remove duplicate rows based on a subset of columns. Choose which occurrence to keep (first, last, or none).',
    hint: 'Use to deduplicate — e.g. keep only the latest record per account.',
    yamlFields: ['columns', 'keep'],
    schema: [
      { key: 'columns', label: 'Columns', kind: 'tags', help: 'subset; empty = all columns' },
      { key: 'keep', label: 'Keep', kind: 'select', options: [
        { value: 'first', label: 'first' }, { value: 'last', label: 'last' }, { value: 'false', label: 'none (false)' },
      ] },
    ],
  },
  json_array_expander: {
    label: 'JSON array expander',
    description: 'Expand a JSON array stored in a single column into multiple rows. Each element of the array becomes its own row.',
    hint: 'Use when a column contains a JSON array string that needs flattening into rows.',
    yamlFields: ['config.column', 'config.include_columns', 'config.exclude_columns'],
    schema: [
      { key: 'config', label: 'Config', kind: 'group', fields: [
        { key: 'column', label: 'JSON column', kind: 'text' },
        { key: 'include_columns', label: 'Include columns', kind: 'json', rows: 2 },
        { key: 'exclude_columns', label: 'Exclude columns', kind: 'tags' },
      ] },
    ],
  },
};

export const PRE_PROCESSOR_ORDER = Object.keys(PRE_PROCESSOR_SCHEMAS);

export function preProcessorSchema(type) {
  return PRE_PROCESSOR_SCHEMAS[type]?.schema ?? [];
}
