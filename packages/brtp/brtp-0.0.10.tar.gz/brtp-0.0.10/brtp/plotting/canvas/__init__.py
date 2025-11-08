"""
Module providing a 'wrapper' class (Canvas) for plotting in matplotlib figures, which takes care of...
  - axis transformations (x/y/z)
  - plotting styles
  - ...
"""

from ._canvas import Canvas
from ._canvas_range import CanvasRange, RangeSpecs
from ._linestyle import LineStyle
