from fancy_logging import logger
import os, traceback
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, inspect
import pandas as pd
import argparse

from helper_functions import *
from visualize_functions import load_xy_as_line_plot, show_plots, FULL_SCREEN

def create_xy_table(engine, table_name, count_y):
    try:
        metadata = MetaData()
        y_columns = [Column(f"y{col}", Float) for col in range(1,count_y)]
        data_table = Table(table_name,
                           metadata,
                           Column('x', Float, nullable=False),
                           *y_columns
                           )
        metadata.create_all(engine)
        logger.debug(f"Table '{table_name}' created successfully.")

    except Exception as e:
        logger.warning(f"{e}")

# TODO UNIT Test, same number of columns , rows in table after filling
def fill_table(engine, table_name, data_path):
    try:
        data = load_csv_data(data_path)
        columns_count = data.shape[1]
        logger.debug(f"Loaded {columns_count} Columns for {table_name}")

        if not inspect(engine).has_table(table_name):
            create_xy_table(engine, table_name, columns_count)

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

def load_dataset(csv_path="Dataset2", db_path_to_file="db.sqlite3", overwrite=False, with_visualizing=True):

    logger.debug(f"CSV-Path: {csv_path}")
    logger.debug(f"DB-Path: {db_path_to_file}")
    logger.debug(f"Overwrite?: {overwrite}")

    db_exists = os.path.exists(db_path_to_file)
    logger.info("Database already exists" if db_exists else "Creating new Database")

    if db_exists and (not isinstance(overwrite, bool) and not overwrite):
        logger.info("Do you want to overwrite the existing database? (yes/no): ")
        while (not isinstance(overwrite, bool) and overwrite is None):
            user_input = input().strip().lower()
            try:
                overwrite = str2bool(user_input)
            except Exception as error:
                logger.warning(error)

    # Create SQLAlchemy engine
    engine = create_engine(f'sqlite:///{db_path_to_file}')

    if db_exists and not overwrite:
        logger.warning("Database already exists, but should not be overwritten, skipping Data Import")

    else:

        if db_exists:
            drop_table(engine, "train")
            drop_table(engine, "ideal")

        fill_table(engine, "train", os.path.join(csv_path, "train.csv"))
        fill_table(engine, "ideal", os.path.join(csv_path, "ideal.csv"))

        logger.info("Database created and filled with training and ideal data")


    if with_visualizing:
        data = get_data_from_table(engine, "train")
        load_xy_as_line_plot(data, "Original Training-Data")
        data = get_data_from_table(engine, "ideal")
        load_xy_as_line_plot(data, "Original Ideal-Data")

        show_plots()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load CSV data into SQLite database.')
    parser.add_argument('--csv_path', type=str, default="Dataset2", help='Path to the CSV files.')
    parser.add_argument('--db_path_to_file', type=str, default="db.sqlite3", help='Path to the SQLite database file.')
    parser.add_argument('--overwrite', type=str2bool, default=None, help='Overwrite the existing database.')
    #TODO Default auf False setzen
    parser.add_argument('--visualize_import', type=str2bool, default=True, help='Show Data after Import')

    args = parser.parse_args()

    load_dataset(args.csv_path, args.db_path_to_file, args.overwrite, args.visualize_import)
