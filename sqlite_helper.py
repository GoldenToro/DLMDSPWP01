import traceback
import pandas as pd
from fancy_logging import logger
from sqlalchemy import MetaData, select, Table, Column, Float, inspect, create_engine, text

class SqliteOperations:
    def __init__(self, db_path):
        self.engine = create_engine(f'sqlite:///{db_path}')
        self.metadata = MetaData()
        self.metadata.reflect(self.engine)
        self.logger = logger

    def get_data_from_table(self, table_name):
        try:
            table = Table(table_name, self.metadata, autoload_with=self.engine)
            stmt = select(table)

            with self.engine.connect() as conn:
                result = conn.execute(stmt)
                data = result.fetchall()

            df = pd.DataFrame(data, columns=[col.name for col in table.columns])
            return df

        # TODO Make better exceptions
        except Exception as e:
            self.logger.warning(f"Could not get data from table '{table_name}': {e}")
            return None

    def create_xy_table(self, table_name, column_names):
        try:
            y_columns = [Column(col, Float) for col in column_names]

            # Check if table already exists
            if table_name in self.metadata.tables:
                # Use extend_existing=True to modify existing table definition
                Table(table_name, self.metadata, extend_existing=True, *y_columns)
            else:
                # Create the table in the metadata
                Table(table_name, self.metadata, *y_columns)

            self.metadata.create_all(self.engine)
            self.logger.debug(f"Table '{table_name}' created successfully.")

        except Exception as e:
            self.logger.warning(f"Failed to create table '{table_name}': {e}")
            self.logger.debug(traceback.format_exc())

    def get_row_count(self, table_name):

        with self.engine.connect() as conn:
            result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
            row_count = result.scalar()

            return row_count

    def fill_table(self, table_name, data):
        try:
            data = data.copy()
            self.logger.debug(f"Loaded {data.shape[1]} columns and {data.shape[0]} rows for {table_name}")

            if inspect(self.engine).has_table(table_name):
                self.drop_table(table_name)

            self.create_xy_table(table_name, data.columns)


            data.set_index('x', inplace=True)
            data.to_sql(table_name, con=self.engine, if_exists='append', index=True)
            self.logger.debug(f"Table '{table_name}' filled successfully.")

        except Exception as e:
            self.logger.warning(f"Failed to fill table '{table_name}': {e}")
            self.logger.debug(traceback.format_exc())

    def drop_table(self, table_name):
        try:
            if inspect(self.engine).has_table(table_name):
                table = Table(table_name, self.metadata, autoload_with=self.engine)
                table.drop(self.engine)
                self.logger.debug(f"Table '{table_name}' dropped successfully.")
            else:
                self.logger.warning(f"Table '{table_name}' does not exist.")

        except Exception as e:
            self.logger.warning(f"Could not drop table '{table_name}'")
            self.logger.debug(traceback.format_exc())

