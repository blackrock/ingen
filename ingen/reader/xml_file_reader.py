#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import collections
import logging
from pyexpat import ExpatError
from xml.etree import ElementTree as et

import pandas as pd
import xmltodict


class XMLFileReader:

    def read(self, src):
        xml_file = open(src['file_path'], 'r')
        try:
            data = xmltodict.parse(xml_file.read())
            tree = et.parse(src['file_path'])
            root = tree.getroot()
            root_with_xmlns = root.tag.split('}')
            if '}' in root.tag:
                parent_tag = root_with_xmlns[1]
            else:
                parent_tag = root.tag
            root_tag = src['root_tag']
            columns = src['columns']
            if root_tag in data[parent_tag]:
                xml_data = data[parent_tag][root_tag]
                rows = []
                if isinstance(xml_data, (dict, collections.OrderedDict)):
                    obj = xml_data
                    create_rows(rows, obj, columns)
                else:
                    for obj in xml_data:
                        create_rows(rows, obj, columns)
                main_df = pd.DataFrame([], columns=columns)
                for row in rows:
                    df = create_dataframe(row, columns)
                    main_df = pd.concat([main_df, df], axis=0, ignore_index=True)
            else:
                main_df = pd.DataFrame([], columns=columns)
        except ExpatError:
            logging.error("XML file is empty or malformed")
            raise
        return main_df


def get_record(obj, name, val_arr):
    n = name.split('.')
    if obj is None or isinstance(obj, str):
        val_arr.append('')
    if len(n) == 1:
        elem_name = n[0]
        if isinstance(obj, list):
            # for each obj in that list print elem
            get_list_record(obj, elem_name, val_arr)
        elif isinstance(obj, (dict, collections.OrderedDict)):
            if isinstance(obj.get(elem_name), str):
                val_arr.append(obj.get(elem_name))
            elif isinstance(obj.get(elem_name), (dict, collections.OrderedDict)):
                val_arr.append(obj.get(elem_name).get('#text'))
            elif isinstance(obj.get(elem_name), type(None)):
                val_arr.append('')

    else:
        if isinstance(obj, list):
            get_list_record(obj, name, val_arr)
        else:
            get_record(obj.get(n[0]), '.'.join(n[1:]), val_arr)


def get_list_record(obj, name, val_arr):
    for _ in obj:
        get_record(_, name, val_arr)


def create_rows(rows, obj, columns):
    row = []
    for col in columns:
        val_arr = []
        get_record(obj, col, val_arr)
        row.append(val_arr)
    rows.append(row)


def create_dataframe(row, columns):
    repeat_count = 1
    dic = {}
    for elem in row:
        repeat_count *= len(elem)
    for idx, elem in enumerate(row):
        dic[columns[idx]] = (elem * (repeat_count // len(elem)))
    df = pd.DataFrame(dic)
    # this is to remove duplicates caused due to repeat_count, but it'll also remove duplicates that are
    # present in original data
    df.drop_duplicates(inplace=True)
    return df
