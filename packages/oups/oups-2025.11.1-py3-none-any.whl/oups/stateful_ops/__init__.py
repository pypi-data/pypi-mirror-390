#!/usr/bin/env python3
"""
Created on Sat Jun 28 18:35:00 2025.

@author: pierrot

"""
import sys


# Avoid importing aggstream during Sphinx autodoc builds (numba dependency)
if "sphinx" in sys.modules:
    AggStream = None
    by_x_rows = None
else:
    from .aggstream import AggStream  # type: ignore
    from .aggstream import by_x_rows  # type: ignore

from .asof_merger import AsofMerger


__all__ = ["AggStream", "AsofMerger", "by_x_rows"]
