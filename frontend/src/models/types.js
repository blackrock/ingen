//  InGen Studio — domain types
//
//  The project is plain JavaScript (no TypeScript toolchain), so domain types are expressed
//  as JSDoc typedefs. Editors get full IntelliSense/checking from these, and they document the
//  exact shape that mirrors the InGen YAML — without adding a build step.
//
//  Two representations exist:
//    1. The DESERIALIZED (raw) YAML shape — what InGen actually reads.
//    2. The NORMALIZED ConfigModel — what the frontend edits in memory.
//  The serializers (src/serializers) translate between them.

// ───────────────────────── Raw / backend-shaped types ─────────────────────────

/**
 * A data source definition (type-discriminated union). Stored mostly verbatim from YAML.
 * Only the fields the UI actually touches are named; everything else is allowed
 * via the index signature so unknown/advanced fields round-trip losslessly.
 *
 * @typedef {Object} Source
 * @property {string} id                       Unique source identifier (referenced by interfaces).
 * @property {'file'|'mysql'|'api'|'json'} type
 * @property {string} [file_type]              file sources: delimited_file|excel|xml|json|fixed_width
 * @property {string} [file_path]
 * @property {string} [delimiter]
 * @property {string[]} [columns]
 * @property {string} [query]                  mysql sources (SQL with {param} placeholders)
 * @property {string} [db_token]               mysql sources
 * @property {string} [url]                    api sources
 * @property {Object[]} [src_data_checks]      raw-data validations applied at the source
 * @property {*} [key]                         any additional backend field (passes through)
 */

/**
 * A single pre-processing step. `type` selects the processor; remaining keys are the step config.
 * Shapes (corrected against backend source):
 *  - merge:              { type, source, left_key, right_key, merge_type }
 *  - outer_join:         { type, source, left_key, right_key }
 *  - union:              { type, source: string[] }
 *  - aggregate:          { type, groupby:{cols:[]}, agg:{operation, col} }
 *  - mask:               { type, on_col, masking_source, masking_col }
 *  - melt:               { type, key_column, value_column, include_keys:[], source:[] }
 *  - filter:             { type, operator:'and'|'or', cols:[{col, val:[]}] }
 *  - not_equals_filter:  { type, source?, cols:[{col, val:[]}] }
 *  - drop_duplicates:    { type, columns:[], keep:'first'|'last'|false }
 *  - json_array_expander:{ type, config:{column, include_columns, exclude_columns} }
 *
 * @typedef {Object} PreProcessStep
 * @property {string} type
 * @property {*} [key]
 */

/**
 * One formatter applied to a column. `format` is polymorphic per type (string | array | object).
 * @typedef {Object} Formatter
 * @property {string} type
 * @property {(string|Array|Object)} [format]
 */

/**
 * An output column mapping with optional ordered formatters.
 * @typedef {Object} Column
 * @property {string} src_col_name
 * @property {string} [dest_col_name]          Defaults to src_col_name in the backend.
 * @property {Formatter[]} [formatters]
 */

/**
 * A post-processing step (currently only `pivot`).
 * @typedef {Object} PostProcessStep
 * @property {string} type
 * @property {Object} [processing_values]
 */

/**
 * Output / writer definition.
 * @typedef {Object} Output
 * @property {string} type                     delimited_file|excel|json|json_writer|splitted_file
 * @property {(Object|Object[])} [props]       props is an array for splitted_file, object otherwise.
 */

/**
 * run_config — pluggable component selection resolved by name in the backend.
 * @typedef {Object} RunConfig
 * @property {string} [generator]
 * @property {string} [writer]
 * @property {string} [formatter]
 */

/**
 * A single interface definition (the unit InGen generates one output file for).
 * In the normalized model, `sources` is a list of source IDs (string), matching the YAML.
 * @typedef {Object} Interface
 * @property {string[]} sources                Ordered source IDs; sources[0] is the pre-process base.
 * @property {PreProcessStep[]} [pre_processing]
 * @property {Column[]} [columns]
 * @property {PostProcessStep[]} [post_processing]
 * @property {Object} [validation_action]
 * @property {Output} [output]
 */

/**
 * The raw YAML document shape InGen consumes (output of serialization / input of parsing).
 * @typedef {Object} RawConfig
 * @property {Source[]} sources
 * @property {Object.<string, Interface>} interfaces
 * @property {RunConfig} [run_config]
 */

// ───────────────────────── Normalized in-memory model ─────────────────────────

/**
 * Metadata about the config document itself (not part of the InGen YAML).
 * @typedef {Object} ConfigMeta
 * @property {string} id
 * @property {string} name
 * @property {number} version                  CONFIG_MODEL_VERSION at time of write.
 * @property {string} createdAt                ISO timestamp.
 * @property {string} updatedAt                ISO timestamp.
 */

/**
 * The normalized config model the UI edits. Sources and interfaces are stored in lookup maps
 * plus order arrays so the editor can reference them by key while preserving the YAML-significant
 * ordering (interfaces run in declaration order).
 *
 * @typedef {Object} ConfigModel
 * @property {ConfigMeta} meta
 * @property {RunConfig} run_config
 * @property {Object.<string, Source>} sourcesById
 * @property {string[]} sourceOrder
 * @property {Object.<string, Interface>} interfacesByName
 * @property {string[]} interfaceOrder
 */

/**
 * A validation/lint issue produced without running the pipeline.
 * @typedef {Object} ConfigIssue
 * @property {'error'|'warning'} level
 * @property {string} code
 * @property {string} message
 * @property {string} [path]                   Dot path into the model, for jump-to-field.
 */

export {}; // module marker; this file only declares JSDoc types.
