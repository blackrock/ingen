#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from ingen.utils.path_parser import PathParser
from ingen.writer.json_writer.convertors.convertor_factory import get_json_convertor
from ingen.writer.json_writer.destinations.destination_factory import get_json_destination


class JSONWriter:
    def __init__(self, df, writer_configs, params=None, json_convertor_factory=get_json_convertor,
                 json_destination_factory=get_json_destination):
        self.df = df
        self.configs = writer_configs
        self.json_convertor_factory = json_convertor_factory
        self.json_destination_factory = json_destination_factory
        self._validate_writer_config()
        self.params = params

    def _validate_writer_config(self):
        required_properties = ['convertor', 'convertor_props', 'destination', 'destination_props']

        for prop in required_properties:
            if prop not in self.configs:
                raise ValueError(f'missing json_writer props "{prop}". Please check the YAML file')

    def write(self):
        convertor_type = self.configs.get('convertor')
        convertor_props = self.configs.get('convertor_props')
        json_convertor = self.json_convertor_factory(convertor_type)
        json_strings = json_convertor.convert(self.df, convertor_props)

        destination_type = self.configs.get('destination')
        destination_props = self.configs.get('destination_props')
        destination = self.json_destination_factory(destination_type, self.params)

        destination.handle(json_strings, destination_props)

    def writecsv(self):

        destination_type = self.configs.get('destination')
        destination_props = self.configs.get('destination_props')
        destination = self.json_destination_factory(destination_type, self.params)

        data = destination_props.get("payload")
        path_parser = PathParser()
        data = path_parser.parse(data)
        test_data = [data]

        destination.handle(test_data, destination_props)
