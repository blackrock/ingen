#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

from ingen.writer.dataframe_writer import DataFrameWriter
from ingen.writer.json_writer.json_writer import JSONWriter
from ingen.writer.old_json_writer import OldJSONWriter
from ingen.writer.util import *

logger = logging.getLogger("writer")


class InterfaceWriter:
    SHOW_DATAFRAME_INDEX = False

    def __init__(self, df, output_type, writer_props, params):
        self._df = df
        self._type = output_type
        self._props = writer_props
        self.header = self._props.get('header')
        self.footer = self._props.get('footer')
        self.action = self._props.get('action')
        self._params = params
        self._apicall = self._props.get('api_call')

    def write(self):

        self.file_writer()
        if self._type == 'delimited_file':
            header_string = ''
            footer_string = ''
            header_or_footer_exists = False
            if self.header and self.header.get('type') == 'custom':
                header_string = self.get_header()
                header_or_footer_exists = True
            if self.footer and self.footer.get('type') == 'custom':
                footer_string = self.get_footer()
                header_or_footer_exists = True
            if header_or_footer_exists:
                self.add_header_footer(header_string, footer_string)

    def file_writer_excel(self, path):

        if self.header and self.header.get('type') == 'delimited_result_header':
            self._df.to_excel(path, index=InterfaceWriter.SHOW_DATAFRAME_INDEX)
        else:
            self._df.to_excel(path, header=False, index=InterfaceWriter.SHOW_DATAFRAME_INDEX)

    def file_writer_delimited(self, path):
        logger.info(f"writing file to {path}")
        sep = self._props['delimiter'] if 'delimiter' in self._props else ','
        if self.header and self.header.get('type') == 'delimited_result_header':
            self._df.to_csv(path, sep, index=InterfaceWriter.SHOW_DATAFRAME_INDEX)
        else:
            self._df.to_csv(path, sep, header=False, index=InterfaceWriter.SHOW_DATAFRAME_INDEX)

    def file_writer(self):
        paths = self._props.get('path')
        if not isinstance(paths, list):
            paths = [paths]

        for path in paths:
            if self._type == 'json':
                json_writer = OldJSONWriter(self._df, self._type, self._props)
                json_writer.write()
            elif self._type == 'json_writer':
                writer = JSONWriter(self._df, self._props, self._params)
                writer.write()
            elif self._type == 'rawdatastore':
                df_writer = DataFrameWriter(self._df, self._props)
                df_writer.write()
            elif self._type == 'excel':
                self.file_writer_excel(path)
            elif self._type == 'delimited_file':
                self.file_writer_delimited(path)
                if self._apicall:
                    writer = JSONWriter(self._df, self._props, self._params)
                    writer.writecsv()
            else:
                logger.error(f'Invalid {self._type} file type')

    def get_header(self):
        header = self._props['header']['function']
        header_string = self.custom_function(header)
        return header_string

    def get_footer(self):
        footer = self._props['footer']['function']
        footer_string = self.custom_function(footer)
        return footer_string

    def add_header_footer(self, header, footer):
        path = self._props['path']
        file = open(path, 'r+')
        if header != '':
            lines = file.readlines()
            file.seek(0)
            file.writelines(header + '\n')
            for line in lines:
                file.write(line)
        if footer != '':
            file.read()
            file.write(footer)
        file.close()

    def custom_function(self, value):
        run_date = self._params['run_date']
        try:
            custom_function_value = get_custom_value(value, self._df, run_date)
            return custom_function_value
        except Exception as e:
            logging.error(f"Failed to find method, {e}")
