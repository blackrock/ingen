#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

class RawDataReader:
    """A class written to read specific input IDs and read the Dataframe stored corresponding to that ID in the Store
    Dictionary"""

    def read(self, _id, df_dict):
        return df_dict[_id]
