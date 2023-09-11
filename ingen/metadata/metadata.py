#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from datetime import date

from ingen.data_source.source_factory import SourceFactory
from ingen.utils.path_parser import PathParser


class MetaData:
    """
    This class represents the metadata of a single interface file. It includes information
    like column details, source(s), output file name and type, etc.
    """

    def __init__(self, name, configurations, params_map, infile=None, dynamic_data=None):
        """
        Loads a MetaData object for a particular interface
        :param name: Name of the interface
        :param configurations: dict-like object to store configurable properties of a metadata
        :param params_map: command line parameters, query_params + run_date
        :param dynamic_data: JSON dictionary as a string to store JSON source payloads
        """
        self._configurations = configurations
        self._name = name
        self._params_map = params_map
        self._infile = infile
        self._dynamic_data = dynamic_data
        self._sources = self._initialize_sources()
        self._output = self._initialize_output()

    @property
    def name(self):
        return self._name

    @property
    def output(self):
        return self._output

    @property
    def columns(self):
        return self._configurations.get('columns', [])

    @property
    def pre_processes(self):
        return self._configurations.get('pre_processing')

    @property
    def sources(self):
        return self._sources

    @property
    def params(self):
        return self._params_map

    @property
    def infile(self):
        return self._infile

    @property
    def validation_action(self):
        return self._configurations.get('validation_action')

    def _initialize_sources(self):
        sources = []
        source_factory = SourceFactory()
        for source in self._configurations['sources']:
            data_source = source_factory.parse_source(source, self._params_map, self._dynamic_data)
            sources.append(data_source)
        return sources

    def _validate_path(self, props):
        path = props.get('path')
        if path is None:
            return
        run_date = self._params_map.get('run_date', date.today())
        path_parser = PathParser(run_date)
        props['path'] = path_parser.parse(path)

    def _initialize_output(self):
        output = self._configurations.get('output', dict())
        props = output.get('props', dict())
        if output.get('type') == 'splitted_file':
            for file in props:
                self._validate_path(file.get('props'))
        elif output.get('type') == 'json_writer':
            props = output.get('props')
            if props is not None and props.get('destination') == 'file':
                self._validate_path(props.get('destination_props'))
        else:
            self._validate_path(props)

        output = {'type': self._configurations.get('output', dict()).get('type'),
                  'props': self._configurations.get('output', dict()).get('props', dict())}
        return output
