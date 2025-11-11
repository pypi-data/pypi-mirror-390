#!/usr/bin/env python3
"""
Created on Wed Dec  4 18:00:00 2021.

@author: pierrot

"""
from collections.abc import Iterator
from pathlib import Path

from pandas import Timestamp
from sortedcontainers import SortedSet

from oups.store.filepath_utils import files_at_depth
from oups.store.indexer import StoreKey
from oups.store.indexer import TopLevelIndexer
from oups.store.indexer import is_toplevel
from oups.store.ordered_parquet_dataset import OrderedParquetDataset
from oups.store.ordered_parquet_dataset.metadata_filename import get_md_basename
from oups.store.store.dataset_cache import cached_datasets
from oups.store.store.iter_intersections import iter_intersections


def get_keys[K: StoreKey](basepath: Path, indexer: TopLevelIndexer[K]) -> SortedSet[K]:
    """
    Identify ordered parquet dataset in directory.

    Scan 'basepath' directory and create instances of 'indexer' class from
    compatible subpaths. Only file which name ends by '_opdmd' are retained
    to construct a key.

    Parameters
    ----------
    basepath : Path
        Path to directory containing a dataset collection, in folders complying
        with the schema defined by the indexer class.
    indexer : TopLevelIndexer[K]
        Class decorated with '@toplevel' decorator, and defining a path
        schema.

    Returns
    -------
    SortedSet[StoreKey]
        Sorted set of keys (i.e. instances of indexer) that can be
        found in 'basepath' directory and with a 'valid' opd metadata file
        (ending by '_opdmd').

    """
    depth = indexer.depth - 1
    # Filter, keeping only folders having files with correct extension,
    # then materialize paths into keys, filtering out those that can't.
    return SortedSet(
        [
            key
            for path, files in files_at_depth(basepath, depth)
            for file in files
            if (
                (opdmd_basename := get_md_basename(file))
                and (
                    key := indexer.from_path(
                        Path(*path.parts[-depth:]) / opdmd_basename,
                    )
                )
            )
        ],
    )


