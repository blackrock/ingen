#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import abc
import logging

import pandas as pd

from ingen.reader.json_reader import JSONFileReader
from ingen.reader.xml_file_reader import XMLFileReader


class Reader(metaclass=abc.ABCMeta):
    DTYPE_LOG_MSG = "Invalid data type provided in column_dtype mapping"

    @abc.abstractmethod
    def read(self, src):
        pass


class CSVFileReader(Reader):

    def read(self, src):
        config = get_config(src)
        dtype = src.get('dtype')
        try:
            result = pd.read_csv(src['file_path'],
                                 sep=src.get('delimiter'),
                                 index_col=False,
                                 skiprows=config['header_size'],
                                 skipfooter=config['trailer_size'],
                                 names=config['all_cols'],
                                 dtype=dtype)
        except TypeError:
            logging.error(self.DTYPE_LOG_MSG)
            raise
        except FileNotFoundError:
            if 'return_empty_if_not_exist' in src and src['return_empty_if_not_exist']:
                result = pd.DataFrame(columns=config['all_cols'])
            else:
                raise

        return result


class ExcelFileReader(Reader):
    def read(self, src):
        config = get_config(src)
        dtype = src.get('dtype')
        file_path = src.get('file_path')
        sheet_name = src.get('sheet_name')
        if sheet_name is None:
            sheet_name = 0

        excel_extension = file_path.split('.')[-1]
        excel_engine = 'openpyxl' if excel_extension == 'xlsx' else None
        try:
            result = pd.read_excel(src['file_path'],
                                   sheet_name=sheet_name,
                                   index_col=False,
                                   skiprows=config['header_size'],
                                   skipfooter=config['trailer_size'],
                                   names=config['all_cols'],
                                   dtype=dtype,
                                   engine=excel_engine)
        except TypeError:
            logging.error(self.DTYPE_LOG_MSG)
            raise
        except FileNotFoundError:
            if 'return_empty_if_not_exist' in src and src['return_empty_if_not_exist']:
                result = pd.DataFrame(columns=config['all_cols'])
            else:
                raise
        return result


class FixedWidthFileReader(Reader):
    def read(self, src):
        config = get_config(src)
        dtype = src.get('dtype')
        file_path = src.get('file_path')
        colspecs = src.get('col_specification')
        try:
            result = pd.read_fwf(file_path,
                                 index_col=False,
                                 colspecs=colspecs,
                                 dtype=dtype,
                                 skiprows=config['header_size'],
                                 skipfooter=config['trailer_size'],
                                 names=config['all_cols'])
        except TypeError:
            logging.error(self.DTYPE_LOG_MSG)
            raise
        except FileNotFoundError:
            if 'return_empty_if_not_exist' in src and src['return_empty_if_not_exist']:
                result = pd.DataFrame(columns=config['all_cols'])
            else:
                raise

        return result


def get_config(src):
    header_size = src.get('skip_header_size' , 0)
    trailer_size = src.get('skip_trailer_size' , 0)
    all_cols = src.get('columns')
    return {
        "header_size": header_size,
        "trailer_size": trailer_size,
        "all_cols": all_cols
    }


class ReaderFactory:

    @classmethod
    def get_reader(cls, src):
        factory_types = {'delimited_file': CSVFileReader,
                         'excel': ExcelFileReader,
                         'xml': XMLFileReader,
                         'json': JSONFileReader,
                         "fixed_width": FixedWidthFileReader
                         }
        reader_cls = factory_types.get(src.get('file_type'))
        if reader_cls:
            return reader_cls()

