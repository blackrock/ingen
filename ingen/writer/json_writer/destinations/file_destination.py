#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

class FileDestination:
    def handle(self, json_strings, destination_props):
        file_path = destination_props.get('path')
        with open(file_path, 'w') as file:
            file.writelines(json_strings)
