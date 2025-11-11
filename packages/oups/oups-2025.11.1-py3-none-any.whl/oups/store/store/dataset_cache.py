#!/usr/bin/env python3
"""
Created on Mon Jun 16 20:00:00 2025.

@author: pierrot

OrderedParquetDataset caching utilities for Store operations.

"""
from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from oups.store.indexer import StoreKey


if TYPE_CHECKING:
    from oups.store.store import Store


@contextmanager
def cached_datasets[K: StoreKey](
    store: Store[K],
    keys: list[K],
):
    """
    Context manager for caching OrderedParquetDataset objects.

    Parameters
    ----------
    store : Store[K]
        Store instance to get datasets from
    keys : list[K]
        List of dataset keys to cache

    Yields
    ------
    dict[K, OrderedParquetDataset]
        Dictionary mapping keys to cached dataset objects

    """
    cache = {}
    try:
        cache = {key: store[key] for key in keys}
        yield cache
    finally:
        # Explicitly trigger OrderedParquetDataset deletion to release the lock.
        for key in keys:
            del cache[key]
