"""
PER Datasets - A module for loading reservoir datasets
"""

__version__ = "0.0.1-alpha"

from .talkaholic.reservoir import Reservoir
from .reservoir import load_random, load
from .utils.init import initialize

__all__ = ['load_random', 'load', 'Reservoir', '__version__', 'initialize']