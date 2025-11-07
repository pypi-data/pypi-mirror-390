"""
PER Datasets - A module for loading reservoir datasets
"""

__version__ = "0.1.23"

from .talkaholic.reservoir import Reservoir
from .reservoir import load_random, load
from .utils.init import initialize

__all__ = ['load_random', 'load', 'Reservoir', '__version__', 'initialize']