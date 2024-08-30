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
            try:
                if path is not None:
                    with open(os.path.join(path, "config.properties"), 'r') as file:
                        properties_line = file.read().splitlines()
                        for prop in properties_line:
                            if prop.strip():
                                list_property = prop.split("=")
                                if len(list_property) == 2:
                                    self.property_map[list_property[0].strip()] = list_property[1].strip()
                                else:
                                    print(f"Invalid property format in line: {prop}")
            except FileNotFoundError:
                print(f"Configuration file not found at path: {path}."
                      f" Please create the file with the necessary properties.")
            except Exception as e:
                print(f"An error occurred while reading the properties file: {e}")

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
