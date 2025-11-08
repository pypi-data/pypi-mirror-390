#!/usr/bin/env python3

"""
Common functions
Version: 1.0.0
Python 3.13+
Date created: February 7th, 2025
Date modified: October 20th, 2025
"""

import logging
import os
import platform
import shutil
import sqlite3
import sys
from datetime import datetime as dt
from logging.config import fileConfig

# Add logger config
fileConfig("logging.ini")
logger = logging.getLogger()


def fetch_data(db, command):
    """
    Send queries to the sqlite database and return the result.
    :param db: The sqlite database
    :param command: The SQL commands
    :return: The data from the sqlite database
    """
    logger.debug(f"Fetching data from {db}")
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(command)
        return cur.fetchall()
    except Exception as e:
        sys.exit(
            f"Error reading the database: {e}\nPlease close the Firefox browser and try again."
        )


def system_info() -> str | None:
    """
    Determines the operating system of the host machine and provides the system identity. Depending on the system type, it returns the name of the operating system (e.g., macOS, Linux) or a combination of the system name and version (e.g., Windows 10).

    :return: The name or identifier of the operating system.
    :rtype: str | None
    """
    if platform.system() == "Darwin":
        return "macOS"
    elif platform.system() == "Linux":
        return "Linux"
    elif platform.system() == "Windows":
        version = platform.system() + " " + platform.release()
        return version
    return None


def convert_epoch(timestamp):
    """
    Convert epoch to human-readable date
    :param timestamp: The epoch timestamp.
    :return: The human-readable date.
    """
    try:
        rval = dt.fromtimestamp(timestamp / 1000000).ctime()
    except Exception as e:
        rval = "No date available (NULL value in database)."
        print(e)
    return rval


def copy_database(db_path: str):
    """
    Copies a database file to the user's desktop.

    This function takes the path of a database file, copies it to the user's
    desktop, and preserves the metadata of the original file during the copy
    process. If the file cannot be found or any other exception occurs, it
    prints an appropriate error message.

    :param db_path: Path to the database file to be copied.
    :type db_path: str
    :return: None
    """
    try:
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")

        shutil.copy2(db_path, desktop_path)  # copy2 preserves metadata

        print(f"Successfully copied database to {desktop_path}")

    except FileNotFoundError:
        print(f"Error: Found no database at {db_path}")
    except Exception as e:
        print(f"Error: {e}")
