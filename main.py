from math import sqrt
import os
import csv
import argparse
import pandas as pd

from fancy_logging import logger
from sqlite_helper import SqliteOperations
from visualize_functions import PlotManager, FULL_SCREEN

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


def load_dataset(db, csv_path, with_visualizing):
    logger.debug(f"CSV-Path: {csv_path}")
    logger.debug(f"Visualize?: {with_visualizing}")

    db.fill_table("train", load_csv_data(os.path.join(csv_path, "train.csv")))
    db.fill_table("ideal", load_csv_data(os.path.join(csv_path, "ideal.csv")))

    logger.info("Database created and filled with training and ideal data")

    if with_visualizing:
        plotmanager = PlotManager()

        data = db.get_data_from_table("train")
        plotmanager.load_xy_as_line_plot(data, "Original Training-Data")

        data = db.get_data_from_table("ideal")
        plotmanager.load_xy_as_line_plot(data, "Original Ideal-Data")

        plotmanager.show_plots()


def get_row(dataframe, column_name, value):
    """
    Get rows from a DataFrame where a specific column has a specific value.

    Args:
    - dataframe (pd.DataFrame): Input DataFrame to filter rows from.
    - column_name (str): Name of the column to check for the specific value.
    - value: Specific value to filter rows by.

    Returns:
    - pd.DataFrame: DataFrame containing all rows where the specified column has the specified value.
    """
    return dataframe[dataframe[column_name] == value]


# TODO Unit Test Calculating
def get_max_deviation(col1, col2):
    # Calculate the absolute deviation between the two columns
    deviation = (col1 - col2).abs()

    # Return the maximum deviation
    max_dev = deviation.max()

    return max_dev


def assign_test_data(csv_path, ideal_data, ideal_functions):
    test_data = pd.DataFrame()

    # get every ideal function that was mapped to a training function
    ideal_data = ideal_data[['x', *[training_function['ideal_function'] for training_function in ideal_functions.values()]]].copy()

    # would load it like the other csv-files, but it has to be loaded "line-by-line"
    # test_data = load_csv_data(os.path.join(csv_path, "test.csv"))

    with open(csv_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)

        # Skip the first row (header)
        next(csv_reader)

        # Iterate over each row in the CSV file
        for index, row in enumerate(csv_reader):
            row_x = float(row[0])
            row_y = float(row[1])

            ideal_data_row = get_row(ideal_data, 'x', row_x)
            if len(ideal_data_row) != 1:
                raise Exception

            deviations = {col: abs(ideal_data_row.iloc[0][col] - row_y) for col in ideal_data_row if col != 'x'}

            min_deviation_function = min(deviations, key=deviations.get)
            min_deviation_value = deviations[min_deviation_function]

            # check if Deviation is higher than max Deviation factor sqrt 2
            max_deviation = next((value['max_deviation_factor_sqrt_two'] for key, value in ideal_functions.items() if value['ideal_function'] == min_deviation_function), None)
            if min_deviation_value > max_deviation:
                min_deviation_function = None
                min_deviation_value = None
                logger.debug(f"For {row_x} with Value y: {row_y} no Min Deviation found")

            else:
                logger.debug(f"For {row_x} with Value y: {row_y} found Min Deviation with Function: {min_deviation_function}: {min_deviation_value}")

            row_data = {
                'x': [row_x],
                'y': [row_y],
                'Delta Y': min_deviation_value,
                'No. of ideal func': min_deviation_function,
            }

            if min_deviation_function:
                row_data['y_point_mapped'] = row_y
                row_data['y_point_not_found'] = None
            else:
                row_data['y_point_mapped'] = None
                row_data['y_point_not_found'] = row_y

            test_data = pd.concat([test_data, pd.DataFrame(row_data).set_index('x')])

    test_data = test_data.sort_index()
    test_data = test_data.reset_index()

    return test_data


# TODO Unit Test Calculating
def find_ideal_function(training_function_name, training_function, ideal_data):
    logger.debug(f"Searching Ideal Function for {training_function.columns.tolist()}")

    # Merge datasets on 'x' to align them if necessary
    merged_data = pd.merge(training_function, ideal_data, on='x', suffixes=('_train', ''))
    merged_training_function_name = training_function_name + '_train'

    # Create an empty DataFrame to store the results
    results = pd.DataFrame({'x': merged_data['x']})

    # Create a dictionary to store the sum of squared deviations for each function
    squared_deviation_sums = {}

    # Iterate over each y(n) column in df2
    for col in ideal_data.columns:
        if col != 'x':
            # Calculate the squared deviation
            squared_deviation = (merged_data[merged_training_function_name] - merged_data[col]) ** 2
            # Calculate the sum of squared deviations, ignoring NaN values
            squared_deviation_sums[col] = squared_deviation.sum(skipna=True)

    min_function = min(squared_deviation_sums, key=squared_deviation_sums.get)

    return min_function


