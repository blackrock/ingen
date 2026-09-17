//  Formatter `format` descriptors. Derived from ingen/formatters/common_formatters.py.
//  Every backend formatter type has an entry here. Types with no configurable args use `none`.
//  Types with structured config use `group`. Simple scalar values use `txt`. JSON fallback only
//  for types where the schema is legitimately arbitrary (get_running_environment, constant_condition).

const txt = (placeholder) => [{ key: 'format', label: 'format', kind: 'text', placeholder }];
const none = [];
const jsonFmt = (rows = 2, help) => [{ key: 'format', label: 'format', kind: 'json', rows, help }];
const group = (fields) => [{ key: 'format', label: 'format', kind: 'group', fields }];

export const FORMATTER_FORMS = {
  // ── Date / Time ──────────────────────────────────────────────────────────
  date: group([
    { key: 'src', label: 'Source format', kind: 'text', placeholder: '%Y-%m-%d', help: 'Use "ms" for epoch milliseconds' },
    { key: 'des', label: 'Output format', kind: 'text', placeholder: '%m/%d/%Y' },
  ]),
  runtime_date: group([
    { key: 'des', label: 'Output format', kind: 'text', placeholder: '%Y%m%d', help: 'Formats the --run_date CLI argument' },
  ]),
  'constant-date': jsonFmt(1, '[day_offset, "%Y%m%d", "US"]  — offset days from run_date, format, holiday calendar'),
  bus_day: group([
    { key: 'col', label: 'Date column', kind: 'text' },
    { key: 'format', label: 'Date format', kind: 'text', placeholder: '%Y-%m-%d' },
    { key: 'cal', label: 'Holiday calendar', kind: 'text', placeholder: 'US', help: 'Country code for pandas_market_calendars' },
  ]),
  last_date_of_prev_month: group([
    { key: 'outdate_format', label: 'Output format', kind: 'text', placeholder: '%Y%m%d' },
  ]),
  current_timestamp: none,

  // ── Numbers ──────────────────────────────────────────────────────────────
  float: txt('${:,.2f}'),
  float_precision: group([
    { key: 'precision', label: 'Decimal places', kind: 'number' },
  ]),
  arithmetic_calc: group([
    { key: 'cols', label: 'Columns', kind: 'tags', help: 'Two columns for binary ops; one for abs' },
    { key: 'operation', label: 'Operation', kind: 'select', options: ['add', 'sub', 'mul', 'div', 'abs'] },
    { key: 'value', label: 'Constant value', kind: 'number', help: 'Optional scalar operand' },
  ]),
  'group-percentage': group([
    { key: 'of', label: 'Numerator column', kind: 'text', help: 'Column whose value is the numerator' },
    { key: 'in', label: 'Group-by column', kind: 'text', help: 'Column that defines each group total' },
  ]),
  sum: [{ key: 'format', label: 'Columns to sum', kind: 'tags' }],
  bucket: group([
    { key: 'buckets', label: 'Bin edges', kind: 'json', rows: 1, help: '[0, 30, 90, 365, "inf"]' },
    { key: 'labels', label: 'Labels', kind: 'tags', help: 'One fewer label than edges' },
    { key: 'include_right', label: 'Include right edge', kind: 'toggle' },
  ]),
  add_trailing_zeros: group([
    { key: 'num_of_chars', label: 'Total width (zero-pad left)', kind: 'number' },
  ]),
  index_counter: none,

  // ── Strings ──────────────────────────────────────────────────────────────
  constant: txt('literal value to set'),
  concat: group([
    { key: 'columns', label: 'Columns', kind: 'tags', help: 'Joined in order with separator' },
    { key: 'separator', label: 'Separator', kind: 'text', placeholder: '' },
  ]),
  prefix_string: group([
    { key: 'columns', label: 'Source columns', kind: 'tags', help: 'Values from these columns are concatenated before the destination column value' },
    { key: 'prefix', label: 'Literal prefix', kind: 'text' },
    { key: 'separator', label: 'Separator', kind: 'text', placeholder: '' },
  ]),
  suffix_string: group([
    { key: 'columns', label: 'Source columns', kind: 'tags' },
    { key: 'suffix', label: 'Literal suffix', kind: 'text' },
    { key: 'separator', label: 'Separator', kind: 'text', placeholder: '' },
  ]),
  sub_string: group([
    { key: 'start', label: 'Start index', kind: 'number' },
    { key: 'end', label: 'End index', kind: 'number' },
  ]),
  add_space: group([
    { key: 'spacing', label: 'Total width (left-justify)', kind: 'number' },
  ]),
  split_col: group([
    { key: 'new_col_names', label: 'New column names', kind: 'tags', help: 'One name per split segment' },
    { key: 'delimiter', label: 'Delimiter', kind: 'text', placeholder: ',' },
  ]),
  extract_from_pattern: group([
    { key: 'pattern', label: 'Regex pattern', kind: 'text', placeholder: '([A-Z]{2}\\d{6})' },
  ]),
  decode_bytes: group([
    { key: 'encoding', label: 'Encoding', kind: 'text', placeholder: 'utf-8' },
    { key: 'strip_whitespace', label: 'Strip whitespace', kind: 'toggle' },
  ]),

  // ── Replace / Fill ───────────────────────────────────────────────────────
  replace_value: group([
    { key: 'from_value', label: 'From values', kind: 'tags', help: 'Parallel list with "To values"' },
    { key: 'to_value', label: 'To values', kind: 'tags' },
    { key: 'replace_missing', label: 'Replace missing (None/NaN)', kind: 'toggle', help: 'When on and From value is null, fills NaN cells with the To value' },
    { key: 'search_list', label: 'Search inside list cells', kind: 'toggle', help: 'Also replaces matching elements inside list-typed cells' },
  ]),
  fill_empty_values: group([
    { key: 'column', label: 'Fill-from column', kind: 'text', help: 'When destination cell is empty, copy value from this column' },
  ]),
  fill_empty_values_with_custom_value: group([
    { key: 'value', label: 'Fill value', kind: 'text' },
    { key: 'condition', label: 'Condition', kind: 'group', fields: [
      { key: 'match_col', label: 'Match column', kind: 'text' },
      { key: 'pattern', label: 'Regex pattern', kind: 'text' },
    ] },
  ]),
  conditional_replace_formatter: group([
    { key: 'from_column', label: 'Source column', kind: 'text', help: 'Copy value from this column when condition matches' },
    { key: 'condition', label: 'Condition', kind: 'group', fields: [
      { key: 'match_col', label: 'Match column', kind: 'text' },
      { key: 'pattern', label: 'Regex pattern', kind: 'text' },
    ] },
  ]),
  // constant_condition is intentionally a JSON field — its schema is a list of compare objects
  // that would require a list-of-groups editor not yet built.
  constant_condition: jsonFmt(4, '{ "compare": [...], "match_col": "col", "values": ["if_true", "if_false"] }'),

  // ── Column control ───────────────────────────────────────────────────────
  duplicate: txt('existing column name to copy'),
  drop_duplicates: group([
    { key: 'keep', label: 'Keep', kind: 'select', options: [
      { value: 'first', label: 'first' }, { value: 'last', label: 'last' }, { value: 'false', label: 'none (false)' },
    ] },
  ]),

  // ── Runtime / Environment ────────────────────────────────────────────────
  override: txt('override_params key name (passed via --override_params)'),
  get_running_environment: jsonFmt(3, '{ "prod": "PROD_VALUE", "uat": "UAT_VALUE" } — keyed by $INGEN_ENV'),
  uuid: none,

  // ── Encryption ───────────────────────────────────────────────────────────
  encryption: none,
  decryption: none,

  // ── date-diff uses list format ────────────────────────────────────────────
  'date-diff': jsonFmt(1, '[from_date_col, to_date_col, "%Y-%m-%d"]'),
};

/** @returns {Array} SchemaForm fields for the given formatter type (raw JSON fallback otherwise). */
export function formatterSchema(type) {
  return FORMATTER_FORMS[type] ?? jsonFmt(2, 'format value — see ingen/formatters/common_formatters.py');
}
