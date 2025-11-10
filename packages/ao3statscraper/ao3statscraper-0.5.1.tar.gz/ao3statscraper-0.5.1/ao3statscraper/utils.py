#!/usr/bin/env python3

# ======================================
# Misc utilities.
# ======================================

import os
import datetime
from termcolor import colored


def clear_terminal():
    """
    Clear the terminal window.
    """
    os.system("cls" if os.name == "nt" else "clear")


def get_datetime_from_time_string(time_string):
    year = int(time_string[:4])
    month = int(time_string[4:6])
    day = int(time_string[6:8])
    hour = int(time_string[8:10])
    mins = int(time_string[10:12])
    sec = int(time_string[12:14])

    t = datetime.datetime(year, month, day, hour, mins, sec)
    return t


def colour_numeric_string(x: str):
    """
    Colours in a string representing an number.
    Green if positive, red if negative.

    If x is zero (the number zero as a string), return
    an empty string.
    """
    try:
        val = float(x)
    except ValueError:
        return x
    if val > 0:
        return colored(" (+" + x + ")", "green")
    elif val < 0:
        return colored(" (" + x + ")", "red")
    else:
        # Don't add a string zero to number.
        # Return empty string instead.
        return ""


def get_title_output(titlestr: str):
    """
    Generate a title from a string.
    """
    title = titlestr.strip()
    n = len(title)
    bar = n * "─" + "\n"
    title_output = bar + title + "\n" + bar
    return title_output
