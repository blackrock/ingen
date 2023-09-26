#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

from great_expectations.core.expectation_configuration import ExpectationConfiguration
from great_expectations.core.expectation_validation_result import ExpectationValidationResult

log = logging.getLogger()
custom_expectation_validation_results = []


def validate(dataframe, ge_dataframe):
    """
    Validates and filters dataframe based on the result of ge_dataframe
    :param dataframe: original dataframe
    :param ge_dataframe: great_expectations dataframe
    :return: filtered dataframe with invalid rows removed
    """
    validation_result = ge_dataframe.validate(result_format='COMPLETE')
    statistics = validation_result.get('statistics')
    log.info(f"Expectations statistics {statistics}")
    results = validation_result.get('results')
    unexpected_records_critical = set()
    validation_summary = []
    get_custom_validation_results(results)

    for result in results:
        if not result['success']:
            config = result.expectation_config
            column_name = list(config.kwargs.items())[0][1]
            expectation_type = config.expectation_type
            meta_data = config.meta
            unexpected_records_count = result.result.get('unexpected_count')
            unexpected_values = result.result.get("unexpected_list")
            unexpected_index_list = result.result.get("unexpected_index_list")

            validation_failed_warning_msg = f"Validation failed for column {column_name} for expectation type : {expectation_type}"
            unexpected_values_count_warning_msg = f"The total count of unexpected values for the column {column_name} is {unexpected_records_count}"
            unexpected_values_warning_msg = f"List of all values that violate the expectation for the column {column_name} : {unexpected_values}"
            unexpected_index_warning_msg = f"List of the indices of the unexpected values for the column {column_name} : {unexpected_index_list}"

            log.warning(validation_failed_warning_msg)
            log.warning(unexpected_values_count_warning_msg)
            log.warning(unexpected_values_warning_msg)
            log.warning(unexpected_index_warning_msg)
            severity = f"severity : {meta_data['severity']}"
            validation_summary.extend([severity, validation_failed_warning_msg, unexpected_values_count_warning_msg,
                                       unexpected_values_warning_msg, unexpected_index_warning_msg])

            if unexpected_index_list and meta_data['severity'] == 'critical':
                unexpected_records_critical.update(unexpected_index_list)

    # need to clear the list as the stale custom expectations will persist and interfere with the next batch
    custom_expectation_validation_results.clear()

    if unexpected_records_critical:
        log.info(f"TOTAL RECORDS IN DATAFRAME : {len(dataframe)}")
        dataframe.drop(unexpected_records_critical, inplace=True)
        log.info(f"TOTAL RECORDS IN DATAFRAME AFTER VALIDATION : {len(dataframe)}")

    return dataframe, validation_summary


def expect_column_to_contain_values(ge_dataframe, column_name, values, meta=None, data=None):
    """
    Expect column entries to contain the provided value.
    :param ge_dataframe: great_expectations dataframe
    :param column_name: column to be validated
    :param: dictionary of key value pair representing the type, severity and params for validations
    :param values: list of values to look for in column
    :param  meta: meta dictionary containing severity
    :param data: data containing all the sources
    :return: great_expectations dataframe with appended expectation for validations
    """

    expectation_type = 'expect_column_to_contain_values'
    unexpected_index_list = []
    unexpected_list = []

    for value in values:
        if not ge_dataframe[column_name].astype('str').eq(str(value)).any():
            unexpected_list.append(value)

    success = not unexpected_list

    custom_expectation_validation_result = build_expectation_validation_result(ge_dataframe, column_name,
                                                                               expectation_type, success,
                                                                               meta, unexpected_index_list,
                                                                               unexpected_list=unexpected_list)

    custom_expectation_validation_results.append(custom_expectation_validation_result)
    return ge_dataframe


def expect_column_values_to_be_of_type(ge_dataframe, column_name, data_type, meta=None, data=None):
    """
    Expect column entries to be parseable to provided type.
    :param ge_dataframe: great_expectations dataframe
    :param column_name: column to be validated
    :param data_type: dictionary of key value pair representing the type, severity and params for validations
    :param  meta: meta dictionary containing severity
    :param data: data containing all the sources
    :return: great_expectations dataframe with appended expectation for validations
    """

    unexpected_index_list = ge_dataframe[column_name].loc[
        [not is_parseable_to_type(value, data_type) for value in ge_dataframe[column_name]]
    ].index.values.tolist()

    success = len(unexpected_index_list) == 0
    expectation_type = 'expect_column_values_to_be_of_type'

    custom_expectation_validation_result = build_expectation_validation_result(ge_dataframe, column_name,
                                                                               expectation_type, success,
                                                                               meta, unexpected_index_list)

    custom_expectation_validation_results.append(custom_expectation_validation_result)
    return ge_dataframe


