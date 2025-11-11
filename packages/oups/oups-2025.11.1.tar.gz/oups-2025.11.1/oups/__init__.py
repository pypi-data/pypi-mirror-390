#!/usr/bin/env python3
"""
Created on Wed Dec  1 18:35:00 2021.

@author: pierrot

"""
import sys

# Import version dynamically from Poetry
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version


# Conditional import for stateful_ops to avoid numba issues during documentation builds
if "sphinx" in sys.modules:
    # During documentation builds, skip heavy stateful_ops imports
    AggStream = None
    by_x_rows = None
else:
    from .stateful_ops import AggStream  # noqa: F401
    from .stateful_ops import by_x_rows  # noqa: F401

from .stateful_loop import StatefulLoop  # noqa: F401
from .stateful_ops import AsofMerger  # noqa: F401
from .store import OrderedParquetDataset  # noqa: F401
from .store import Store  # noqa: F401
from .store import check_cmidx  # noqa: F401
from .store import conform_cmidx  # noqa: F401
from .store import is_toplevel  # noqa: F401
from .store import sublevel  # noqa: F401
from .store import toplevel  # noqa: F401
from .store import write  # noqa: F401


try:
    __version__ = version("oups")
except PackageNotFoundError:
    # Package is not installed, likely in development
    __version__ = "development"
