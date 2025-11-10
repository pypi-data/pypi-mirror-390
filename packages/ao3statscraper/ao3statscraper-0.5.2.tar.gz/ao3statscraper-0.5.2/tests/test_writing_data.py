#!/usr/bin/env python3

import argparse
import pandas
import os

from ao3statscraper import Config, WorkStatsData


if __name__ == "__main__":
    #  TODO: modify where data is stored. Also change base filename.
    conf = Config()

    worklist = [["Ham", 12], ["eggs", 23], ["bacon", 1234]]
    work = pandas.DataFrame(worklist)

    # TODO: check different file formats.
    new_stats = WorkStatsData(conf, work)
    new_stats.datadir = os.path.curdir
    new_stats.dump()

    readtest = WorkStatsData(conf, source=new_stats._generate_dump_filename() + ".csv")
    #  print(readtest.data)

    # TODO: check read data is same as written.
