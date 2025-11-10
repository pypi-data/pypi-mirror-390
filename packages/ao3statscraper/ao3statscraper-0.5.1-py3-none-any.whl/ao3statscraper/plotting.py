#!/usr/bin/env python3

import matplotlib
from matplotlib import pyplot as plt
import matplotlib.patheffects as pe
import pandas as pd
from typing import Union
import datetime

from .configuration import Config
from .statsdata import WorkStatsData, TotStatsData
from .interactive_legend import interactive_legend


_plotkwargs = {
    "linewidth": 2,
    "linestyle": "-",
    "alpha": 0.75,
}


_normalizedplotkwargs = {
    "linewidth": 4,
    "linestyle": "-",
    "alpha": 0.75,
    #  "markersize": 3,
}


_backgroundplotkwargs = {
    "linewidth": _normalizedplotkwargs["linewidth"] * 2,
    "alpha": 0.45,
}


_scatterkwargs = {
    "s": 10,
    "alpha": 0.75,
}

_secondplotkwargs = {"linewidth": 2, "linestyle": "--", "alpha": 0.65}

_secondscatterkwargs = {"s": 10, "alpha": 0.75}

_normalizedplotmarkers = ["o", "v", "^", "s", "*", "+", "D", "X"]

_iact_legend_str = """
Click legend entry to toggle display.
Right-click to hide all.
Middle-click to show all.
"""


def _set_matplotlib_style():
    styles = [
        #  "seaborn-v0_8-darkgrid",
        "ggplot"
    ]

    for style in styles:
        if style in matplotlib.style.available:
            plt.style.use(style)
            return


def _plot_on_axis(
    ax: matplotlib.axes.Axes,
    abscissa: Union[pd.DataFrame, pd.Series],
    ordinate: Union[pd.DataFrame, pd.Series],
    label: str,
    prettify: bool = True,
    index: int = 0,
):
    """
    Plot abscissa data on the x-axis and ordinate data on the y-axis.
    Set y_label according to data names.

    index: index of line to plot. Determines its colour.
    """

    col = "C" + str(index)

    ax.plot(abscissa, ordinate, **_plotkwargs, c=col, label=label)
    ax.scatter(abscissa, ordinate, **_scatterkwargs, c=col)

    #  ax.set_xlabel(abscissa.name)
    ax.set_ylabel(ordinate.name)
    if prettify:
        ax.grid(True)
        ax.tick_params(axis="x", labelrotation=45)

    return


def _plot_accumulated_diff_on_axis(
    ax: matplotlib.axes.Axes,
    times: Union[pd.DataFrame, pd.Series],
    ordinate: Union[pd.DataFrame, pd.Series],
    label: str,
    diff_delta: str = "weekly",
    prettify: bool = True,
    index: int = 0,
):
    """
    Plot times data on the x-axis and diff of time-accumulated ordinate data
    on the y-axis. Set y_label according to data names.

    @param diff_delta: string ["daily", "weekly", "monthly"]
        Selects time frame to accumulate diff over
    """

    col = "C" + str(index)

    if diff_delta not in ["daily", "weekly", "monthly"]:
        raise ValueError(f"invalid averaging '{diff_delta}'")

    delta = None

    if diff_delta == "daily":
        delta = datetime.timedelta(days=1.0)
    elif diff_delta == "weekly":
        delta = datetime.timedelta(days=7.0)
    elif diff_delta == "monthly":
        delta = datetime.timedelta(days=30.0)

    last_val = ordinate[0]
    last_time = times[0]
    times_plot = [last_time]
    ordinate_plot = [last_val]

    i = 0
    while i < ordinate.shape[0]:
        if times[i] - last_time > delta:
            times_plot.append(times[i])
            ordinate_plot.append(ordinate[i] - last_val)

            last_time = times[i]
            last_val = ordinate[i]

        i += 1

    if last_time != times[times.shape[0] - 1]:
        times_plot.append(times[times.shape[0] - 1])
        ordinate_plot.append(ordinate[ordinate.shape[0] - 1] - last_val)

    ax.plot(
        times_plot, ordinate_plot, **_secondplotkwargs, c=col, label=f"Diff {label}"
    )
    ax.scatter(times_plot, ordinate_plot, **_secondscatterkwargs, c=col)

    ax.set_ylabel(diff_delta + " " + ordinate.name + " diff")
    if prettify:
        ax.grid(True)
        ax.tick_params(axis="x", labelrotation=45)

    return


