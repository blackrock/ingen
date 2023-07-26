from enum import Enum


class DataSourceType(Enum):
    """
    Enumeration of DataSource types

    """

    DB = "db"
    File = "file"
    Api = "api"
    MYSQL = "mysql"
    RawDataStore = "rawdatastore"
