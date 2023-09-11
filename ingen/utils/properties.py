#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

import os


class Properties:
    """
        A class to read key value properties from a properties file named config.properties located at a path
        defined as environment variable config_path
        separated by '='

    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(Properties, cls).__new__(cls)
            return cls._instance

    def __init__(self):
        self.property_map = None
        self.initialize_properties()

    def initialize_properties(self):
        """
            Initializes the property map by reading the properties file.
        """
        if self.property_map is None:
            self.property_map = dict()
            path = os.getenv('config_path')
            if path is not None:
                file = open(os.path.join(path, "config.properties"), 'r')
                properties_line = file.read().splitlines()
                for prop in properties_line:
                    list_property = prop.split("=")
                    self.property_map[list_property[0]] = list_property[1]

    def get_property(self, token_name, default=None):
        """
            A method to return value of a property as defined in a properties file
            Returns a string

            argument:
                token name: name of property to be fetched.
                default: default value incase prop key is not found in properties file
        """
        prop_value = self.property_map.get(token_name)
        return prop_value if prop_value else default


properties = Properties()