def _plot_all_normalized_on_axis(
    ax: matplotlib.axes.Axes,
    data: pd.DataFrame,
    legendax: matplotlib.axes.Axes = None,
    prettify: bool = True,
    index: int = 0,
    single: bool = True,
):
    """
    plot all columns of the dataframe and normalize data by setting the last
    entry as 1.

    If `legendax` is not none, that axis will be used to display the legend.

    @param single: Is there going to be only one work plotted
    """

    time = data["Timestamp"]

    skip_columns = ["Timestamp", "index", "Title", "Fandom", "ID"]

    marker = _normalizedplotmarkers[index % len(_normalizedplotmarkers)]

    i = 0
    for col in data.columns:
        if col in skip_columns:
            continue

        d = data[col]
        val = d.iat[-1]
        d_norm = d / val

        if prettify and not single:
            # set up background line colouring
            bgcolor = "C" + str(index)
            patheffects = [
                pe.Stroke(foreground=bgcolor, **_backgroundplotkwargs),
                pe.Normal(),
            ]
        else:
            patheffects = None

        if single:
            label_prefix = ""
        else:
            # Add index to line labels (so interactive legend works)
            label_prefix = f"[{index+1}] "

            # Add the work title to the legend title
            if i == 0:
                try:
                    # Is available if we're plotting work stats, not total user stats
                    title = f"\n[{index+1}] " + data["Title"].at[0]
                except KeyError:
                    print("Trying to access work title while plotting user stats???")
                    title = "ERROR IN LABEL GENERATION"

                # store them in axis member I add
                if not hasattr(ax, "_my_title_buffer"):
                    ax._my_title_buffer = ""
                ax._my_title_buffer = ax._my_title_buffer + title

        # plot actual line
        fgcolor = "C" + str(i)
        ax.plot(
            time,
            d_norm,
            label=label_prefix + f"{col}",
            **_normalizedplotkwargs,
            color=fgcolor,
            zorder=index + 100,
            path_effects=patheffects,
        )

        i += 1

    #  ax.set_xlabel("Timestamp")
    ax.set_ylabel("All data (normalized)")

    if legendax is not None:
        # We're making the legend on a second, non-interactive ax.

        if not hasattr(ax, "_my_title_buffer"):
            title = None
        else:
            title = ax._my_title_buffer

        handles, labels = ax.get_legend_handles_labels()
        legendax.legend(handles=handles, labels=labels, loc="center left", title=title)

    # else:
    # we're making interactive legend outside of this function call.

    if prettify:
        ax.tick_params(axis="x", labelrotation=45)
        ax.grid(True)

    return


def plot_total_stats(tsfiles: list, conf: Config):
    """
    Plots the total user statistics.

    tsfiles: list
        list of file names of total user statistics to read in

    conf:
        AO3Stats configuration object
    """

    prettify = conf.plotting.prettify

    # Grab data
    ts_data = []

    for f in tsfiles:
        ts = TotStatsData(conf, source=f)
        ts.data["Timestamp"] = ts.timestamp

        ts_data.append(ts.data)

    # Combine it into a single dataframe
    alldata = pd.concat(ts_data)
    alldata.reset_index(inplace=True)
    alldata.sort_values(by="Timestamp")

    # get shorthands
    time = alldata["Timestamp"]
    user_subscriptions = alldata["User Subscriptions"]
    kudos = alldata["Kudos"]
    comments = alldata["Comment Threads"]
    bookmarks = alldata["Bookmarks"]
    subscriptions = alldata["Subscriptions"]
    words = alldata["Word Count"]
    hits = alldata["Hits"]

    if prettify:
        _set_matplotlib_style()

    fig = plt.figure()
    fig.suptitle("Total User Statistics")

    ax1 = fig.add_subplot(3, 3, 1)
    ax2 = fig.add_subplot(3, 3, 2)
    ax3 = fig.add_subplot(3, 3, 3)
    ax4 = fig.add_subplot(3, 3, 4)
    ax5 = fig.add_subplot(3, 3, 5)
    ax6 = fig.add_subplot(3, 3, 6)
    ax7 = fig.add_subplot(3, 3, 7)
    ax8 = fig.add_subplot(3, 3, 8)
    ax9 = fig.add_subplot(3, 3, 9)

    _plot_on_axis(ax1, time, user_subscriptions, prettify)
    _plot_on_axis(ax2, time, kudos, prettify)
    _plot_on_axis(ax3, time, comments, prettify)
    _plot_on_axis(ax4, time, bookmarks, prettify)
    _plot_on_axis(ax5, time, subscriptions, prettify)
    _plot_on_axis(ax6, time, words, prettify)
    _plot_on_axis(ax7, time, hits, prettify)

    # abuse neighbouring subplot for legend.
    legendax = ax9
    legendax.grid(False)
    legendax.axis("off")

    if prettify:
        # if visible=True, it may interfere with clicking on legend.
        legendax.set_visible(False)
        # Tell _plot_all_normalized_on_axis we're making interactive
        # legend.
        legendax = None

    _plot_all_normalized_on_axis(ax8, alldata, legendax, prettify, single=True)

    if prettify:
        plt.subplots_adjust(
            top=0.952, bottom=0.078, left=0.044, right=0.992, hspace=0.337, wspace=0.169
        )

        if not hasattr(ax8, "_my_title_buffer"):
            title = _iact_legend_str
        else:
            title = _iact_legend_str + "\n" + ax8._my_title_buffer
        ax8.legend(
            loc="upper left",
            ncols=2,
            frameon=True,
            bbox_to_anchor=(1.05, 1),
            title=title,
        )
        leg = interactive_legend(ax8)

    plt.show()

    return


