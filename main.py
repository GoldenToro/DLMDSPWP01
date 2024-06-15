import argparse
import logging

from fancy_logging import logger
from load_data_sets import load_dataset

def main():
    logger.info("Load Dataset into SQLite Database")
    load_dataset(overwrite=False, with_visualizing=True)






if __name__ == '__main__':
    main()