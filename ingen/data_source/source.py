#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

class DataSource:
    """
    A DataSource represents the properties of a source of the interface data. All data source must implement
    a method called fetch, which is responsible for fetching data and returning it in a pandas DataFrame fromat
    """

    def __init__(self, _id):
        self._id = _id

    @property
    def id(self):
        return self._id

    def fetch(self):
        """
        Method responsible for fetching data from source

        :return: A Pandas DataFrame
        """
        pass

    def fetch_validations(self):
        """
        Method to fetch validations from the source
        :return: list of dictionaries containing mentioned validations on all columns
        """
        pass
