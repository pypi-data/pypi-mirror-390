"""
SeisPy is a Python library for seismic data processing.
"""

__version__ = "0.2.243"

from .seis_data import SeisData, SeisGrid
from .horiz import Horiz
from .mapping import TraceField, BinField, Trace
from .base import CVDFile, BaseConfig, io

__all__ = ['SeisData', 'SeisGrid', 'Horiz', 'TraceField', 'BinField', 'Trace', 'CVDFile', 'BaseConfig', 'io']

"""
py -m build
py -m twine check dist/*
py -m twine upload --non-interactive -r pypi dist/*
"""
