from __future__ import annotations

import dataclasses
from dataclasses import dataclass
from typing import Iterable

from matplotlib.pyplot import Axes


@dataclass(frozen=True)
class LineStyle:
    """
    Class representing a line and marker style, allowing easy plotting with matplotlib.
    """

    # -------------------------------------------------------------------------
    #  Fields
    # -------------------------------------------------------------------------
    color: str | tuple[float, float, float] = (0.0, 0.0, 0.0)
    width: float = 1.0
    style: str | tuple = "-"
    line_enabled: bool = True
    marker: str = ""
    marker_size: float = 1.0
    marker_filled: bool = True
    alpha: float = 1.0
    zorder: float = 0.0

    # -------------------------------------------------------------------------
    #  Internal
    # -------------------------------------------------------------------------
    def get_line_kwargs(self) -> dict:
        if self.line_enabled:
            return dict(
                color=self.color,
                linewidth=self.width,
                linestyle=self.style,
                alpha=self.alpha,
                zorder=self.zorder,
            )
        else:
            return dict(linewidth=0.0)

    def get_marker_kwargs(self) -> dict:
        if (self.alpha < 1.0) and isinstance(self.color, tuple):
            # we need to and can set alpha of marker
            color = (self.color[0], self.color[1], self.color[2], self.alpha)
        else:
            # we don't need to, or we can't set the alpha of marker
            color = self.color

        return dict(
            marker=self.marker,
            markersize=self.marker_size,
            markerfacecolor=color if self.marker_filled else (1, 1, 1, self.alpha),
            markeredgecolor=color,
            markeredgewidth=self.width,
            zorder=self.zorder,
        )

    # -------------------------------------------------------------------------
    #  Modifiers
    # -------------------------------------------------------------------------
    def modify(
        self,
        color: str | tuple[float, float, float] = None,
        width: float = None,
        style: str | tuple = None,
        line_enabled: bool = None,
        marker: str = None,
        marker_size: float = None,
        marker_filled: bool = None,
        alpha: float = None,
        zorder: float = None,
    ) -> LineStyle:
        kwargs = dict()
        if color is not None:
            kwargs["color"] = color
        if width is not None:
            kwargs["width"] = width
        if style is not None:
            kwargs["style"] = style
        if line_enabled is not None:
            kwargs["line_enabled"] = line_enabled
        if marker is not None:
            kwargs["marker"] = marker
        if marker_size is not None:
            kwargs["marker_size"] = marker_size
        if marker_filled is not None:
            kwargs["marker_filled"] = marker_filled
        if alpha is not None:
            kwargs["alpha"] = alpha
        if zorder is not None:
            kwargs["zorder"] = zorder

        return dataclasses.replace(self, **kwargs)

    # -------------------------------------------------------------------------
    #  Plotting
    # -------------------------------------------------------------------------
    def plot(self, ax: Axes, x: float | Iterable[float], y: float | Iterable[float]) -> None:
        # argument handling
        x = [x] if isinstance(x, float) else list(x)
        y = [y] if isinstance(y, float) else list(y)
        if len(x) == 1:
            x = x * len(y)
        elif len(y) == 1:
            y = y * len(x)
        elif len(x) != len(y):
            raise ValueError(
                f"x and y must have the same length or one of them must be a single value (here: {len(x)} vs {len(y)})."
            )

        # plot line with markers
        ax.plot(x, y, **(self.get_line_kwargs() | self.get_marker_kwargs()))

    def plot_sample(self, ax: Axes, x: Iterable[float], y: float) -> None:
        """
        Plot horizontal sample of line with the specified style.
        Same as regular plotting, except...
          - only horizontal line is supported
          - x can only have 2 values
          - any marker will only be shown once in the middle of the line, not at nodes.
        """

        # argument handling
        x = list(x)
        if len(x) != 2:
            raise ValueError("x must have exactly 2 values for plot_sample.")
        y = [y, y]

        # plot
        ax.plot(x, y, **self.get_line_kwargs())
        ax.plot(0.5 * (x[0] + x[1]), y[0], **self.get_marker_kwargs())
