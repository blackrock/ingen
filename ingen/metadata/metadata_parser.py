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

    def __init__(
        self,
        filepath,
        query_params,
        run_date,
        selected_interfaces,
        infile=None,
        dynamic_data=None,
    ):
        """Initializes a metadata parser

        Args:
            filepath: Metadata file path
            query_params: Key Value pairs passed from CLI that is used to replace keys with values in sql queries
            run_date: A date param to determine the date on which InGen runs, defaults to current date
            selected_interfaces: List of interface names. This should be a subset of names declared in the metadata file
            infile: A file path passed from command line to load a File Source
            dynamic_data: JSON String passed from command line to load a JSON Source
        """
        self._filepath = filepath
        self._run_date = run_date
        self._query_params = query_params
        self._selected_interfaces = selected_interfaces
        self._run_config = None
        self._infile = infile
        self._dynamic_data = dynamic_data

    @property
    def run_config(self):
        return self._run_config

    def parse_metadata(self):
        """
        Parse the YAML metadata file

        :return: A list of interface MetaData objects
        """
        with open(self._filepath) as file:
            log.info(f"Loading file {self._filepath} to parse metadata config")
            metadata = yaml.load(file, Loader=yaml.FullLoader)
            self._run_config = RunConfiguration(metadata.get("run_config", {}))
            if self._selected_interfaces:
                interfaces_from_metadata = metadata["interfaces"]
                interfaces = {
                    k: v
                    for (k, v) in interfaces_from_metadata.items()
                    if k in self._selected_interfaces
                }
            else:
                interfaces = metadata["interfaces"]

            sources = {source["id"]: source for source in metadata["sources"]}

            for interface in interfaces.values():
                source_ids = interface.get("sources")
                interface["sources"] = [sources[sid] for sid in source_ids]

            params_map = {
                "query_params": self._query_params,
                "run_date": self._run_date,
                "infile": self._infile,
            }

            interface_configs = [
                MetaData(x, interfaces[x], params_map, self._dynamic_data)
                for x in interfaces
            ]
            return interface_configs
