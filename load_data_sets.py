from fancy_logging import logger
import os
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, Float, inspect
import pandas as pd
import argparse

from helper_functions import *
from visualize_functions import load_xy_as_line_plot, show_plots


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
        logger.warning("Database already exists and should not be overwritten. Skipping data import.")

    else:

        if db_exists:
            drop_table(engine, "train")
            drop_table(engine, "ideal")

        fill_table(engine, "train", load_csv_data(os.path.join(csv_path, "train.csv")))
        fill_table(engine, "ideal", load_csv_data(os.path.join(csv_path, "ideal.csv")))

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
