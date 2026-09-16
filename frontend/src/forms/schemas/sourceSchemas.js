//  Field descriptors for each source type. Derived from ingen/data_source + docs/config_reference.
//  `id` and `type` are handled by the SourcesEditor outside SchemaForm (id is the key; type the
//  discriminator). These schemas cover the type-specific body.

import { FILE_TYPES } from '../../models/constants.js';

// Trimmed to the two essentials. Niche knobs (delimiter, encoding, sheet_name, skip rows, dtype,
// col_specification, etc.) were removed from the builder — they're still settable via raw YAML.
const FILE = [
  { key: 'file_type', label: 'File type', kind: 'select', options: Object.values(FILE_TYPES), required: true },
  { key: 'file_path', label: 'File path', kind: 'text', placeholder: 'data/file_$date(%Y%m%d).csv', required: true },
];

const MYSQL = [
  { key: 'database', label: 'Database name', kind: 'text', help: 'Matches the database key in your properties file', required: true },
  { key: 'query', label: 'SQL query', kind: 'textarea', rows: 4, placeholder: 'SELECT col1, col2 FROM table WHERE date = {date}', required: true },
];

// Ordered by how often you reach for it: request → response shaping → retries.
// Niche knobs are gated behind the field that gives them meaning (visibleIf), so the Advanced
// panel starts short and grows only as you opt in.
const API = [
  { key: 'url', label: 'Base URL', kind: 'text', required: true },
  { key: 'method', label: 'Method', kind: 'select', options: ['GET', 'POST', 'PUT', 'DELETE'], required: true },
  // — request —
  { key: 'headers', label: 'Headers', kind: 'json', rows: 3 },
  { key: 'request_body', label: 'Request body', kind: 'textarea', rows: 3, visibleIf: (v) => ['POST', 'PUT', 'PATCH'].includes(v.method) },
  { key: 'auth', label: 'Auth', kind: 'group', fields: [
    { key: 'type', label: 'Type', kind: 'text', placeholder: 'BasicAuth' },
    { key: 'username', label: 'Username/token', kind: 'text' },
    { key: 'pwd', label: 'Password/token', kind: 'text' },
  ] },
  { key: 'url_params', label: 'URL params', kind: 'json', rows: 3 },
  // — response shaping —
  { key: 'data_node', label: 'data_node', kind: 'tags' },
  { key: 'data_key', label: 'data_key', kind: 'tags' },
  { key: 'success_criteria', label: 'Success criteria', kind: 'text' },
  { key: 'criteria_option', label: 'Criteria option', kind: 'json', rows: 2, visibleIf: (v) => !!v.success_criteria },
  // — retries (interval only matters once you retry) —
  { key: 'retries', label: 'Retries', kind: 'number' },
  { key: 'interval', label: 'Interval (s)', kind: 'number', visibleIf: (v) => v.retries != null },
];

// json has no body fields (payload supplied at runtime).
const NONE = [];

const SCHEMAS = { file: FILE, mysql: MYSQL, api: API, json: NONE };

export function sourceSchema(type) {
  return SCHEMAS[type] ?? [];
}

/** Fields flagged `required` — shown up-front in the source loader. */
export function requiredSourceFields(type) {
  return (SCHEMAS[type] ?? []).filter((f) => f.required);
}

/** Everything else — collapsed under "Advanced". */
export function advancedSourceFields(type) {
  return (SCHEMAS[type] ?? []).filter((f) => !f.required);
}
