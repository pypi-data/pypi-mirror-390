#!python3

"""
Prints the hits/kudos ratio of all your works, in ascending order.
"""


def ao3_hits_to_kudos():
    from ..configuration import Config
    from ..statsdata import WorkStatsData, TotStatsData, get_latest_dump_filename

    # Setup
    conf = Config()

    wsfile = get_latest_dump_filename(conf, WorkStatsData)
    ws_old = WorkStatsData(conf, source=wsfile)

    work_data = ws_old.data
    work_data.drop_duplicates(["ID"], ignore_index=True, inplace=True)

    work_data["Hits/Kudos"] = 0.0
    hpk = work_data.loc[:, "Hits"] / work_data.loc[:, "Kudos"]
    work_data.loc[:, "Hits/Kudos"] = hpk[:]
    work_data.sort_values(by="Hits/Kudos", ignore_index=True, inplace=True)

    columns = [
        "Title",
        "Fandom",
        "Words",
        "Hits",
        "Kudos",
        "Hits/Kudos",
    ]

    ws_old._print_database(work_data, columns=columns)


if __name__ == "__main__":
    ao3_hits_to_kudos()
