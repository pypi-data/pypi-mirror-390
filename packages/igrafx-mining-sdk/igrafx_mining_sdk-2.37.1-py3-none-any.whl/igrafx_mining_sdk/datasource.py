# MIT License, Copyright 2023 iGrafx
# https://github.com/igrafx/mining-python-sdk/blob/dev/LICENSE
import pandas
import jaydebeapi
from igrafx_mining_sdk.api_connector import APIConnector


class Datasource:
    """A Druid table that can be requested by the user"""
    def __init__(self, name: str, ds_type: str, api_connector: APIConnector):
        """Initialise a datasource

        :param name: the name of the datasource
        :param ds_type: the type of the datasource
        :param api_connector: an APIConnector object that can be used to send requests to the datasource
        """

        self.name = name
        self.type = ds_type
        self.api_connector = api_connector
        self._connection = None
        self._cursor = None
        self._columns = None
        self._closed = False

    @property
    def connection(self):
        """Returns a JDBC connection to Druid using Avatica."""
        if self._closed:
            return None
        if self._connection is None:
            self._connection = jaydebeapi.connect(
                self.api_connector.jdbc_driver_class,  # Avatica JDBC driver class
                self.api_connector.jdbc_url,  # JDBC URL for Avatica
                [self.api_connector.wg_id, self.api_connector.wg_key],  # User & Password
                self.api_connector.jdbc_driver_path  # Path to Avatica JDBC driver .jar file
            )
        return self._connection

    @property
    def cursor(self):
        """Returns the Jaydebeapi cursor on the datasource, after initializing it if it doesn't exist"""
        if self._closed:
            return None
        if self._cursor is None:
            self._cursor = self.connection.cursor()
        return self._cursor

    def request(self, sqlreq):
        """Sends an SQL request to the datasource and returns the results as a pandas Dataframe

        :param sqlreq: the SQL request to execute
        """
        cur = self.cursor
        if cur is None:
            raise Exception("Datasource cursor is not initialized. The datasource connection is probably closed.")
        self.cursor.execute(sqlreq)
        rows = self.cursor.fetchall()
        cols = [i[0] for i in self.cursor.description]
        return pandas.DataFrame(rows, columns=cols)

    def load_dataframe(self, load_limit=None):
        """Loads an SQL request and returns as a dataframe

        :param load_limit: Maximum number of rows to load
        """
        sqlreq = f'SELECT * FROM "{self.name}"'
        if load_limit is not None:
            sqlreq += f' LIMIT {load_limit}'
        return self.request(sqlreq)

    @property
    def columns(self):
        """Returns the columns of the datasource"""
        if self._columns is None:
            res = self.request(
                "SELECT COLUMN_NAME, ORDINAL_POSITION, DATA_TYPE "
                "FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = 'druid' "
                f"AND TABLE_NAME = '{self.name}' "
                "ORDER BY ORDINAL_POSITION"
            )
            self._columns = res["COLUMN_NAME"].to_list()
        return self._columns

    def close_ds_connection(self):
        """Closes the connection and the cursor when called"""
        if self._cursor is not None:
            try:
                self._cursor.close()
            except Exception as e:
                print(f"Error closing cursor: {e}")
            finally:
                self._cursor = None  # Ensure it's set to None

        if self._connection is not None:
            try:
                self._connection.close()
            except Exception as e:
                print(f"Error closing connection: {e}")
            finally:
                self._connection = None  # Ensure it's set to None
        self._closed = True
