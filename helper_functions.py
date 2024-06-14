import logging
import traceback

import pandas as pd
from sqlalchemy import MetaData, Table, select
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