def main(csv_path, db_path_to_file, overwrite=None, with_visualizing_steps=False, with_visualizing_result=False):
    logger.info("Starting Program")

    logger.info("Checking Database")
    db_exists = os.path.exists(db_path_to_file)
    logger.info("Database already exists" if db_exists else "Creating new Database")

    if db_exists and (not isinstance(overwrite, bool)):
        logger.info("Do you want to overwrite the existing database? (yes/no): ")
        while (not isinstance(overwrite, bool) and overwrite is None):
            user_input = input().strip().lower()
            try:
                overwrite = str2bool(user_input)
            except Exception as error:
                logger.warning(error)

    db = SqliteOperations(db_path_to_file)
    plotmanager = PlotManager()

    # when database does not exist, or should be overwritten, load dataset, else use existing database
    if not db_exists or overwrite:

        if db_exists:
            logger.warning("Database gets overwritten.")

        load_dataset(db=db, csv_path=csv_path, with_visualizing=with_visualizing_steps)

    else:
        logger.warning("Database already exists and should not be overwritten. Skipping data import.")

    # Loading Data from Database
    training_data = db.get_data_from_table("train")
    ideal_data = db.get_data_from_table("ideal")

    logger.info("Searching Ideal Functions")
    ideal_functions = {}
    for col in training_data:
        if col != 'x':
            min_function = find_ideal_function(col, training_data[['x', col]], ideal_data)
            max_deviation = get_max_deviation(training_data[col], ideal_data[min_function])

            ideal_functions[col] = {
                'ideal_function': min_function,
                'max_deviation': max_deviation,
                'max_deviation_factor_sqrt_two': max_deviation * sqrt(2)
            }

    logger.info("Ideal Functions: " + str(ideal_functions))

    # Visualize found ideal and training data
    if with_visualizing_steps:

        for training_function in ideal_functions:
            # get training and ideal function data
            training_function_data = training_data[['x', training_function]]
            ideal_function_data = ideal_data[['x', ideal_functions[training_function]['ideal_function']]]

            # Rename columns with suffixes
            training_function_data = training_function_data.rename(columns={col: col + '_train' for col in training_function_data.columns if col != 'x'})
            ideal_function_data = ideal_function_data.rename(columns={col: col + '_ideal' for col in ideal_function_data.columns if col != 'x'})

            data = pd.merge(training_function_data, ideal_function_data, on='x')

            plotmanager.load_xy_as_line_plot(data, f"Training Function {training_function} with Ideal Function {ideal_functions[training_function]['ideal_function']}")

        plotmanager.show_plots()

    test_data = assign_test_data(csv_path=os.path.join(csv_path, 'test.csv'), ideal_data=ideal_data, ideal_functions=ideal_functions)

    points_unassigned = test_data['No. of ideal func'].isna().sum()
    points_assigned = test_data['No. of ideal func'].notna().sum()
    logger.info(f"Results for Test-Data: \nPoints Assigned: {points_assigned}\nPoints Unassigned: {points_unassigned}\n")

    if not db_exists or overwrite:
        db.drop_table("test")
        db.fill_table("test", test_data.drop(columns=['y_point_mapped', 'y_point_not_found']))
        logger.info(f"Database filled with test data")
    else:
        logger.info(f"Not allowed to overwrite Database, set --overwrite to True for overwriting")

    if with_visualizing_steps or with_visualizing_result:

        logger.info("Showing Results")
        style = {}

        visualize_data = test_data.drop(columns=['Delta Y', 'No. of ideal func'])

        style['y'] = {
            'linewidth': 3,
            'alpha': 0.5,
            'color': 'black'
        }

        style['y_point_mapped'] = {
            'type': 'scatter',
            'linewidth': 3,
            'alpha': 1,
            'color': 'green'
        }

        style['y_point_not_found'] = {
            'type': 'scatter',
            'linewidth': 3,
            'alpha': 1,
            'color': 'red'
        }

        ideal_data = ideal_data[['x', *[training_function['ideal_function'] for training_function in ideal_functions.values()]]].copy()
        visualize_data = pd.merge(visualize_data, ideal_data, on='x')

        i = 0
        for col in ideal_data.columns:
            style[col] = {
                'linewidth': 10,
                'alpha': 0.3
            }

            i += 1

        text_functions = "Train;Ideal"
        for train_function in ideal_functions:
            text_functions += f"\n{train_function};{ideal_functions[train_function]['ideal_function']}"

        plotmanager.load_xy_as_line_plot(
            data=visualize_data,
            name="Test Data mapped to Ideal Functions",
            position=FULL_SCREEN,
            styles=style,
            text=f'''
INFO:\nThis Graph only shows the ideal function 
for each training function, which are:
\n{text_functions}\n
and the test function y. The red and
green points show the x,y values 
that could or couldn't be mapped. 
'''
        )

        plotmanager.show_plots()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load CSV data into SQLite database.')
    parser.add_argument('-csv', '--csv_path', type=str, default='Dataset2', help='Path to the CSV files.')
    parser.add_argument('-db', '--db_path_to_file', type=str, default='db.sqlite3', help='Path to the SQLite database file.')
    parser.add_argument('-o', '--overwrite', action='store_true', default=None, help='Overwrite the existing database if it already exists')
    parser.add_argument('-v', '--visualize_import', action='store_true', default=False, help='Visualize every important step')
    parser.add_argument('-e', '--visualize_result', action='store_true', default=False, help='Visualize Only End-Results')

    args = parser.parse_args()

    main(args.csv_path, args.db_path_to_file, args.overwrite, args.visualize_import, args.visualize_result)
