#!/usr/bin/env python3

"""
Read data from the Firefox browser and extract useful information.
OS: macOS-only
Version: 1.0.0
Python 3.13+
Date created: February 4th, 2025
Date modified: June 4th, 2025
"""

import logging

from logging.config import fileConfig

from src import argument_handler
from src import firefox_data
from src import info

fileConfig("logging.ini")
logger = logging.getLogger()


def evaluate_args(args) -> None:
    """
    Evaluates the provided arguments and calls the respective functions or handles
    logic based on the arguments. This includes fetching data or displaying
    version information based on the flags provided.

    :param args: The arguments are provided from the command-line interface. The
        object is expected to have properties `websites`, `output`, and `version`.

    :return: None
    """
    if args.websites:
        firefox_data.fetch_history_data(save=False)
    if args.output:
        firefox_data.fetch_history_data(save=True)
    if args.version:
        logger.debug("Displays the current version")
        info.show_version()


def main() -> None:
    """
    Entry point of the program.
    """
    args_handler = argument_handler.ArgumentHandler()
    args = args_handler.parse()

    evaluate_args(args)


if __name__ == "__main__":
    main()
