from dataclasses import dataclass
from functools import cached_property

import numpy as np

from brtp.plotting.utils import Transform


# =================================================================================================
#  Range Specs
# =================================================================================================
@dataclass(frozen=True)
class RangeSpecs:
    """Data class describing the range specs (x,y,z) of either the user- or figure-facing part of a CanvasRange."""

    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_min: float
    z_max: float

    top: float
    bottom: float
    left: float
    right: float


# =================================================================================================
#  Canvas Range
# =================================================================================================
class CanvasRange:
    """
    Class describing the range transformations of a Canvas (x,y,z).
    The implicit assumption is made that the underlying matplotlib Axes is set up in default mode:
       x = left to right
       y = bottom to top
    """

    # -------------------------------------------------------------------------
    #  Constructor
    # -------------------------------------------------------------------------
    def __init__(
        self,
        x_transform: Transform,
        y_transform: Transform,
        z_transform: Transform,
    ):
        self._x = x_transform
        self._y = y_transform
        self._z = z_transform

    # -------------------------------------------------------------------------
    #  Properties
    # -------------------------------------------------------------------------
    @property
    def x_transform(self) -> Transform:
        return self._x

    @property
    def y_transform(self) -> Transform:
        return self._y

    @property
    def z_transform(self) -> Transform:
        return self._z

    @cached_property
    def user_range(self) -> RangeSpecs:
        return RangeSpecs(
            x_min=self._x.user_range()[0],
            x_max=self._x.user_range()[1],
            y_min=self._y.user_range()[0],
            y_max=self._y.user_range()[1],
            z_min=self._z.user_range()[0],
            z_max=self._z.user_range()[1],
            top=self._y.user_range()[0] if self._y.is_reverse() else self._y.user_range()[0],
            bottom=self._y.user_range()[1] if self._y.is_reverse() else self._y.user_range()[1],
            left=self._x.user_range()[1] if self._x.is_reverse() else self._x.user_range()[0],
            right=self._x.user_range()[0] if self._x.is_reverse() else self._x.user_range()[1],
        )

    @cached_property
    def fig_range(self) -> RangeSpecs:
        return RangeSpecs(
            x_min=self._x.figure_range()[0],
            x_max=self._x.figure_range()[1],
            y_min=self._y.figure_range()[0],
            y_max=self._y.figure_range()[1],
            z_min=self._z.figure_range()[0],
            z_max=self._z.figure_range()[1],
            top=self._y.figure_range()[1],
            bottom=self._y.figure_range()[0],
            left=self._x.figure_range()[0],
            right=self._x.figure_range()[1],
        )

    # -------------------------------------------------------------------------
    #  Transforms
    # -------------------------------------------------------------------------
    def user_to_fig(
        self,
        x: float | list[float] | np.ndarray,
        y: float | list[float] | np.ndarray,
        z: float | list[float] | np.ndarray,
    ) -> tuple[float | list[float] | np.ndarray, float | list[float] | np.ndarray, float | list[float] | np.ndarray]:
        return self._x(x), self._y(y), self._z(z)

    def fig_to_user(
        self,
        x: float | list[float] | np.ndarray,
        y: float | list[float] | np.ndarray,
        z: float | list[float] | np.ndarray,
    ) -> tuple[float | list[float] | np.ndarray, float | list[float] | np.ndarray, float | list[float] | np.ndarray]:
        return self._x.inv(x), self._y.inv(y), self._z.inv(z)
