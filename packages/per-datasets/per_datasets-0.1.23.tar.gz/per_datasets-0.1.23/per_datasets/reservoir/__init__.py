"""
Reservoir module for per_datasets
"""

from .load_random import load_random
from .load import load
from ..talkaholic.reservoir import Reservoir

__all__ = ['load_random', 'load', 'Reservoir']