#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

class FileDestination:
    def handle(self, json_strings, destination_props):
        paths = destination_props.get('path')
        if not isinstance(paths, list):
            paths = [paths]
        for file_path in paths:
            with open(file_path, 'w') as file:
                file.writelines(json_strings)
