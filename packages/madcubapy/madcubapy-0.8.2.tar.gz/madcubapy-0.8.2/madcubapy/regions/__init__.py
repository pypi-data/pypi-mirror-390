# madcubapy/regions/__init__.py

"""
The `madcubapy.regions` package provides utility functions to work with Regions
of Interest (rois) in different formats. This package allows the use of roi
files from MADCUBA (.mcroi), DS9 (.ds9), and CARTA (.crtf) roi formats,
alongside a custom format (.pyroi).
"""

from .interface import *
from .carta import *
from .ds9 import *
from .madcuba import *
from .pyroi import *
from .patches import *
from .contours import *
