from sqlalchemy import create_engine, MetaData, Table, Column, Float, select, inspect, text
import pandas as pd
import traceback
from fancy_logging import logger


class SqliteOperations:
    """
    Class to handle SQLite database operations.
    """

    def __init__(self, db_path):
        """
        Initialize the SqliteOperations with a database path.

        :param db_path: Path to the SQLite database file.
        """
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.metadata = MetaData()
        self.metadata.reflect(self.engine)
        self.logger = logger

    def get_data_from_table(self, table_name):
        """
        Retrieve data from a specified table.

        :param table_name: Name of the table to retrieve data from.
        :return: DataFrame containing the table data or None if an error occurs.
        """
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            stmt = select(table)

            with self.engine.connect() as conn:
                result = conn.execute(stmt)
                data = result.fetchall()

            df = pd.DataFrame(data, columns=[col.name for col in table.columns])
            return df

        except Exception as e:
            self.logger.warning(f"Could not get data from table '{table_name}': {e}")
            self.logger.debug(traceback.format_exc())
            return None

    def create_xy_table(self, table_name, column_names):
        """
        Create a table with specified column names.

        :param table_name: Name of the table to create.
        :param column_names: List of column names for the table.
        """
        try:
            y_columns = [Column(col, Float) for col in column_names]

            if table_name in self.metadata.tables:
                Table(table_name, self.metadata, extend_existing=True, *y_columns)
            else:
                Table(table_name, self.metadata, *y_columns)

            self.metadata.create_all(self.engine)
            self.logger.debug(f"Table '{table_name}' created successfully.")

        except Exception as e:
            self.logger.warning(f"Failed to create table '{table_name}': {e}")
            self.logger.debug(traceback.format_exc())

    def get_row_count(self, table_name):
        """
        Get the row count of a specified table.

        :param table_name: Name of the table to count rows in.
        :return: Integer count of rows.
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                row_count = result.scalar()
                return row_count
        except Exception as e:
            self.logger.warning(f"Could not get row count for table '{table_name}': {e}")
            self.logger.debug(traceback.format_exc())
        return None


    def fill_table(self, table_name, data):
        """
        Fill a table with data from a DataFrame.

        :param table_name: Name of the table to fill.
        :param data: DataFrame containing the data to fill the table with.
        """
        try:
            data = data.copy()
            self.logger.debug(f"Loaded {data.shape[1]} columns and {data.shape[0]} rows for {table_name}")

            if inspect(self.engine).has_table(table_name):
                self.drop_table(table_name)

            self.create_xy_table(table_name, data.columns)

            data.to_sql(table_name, con=self.engine, if_exists='append', index=False)
            self.logger.debug(f"Table '{table_name}' filled successfully.")

        except Exception as e:
            self.logger.warning(f"Failed to fill table '{table_name}': {e}")
            self.logger.debug(traceback.format_exc())


    def drop_table(self, table_name):
        """
        Drop a specified table from the database.

        :param table_name: Name of the table to drop.
        """
        try:
            if inspect(self.engine).has_table(table_name):
                table = Table(table_name, self.metadata, autoload_with=self.engine)
                table.drop(self.engine)
                self.logger.debug(f"Table '{table_name}' dropped successfully.")
            else:
                self.logger.warning(f"Table '{table_name}' does not exist.")
        except Exception as e:
            self.logger.warning(f"Could not drop table '{table_name}': {e}")
            self.logger.debug(traceback.format_exc())

