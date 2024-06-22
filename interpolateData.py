import os
from fancy_logging import logger

import pandas as pd
import numpy as np
import time

def ensure_dir_exists(directory):
    """
    Check if the specified directory exists, and create it if it does not.

    :param directory: Path of the directory to check and create.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def interpolate_data(df, factor=10):
    """
    Interpolate the data to create a larger dataset by the given factor.

    :param df: Original DataFrame with data to interpolate.
    :param factor: Factor by which to increase the dataset size.
    :return: DataFrame with interpolated data.
    """

    new_index = np.linspace(df.index.min(), df.index.max(), len(df.index) * factor)
    new_df = pd.DataFrame(index=new_index)

    for column in df.columns:
        new_df[column] = np.round(np.interp(new_index, df.index, df[column]),6)

    new_df.reset_index(drop=True, inplace=True)
    return new_df


def main(factor):

    measured_data = []

    for data_path in ['Dataset2/train.csv', 'Dataset2/test.csv', 'Dataset2/ideal.csv']:


        start_time = time.process_time()
        data = pd.read_csv(data_path, index_col='x')
        end_time = time.process_time()
        diff_load_time = end_time - start_time

        data = data.sort_index().reset_index()

        if data_path == "Dataset2/test.csv":

            # Generate the new x values3
            new_x = np.round(np.arange(-20.0, 20.0, 0.1),1)
            test_data = pd.DataFrame({'x': new_x})

            test_data['y'] = np.interp(test_data['x'], data.index, data['y'])


            data = test_data

        lines = data.shape[0]
        columns = data.shape[1]

        logger.debug(f"Interpolating {data_path}: Col: {columns}, Lin: {lines}, Factor: {factor} = {columns * lines * factor} entries")

        start_time = time.process_time()
        larger_data = interpolate_data(df=data, factor=factor)
        end_time = time.process_time()
        diff_ip_time = end_time - start_time

        new_folder = data_path.split('/', 1)[0] + "_" + str(factor)
        new_file = data_path.split('/', 1)[1]

        ensure_dir_exists(new_folder)

        new_path = os.path.join(new_folder, new_file)
        start_time = time.process_time()

        larger_data.to_csv(new_path, index=False)
        end_time = time.process_time()
        diff_save_time = end_time - start_time

        measured_data.append({
            'function': 'load CSV File',
            'file': new_file,
            'time': diff_load_time
        })
        measured_data.append({
            'function': 'interpolate Data',
            'file': new_file,
            'time': diff_ip_time
        })
        measured_data.append({
            'function': 'save CSV File',
            'file': new_file,
            'time': diff_save_time
        })

    return pd.DataFrame(measured_data)
