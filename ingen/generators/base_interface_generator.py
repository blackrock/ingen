#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging
from abc import ABC, abstractmethod

log = logging.getLogger(__name__)


class BaseInterfaceGenerator(ABC):
    def generate(
        self,
        interface_name,
        sources,
        pre_processes,
        columns,
        destination,
        params,
        validation_action,
    ):
        """
        Template method that defines the skeleton of interface generation
        :param interface_name: name of the interface, used for logging purpose
        :param sources: datasource definitions
        :param pre_processes: pre_processing steps, to be executed on the dataframe(s)
        :param columns: defines the columns and their formatting options
        :param destination: defines the destination parameters
        :param params: has the command line arguments used while invoking
        :param validation_action: Defines the validation action in the form of sending email in case of validation failure
        """
        try:
            data = self.read(sources)

            # validation on raw data
            _, validation_summary_raw = self.validate(
                data, columns, data=data, sources=sources
            )
            validation_summary = {
                key.id: value for key, value in zip(sources, validation_summary_raw)
            }

            if "blocker" not in str(validation_summary):
                processed_data = self.pre_process(pre_processes, data)
                formatted_data = self.format(processed_data, columns, params)
                # validation on formatted data
                validated_data, validation_summary_formatted = self.validate(
                    formatted_data, columns, data=data
                )
                validation_summary[interface_name] = validation_summary_formatted[0]

            self.notify(params, validation_action, validation_summary)

            if destination.get("type"):
                self.write(validated_data, destination, params)
            else:
                return validated_data.to_json(orient="records", lines=True)
        except Exception as e:
            log.exception(
                f"Error generating interface file for {interface_name} \n {e}"
            )
            raise

    @abstractmethod
    def read(self, sources):
        """
        Responsible for reading data from multiple sources
        :param sources: A list of DataSources
        :return: A dataframe containing raw data
        """
        pass

    @abstractmethod
    def pre_process(self, pre_processes, sources):
        """
        Responsible for preprocessing data after reading from source
        :param pre_processes: pre_processes to perform after the data is fetched from the source
        :param sources: A dictionary of DataSources with key as the source.id
        :return: A dataframe after executing the pre_processing step(s)
        """
        pass

    @abstractmethod
    def format(self, data, columns, params):
        """
        Applies formatting to raw_data
        :param data: A dataframe containing raw data
        :param columns: List of columns and their formatting options
        :param params: has the command line arguments used while invoking
        """
        pass

    @abstractmethod
    def write(self, data, destination, params):
        """
        Method to persist the data as per destination properties
        :param data: A dataframe containing actual data
        :param destination: Properties defining how and whereto persist data
        :param params: has the command line arguments used while invoking
        """
        pass

    @abstractmethod
    def validate(self, df, columns, data=None, sources=None):
        """
        :param df: dataframe containing all the data from the csv
        :param columns: list containing column names from csv
        :param data: optional arg containing data from all the sources
        :param sources: list of all validation applied on raw data
        """
        pass

    def notify(self, params, validation_action, validation_summary):
        """
        :param params: has the command line arguments used while invoking
        :param validation_action: contains type of validation action to trigger in case of validation failure
        :param validation_summary: Dictionary of source name and their validation summary
        """
        pass
