#!/usr/bin/env python3

"""
Process user input
Python 3.13+
Date created: February 5th, 2025
Date modified: June 4th, 2025
"""

import argparse
import logging

from logging.config import fileConfig
from argparse import Namespace

fileConfig("logging.ini")
logger = logging.getLogger()


class ArgumentHandler:
    def __init__(self) -> None:
        """
        Initialize a class instance with an argparse.ArgumentParser for reading browser
        history files and set up the required arguments.
        """
        self.parser: argparse.ArgumentParser = argparse.ArgumentParser(
            description="A tool for reading the browser's history file."
        )
        self._setup_arguments()

    def _setup_arguments(self):
        """
        Define all arguments here
        """
        self.parser.add_argument(
            "-w",
            "--websites",
            required=False,
            help="Show visited websites",
            action="store_true",
        )

        self.parser.add_argument(
            "-o", "--output", help="Create a text file", action="store_true"
        )

        self.parser.add_argument(
            "-v", "--version", help="Displays the current version", action="store_true"
        )

    def parse(self) -> Namespace:
        """
        Parses command-line arguments provided to the program using the defined parser and
        returns the resulting Namespace object. This method processes the arguments
        based on how the parser was configured previously and encapsulates them into a
        Namespace object.

        :return: The Namespace object containing the parsed command-line arguments as attributes
        :rtype: Namespace
        """
        logger.debug("Parsing command-line arguments")
        return self.parser.parse_args()