def plot_work_stats(wsfiles: list, IDlist: list, conf: Config):
    """
    Plots the statistics of a single work specified via its AO3 ID.

    wsfiles: list
        list of file names of work statistics to read in

    IDlist: list of int
        List of AO3 ID of work to plot

    conf:
        AO3Stats configuration object
    """

    prettify = conf.plotting.prettify
    diff = conf.plotting.diff
    delta = conf.plotting.diff_delta

    # Grab data
    all_ws_data = [[] for i in IDlist]

    for f in wsfiles:
        ws = WorkStatsData(conf, source=f)
        ws.data["Timestamp"] = ws.timestamp

        for i, ID in enumerate(IDlist):
            work = ws.data[ws.data["ID"] == ID]
            if work.empty:
                continue
            else:
                all_ws_data[i].append(work)

    # Safety check
    for i, ID in enumerate(IDlist):
        if len(all_ws_data[i]) == 0:
            raise ValueError(f"Didn't find any data on work with ID {ID}.")

    figtitle = ""
    if prettify:
        _set_matplotlib_style()

    fig1 = plt.figure()
    ax1 = fig1.add_subplot(2, 3, 1)
    ax2 = fig1.add_subplot(2, 3, 2)
    ax3 = fig1.add_subplot(2, 3, 3)
    ax4 = fig1.add_subplot(2, 3, 4)
    ax5 = fig1.add_subplot(2, 3, 5)
    ax6 = fig1.add_subplot(2, 3, 6)

    fig2, ax21 = plt.subplots(1, 1)

    single = len(IDlist) == 1

    for i, ID in enumerate(IDlist):
        # Combine it into a single dataframe
        alldata = pd.concat(all_ws_data[i])
        alldata.reset_index(inplace=True)
        alldata.sort_values(by="Timestamp")

        # get shorthands
        time = alldata["Timestamp"]
        words = alldata["Words"]
        hits = alldata["Hits"]
        kudos = alldata["Kudos"]
        comments = alldata["Comment Threads"]
        bookmarks = alldata["Bookmarks"]
        subscriptions = alldata["Subscriptions"]

        title = alldata["Title"].at[0]
        if figtitle == "":
            figtitle = f"'{title}'"
        else:
            figtitle += f", '{title}'"

        _plot_on_axis(ax1, time, words, title, prettify, i)
        _plot_on_axis(ax2, time, hits, title, prettify, i)
        _plot_on_axis(ax3, time, kudos, title, prettify, i)
        _plot_on_axis(ax4, time, comments, title, prettify, i)
        _plot_on_axis(ax5, time, bookmarks, title, prettify, i)
        _plot_on_axis(ax6, time, subscriptions, title, prettify, i)

        if diff:
            if i == 0:
                ax1twin = ax1.twinx()
                ax2twin = ax2.twinx()
                ax3twin = ax3.twinx()
                ax4twin = ax4.twinx()
                ax5twin = ax5.twinx()
                ax6twin = ax6.twinx()

            _plot_accumulated_diff_on_axis(
                ax1twin,
                time,
                words,
                title,
                diff_delta=delta,
                prettify=prettify,
                index=i,
            )
            _plot_accumulated_diff_on_axis(
                ax2twin, time, hits, title, diff_delta=delta, prettify=prettify, index=i
            )
            _plot_accumulated_diff_on_axis(
                ax3twin,
                time,
                kudos,
                title,
                diff_delta=delta,
                prettify=prettify,
                index=i,
            )
            _plot_accumulated_diff_on_axis(
                ax4twin,
                time,
                comments,
                title,
                diff_delta=delta,
                prettify=prettify,
                index=i,
            )
            _plot_accumulated_diff_on_axis(
                ax5twin,
                time,
                bookmarks,
                title,
                diff_delta=delta,
                prettify=prettify,
                index=i,
            )
            _plot_accumulated_diff_on_axis(
                ax6twin,
                time,
                subscriptions,
                title,
                diff_delta=delta,
                prettify=prettify,
                index=i,
            )

        _plot_all_normalized_on_axis(
            ax21, alldata, legendax=None, prettify=prettify, index=i, single=single
        )

    fig1.suptitle(f"Work Statistics for {figtitle}")
    fig2.suptitle(f"Work Statistics for {figtitle}")

    # Make space for the legend outside of the plot
    fig2.subplots_adjust(right=0.75)

    # make legend on this ax interactive.
    if not hasattr(ax21, "_my_title_buffer"):
        title = _iact_legend_str
    else:
        title = _iact_legend_str + "\n" + ax21._my_title_buffer

    ax21.legend(
        loc="upper left", ncols=2, frameon=True, bbox_to_anchor=(1.05, 1), title=title
    )
    leg = interactive_legend(ax21)

    if len(IDlist) > 1:
        # show a legend on each subplot if we're plotting multiple works
        for ax in fig1.axes:
            ax.legend()

    if prettify:
        plt.figure(fig1.number)

        wspace = 0.169
        right = 0.992

        if diff:
            wspace = 0.264
            right = 0.962

        plt.subplots_adjust(
            top=0.952,
            bottom=0.078,
            left=0.044,
            right=right,
            hspace=0.337,
            wspace=wspace,
        )

    plt.show()

    return
