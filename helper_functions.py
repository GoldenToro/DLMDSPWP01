import traceback
import pandas as pd
from sqlalchemy import MetaData, select, Table, Column, Integer, Float, inspect
from fancy_logging import logger
import argparse


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def load_csv_data(csv_file):
    try:
        # Load CSV data into pandas DataFrame
        data = pd.read_csv(csv_file)
        return data
    except Exception as e:
        print(f"Error loading CSV file: {e}")
        return None


def get_data_from_table(engine, table_name):
    try:
        # Create a MetaData instance
        metadata = MetaData()

        # Reflect the table from the database
        table = Table(table_name, metadata, autoload_with=engine)

        # Create a select statement to query the table
        stmt = select(table)

        # Execute the statement and fetch the result
        with engine.connect() as conn:
            result = conn.execute(stmt)
            data = result.fetchall()

        # Convert the result to a pandas DataFrame
        df = pd.DataFrame(data, columns=[col.name for col in table.columns])

        return df

    except Exception as e:
        logger.warning(f"Could not get Data from Table {table_name}: {e}")
        return None


def create_xy_table(engine, table_name, column_names):
    try:
        metadata = MetaData()
        y_columns = [Column(f"{col}", Float) for col in column_names]
        data_table = Table(table_name,
                           metadata,
                           *y_columns
                           )
        metadata.create_all(engine)
        logger.debug(f"Table '{table_name}' created successfully.")

    except Exception as e:
        logger.warning(f"{e} : {traceback.format_exc()}")


# TODO UNIT Test, same number of columns , rows in table after filling
def fill_table(engine, table_name, data):
    try:
        data = data.copy()
        columns_count = data.shape[1]
        logger.debug(f"Loaded {columns_count} Columns for {table_name}")

        if not inspect(engine).has_table(table_name):
            create_xy_table(engine, table_name, data.columns)

        # Write data to SQLite table, using 'x' as index
        data.set_index('x', inplace=True)
        data.to_sql(table_name, con=engine, if_exists='append', index=True)
        logger.debug(f"Table '{table_name}' filled successfully.")

    except Exception as e:
        logger.warning(f"{e}\n{traceback.format_exc()}")


def drop_table(engine, table_name):
    try:
        metadata = MetaData()
        if inspect(engine).has_table(table_name):
            data_table = Table(table_name, metadata, autoload_with=engine)
            data_table.drop(engine)
        logger.debug(f"Table '{table_name}' dropped successfully.")

    except Exception as e:
        logger.warning(f"Could not drop Table '{table_name}'. {e}")


def get_value(df, search_value, search_column_name, column_name):
    """
    Get the value of a specific cell in a DataFrame.

    Parameters:
    - df: Pandas DataFrame
    - search_value: Value to search for in the 'x' column
    - column_name: Name of the column from which to retrieve the value

    Returns:
    - Value found in the specified cell
    """
    try:
        # Find the index of the row where 'x' column matches search_value
        idx = df.index[df[search_column_name] == search_value].tolist()[0]
        # Get the value from the specified column and row
        return df.at[idx, column_name]
    except IndexError:
        print(f"Error: Value '{search_value}' not found in column '{search_column_name}'.")


def set_value(df, search_value, search_column_name, column_name, new_value):
    """
    Set the value of a specific cell in a DataFrame.

    Parameters:
    - df: Pandas DataFrame
    - search_value: Value to search for in the 'x' column
    - column_name: Name of the column where the value will be set
    - new_value: New value to set in the cell

    Returns:
    - None (modifies df in place)
    """
    try:
        # Find the index of the row where 'x' column matches search_value
        idx = df.index[df[search_column_name] == search_value].tolist()[0]
        # Set the value in the specified column and row
        df.at[idx, column_name] = new_value
    except IndexError:
        print(f"Error: Value '{search_value}' not found in column '{search_column_name}'.")
