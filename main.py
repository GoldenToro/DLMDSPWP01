import argparse
import logging

from fancy_logging import logger
from load_data_sets import load_dataset

def main():
    logger.debug("Start")
    logger.info("Test")
    load_dataset(overwrite=True,with_visualizing=False)


if __name__ == '__main__':

    main()
