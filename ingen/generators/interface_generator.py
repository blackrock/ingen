#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

from ingen.formatters.formatter import Formatter
from ingen.generators.base_interface_generator import BaseInterfaceGenerator
from ingen.pre_processor.pre_processor import PreProcessor
from ingen.validation.notification import email_attributes
from ingen.validation.validations import Validation
from ingen.writer.writer import InterfaceWriter

log = logging.getLogger()


class InterfaceGenerator(BaseInterfaceGenerator):

    def __init__(self, writer=InterfaceWriter, formatter=Formatter, pre_processor=PreProcessor,
                 validations=Validation):
        self.writer = writer
        self.formatter = formatter
        self.pre_processor = pre_processor
        self.validations = validations

    def read(self, sources):
        return {source.id: source.fetch() for source in sources}

    def pre_process(self, pre_processes, data):
        pre_processor = self.pre_processor(pre_processes, data)
        return pre_processor.pre_process()

    def format(self, data, columns, params):
        formatter = self.formatter(data, columns, params)
        formatted_data = formatter.apply_format()
        return formatted_data

    def validate(self, df, columns, data=None, sources=None):
        """
        :param df: dataframe containing all the data from the csv
        :param columns: list containing column names from csv
        :param data: optional arg containing data from all the sources
        :param sources: list of all validation applied on raw data
        """

        validation_summaries = []
        validated_dataframe = None
        if sources is None:
            log.info(f"Starting validations on Formatted data")
            self.validations = Validation(df, columns, data=data)
            validated_dataframe, validation_summary = self.validations.apply_validations()
            validation_summaries.append(validation_summary)
            log.info(f" Finished validations on Formatted data")
        else:
            for source in sources:
                validation_list = source.fetch_validations()
                if validation_list:
                    log.info(f"Starting validations on Raw data for {source.id}")
                    self.validations = Validation(source.fetch(), validation_list, data=data)
                    validated_dataframe, validation_summary = self.validations.apply_validations()
                    validation_summaries.append(validation_summary)
                    log.info(f" Finished validations on Raw data for {source.id}")

        return validated_dataframe, validation_summaries

    def notify(self, params, validation_action, validation_summary):
        """
        :param params: has the command line arguments used while invoking
        :param validation_action: contains type of validation action to trigger in case of validation failure
        :param validation_summary: Dictionary of source name and their validation summary
        """
        if validation_action and validation_action.get('send_email'):
            email_attributes(params, validation_action, validation_summary)

    def write(self, data, destination, params):
        output_type = destination['type']
        props = destination.get('props', dict())
        writer = self.writer(data, output_type, props, params)
        writer.write()
