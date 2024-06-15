import argparse
import pandas as pd
from sqlalchemy import create_engine

from fancy_logging import logger
from helper_functions import get_data_from_table
from load_data_sets import load_dataset
from visualize_functions import show_plots, load_xy_as_line_plot


# TODO Unit Test Calculating
def find_ideal_function(engine, training_function):
    logger.debug(f"Searching Ideal Function for {training_function}")
    training_data = get_data_from_table(engine, "train")
    ideal_data = get_data_from_table(engine, "ideal")

    logger.debug("Training-Data: " + str(training_data.shape))
    logger.debug("Ideal-Data: " + str(ideal_data.shape))

    # Create an empty DataFrame with the same index and columns as ideal_data
    least_square_data = pd.DataFrame(index=ideal_data.index, columns=ideal_data.columns)
    least_square_data['x'] = ideal_data['x']

    # Merge datasets on 'x' to align them if necessary
    merged_data = pd.merge(training_data, ideal_data, on='x', suffixes=('_train', ''))

    for col in ideal_data.columns:
        if col != 'x':
            least_square_data[col] = (merged_data[training_function+"_train"] - merged_data[col]) ** 2

    logger.debug("Calculated-Data: " + str(least_square_data.shape))

    # Take all columns from least_square_data beside x and calculate the sum
    column_sums = least_square_data[(col for col in least_square_data.columns if col != 'x')].sum()

    # Find column name with the smallest sum
    min_sum_column = column_sums.idxmin()

    return min_sum_column


def main(db_path_to_file="db.sqlite3", with_visualizing=True):
    logger.info("Load Dataset into SQLite Database")
    load_dataset(overwrite=False, with_visualizing=with_visualizing)

    engine = create_engine(f'sqlite:///{db_path_to_file}')

    logger.info("Searching Ideal Functions")
    ideal_functions = {}

    training_data = get_data_from_table(engine, "train")
    ideal_data = get_data_from_table(engine, "ideal")
    for col in training_data:
        if col != 'x':
            ideal_function = find_ideal_function(engine, col)
            ideal_functions[col] = ideal_function

    logger.info("Ideal Functions: " + str(ideal_functions))

    if with_visualizing:
        for training_function in ideal_functions:
            data = pd.DataFrame(index=training_data.index)
            data['x'] = training_data['x']
            data[training_function+"_train"] = training_data[training_function]
            data[ideal_functions[training_function]+"_ideal"] = ideal_data[ideal_functions[training_function]]

            print(data)
            load_xy_as_line_plot(data, f"Training Function {training_function} with Ideal Function {ideal_functions[training_function]}")

        show_plots()



if __name__ == '__main__':
    main()
