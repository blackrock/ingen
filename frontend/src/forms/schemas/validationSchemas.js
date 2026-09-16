//  Validation expectation metadata. Formatted-frame validations are stored PER COLUMN under
//  columns[i].validations[] as { type, severity, args } — confirmed against ingen/validation/
//  validations.py (it reads column.get('validations')). args are expectation-specific.

import { VALIDATION_TYPES, VALIDATION_SEVERITIES } from '../../models/constants.js';

/** Per-expectation arg hint (shown in the args JSON editor). Empty string ⇒ no args. */
export const VALIDATION_ARG_HINTS = {
  expect_column_values_to_not_be_null: '',
  expect_column_values_to_be_unique: '',
  expect_column_values_to_match_regex_list: '[["^[0-9]+$"], "any"]',
  expect_column_values_to_match_strftime_format: '["%Y-%m-%d"]',
  expect_column_values_to_be_between: '[10, 20]',
  expect_column_value_lengths_to_equal: '[8]',
  expect_column_to_contain_values: '[["XUSD0000", "ABC1234F"]]',
  expect_column_values_to_be_of_type: '["float"]',
  expect_column_values_to_be_present_in: '[["src", "col"]]',
  expect_column_to_be_present_in: '[["COL_2", "cusip"]]',
};

export const ALL_EXPECTATIONS = [...VALIDATION_TYPES.BUILTIN, ...VALIDATION_TYPES.CUSTOM];

export const SEVERITY_OPTIONS = Object.values(VALIDATION_SEVERITIES);

/** Human note on what each severity does post-failure (from the backend severity handling). */
export const SEVERITY_ACTION = {
  blocker: 'aborts the interface',
  critical: 'drops failing rows',
  warning: 'reports only',
};
