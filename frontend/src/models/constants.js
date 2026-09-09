//  InGen Studio — domain constants
//
//  These registries are derived directly from the InGen backend source. They are the
//  authoritative vocabulary the UI palettes, forms, and validators are generated from.
//  Keep them in sync with the backend registries cited next to each block.

/**
 * Source types implemented by `SourceFactory.parse_source`
 * (ingen/data_source/source_factory.py).
 *
 * NOTE: `DataSourceType.DB = "db"` exists in the backend enum but is NOT wired into the
 * factory — it raises ValueError. The only relational source is `mysql`. Do not expose `db`.
 */
export const SOURCE_TYPES = Object.freeze({
  FILE: 'file',
  MYSQL: 'mysql',
  API: 'api',
  JSON: 'json',
});

/** File reader types from `ReaderFactory.get_reader` (ingen/reader/file_reader.py). */
export const FILE_TYPES = Object.freeze({
  DELIMITED_FILE: 'delimited_file',
  EXCEL: 'excel',
  XML: 'xml',
  JSON: 'json',
  FIXED_WIDTH: 'fixed_width',
});

/** Pre-processor types from `PreProcessor.PRE_PROCESSORS` (ingen/pre_processor/pre_processor.py). */
export const PRE_PROCESSOR_TYPES = Object.freeze({
  MERGE: 'merge',
  UNION: 'union',
  AGGREGATE: 'aggregate',
  MASK: 'mask',
  MELT: 'melt',
  DROP_DUPLICATES: 'drop_duplicates',
  FILTER: 'filter',
  JSON_ARRAY_EXPANDER: 'json_array_expander',
  NOT_EQUALS_FILTER: 'not_equals_filter',
  OUTER_JOIN: 'outer_join',
});

/** Post-processor types from `PostProcessor.POST_PROCESSORS` (ingen/post_processor/post_processor.py). */
export const POST_PROCESSOR_TYPES = Object.freeze({
  PIVOT: 'pivot',
});

/**
 * Formatter type keys from the `formatters_dict` registry in
 * ingen/formatters/common_formatters.py (get_formatter_from_type).
 */
export const FORMATTER_TYPES = Object.freeze([
  'date', 'float', 'concat', 'constant', 'constant-date', 'duplicate', 'decryption',
  'encryption', 'group-percentage', 'sum', 'date-diff', 'bucket', 'arithmetic_calc',
  'fill_empty_values', 'fill_empty_values_with_custom_value', 'replace_value', 'runtime_date',
  'uuid', 'sub_string', 'conditional_replace_formatter', 'bus_day', 'split_col', 'decode_bytes',
  'float_precision', 'extract_from_pattern', 'index_counter', 'add_space', 'add_trailing_zeros',
  'last_date_of_prev_month', 'current_timestamp', 'get_running_environment', 'drop_duplicates',
  'prefix_string', 'suffix_string', 'constant_condition', 'override',
]);

/**
 * Validation expectation types.
 * Built-ins come from great_expectations; customs from `custom_validations_map`
 * (ingen/validation/common_validations.py).
 */
export const VALIDATION_TYPES = Object.freeze({
  BUILTIN: [
    'expect_column_values_to_not_be_null',
    'expect_column_values_to_match_regex_list',
    'expect_column_values_to_match_strftime_format',
    'expect_column_values_to_be_between',
    'expect_column_values_to_be_unique',
    'expect_column_value_lengths_to_equal',
  ],
  CUSTOM: [
    'expect_column_to_contain_values',
    'expect_column_values_to_be_of_type',
    'expect_column_values_to_be_present_in',
    'expect_column_to_be_present_in',
  ],
});

/** Validation severities (ingen/validation) — drives the post-failure action. */
export const VALIDATION_SEVERITIES = Object.freeze({
  BLOCKER: 'blocker', // aborts the interface
  CRITICAL: 'critical', // drops failing rows
  WARNING: 'warning', // reports only
});

/** Output/writer `output.type` values handled by InterfaceWriter / json_writer / split writer. */
export const OUTPUT_TYPES = Object.freeze({
  DELIMITED_FILE: 'delimited_file',
  EXCEL: 'excel',
  JSON: 'json',
  JSON_WRITER: 'json_writer',
  SPLITTED_FILE: 'splitted_file',
});

/** run_config pluggable component names resolved by RunConfiguration (ingen/utils/run_configuration.py). */
export const RUN_CONFIG_DEFAULTS = Object.freeze({
  generator: 'InterfaceGenerator',
  writer: 'InterfaceWriter', // or 'SplitFileWriter' for splitted_file output
  formatter: 'Formatter',
});

/** Interpolator functions usable in paths/headers/url_params (ingen/utils/interpolators). */
export const INTERPOLATORS = Object.freeze({
  STATIC: ['date', 'token', 'token_secret', 'timestamp', 'uuid'],
  RUNTIME: ['infile', 'override'],
});

/** Adapter selection — flips the whole app between mocks and a future HTTP backend. */
export const ADAPTER_MODE = Object.freeze({
  MOCK: 'mock',
  HTTP: 'http',
});

/** Storage key namespace for the localStorage-backed mock persistence. */
export const STORAGE_NAMESPACE = 'ingen-studio';

/**
 * Stable id of the blank "draft" config the app starts fresh with on every load. A fixed id (rather
 * than a random one) means deep links like /configs/cfg_draft/... still resolve after a reload.
 */
export const DRAFT_CONFIG_ID = 'cfg_draft';

/** Current ConfigModel schema version — bump when the normalized shape changes. */
export const CONFIG_MODEL_VERSION = 1;

/**
 * Bump this string whenever the localStorage schema changes or a clean reseed is needed.
 * On mismatch, the boot sequence wipes all ingen-studio:* keys and reseeds from scratch.
 */
export const DATA_VERSION = 'v2';
