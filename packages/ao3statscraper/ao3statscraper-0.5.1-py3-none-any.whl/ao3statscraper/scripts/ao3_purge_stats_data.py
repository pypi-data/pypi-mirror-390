#! python3

import argparse


def _parse_purge_args():
    """
    Setup argument parser and read cmdline args.
    """

    parser = argparse.ArgumentParser(
        prog="ao3_purge_stats_data",
        description="purge downloaded stats data that are too close in time to each other.",
    )

    parser.add_argument(
        "-f",
        "--frequency",
        action="store",
        type=int,
        nargs=1,
        default=12,
        dest="dt",
        help="Number of minimum hours between two snapshots to keep. Default: 12",
    )

    args = parser.parse_args()

    return args


def ao3_purge_stats_data():
    import datetime
    import os

    from ..configuration import Config
    from ..statsdata import (
        WorkStatsData,
        TotStatsData,
        get_dump_file_list,
        get_timestamp_from_filename,
    )

    # Setup
    args = _parse_purge_args()
    conf = Config()

    # Get and check list of dump files.
    tsfiles = get_dump_file_list(conf, TotStatsData)
    wsfiles = get_dump_file_list(conf, WorkStatsData)

    tsDummy = TotStatsData(conf, source=tsfiles[0])
    wsDummy = WorkStatsData(conf, source=wsfiles[0])

    times = []

    for i in range(len(tsfiles)):
        try:
            tt = get_timestamp_from_filename(tsDummy, tsfiles[i])
            tw = get_timestamp_from_filename(wsDummy, wsfiles[i])
        except IndexError:
            print("Unequal number of total stats data files and work data files")
            print("This needs special handling.")
            quit()

        if tt != tw:
            raise ValueError("Total and work times are not equal", tt, tw)

        times.append(tt)

    diffhours = args.dt
    if type(diffhours) == list:
        diffhours = diffhours[0]
    mindiff = datetime.timedelta(hours=diffhours)

    ts_to_purge = []
    ws_to_purge = []
    times_to_purge = []

    time_last = times[0]

    for i in range(1, len(tsfiles)):
        timediff_1 = times[i] - time_last
        # make sure we respect the minimal time
        # between both past and future snapshots
        if i < len(tsfiles) - 1:
            timediff_2 = times[i + 1] - times[i]
        else:
            timediff_2 = 2.0 * mindiff

        if timediff_1 < mindiff and timediff_2 < mindiff:
            # this one needs purging.
            ts_to_purge.append(tsfiles[i])
            ws_to_purge.append(wsfiles[i])
            times_to_purge.append(times[i])
        else:
            # only update the last time to compare to if we're
            # not purging
            time_last = times[i]

    if len(ws_to_purge) > 0:
        print("The following snapshots will be purged:")
        for i in range(len(times_to_purge)):
            print(f"{times_to_purge[i]} - {ts_to_purge[i]}, {ws_to_purge[i]}")

        answer = input("Continue? This can't be undone. [yN] ")
        if answer.startswith(("y", "Y")):
            count = 0
            for f in ts_to_purge:
                os.remove(f)
                count += 1
            for f in ws_to_purge:
                os.remove(f)
                count += 1

            print(f"Deleted {count} files.")
        else:
            print("Aboring.")
            quit()
    else:
        print("Found no files that need purging.")
        quit()


if __name__ == "__main__":
    ao3_purge_stats_data()
