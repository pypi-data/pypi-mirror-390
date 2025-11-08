# (C) Copyright 2018-2023 Enthought, Inc., Austin, TX
# All rights reserved.
#
# This software is provided without warranty under the terms of the BSD
# license included in LICENSE.txt and may be redistributed only under
# the conditions described in the aforementioned license. The license
# is also available online at http://www.enthought.com/licenses/BSD.txt
#
# Thanks for using Enthought open source!

# from ._ibm2ieee import ibm2float32, ibm2float64
from .ibm2ieee import ibm2float32, ibm2float64

__all__ = [
    "ibm2float32",
    "ibm2float64",
]


"""
cd e:\projects\python\redo_v1.0\seispy\GridSeisPy\ibm2ieee
py -m pip install -U setuptools wheel numpy
py setup_ext.py build_ext --inplace
"""