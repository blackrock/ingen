#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging
from datetime import date

from ingen.data_source.source import DataSource
from ingen.reader.file_reader import ReaderFactory
from ingen.utils.interpolators.Interpolator import Interpolator
from ingen.utils.path_parser import PathParser
from ingen.utils.timer import log_time

log = logging.getLogger()


class FileSource(DataSource):
    """
    This class represents a File source
    """

    def __init__(self, source, params_map, interpolator=Interpolator()):
        """
        Loads a file

        :param source : An interface source contains all the attributes i.e. file_id, file_path, file_type, input_columns and others
        :param params_map : command line parameters, query_params + run_date

        """
        super().__init__(source.get('id'))
        self.interpolator = interpolator
        if params_map.get('infile') and source['use_infile']:
            source['file_path'] = params_map['infile']
            self._src = source
        else:
            self._src = self.format_file_path(source, params_map)

    def fetch(self):
        """
        reads the input file

        :return: A DataFrame created using the result of the reading the file
        """
        reader = ReaderFactory.get_reader(self._src)
        return self.fetch_data(reader)

    @log_time
    def fetch_data(self, reader):
        """
        returns a DataFrame of data fetched from input FileSource.
        """
        return reader.read(self._src)

    def fetch_validations(self):
        """
        Method to fetch validations from the source
        :return: list of dictionaries containing mentioned validations on all columns
        """
        return self._src.get('src_data_checks', [])

    def format_file_path(self, source, params_map):
        if params_map is None:
            run_date = date.today()
        else:
            run_date = params_map.get('run_date', date.today())

        path_parser = PathParser(run_date, interpolator=self.interpolator)
        if 'file_path' in source:
            source['file_path'] = path_parser.parse(source['file_path'])
        return source
