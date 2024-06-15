import os
import csv
import argparse
import pandas as pd
from sqlalchemy import create_engine

from fancy_logging import logger
from load_data_sets import load_dataset
from helper_functions import get_data_from_table, fill_table, drop_table, set_value, get_value
from visualize_functions import show_plots, load_xy_as_line_plot, FULL_SCREEN


# TODO Unit Test Calculating
def get_column_with_least_deviation(data, row, max_deviations):
    x = float(row[0])
    y = float(row[1])

    # logger.debug(f"Searching for x:{x}, y:{y}")

    # Extract the specific row (excluding the first column)
    matching_rows = data[data['x'] == x]

    index_of_matching_row = matching_rows.index.tolist()[0]

    # logger.debug(f"Matching row: {str(matching_rows)}")

    # Drop the first column from the matching rows
    if not matching_rows.empty:
        matching_rows = matching_rows.drop(columns=[data.columns[0]])

    # Calculate the absolute deviation from the specific value
    deviations = (matching_rows - y).abs()

    # Find the column with the smallest deviation
    min_deviation_column_name = deviations.iloc[0].idxmin()

    # Deviation between column and y
    deviation = deviations[min_deviation_column_name].iloc[0]

    # check if deviation is larger than largest deviation between training dataset and ideal function by more than factor sqrt 2
    sqrt_of_two = 2 ** 0.5
    max_deviation = max_deviations[min_deviation_column_name] * sqrt_of_two

    if deviation > max_deviation:
        deviation = None
        min_deviation_column_name = None


    return {
        'x': x,
        'y': y,
        'Delta Y': deviation,
        'No. of ideal func': min_deviation_column_name
    }


# TODO Unit Test Calculating
def get_max_deviation(col1, col2):
    # Calculate the absolute deviation between the two columns
    deviation = (col1 - col2).abs()

    # Return the maximum deviation
    max_dev = deviation.max()

    return max_dev


def assign_test_data(csv_path, ideal_functions_data, max_deviation):
    test_data = pd.DataFrame()

    # would load it like the other csv, but it has to be loaded "line-by-line"
    # test_data = load_csv_data(os.path.join(csv_path, "test.csv"))

    with open(csv_path, mode='r', newline='') as file:
        csv_reader = csv.reader(file)

        # Skip the first row (header)
        next(csv_reader)

        # Iterate over each row in the CSV file
        for index, row in enumerate(csv_reader):
            deviation_data = get_column_with_least_deviation(ideal_functions_data, row, max_deviation)


            deviation_data = pd.DataFrame(deviation_data, index=[index])
            deviation_data = deviation_data.dropna(axis=1, how='all')

            test_data = pd.concat([test_data, deviation_data])

    return test_data


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
            least_square_data[col] = (merged_data[training_function + "_train"] - merged_data[col]) ** 2

    logger.debug("Calculated-Data: " + str(least_square_data.shape))

    # Take all columns from least_square_data beside x and calculate the sum
    column_sums = least_square_data[(col for col in least_square_data.columns if col != 'x')].sum()

    # Find column name with the smallest sum
    min_sum_column = column_sums.idxmin()

    return min_sum_column


def main(csv_path="Dataset2", db_path_to_file="db.sqlite3", with_visualizing=False):
    logger.info("Load Dataset into SQLite Database")
    load_dataset(csv_path="Dataset2", overwrite=True, with_visualizing=False)

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

    max_deviations = {}
    ideal_functions_data = pd.DataFrame(index=training_data.index)
    ideal_functions_data['x'] = training_data['x']

    for training_function in ideal_functions:
        data = pd.DataFrame(index=training_data.index)
        data['x'] = training_data['x']

        data[training_function + "_train"] = training_data[training_function]
        data[ideal_functions[training_function] + "_ideal"] = ideal_data[ideal_functions[training_function]]

        ideal_functions_data[ideal_functions[training_function]] = ideal_data[ideal_functions[training_function]]
        max_deviations[ideal_functions[training_function]] = get_max_deviation(training_data[training_function], ideal_data[ideal_functions[training_function]])

        if with_visualizing:
            load_xy_as_line_plot(data, f"Training Function {training_function} with Ideal Function {ideal_functions[training_function]}")

    if with_visualizing:
        show_plots()

    logger.debug("Maximum Deviation: " + str(max_deviations))
    test_data = assign_test_data(os.path.join(csv_path, 'test.csv'), ideal_functions_data, max_deviations)

    test_data  = test_data.reset_index()
    ideal_functions_data  = ideal_functions_data.reset_index()


    #TODO Same Logic as loaddataset
    drop_table(engine, "test")


    # TODO var
    if True:

        visualize_data = ideal_functions_data.copy().drop(columns=['index'])
        colors = ['orchid', 'cyan', 'orange', 'yellow', 'orchid', 'orange']

        style = {}
        i = 0
        print("visualize_data:")
        print(visualize_data)
        for col in visualize_data.columns:
            print(f"{col} : {i}")
            style[col] = {
                'linewidth': 15,
                'alpha': 0.3,
                'color': colors[i]
            }
            i += 1


        style['y'] = {
            'linewidth': 10,
            'alpha': 0.3,
            'color': 'black'
        }


        visualize_data = pd.merge(visualize_data, test_data[['y','x']], on='x')

        style['y_points'] = {
            'type': 'scatter',
            'linewidth': 5,
            'alpha': 0.5,
            'color': 'black'
        }

        visualize_data = pd.merge(visualize_data, test_data[['y','x']], on='x', suffixes=('', '_points'))

        scatter_data = test_data.copy().drop(columns=['Delta Y', 'y'])

        for col in ideal_functions_data.drop(columns=['x']).columns:
            scatter_data[col] = None


        for index, row in scatter_data.iterrows():
            x = row['x']
            func = row['No. of ideal func']

            if not pd.isna(func):
                value = get_value(ideal_functions_data, x, 'x', func)
                set_value(scatter_data, x, 'x', func, value)

        scatter_data = scatter_data.drop(columns=['No. of ideal func','index'])

        visualize_data = pd.merge(visualize_data, scatter_data, on='x', suffixes=('', '_mapped'))

        i = 0

        for col in scatter_data.columns:
            style[col+'_mapped'] = {
                'type': 'scatter',
                'linewidth': 5,
                'alpha': 1,
                'color': colors[i]
            }
            i += 1


        load_xy_as_line_plot(
            data=visualize_data,
            name="Test Data mapped to Ideal Functions",
            position=FULL_SCREEN,
            styles=style)

        show_plots()


if __name__ == '__main__':
    main()
