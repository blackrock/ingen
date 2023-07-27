class RawDataReader:
    """A class written to read specific input IDs and read the Dataframe stored corresponding to that ID in the Store
    Dictionary"""

    def read(self, _id, df_dict):
        if _id in df_dict.keys():
            return df_dict.get(_id)
        else:
            raise KeyError(f"key '{_id}' missing in RawDataStore.")
