#!/usr/bin/env python3

import datetime
import pandas
import os
from typing import Union, Type
import tabulate

from .configuration import Config
from .utils import (
    get_datetime_from_time_string,
    get_title_output,
    colour_numeric_string,
)


class StatsData(object):
    datatype = "Generic"
    data = None
    dump_base_name = "ao3stats"
    dump_delimiter = "-"

    def __init__(self, conf: Config, data: Union[None, pandas.DataFrame] = None):
        self.timestamp = datetime.datetime.now()
        self.datadir = conf.datadir
        self.username = conf.username
        self.data = data
        return

    def _generate_dump_filename(self):
        """
        Generate the file name of the dump.
        Returns the file name as a string.
        """
        t = self.timestamp
        timestamp = f"{t.year:04d}{t.month:02d}{t.day:02d}{t.hour:02d}{t.minute:02d}{t.second:02d}"

        return generate_dump_base_name(self) + timestamp

    def dump(self):
        """
        Dump the data this object contains into a dump file.
        """

        filename = self._generate_dump_filename()
        filepath = os.path.join(self.datadir, filename)

        filepath += ".csv"
        self.data.to_csv(filepath, index=False)
        return

    def _read(self, filepath):
        suffix = ".csv"
        self.data = pandas.read_csv(filepath)

        self.timestamp = get_timestamp_from_filename(self, filepath, suffix=suffix)

        #  print(
        #      f"Read in stats from {t.year}-{t.month:02d}-{t.day:02d} {t.hour:02d}:{t.minute:02d}:{t.second:02d}"
        #  )

        return


class WorkStatsData(StatsData):
    datatype = "Works"

    def __init__(
        self,
        conf: Config,
        data: Union[list, None] = None,
        source: Union[str, None] = None,
    ):
        """
        You need to provide either data or source
        """

        if data is None and source is None:
            raise ValueError(
                "You need to provide either `data` or `source` for the database"
            )

        # Needs to be done before reading from file to not
        # overwrite timestamp
        super(WorkStatsData, self).__init__(conf)

        if source is None:
            self.data = pandas.DataFrame(data)

        else:
            self._read(source)

        return

    def _print_database(self, data: pandas.DataFrame, columns=None):
        """
        Print out a nice table.
        Provide list of columns to print as list of strings (column keys)
        via the `columns` parameter.
        """

        if data.empty:
            print("Error in WorkStatsData._print_database: Empty DataFrame?")
            return

        titlestr = f"Work Statistics For User {self.username}"
        title_output = get_title_output(titlestr)

        if columns is None:
            columns = [
                "Title",
                "Kudos",
                "Comment Threads",
                "Bookmarks",
                "Subscriptions",
                "Words",
                "Hits",
            ]

        table = data[columns]
        output = tabulate.tabulate(
            table,
            tablefmt="fancy_grid",
            showindex=False,
            headers="keys",
            maxcolwidths=45,
            stralign="left",
            numalign="left",
        )

        print(title_output)
        print(output)

        return

    def print(self):
        self._print_database(self.data)

        return

    def diff(self, old_data: StatsData):
        """
        Diff this dataset with another, `old_data`.

        Returns True if changes were detected.
        """

        if self.data.empty:
            print("Error in WorkStatsData.diff: Empty new DataFrame?")
            return

        if old_data.data.empty:
            print("Error in WorkStatsData.diff: Empty old DataFrame?")
            return

        new_original = self.data
        new_original_purged = new_original.drop_duplicates(["ID"], ignore_index=True)
        new = new_original_purged.copy().astype(str)

        old_purged = old_data.data.drop_duplicates(["ID"], ignore_index=True)
        old = old_purged.astype(str)

        # Merge old and new data into one dataframe
        # This creates a new column except for the ones specified with `on=`
        merged = new.merge(old, how="outer", on=["ID", "Fandom", "Title"])
        merged["Changed"] = False
        merged.fillna(0, inplace=True)
        merged.reset_index(inplace=True)

        # Compute diff using old and new values, which now have new column names
        for col in new.columns:
            if col in ["ID", "Title", "Fandom", "Changed"]:
                continue
            n = col + "_x"
            o = col + "_y"

            diff = merged[n].astype(int) - merged[o].astype(int)
            merged.loc[diff != 0, "Changed"] = True
            diff_str = diff.astype(str)
            diff_str = diff_str.apply(lambda x: colour_numeric_string(x))
            merged[col] = merged[n].astype(str) + diff_str

        if not merged["Changed"].any():
            return False

        # Only print out things that have changed.
        output_trimmed = merged.loc[merged["Changed"]]
        self._print_database(output_trimmed)

        return True


