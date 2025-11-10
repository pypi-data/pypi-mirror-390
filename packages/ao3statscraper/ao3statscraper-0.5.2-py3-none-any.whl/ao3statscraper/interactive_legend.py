#!/usr/bin/env python3

from typing import Union
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib import legend as lgd


class InteractiveLegend(object):
    """
    Class defining the interactive, clickable legend. When plt.show() is used,
    you can click on the legend entries to toggle whether to show a particluar
    line in your plot. A right click on the legend removes all drawn lines, a
    middle click displays all.

    Taken from https://stackoverflow.com/a/31417070/6168231
    """

    def __init__(self, legend: lgd.Legend) -> None:
        self.legend = legend
        self.fig = legend.axes.figure

        self.lookup_artist, self.lookup_handle = self._build_lookups(legend)
        self._setup_connections()

        self.update()
        return

    def _setup_connections(self) -> None:
        """
        Initialise connection to matplotlib interactive backend
        """
        for artist in self.legend.texts + self.legend.legend_handles:
            artist.set_picker(7)  # 7 points tolerance

        self.fig.canvas.mpl_connect("pick_event", self.on_pick)
        self.fig.canvas.mpl_connect("button_press_event", self.on_click)
        return

    def _build_lookups(self, legend: lgd.Legend) -> (dict, dict):
        """
        Build dicts for quick lookups between legend handles and artists
        """
        labels = [t.get_text() for t in legend.texts]
        handles = legend.legend_handles
        label2handle = dict(zip(labels, handles))
        handle2text = dict(zip(handles, legend.texts))

        lookup_artist = {}
        lookup_handle = {}
        for artist in legend.axes.get_children():
            if artist.get_label() in labels:
                handle = label2handle[artist.get_label()]
                lookup_handle[artist] = handle
                lookup_artist[handle] = artist
                lookup_artist[handle2text[handle]] = artist

        lookup_handle.update(zip(handles, handles))
        lookup_handle.update(zip(legend.texts, handles))

        return lookup_artist, lookup_handle

    def on_pick(
        self, event: Union[mpl.backend_bases.KeyEvent, mpl.backend_bases.MouseEvent]
    ) -> None:
        """
        Toggle visibility state of a single legend entry.
        """
        handle = event.artist
        if handle in self.lookup_artist:
            artist = self.lookup_artist[handle]
            artist.set_visible(not artist.get_visible())
            self.update()
        return

    def on_click(
        self, event: Union[mpl.backend_bases.KeyEvent, mpl.backend_bases.MouseEvent]
    ) -> None:
        """
        Show none on right click, show all on middle click.
        """
        if event.button == 3:
            visible = False
        elif event.button == 2:
            visible = True
        else:
            return

        for artist in self.lookup_artist.values():
            artist.set_visible(visible)
        self.update()
        return

    def update(self):
        """
        Update what is displayed based on what we have stored in
        self.lookup_artist visible booleans.
        """
        for artist in self.lookup_artist.values():
            handle = self.lookup_handle[artist]
            if artist.get_visible():
                handle.set_visible(True)
            else:
                handle.set_visible(False)
        self.fig.canvas.draw()

    def show(self):
        plt.show()


def interactive_legend(ax: Union[mpl.axes.Axes, None] = None) -> InteractiveLegend:
    """
    Make a legend of an axis object interactive when displayed using plt.show():
    - Click on a legend entry to toggle whether line is drawn
    - Right click to remove all
    - Middle click to show all

    Example usage:

    ```
    fig, ax = plt.subplots()
    ax.plot(..., label="label1")
    ax.plot(..., label="label2")
    leg = interactive_legend(ax=ax)
    plt.show()
    ```

    Note: Make sure the legend is on the top, clickable layer. Easiest
    way to do that is to put legend outside of plot, using e.g.
    ax.legend(loc="upper left", bbox_to_anchor=(1.05, 1))

    Note: Assumes that all legend labels are unique.

    """
    if ax is None:
        ax = plt.gca()
    if ax.legend_ is None:
        ax.legend()

    return InteractiveLegend(ax.get_legend())
