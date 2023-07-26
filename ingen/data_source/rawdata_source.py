import logging
import time

from ingen.data_source.dataframe_store import store
from ingen.data_source.source import DataSource
from ingen.reader.rawdata_reader import RawDataReader

log = logging.getLogger()


class RawDataSource(DataSource):
    """
       This class represents a raw data source, from where we can have dataframes given an id
       """

    def __init__(self, source):
        super().__init__(source.get('id'))
        self._src_data_checks = source.get('src_data_checks', [])

    def fetch(self):
        """
        reads the input id
        :return: A DataFrame fetched from the dataframe store corresponding to the id given by the user
        """
        reader = RawDataReader()
        start = time.time()

        result = reader.read(self._id, store)

        end = time.time()
        log.info(f"Successfully fetched Data Frame from {self._id} in {end - start:.2f} seconds")

        return result

    def fetch_validations(self):
        """
        Method to fetch validations from the source
        :return: list of dictionaries containing mentioned validations on all columns
        """
        return self._src_data_checks