class TotStatsData(StatsData):
    datatype = "Total"

    def __init__(
        self,
        conf: Config,
        data: Union[list, None] = None,
        source: Union[str, None] = None,
    ):
        """
        You need to provide either data or source
        """

        if data is None and source is None:
            raise ValueError(
                "You need to provide either `data` or `source` for the database"
            )

        # Needs to be done before reading from file to not
        # overwrite timestamp
        super(TotStatsData, self).__init__(conf)

        if source is None:
            self.data = pandas.DataFrame(data)

        else:
            self._read(source)

        return

    def _print_database(self, data: pandas.DataFrame):
        titlestr = f"Total Statistics For User {self.username}"
        title_output = get_title_output(titlestr)

        if data.empty:
            print("Error in TotStatsData._print_database: Empty DataFrame?")
            return

        output = tabulate.tabulate(
            data,
            tablefmt="simple_grid",
            showindex=False,
            headers="keys",
            maxcolwidths=60,
            stralign="left",
            numalign="left",
        )

        print(title_output)
        print(output)
        return

    def print(self):
        """
        Print the total statistics.
        """

        self._print_database(self.data)
        return

    def diff(self, old_data: StatsData):
        if self.data.empty:
            print("Error in TotStatsData.diff: Empty new DataFrame?")
            return

        if old_data.data.empty:
            print("Error in TotStatsData.diff: Empty old DataFrame?")
            return

        new = self.data
        old = old_data.data
        diff = new - old

        diff_str = diff.astype(str)
        new_str = new.astype(str)

        diff_str_colored = diff_str.map(lambda x: colour_numeric_string(x))

        # Without coloring
        #  diff_str[diff > 0] = " (+" + diff_str[diff > 0] + ")"
        #  # Don't add a minus: integer will be negative already
        #  diff_str[diff < 0] = " (" + diff_str[diff < 0] + ")"

        new_str += diff_str_colored

        self._print_database(new_str)

        return


def get_timestamp_from_filename(
    st: Type[StatsData], filepath: str, suffix: str = "csv"
):
    """
    Extract the time stamp from the stats file name of stats with the type StatsData.
    st: A class of StatsData
    filepath: the path of the file to extract timestamp from

    Returns: Datetime object of the time
    """

    filename = filepath.rstrip(suffix)

    ao3stats, datatype, timestamp = filename.split(st.dump_delimiter)

    t = get_datetime_from_time_string(timestamp)

    return t


def generate_dump_base_name(st: Type[StatsData]):
    """
    Generate the base name of the dump file for a StatsData object
    st: A class of StatsData

    returns: dump base name as string
    """
    return st.dump_base_name + st.dump_delimiter + st.datatype + st.dump_delimiter


def get_dump_file_list(conf: Config, st: Type[StatsData]):
    """
    Get a list of all written dump data files of StatsData object.
    conf: a Config object
    st: A class of StatsData

    Returns: list of strings of paths of files
    """

    datadir = conf.datadir
    base = generate_dump_base_name(st)
    ls = os.listdir(datadir)
    candidates = []
    for f in ls:
        if f.startswith(base):
            candidates.append(f)

    filelist = sorted(candidates)

    return [os.path.join(datadir, f) for f in filelist]


def get_latest_dump_filename(conf: Config, st: Type[StatsData]):
    """
    Find the file name of the latest snapshot of StatsData object.
    conf: a Config object
    st: A class of StatsData

    Returns: the path to the file as a string.

    """

    fl = get_dump_file_list(conf, st)
    if len(fl) == 0:
        print("Error: I couldn't find any previously saved statistics files in")
        print(f"       {conf.datadir}. If this is your first time running")
        print("       this script, run it with the --all flag.")
        quit(1)
    return fl[-1]


def get_2_latest_dump_filenames(conf: Config, st: Type[StatsData]):
    """
    conf: a Config object
    st: A class of StatsData
    Returns: 2 strings of dump file names in the order older, newest
    """

    fl = get_dump_file_list(conf, st)
    return fl[-2], fl[-1]