class Store[K: StoreKey]:
    """
    Sorted list of keys (indexes to parquet datasets).

    Attributes
    ----------
    basepath : Path
        Directory path to the set of parquet datasets.
    indexer : TopLevelIndexer[KT]
        Indexer schema (class) to be used to index parquet datasets.
    keys : SortedSet[K]
        Set of indexes of existing parquet datasets.
    _needs_keys_refresh : bool
        Flag indicating that the 'keys' property needs to be refreshed from
        disk. Set to True when a new 'OrderedParquetDataset' is accessed but
        doesn't yet have a metadata file on disk. When True, the next access to
        the 'keys' property will rescan the filesystem to update the keys
        collection.

    Methods
    -------
    get
        Return the ``OrderedParquetDataset`` instance corresponding to ``key``.
    iter_intersections
        Iterate over row group intersections across multiple datasets in store.
    __getitem__
        Return the ``OrderedParquetDataset`` instance corresponding to ``key``.
    __delitem__
        Remove dataset from parquet set.
    __iter__
        Iterate over keys.
    __len__
        Return number of datasets.
    __repr__
        List of datasets.
    __contains__
        Assess presence of this dataset.

    Notes
    -----
    ``SortedSet`` is the data structure retained for ``keys`` instead of
    ``SortedList`` as its ``__contains__`` appears faster.

    """

    def __init__(self, basepath: str | Path, indexer: TopLevelIndexer[K]):
        """
        Instantiate parquet set.

        Parameters
        ----------
        basepath : Union[str, Path]
            Path of directory containing parquet datasets.
        indexer : TopLevelIndexer[K]
            Class (not class instance) of the indexer to be used for:

              - identifying existing parquet datasets in 'basepath' directory,
              - creating the folders where recording new parquet datasets.

        """
        if not is_toplevel(indexer):
            raise TypeError(f"{indexer.__name__} has to be '@toplevel' decorated.")
        self._basepath = Path(basepath).resolve()
        self._indexer = indexer
        self._keys = get_keys(basepath, indexer)
        self._needs_keys_refresh = False

    @property
    def basepath(self) -> Path:
        """
        Return basepath.

        Returns
        -------
        Path
            Basepath.

        """
        return self._basepath

    @property
    def indexer(self) -> TopLevelIndexer[K]:
        """
        Return indexer.

        Returns
        -------
        TopLevelIndexer[K]
            The toplevel indexer class used by this store.

        """
        return self._indexer

    @property
    def keys(self) -> SortedSet[K]:
        """
        Return keys.

        Returns
        -------
        SortedSet[K]
            Sorted set of keys.

        """
        if self._needs_keys_refresh:
            # Refresh keys.
            self._keys = get_keys(self.basepath, self.indexer)
            self._needs_keys_refresh = False
        return self._keys

    def __len__(self) -> int:
        """
        Return number of datasets.

        Returns
        -------
        int
            Number of datasets.

        """
        return len(self.keys)

    def __repr__(self) -> str:
        """
        List of datasets.

        Returns
        -------
        str
            String representation of the store.

        """
        return "\n".join(map(str, self.keys))

    def __contains__(self, key: K) -> bool:
        """
        Assess presence of this dataset.

        Parameters
        ----------
        key : K
            Key to assess presence of.

        Returns
        -------
        bool
            True if the dataset exists, False otherwise.

        """
        return key in self.keys

    def __iter__(self) -> Iterator[K]:
        """
        Iterate over keys.

        Yields
        ------
        KT
            Key of each dataset.

        """
        yield from self.keys

    def __delitem__(self, key: K):
        """
        Remove dataset from parquet set.

        Parameter
        ---------
        key : K
            Key specifying the location where to delete the data. It has to be
            an instance produced by the indexer class provided at Store
            instantiation.

        Raises
        ------
        KeyError
            If the key is not found in the store.

        """
        if key in self.keys:
            # Get OPD instance and remove its files
            self.get(key).remove_from_disk()
            # Update store's key collection
            self._keys.remove(key)
            # Clean up empty parent directories
            upper_dir = (self.basepath / key.to_path()).parent
            while (upper_dir != self.basepath) and (not list(upper_dir.iterdir())):
                upper_dir.rmdir()
                upper_dir = upper_dir.parent
        else:
            raise KeyError(f"key '{key}' not found in store.")

    def __getitem__(self, key: K) -> OrderedParquetDataset:
        """
        Return the ``OrderedParquetDataset`` instance corresponding to ``key``.

        Wrapper to ``get`` method.

        Parameters
        ----------
        key : K
            Key specifying the location where to read the data from. It has to
            be an instance produced by the indexer class provided at Store
            instantiation.

        Returns
        -------
        OrderedParquetDataset
            The ``OrderedParquetDataset`` instance corresponding to ``key``.

        """
        return self.get(key)

    def get(self, key: K, **kwargs) -> OrderedParquetDataset:
        """
        Return the OrderedParquetDataset instance with custom parameters.

        Parameters
        ----------
        key : K
            Key specifying the location where to read the data from.
        **kwargs : dict
            Additional parameters to pass to OrderedParquetDataset constructor
            (e.g., 'ordered_on', 'lock_timeout', 'lock_lifetime').

        Returns
        -------
        OrderedParquetDataset
            The OrderedParquetDataset instance corresponding to key. Creates a
            new OrderedParquetDataset object if the key doesn't exist.

        """
        opd = OrderedParquetDataset(self.basepath / key.to_path(), **kwargs)
        if opd.is_newly_initialized:
            self._needs_keys_refresh = True
        return opd

    def iter_intersections(
        self,
        keys: list[K],
        start: float | Timestamp | None = None,
        n_prev: int | list[int] | None = 0,
        end_excl: float | Timestamp | None = None,
    ):
        """
        Iterate over row group intersections across multiple datasets in store.

        This method handles dataset caching and lifecycle management, then
        delegates to the core iter_intersections function.

        Parameters
        ----------
        keys : list[K]
            List of dataset keys.
        start : Optional[Union[int, float, Timestamp]], default None
            Start value (inclusive) for the 'ordered_on' column range.
        n_prev : Union[int, list[int]], default 0
            Number of previous rows (number of values before 'start') to prepend
            to first yielded dataframe for each key.
            If a list, values are used for each key in the same order as 'keys'.
        end_excl : Optional[Union[int, float, Timestamp]], default None
            End value (exclusive) for the 'ordered_on' column range.

        Yields
        ------
        dict[K, DataFrame]
            Dictionary mapping each key to its corresponding DataFrame chunk.

        """
        with cached_datasets(self, keys) as datasets:
            yield from iter_intersections(
                datasets=datasets,
                start=start,
                n_prev=n_prev,
                end_excl=end_excl,
            )
