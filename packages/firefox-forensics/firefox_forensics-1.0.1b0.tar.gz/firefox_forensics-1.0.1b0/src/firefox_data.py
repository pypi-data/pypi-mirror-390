#!/usr/bin/env python3

"""
Firefox data extraction
Python 3.13+
Date created: February 7th, 2025
Date modified: September 2nd, 2025
"""

import getpass
import logging
import os
import sys
from logging.config import fileConfig

from src import common

fileConfig("logging.ini")
logger = logging.getLogger()


def fetch_history_data(save: bool) -> None:
    """
    Fetches browsing history data from the local Firefox database and optionally saves it to a file.

    This function retrieves data from the Firefox `places.sqlite` database, which contains
    browsing and history information. The retrieved history items, including the URL,
    ID, and the date of the last visit, are displayed on the console. Optionally, if the
    `save` parameter is set to True, the history is saved to a text file on the desktop
    directory of the current user.

    :param save: A boolean flag that indicates whether the browsing history data
        should be saved to a file. If True, the data is written to 'history_data.txt'
        on the desktop. If False, only console output is generated.
    :type save: Bool
    :return: This function does not return any value.
    :rtype: None
    """
    logger.debug(f"Output: {save}")

    os_version = common.system_info()
    history_file = "places.sqlite"
    db = firefox_db_path(os_version, history_file)  # type: ignore
    logger.debug(f"Database: {db}")

    print()
    print("The path to the database is: {}".format(db))
    print()

    # Copy database to desktop
    common.copy_database(db)
    copied_db = os.path.join(os.path.expanduser("~"), "Desktop", history_file)

    history_data = read_history(copied_db)  # type: ignore

    print()
    print("Show the id, the URL and the last date:")
    print("=======================================")
    print()

    desktop_path = "/Users/{0}/Desktop/".format(getpass.getuser())

    if save:
        with open(desktop_path + "history_data.txt", "w") as file:
            for line in history_data:
                (
                    id,
                    url,
                    title,
                    rev_host,
                    visit_count,
                    hidden,
                    typed,
                    frequency,
                    last_visit_date,
                    guid,
                    foreign_count,
                    url_hash,
                    description,
                    preview_image_url,
                    site_name,
                    origin_id,
                    recalc_frequency,
                    alt_frequency,
                    recalc_alt_frequency,
                ) = line

                date = common.convert_epoch(last_visit_date)

                output = f"id: {str(id)}\nURL: {url}\nDate of last visit: {str(date)}\n"
                print(output)
                file.write(output + "\n")
    else:
        for line in history_data:
            (
                id,
                url,
                title,
                rev_host,
                visit_count,
                hidden,
                typed,
                frequency,
                last_visit_date,
                guid,
                foreign_count,
                url_hash,
                description,
                preview_image_url,
                site_name,
                origin_id,
                recalc_frequency,
                alt_frequency,
                recalc_alt_frequency,
            ) = line

            date = common.convert_epoch(last_visit_date)

            output = f"id: {str(id)}\nURL: {url}\nDate of last visit: {str(date)}\n"
            print(output)
        print("No output file created.")


def platform_paths() -> dict[str, str]:
    """
    Determines and returns the file paths for Mozilla Firefox profiles according
    to the user's operating system.

    This function generates platform-specific file paths based on the current
    user's profile and returns a dictionary mapping operating system names
    to the file paths.

    :return: A dictionary containing operating system names as keys and the
        corresponding Firefox profile paths as values.
    :rtype: dict
    """
    paths = {
        "Windows 7": "C:\\Users\\{0}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles".format(
            getpass.getuser()
        ),
        "Windows 8": "C:\\Users\\{0}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles".format(
            getpass.getuser()
        ),
        "Windows 10": "C:\\Users\\{0}\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles".format(
            getpass.getuser()
        ),
        "Linux": "/home/{0}/.mozilla/firefox/".format(getpass.getuser()),
        "Darwin": "/Users/{0}/Library/Application Support/Firefox/Profiles".format(
            getpass.getuser()
        ),
    }

    return paths


def profile_paths(operating_system: str) -> str:
    """
    Determines the profile path for the given operating system. The function checks the
    provided operating system and maps it to the corresponding profile path based on the
    predefined platform paths. If the operating system is not supported, it prints an
    appropriate message and returns an empty string.

    :param operating_system: The name of the operating system whose profile path needs
        to be determined.
    :type operating_system: Str

    :raises KeyError: If the operating system is unknown and cannot be mapped to a
        profile path.

    :return: The profile path corresponding to the provided operating system. If the
        operating system is unsupported or unknown, it returns an empty string.
    :rtype: str
    """
    profile_path: str = ""
    platform_path: dict[str, str] = platform_paths()

    # Check the operating system
    if operating_system == "Windows 7":
        print("Sorry, Windows 7 is not supported!")
    elif operating_system == "Windows 8":
        print("Sorry, Windows 8 is not supported!")
    elif operating_system == "Windows 10":
        print("Sorry, Windows 10 is not supported!")
    elif operating_system == "Linux":
        print("Sorry, Linux is not supported!")
    elif operating_system == "macOS":
        profile_path = platform_path["Darwin"]
    else:
        print("Error: Unknown Operating System!")
    return profile_path


def firefox_db_path(operating_system: str, db_file: str) -> str | None:
    """
    Determine the path to a specified database file within a Firefox profile directory for the given
    operating system. The function searches for a profile folder that includes the text 'release'
    and verifies if the specified database file exists within that profile folder. If no matching
    profile folder or database file is found, the function returns None.

    :param operating_system: A string indicating the operating system type:
    (e.g., 'windows', 'linux', 'macOS'). This is used to resolve the
    appropriate base path for Firefox profiles.
    :type operating_system: str
    :param db_file: The name of the database file to locate within the Firefox
    profile directory.
    :type db_file: str
    :return: The full path to the specified database file if found, otherwise None.
    :rtype: str
    """
    profile_path: str = profile_paths(operating_system)
    full_path: str = ""

    # Try to find the x.default directory in the Profiles folder.
    try:
        for item in os.listdir(profile_path):
            # Check for the x.default directory
            # and return the database file's path
            if (
                os.path.isdir(os.path.join(profile_path, item))
                and "release" in item
                and os.path.isfile(os.path.join(profile_path, item, db_file))
            ):
                # return os.path.join(profile_path, item, db_file)
                full_path = os.path.join(profile_path, item, db_file)
        return full_path
    except FileNotFoundError as e:
        print(e)
        sys.exit(
            "Could not find Firefox Profiles folder!\nAre you sure Firefox is installed on this system?"
        )


def read_history(history_db: str) -> list:
    """
    Fetches browsing history records from the specified database.

    This function connects to the provided SQLite database file, executes an SQL
    command to retrieve all browsing history details stored in the ``moz_places``
    table, and returns the fetched data.

    :param history_db: Path to the SQLite database containing the browsing history.
    :type history_db: str
    :return: List of records fetched from the ``moz_places`` table.
    :rtype: list
    """
    sql_command = "SELECT * FROM moz_places"
    rval = common.fetch_data(history_db, sql_command)
    return rval
