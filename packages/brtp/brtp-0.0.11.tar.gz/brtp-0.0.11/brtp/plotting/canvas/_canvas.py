from functools import cached_property
from typing import Iterable

import numpy as np
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle

from ._canvas_range import CanvasRange, RangeSpecs
from ._linestyle import LineStyle


class Canvas:
    """
    Class with 'plt.Axes' like methods for plotting, while mapping the user-facing x/y/z-coordinates to
    axis('figure') coordinates under-the-hood.
    """

    # -------------------------------------------------------------------------
    #  Constructor & core properties
    # -------------------------------------------------------------------------
    def __init__(self, canvas_range: CanvasRange, ax: plt.Axes):
        self.__range = canvas_range
        self.__ax = ax

    @cached_property
    def user_range(self) -> RangeSpecs:
        """Return the user-facing CanvasRange."""
        return self.__range.user_range

    @cached_property
    def fig_range(self) -> RangeSpecs:
        """Return the figure-facing CanvasRange."""
        return self.__range.fig_range

    @cached_property
    def ax(self) -> plt.Axes:
        """Return the underlying Axes object."""
        return self.__ax

    # -------------------------------------------------------------------------
    #  Plotting - LINES
    # -------------------------------------------------------------------------
    def plot(self, x: float | list[float] | np.ndarray, y: float | list[float] | np.ndarray, ls: LineStyle):
        x_trans, y_trans, z_trans = self.__range.user_to_fig(x, y, ls.zorder)
        ls.modify(zorder=z_trans).plot(self.__ax, x_trans, y_trans)

    def plot_sample(self, x_min: float, x_max: float, y: float, ls: LineStyle):
        x_trans, y_trans, z_trans = self.__range.user_to_fig([x_min, x_max], y, ls.zorder)
        ls.modify(zorder=z_trans).plot_sample(self.__ax, x=[x_trans[0], x_trans[1]], y=y_trans)

    def hline(
        self, y: float | list[float] | np.ndarray, ls: LineStyle, x_min: float | None = None, x_max: float | None = None
    ):
        # --- argument handling ----------------------------
        if not isinstance(y, Iterable):
            y_lst = [y]
        else:
            y_lst = list(y)
        if x_min is None:
            x_min = self.__range.user_range.x_min
        if x_max is None:
            x_max = self.__range.user_range.x_max

        # --- transform ------------------------------------
        x_trans, y_trans, z_trans = self.__range.user_to_fig([x_min, x_max], y_lst, ls.zorder)

        # --- plot -----------------------------------------
        for y_trans_el in y_trans:
            ls.modify(zorder=z_trans).plot(self.__ax, x_trans, y_trans_el)

    def vline(
        self, x: float | list[float] | np.ndarray, ls: LineStyle, y_min: float | None = None, y_max: float | None = None
    ):
        # --- argument handling ---------------------------
        if not isinstance(x, Iterable):
            x_lst = [x]
        else:
            x_lst = list(x)
        if y_min is None:
            y_min = self.__range.user_range.y_min
        if y_max is None:
            y_max = self.__range.user_range.y_max

        # --- transform -----------------------------------
        x_trans, y_trans, z_trans = self.__range.user_to_fig(x_lst, [y_min, y_max], ls.zorder)

        # --- plot ----------------------------------------
        for x_trans_el in x_trans:
            ls.modify(zorder=z_trans).plot(self.__ax, x_trans_el, y_trans)

    # -------------------------------------------------------------------------
    #  Plotting - SHAPES
    # -------------------------------------------------------------------------
    def rectangle(
        self,
        x_min: float,
        x_max: float,
        y_min: float,
        y_max: float,
        fill_color: tuple | str,
        edgecolor: tuple | str | None = None,
        linewidth: float = 0.0,
        zorder: float = 0.0,
        **kwargs,
    ):
        # --- transform ------------------------------------
        x_trans, y_trans, z_trans = self.__range.user_to_fig([x_min, x_max], [y_min, y_max], zorder)
        x_min_trans, x_max_trans = min(x_trans), max(x_trans)
        y_min_trans, y_max_trans = min(y_trans), max(y_trans)

        corner_x, width = x_min_trans, x_max_trans - x_min_trans
        corner_y, height = y_min_trans, y_max_trans - y_min_trans

        rect = Rectangle(
            xy=(corner_x, corner_y),
            width=width,
            height=height,
            facecolor=fill_color,
            edgecolor=edgecolor,
            linewidth=linewidth,
            zorder=z_trans,
            **kwargs,
        )
        self.__ax.add_patch(rect)

    # -------------------------------------------------------------------------
    #  Plotting - TEXT
    # -------------------------------------------------------------------------
    pass  # TODO
