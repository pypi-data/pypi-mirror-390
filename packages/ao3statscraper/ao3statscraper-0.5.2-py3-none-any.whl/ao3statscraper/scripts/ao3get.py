#!/usr/bin/env python3

import argparse
import os


def _parse_scrape_args():
    """
    Setup argument parser and read cmdline args.
    """

    parser = argparse.ArgumentParser(
        prog="ao3get.py",
        description="Scrape your AO3 statistics.",
        epilog="The program will require you to log in to your AO3 account.",
    )

    parser.add_argument(
        "-a",
        "--all",
        action="store_true",
        default=False,
        dest="print_all",
        help="print out all statistics",
    )
    parser.add_argument(
        "-r",
        "--repeat",
        action="store_true",
        default=False,
        dest="repeat",
        help="show last diff again",
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store_true",
        default=False,
        dest="run_config",
        help="run the configuration dialogue and exit.",
    )
    parser.add_argument(
        "-d",
        "--diff",
        action="store_true",
        default=True,
        dest="diff",
        help="show diff only (default running mode)",
    )
    parser.add_argument(
        "-rm",
        "--remove-last",
        action="store_true",
        default=False,
        dest="remove_last",
        help="remove the last saved stats snapshot and exit.",
    )
    parser.add_argument(
        "-nw",
        "-n",
        "--no-write",
        action="store_true",
        default=False,
        dest="no_write",
        help="Don't write new stats snapshots after displaying them.",
    )
    parser.add_argument(
        "-s",
        "--show-dir",
        action="store_true",
        default=False,
        dest="showdir",
        help="Print out directory where data is stored and exit.",
    )
    parser.add_argument(
        "-f",
        "--file",
        action="store",
        type=str,
        default=None,
        nargs=1,
        dest="filename",
        help="Instead of downloading data, read them from a saved website provided with FILENAME.",
    )

    args = parser.parse_args()

    return args


def ao3get():
    from ..configuration import Config
    from ..statsdata import (
        WorkStatsData,
        TotStatsData,
        get_latest_dump_filename,
        get_2_latest_dump_filenames,
    )
    from ..scrape import UserSession

    args = _parse_scrape_args()
    conf = Config(reset_conffile=args.run_config)

    if args.showdir:
        print(f"Data directory is '{conf.datadir}'")
        quit()

    file = None
    if args.filename is not None:
        file = args.filename[0]
        if not os.path.isfile(file):
            raise FileNotFoundError(file)

    if args.remove_last:
        tsfile = get_latest_dump_filename(conf, TotStatsData)
        wsfile = get_latest_dump_filename(conf, WorkStatsData)

        print(f"This will remove files {tsfile} and {wsfile}.")
        answer = input("Continue? [y/N] ")
        if answer.startswith(("y", "Y")):
            os.remove(tsfile)
            print(f"Deleted {tsfile}")
            os.remove(wsfile)
            print(f"Deleted {wsfile}")
        elif answer.startswith(("n", "N")):
            print("Aborting.")
        else:
            print("Invalid input.")
        quit()

    if args.print_all:
        session = UserSession(conf, file)
        ts_new, ws_new = session.get_stats(conf)
        ts_new.print()
        ws_new.print()
        if not args.no_write:
            # synchronize time stamp first, just in case.
            ts_new.timestamp = ws_new.timestamp
            ts_new.dump()
            ws_new.dump()

    elif args.repeat:
        tsfile1, tsfile2 = get_2_latest_dump_filenames(conf, TotStatsData)
        wsfile1, wsfile2 = get_2_latest_dump_filenames(conf, WorkStatsData)

        ts_old = TotStatsData(conf, source=tsfile1)
        ws_old = WorkStatsData(conf, source=wsfile1)
        ts_new = TotStatsData(conf, source=tsfile2)
        ws_new = WorkStatsData(conf, source=wsfile2)

        ts_new.diff(ts_old)
        ws_new.diff(ws_old)

    elif args.diff:
        # Diff is skipped if repeat is on

        session = UserSession(conf, file)
        ts_new, ws_new = session.get_stats(conf)

        tsfile = get_latest_dump_filename(conf, TotStatsData)
        wsfile = get_latest_dump_filename(conf, WorkStatsData)
        ts_old = TotStatsData(conf, source=tsfile)
        ws_old = WorkStatsData(conf, source=wsfile)

        ts_new.diff(ts_old)
        changes = ws_new.diff(ws_old)

        if changes and not args.no_write:
            # synchronize time stamp first, just in case.
            ts_new.timestamp = ws_new.timestamp
            ts_new.dump()
            ws_new.dump()


if __name__ == "__main__":
    ao3get()
