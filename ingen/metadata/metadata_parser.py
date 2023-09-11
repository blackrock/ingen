#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import logging

import yaml

from ingen.metadata.metadata import MetaData
from ingen.utils.run_configuration import RunConfiguration

log = logging.getLogger()


class MetaDataParser:
    """
    MetaDataParser reads a YAML file and creates a MetaData object for each interface
    """

    def __init__(self, filepath, query_params, run_date, selected_interfaces, infile=None, user_domain=None,
                 dynamic_data=None):
        """
        Loads a parser for the given metadata file

        :param filepath: file path of the interface metadata file (aka metadata file)
        """
        self._filepath = filepath
        self._run_date = run_date
        self._query_params = query_params
        self._selected_interfaces = selected_interfaces
        self._run_config = None
        self._infile = infile
        self._user_domain = user_domain
        self._dynamic_data = dynamic_data

    @property
    def run_config(self):
        return self._run_config

    def parse_metadata(self):
        """
        Parse the YAML metadata file

        :return: A list of interface MetaData objects
        """
        interface_configs = []
        with open(self._filepath) as file:
            log.info(f"Loading file {self._filepath} to parse metadata config")
            metadata = yaml.load(file, Loader=yaml.FullLoader)
            self._run_config = self.parse_run_config(metadata)
            if self._selected_interfaces:
                interfaces_from_metadata = metadata['interfaces']
                interfaces = {k: v for (k, v) in interfaces_from_metadata.items() if k in self._selected_interfaces}
            else:
                interfaces = metadata['interfaces']
            sources = self.make_source_dict(metadata['sources'])
            self.map_interface_sources(interfaces, sources)
            params_map = self.make_runtime_parameters_map(self._query_params, self._run_date, self._user_domain,
                                                          self._infile)
            interface_configs = [MetaData(x, interfaces[x], params_map, self._infile, self._dynamic_data) for x in
                                 interfaces]
        return interface_configs

    def make_runtime_parameters_map(self, query_params, run_date, user_domain, infile=None):
        runtime_parameters = {'query_params': query_params, 'run_date': run_date, 'user_domain': user_domain,
                              'infile': infile}
        return runtime_parameters

    def make_source_dict(self, sources):
        sources_dict = {}
        for source in sources:
            sources_dict[source['id']] = source
        return sources_dict

    def map_interface_sources(self, interfaces, sources):
        for interface in interfaces.values():
            source_ids = interface.get('sources')
            interface['sources'] = [sources[sid] for sid in source_ids]

    def parse_run_config(self, metadata):
        config = {}
        if 'run_config' in metadata:
            config = metadata['run_config']
        return RunConfiguration(config)