def expect_column_values_to_be_present_in(ge_dataframe, column_name, *file_col_list, meta=None, data=None):
    """
    Expects column_name values to be present in all columns of file_col_list
    :param ge_dataframe: great_expectations dataframe
    :param column_name: column to be validated
    :param file_col_list: vararg containing all column names along with their sources name
    :param meta: meta dictionary containing severity
    :param data: data containing all the sources
    :return: great_expectations dataframe with the appended expectations for validations
    """

    unexpected_index_list = set()
    unexpected_list = []

    for intersection_source, intersection_column in file_col_list:
        if intersection_source not in data or intersection_column not in data[intersection_source]:
            raise ValueError(f"Invalid {intersection_source} or {intersection_column} unable to find in source")

        are_col_values_present = ge_dataframe[column_name].isin(data[intersection_source][intersection_column])
        column_values_not_present = ge_dataframe[column_name][~are_col_values_present]

        unexpected_list.append(list(
            map(lambda x, i_source=intersection_source, i_column=intersection_column: [x, i_source, i_column],
                column_values_not_present.values)))
        unexpected_index_list.update(list(column_values_not_present.index))

    success = len(unexpected_list) == 0
    expectation_type = 'expect_column_values_to_be_present_in'

    custom_expectation_validation_result = build_expectation_validation_result(ge_dataframe, column_name,
                                                                               expectation_type, success,
                                                                               meta, unexpected_index_list,
                                                                               unexpected_list=unexpected_list)
    custom_expectation_validation_results.append(custom_expectation_validation_result)
    return ge_dataframe


def build_expectation_validation_result(ge_dataframe, column_name, expectation_type, success, metadata,
                                        unexpected_index_list, unexpected_list=[]):
    """
    Builds the object of ExpectValidationResult for custom expectation usage
    :param ge_dataframe: great_expectations dataframe
    :param column_name: name of the column
    :param expectation_type: custom expectations type
    :param success: bool value representing whether custom expectation is successful
    :param metadata: metadata to be passed to ge_dataframe
    :param unexpected_index_list: list of unexpected indices that fails the custom expectation
    :param unexpected_list: Optional, if not specified then unexpected_index_list used to fetch unexpected_list from the dataframe
    :return: ExpectationValidationResult
    """
    kwargs = {
        'column': column_name
    }
    expectation_configuration = ExpectationConfiguration(expectation_type, kwargs, metadata)

    expectation_validation_result = ExpectationValidationResult()
    expectation_validation_result.success = success
    expectation_validation_result.expectation_config = expectation_configuration

    unexpected_count = len(unexpected_index_list)
    if not unexpected_list:
        unexpected_list = ge_dataframe[column_name][unexpected_index_list].values.tolist()

    expectation_validation_result.result = {
        'unexpected_count': unexpected_count,
        'unexpected_list': unexpected_list,
        'unexpected_index_list': unexpected_index_list
    }
    return expectation_validation_result


def is_parseable_to_type(value, data_type):
    """
    Checks whether value can be type casted to data_type
    :param value: any value
    :param data_type: data type, any type from int, float and str
    :return: bool
    """
    data_types = [int, float, str]
    type_cast_func = [f for f in data_types if f.__name__ == data_type or f == data_type]
    try:
        type_cast_func[0](value)
    except ValueError:
        return False
    return True


def get_custom_validation_results(results):
    for expectation_validation_result in custom_expectation_validation_results:
        results.append(expectation_validation_result)


def get_custom_validations_from_type(validations_type):
    return custom_validations_map.get(validations_type)


custom_validations_map = {
    'expect_column_to_contain_values': expect_column_to_contain_values,
    'expect_column_values_to_be_of_type': expect_column_values_to_be_of_type,
    'expect_column_values_to_be_present_in': expect_column_values_to_be_present_in
}
