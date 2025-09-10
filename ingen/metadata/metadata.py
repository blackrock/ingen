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

    def __init__(
        self, name, configurations, params_map, dynamic_data=None
    ):
        """Initializes a MetaData object for an interface

        Args:
            name: Name of the interface
            configurations: A dictionary representing the properties of the interface
            params_map: A dictionary containing command line parameters: query_params, run_date and infile
            dynamic_data: JSON String passed from command line to load a JSON Source
        """

        self._configurations = configurations
        self._name = name
        self._params_map = params_map if params_map else {}
        self._infile = self._params_map.get('infile')
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
        return self._configurations.get("columns", [])

    @property
    def pre_processes(self):
        return self._configurations.get("pre_processing")

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
        return self._configurations.get("validation_action")

    def _initialize_sources(self):
        sources = []
        source_factory = SourceFactory()
        for source in self._configurations["sources"]:
            data_source = source_factory.parse_source(
                source, self._params_map, self._dynamic_data
            )
            sources.append(data_source)
        return sources

    def _validate_path(self, props):
        path = props.get("path")
        if path is None:
            return
        if isinstance(path, str):
            path = [path]

        run_date = self._params_map.get("run_date", date.today())
        path_parser = PathParser(run_date)
        parsed_paths = [path_parser.parse(p) for p in path]
        props["path"] = parsed_paths

    def _initialize_output(self):
        output = self._configurations.get("output", {})
        props = output.get("props", {})
        if output.get("type") == "splitted_file":
            for file in props:
                self._validate_path(file.get("props"))
        elif output.get("type") == "json_writer":
            props = output.get("props")
            if props is not None and props.get("destination") == "file":
                self._validate_path(props.get("destination_props"))
        else:
            self._validate_path(props)

        output = {
            "type": self._configurations.get("output", {}).get("type"),
            "props": self._configurations.get("output", {}).get("props", {}),
        }
        return output
