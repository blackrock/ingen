#  Copyright (c) 2023 BlackRock, Inc.
#  All Rights Reserved.

from mysql.connector import connection, Error


class DataSource(object):
    def __init__(self, host=None, user=None, passwd=None, database=None):
        self.__connection = None
        self.__host = host
        self.__user = user
        self.__passwd = passwd
        self.__database = database
        self.__cursor = set()

    def get_connection(self):
        try:
            self.__connection = connection.MySQLConnection(host=self.__host, user=self.__user, password=self.__passwd,
                                 database=self.__database) if not self.__connection else self.__connection
            return self.__connection
        except Error as e:
            raise RuntimeError("Not able to establish connection with this database.")

    def get_cursor(self):
        self.__cursor = self.__connection.cursor()
        return self.__cursor
