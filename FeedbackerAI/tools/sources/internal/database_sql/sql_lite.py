import sqlite3
from innovation.FeedbackerAi.tools.sources.internal.database_sql.sqldb import SQLDb
from innovation.FeedbackerAi.tools.local.utilities import Utility
from typing import Optional, Dict, Any

class SQLite(SQLDb):
    def __init__(self, config, db_path, to_debug):
        super().__init__(config, "sqlite3", to_debug)
        self.conn = sqlite3.connect(f"{db_path}{self.config['storage']}")
        self.cursor = self.conn.cursor()

    def create(self, table_name, columns):
        """
        Create a table in the database.

        Args:
        table_name (str): Name of the table.
        columns (dict): Dictionary of column names and data types.
        """
        column_str = ', '.join(f'{key} {value}' for key, value in columns.items())
        query = f'CREATE TABLE {table_name} ({column_str})'
        self.cursor.execute(query)
        self.conn.commit()

    def read(self, table_name, column=None, condition=None):
        """
        Read data from a table in the database.

        Args:
        table_name (str): Name of the table.
        column (str, optional): Name of the column to select. Defaults to all columns.
        condition (str, optional): SQL condition to filter results. Defaults to no condition.

        Returns:
        list: List of tuples containing the data.
        """
        if column:
            query = f'SELECT {column} FROM {table_name}'
        else:
            query = f'SELECT * FROM {table_name}'
        if condition:
            query += f' WHERE {condition}'
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def update(self, table_name, column, value, condition):
        """
        Update data in a table in the database.

        Args:
        table_name (str): Name of the table.
        column (str): Name of the column to update.
        value (str): New value for the column.
        condition (str): SQL condition to filter which rows to update.
        """
        query = f'UPDATE {table_name} SET {column} =? WHERE {condition}'
        self.cursor.execute(query, (value,))
        self.conn.commit()

    def delete(self, table_name, condition):
        """
        Delete data from a table in the database.

        Args:
        table_name (str): Name of the table.
        condition (str): SQL condition to filter which rows to delete.
        """
        query = f'DELETE FROM {table_name} WHERE {condition}'
        self.cursor.execute(query)
        self.conn.commit()
