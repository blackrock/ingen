#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging
import time

import great_expectations as ge

from ingen.validation.common_validations import get_custom_validations_from_type, validate

log = logging.getLogger()


class Validation:

    def __init__(self, df, columns, data=None):
        """
        :param df: dataframe containing all the data from the csv
        :param columns: list containing column names from csv
        :param data: data containing all the sources
        """
        self._df = df
        self._columns = columns
        self._data = data

    def apply_validations(self):
        """
        Applies validations to the dataframe
        :return: Filtered dataframe after removing all the rows that failed validations if severity is critical
                 Same dataframe after showing logs of all the failed validations if severity is warning
                 Exits the application after encountering failed validations if severity is blocker
        """
        ge_dataframe = ge.from_pandas(self._df)
        for column in self._columns:
            column_name = column.get('dest_col_name', column.get('src_col_name'))

            for validation in column.get('validations', []):
                validation_type = validation.get('type')
                severity = validation.get('severity', 'warning')
                args_list = validation.get('args', [])

                validation_options = {'severity': severity}
                args_list = [column_name] + args_list

                validation_func = get_custom_validations_from_type(validation_type)

                is_custom_validation = True

                if validation_func is None:
                    try:
                        # fetching the function from ge as type is not custom
                        validation_func = getattr(ge_dataframe, validation_type)
                        is_custom_validation = False
                    except AttributeError:
                        raise ValueError(f"Invalid validation type: {validation_type} on column {column_name}")
                else:
                    args_list = [ge_dataframe] + args_list

                log.info(f"Validating column {column_name} using {validation_type} validation")
                start = time.time()
                if is_custom_validation:
                    validation_func(*args_list, meta=validation_options, data=self._data)
                else:
                    validation_func(*args_list, meta=validation_options)
                end = time.time()
                log.info(f"Finished '{validation_type}' validations on column {column_name} "
                         f"in {end - start:.2f} seconds")

        self._df, validation_summary = validate(self._df, ge_dataframe)
        return self._df, validation_summary
