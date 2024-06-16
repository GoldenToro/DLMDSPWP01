import math
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import argparse
from io import StringIO

# Import the functions and classes from your script
from csv_processor import *
from visualize_functions import *
from sqlite_helper import *
from fancy_logging import *


class TestUtilityFunctions(unittest.TestCase):

    def test_str2bool(self):
        self.assertTrue(str2bool('yes'))
        self.assertTrue(str2bool('true'))
        self.assertTrue(str2bool('t'))
        self.assertTrue(str2bool('y'))
        self.assertTrue(str2bool('1'))
        self.assertFalse(str2bool('no'))
        self.assertFalse(str2bool('false'))
        self.assertFalse(str2bool('f'))
        self.assertFalse(str2bool('n'))
        self.assertFalse(str2bool('0'))
        with self.assertRaises(argparse.ArgumentTypeError):
            str2bool('invalid')

    @patch('csv_processor.pd.read_csv')
    def test_load_csv_data(self, mock_read_csv):
        # Mock the pandas read_csv function
        mock_read_csv.return_value = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
        result = load_csv_data('dummy_path.csv')
        self.assertIsNotNone(result)
        self.assertEqual(result.shape, (2, 2))

        # Test with read_csv raising an exception
        mock_read_csv.side_effect = Exception('Failed to read CSV')
        result = load_csv_data('dummy_path.csv')
        self.assertIsNone(result)

    def test_get_row(self):
        df = pd.DataFrame({'col1': [1, 2, 3], 'col2': ['a', 'b', 'c']})
        result = get_row(df, 'col1', 2)
        self.assertEqual(result.shape[0], 1)
        self.assertEqual(result.iloc[0]['col2'], 'b')

    def test_get_max_deviation(self):
        col1 = pd.Series([1, 2, 3])
        col2 = pd.Series([1, 3, 2])
        result = get_max_deviation(col1, col2)
        self.assertEqual(result, 1)


class TestAssignTestData(unittest.TestCase):

    @patch('csv_processor.get_row')
    def test_assign_test_data(self, mock_get_row):
        csv_content = StringIO("x,y\n1,2\n2,3\n3,4")
        ideal_data = pd.DataFrame({'x': [1, 2, 3], 'ideal1': [1.1, 2.1, 3.1], 'ideal2': [1.2, 2.2, 3.2]})
        ideal_functions = {'train1': {'ideal_function': 'ideal1', 'max_deviation': 0.2, 'max_deviation_factor_sqrt_two': 0.2 * math.sqrt(2)}}

        mock_get_row.side_effect = lambda df, col, val: df[df[col] == val]

        with patch('builtins.open', return_value=csv_content):
            result = assign_test_data('dummy_path.csv', ideal_data, ideal_functions)
            self.assertEqual(result.shape[0], 3)
            self.assertIn('Delta Y', result.columns)


class TestFindIdealFunction(unittest.TestCase):

    def test_find_ideal_function(self):
        training_data = pd.DataFrame({'x': [1.0, 2.0, 3.0], 'y1': [1.0, 2.0, 3.0]})
        ideal_data = pd.DataFrame({'x': [1.0, 2.0, 3.0], 'y1': [1.1, 2.1, 3.1], 'y2': [1.2, 2.2, 3.2]})
        result = find_ideal_function('y1', training_data[['x', 'y1']], ideal_data)
        self.assertEqual(result, 'y1')


class TestPlotManager(unittest.TestCase):
    def setUp(self):
        self.plot_manager = PlotManager()

    def test_initialization(self):
        self.assertEqual(self.plot_manager.screen_size_x, 3440)
        self.assertEqual(self.plot_manager.screen_size_y, 1365)
        self.assertEqual(self.plot_manager.num_plots_vertical, 2)
        self.assertEqual(self.plot_manager.num_plots_horizontal, 4)

    def test_position_figure(self):
        self.plot_manager.number_of_plots = 8
        self.plot_manager.position_figure()
        self.assertEqual(self.plot_manager.number_of_plots, 1)

    def test_load_xy_as_line_plot(self):
        data = pd.DataFrame({'x': [1, 2, 3, 4, 5], 'y': [2, 3, 4, 5, 6]})
        self.plot_manager.load_xy_as_line_plot(data, "Test Plot")
        self.assertEqual(self.plot_manager.number_of_plots, 1)

    def tearDown(self):
        # Clean up resources
        self.plot_manager.delete_plots()

class TestSqliteOperations(unittest.TestCase):
    def setUp(self):
        self.db_path = ':memory:'  # Use an in-memory SQLite database for testing
        self.db_ops = SqliteOperations(self.db_path)

        # Create a test table
        self.db_ops.create_xy_table('test_table', ['x', 'y'])
        self.db_ops.fill_table('test_table', pd.DataFrame({'x': [1, 2, 3], 'y': [4, 5, 6]}))

    def test_get_data_from_table(self):
        df = self.db_ops.get_data_from_table('test_table')
        self.assertIsNotNone(df)
        self.assertEqual(len(df), 3)

    def test_create_xy_table(self):
        self.db_ops.create_xy_table('new_table', ['x', 'y'])
        self.assertTrue(inspect(self.db_ops.engine).has_table('new_table'))

    def test_get_row_count(self):
        count = self.db_ops.get_row_count('test_table')
        self.assertEqual(count, 3)

    def test_fill_table(self):
        new_data = pd.DataFrame({'x': [7, 8, 9], 'y': [10, 11, 12]})
        self.db_ops.fill_table('test_table', new_data)
        count = self.db_ops.get_row_count('test_table')
        self.assertEqual(count, 3)  # Expecting 3 since the table is dropped and recreated before fill

    def test_drop_table(self):
        self.db_ops.drop_table('test_table')
        self.assertFalse(inspect(self.db_ops.engine).has_table('test_table'))


class TestLogger(unittest.TestCase):
    def setUp(self):
        self.logger = Logger("TestLogger", logging.DEBUG)

    def test_logger_level(self):
        self.assertEqual(self.logger.logger.level, logging.DEBUG)



if __name__ == '__main__':
    unittest.main()
