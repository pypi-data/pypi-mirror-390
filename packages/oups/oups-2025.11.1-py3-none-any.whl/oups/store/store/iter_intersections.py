#!/usr/bin/env python3
"""
Created on Mon May 26 18:00:00 2025.

@author: pierrot

"""
from collections import defaultdict
from collections.abc import Iterator

from numpy import arange
from numpy import full
from numpy import insert
from numpy import nan
from numpy import ones
from numpy import r_
from numpy import roll
from numpy import searchsorted
from pandas import DataFrame
from pandas import Int64Dtype
from pandas import Timestamp
from pandas import concat

from oups.defines import KEY_N_ROWS
from oups.defines import KEY_ORDERED_ON_MAXS
from oups.defines import KEY_ORDERED_ON_MINS
from oups.numpy_utils import isnotin_ordered
from oups.store.indexer import StoreKey
from oups.store.ordered_parquet_dataset import OrderedParquetDataset


KEY_LEFT = "left"


def _get_and_validate_ordered_on_column[K: StoreKey](datasets: dict[K, OrderedParquetDataset]) -> str:
    """
    Get and validate the 'ordered_on' column name across all datasets.

    Parameters
    ----------
    datasets : dict[K, OrderedParquetDataset]
        Dictionary mapping dataset keys to their corresponding datasets.

    Returns
    -------
    str
        The common 'ordered_on' column name.

    Raises
    ------
    ValueError
        If ordered_on column names differ between datasets.

    """
    # Get 'ordered_on' from first key.
    iter_datasets = iter(datasets.items())
    first_key, first_dataset = next(iter_datasets)
    # Validate all keys have the same 'ordered_on' column.
    for key, dataset in iter_datasets:
        if dataset.ordered_on != first_dataset.ordered_on:
            raise ValueError(
                f"inconsistent 'ordered_on' columns. '{first_key}' has "
                f"'{first_dataset.ordered_on}', but '{key}' has '{dataset.ordered_on}'.",
            )
    return first_dataset.ordered_on


def _get_intersections[K: StoreKey](
    datasets: dict[K, OrderedParquetDataset],
    start: float | Timestamp | None = None,
    end_excl: float | Timestamp | None = None,
) -> tuple[dict[K, int], dict[K, int], Iterator[tuple]]:
    """
    Create an iterator over intersection boundaries with row group indices.

    This function analyzes row group statistics across all keys to determine
    intersection boundaries and the corresponding row group indices for each
    key. Returns starting row group indices, first ending indices, and
    intersection boundaries.

    Parameters
    ----------
    datasets : dict[K, OrderedParquetDataset]
        Dictionary mapping dataset keys to their corresponding datasets.
    start : Optional[Union[int, float, Timestamp]], default None
        Start value for the 'ordered_on' column range.
    end_excl : Optional[Union[int, float, Timestamp]], default None
        End value (exclusive) for the 'ordered_on' column range.

    Returns
    -------
    tuple[dict[K, int], dict[K, int], Iterator[tuple]]
        tuple containing:
        - Dictionary mapping each key to its starting row group index,
        - Dictionary mapping each key to its first ending row group index
          (exclusive) in the trimmed range,
        - Iterator yielding (current_end_excl, rg_idx_ends_excl) tuples where:
          * current_end_excl: End boundary (exclusive) for current intersection
          * rg_idx_ends_excl: dict mapping each key to its row group index for
            this intersection

    Notes
    -----
    - A key without value in the span of interest will not appear in returned
      dict of row group indices (start, first end excl, and end excl).
    - The first row group to appear for each key is loaded right at the first
      iteration, even though it would not be needed immediately.
    - For a given dataset, successive row groups sharing same 'ordered_on'
      values (last of first row group is equal to first of second row group) are
      'collapsed' into a single row group. More exactly, indices returned to
      'iter_intersections()' will ensure that both row groups (as many as
      complying with the condition) are returned as a single row group.
      This may result in larger intersections being yielded in a same iteration
      by 'iter_intersections()'.

    """
    if isinstance(start, Timestamp):
        start = start.to_numpy()
    if isinstance(end_excl, Timestamp):
        end_excl = end_excl.to_numpy()
    # Store "ordered_on_mins" in a dict, only keeping unique value and
    # corresponding row group indices.
    unique_ordered_on_mins = None
    keys_ordered_on_ends_excl = {}
    keys_rg_idx_starts = {}
    keys_rg_idx_first_ends_excl = {}
    keys_rg_idx_ends_excl = {}
    for key, dataset in datasets.items():
        row_group_stats = dataset.row_group_stats
        ordered_on_mins = row_group_stats.loc[:, KEY_ORDERED_ON_MINS].to_numpy()
        ordered_on_maxs = row_group_stats.loc[:, KEY_ORDERED_ON_MAXS].to_numpy()
        n_rgs = len(row_group_stats)
        # Main row groups are those not overlapping with next ones.
        mask_main_rgs_for_mins = ones(n_rgs).astype(bool)
        mask_main_rgs_for_mins[1:] = ordered_on_mins[1:] != ordered_on_maxs[:-1]
        mask_main_rgs_for_maxs = roll(mask_main_rgs_for_mins, -1)
        # Skip first row group in trimming.
        trim_idx_first_end_excl = (
            searchsorted(ordered_on_maxs[mask_main_rgs_for_maxs], start, side=KEY_LEFT) + 1 if start else 1
        )
        _unique_ordered_on_mins = ordered_on_mins[mask_main_rgs_for_mins]
        trim_idx_last_end_excl = (
            searchsorted(_unique_ordered_on_mins, end_excl, side=KEY_LEFT)
            if end_excl
            else len(_unique_ordered_on_mins)
        )
        # 'unique_rg_idx_ends_excl' is completed with its length as last value.
        if trim_idx_first_end_excl < trim_idx_last_end_excl + 1:
            keys_ordered_on_ends_excl[key] = _unique_ordered_on_mins[
                trim_idx_first_end_excl:trim_idx_last_end_excl
            ]
            # Collect 'ordered_on_mins' for each key, keeping unique values only.
            if unique_ordered_on_mins is None:
                unique_ordered_on_mins = keys_ordered_on_ends_excl[key]
            else:
                is_not_found, unfound_insert_idx = isnotin_ordered(
                    sorted_array=unique_ordered_on_mins,
                    query_elements=keys_ordered_on_ends_excl[key],
                    return_insert_positions=True,
                )
                unique_ordered_on_mins = insert(
                    unique_ordered_on_mins,
                    unfound_insert_idx,
                    keys_ordered_on_ends_excl[key][is_not_found],
                )
            rg_idx = arange(n_rgs)
            _unique_rg_idx_ends_excl = r_[rg_idx[mask_main_rgs_for_mins], n_rgs]
            keys_rg_idx_starts[key] = _unique_rg_idx_ends_excl[trim_idx_first_end_excl - 1]
            keys_rg_idx_ends_excl[key] = _unique_rg_idx_ends_excl[
                trim_idx_first_end_excl : trim_idx_last_end_excl + 1
            ]
            keys_rg_idx_first_ends_excl[key] = keys_rg_idx_ends_excl[key][0]
    if unique_ordered_on_mins is None:
        return {}, {}, iter([])
    # Adding one for last value, will be either 'end_excl' or None.
    len_unique_ordered_on_mins = len(unique_ordered_on_mins) + 1
    for key, rg_idx_ends_excl in keys_rg_idx_ends_excl.items():
        _rg_idx_ends_excl = full(len_unique_ordered_on_mins, nan)
        # Forcing last row group index, which cannot be always positioned,
        # in the case 'end_excl' is None, and therefore is not in
        # 'keys_ordered_on_ends_excl[key]'.
        _rg_idx_ends_excl[-1] = rg_idx_ends_excl[-1]
        confirmed_ordered_on_ends_excl_idx = searchsorted(
            unique_ordered_on_mins,
            keys_ordered_on_ends_excl[key],
            side=KEY_LEFT,
        )
        _rg_idx_ends_excl[confirmed_ordered_on_ends_excl_idx] = rg_idx_ends_excl[
            : len(confirmed_ordered_on_ends_excl_idx)
        ]
        keys_rg_idx_ends_excl[key] = _rg_idx_ends_excl
    intersections = DataFrame(keys_rg_idx_ends_excl, dtype=Int64Dtype())
    intersections.bfill(axis=0, inplace=True)
    return (
        keys_rg_idx_starts,
        keys_rg_idx_first_ends_excl,
        zip(
            list(unique_ordered_on_mins) + [end_excl],
            intersections.to_dict(orient="records"),
            strict=False,
        ),
    )


def _initialize_first_load[K: StoreKey](
    datasets: dict[K, OrderedParquetDataset],
    ordered_on_col_name: str,
    rg_idx_starts: dict[K, int],
    prev_rg_idx_ends_excl: dict[K, int],
    start: float | Timestamp | None,
    n_prev: list[int],
) -> tuple[dict[K, DataFrame], dict[K, int | None]]:
    """
    Prepare first in-memory dataframes and initial start indices, honoring n_prev.

    Parameters
    ----------
    datasets : dict[K, OrderedParquetDataset]
        Datasets to read from.
    ordered_on_col_name : str
        Column used for ordering.
    rg_idx_starts : dict[K, int]
        Row-group start indices for each key.
    prev_rg_idx_ends_excl : dict[K, int]
        First row-group end-excluded indices within the trimmed range.
    start : Union[int, float, Timestamp, None]
        Start boundary (inclusive).
    n_prev : list[int]
        Number of previous rows to prepend to the first slice if available.

    Returns
    -------
    tuple[dict[K, DataFrame], dict[K, Optional[int]]]
        in_memory_data and current_start_indices for the first iteration.

    Notes
    -----
    - When additional rows are needed, only the minimal number of previous
      row-groups is loaded, and only their tail rows necessary to reach
      'n_prev' are kept.

    """
    # Base first load.
    in_memory_data = {
        key: datasets[key][rg_idx_start : prev_rg_idx_ends_excl[key]].to_pandas()
        for key, rg_idx_start in rg_idx_starts.items()
    }
    # Fast-path when no 'start' anchor.
    if start is None:
        return in_memory_data, defaultdict(lambda: None)

    # Else, compute initial start indices anchored at 'start'.
    current_start_indices = {
        key: df.loc[:, ordered_on_col_name].searchsorted(start, side=KEY_LEFT)
        for key, df in in_memory_data.items()
    }
    # Fast-path when no 'n_prev' anchor.
    if not any(n_prev):
        return in_memory_data, current_start_indices

    # Else, shift start indices backward by 'n_prev' if possible.
    # Load minimal previous data if needed.
    for key_idx, (key, df) in enumerate(in_memory_data.items()):
        # Fast-path when no previous rows are needed.
        if n_prev[key_idx] == 0:
            continue
        new_idx = current_start_indices[key] - n_prev[key_idx]
        # Fast-path when no previous row groups are needed.
        if new_idx >= 0:
            current_start_indices[key] = new_idx
            continue
        # Else, need to fetch previous rows from prior row groups.
        missing = -new_idx
        rg_idx_start = rg_idx_starts[key]
        # Fast-path when no previous row groups are available.
        if rg_idx_start == 0:
            current_start_indices[key] = 0
            continue
        n_rows_array = datasets[key].row_group_stats.loc[:, KEY_N_ROWS].to_numpy()
        sum_rows = 0
        for first_needed_rg in range(rg_idx_start - 1, -1, -1):
            sum_rows += int(n_rows_array[first_needed_rg])
            if sum_rows >= missing:
                break
        # Load previous row groups.
        prev_block = datasets[key][first_needed_rg:rg_idx_start].to_pandas()
        # Add previous rows to in-memory data.
        prev_tail = prev_block.iloc[-min(missing, len(prev_block)) :, :]
        in_memory_data[key] = concat([prev_tail, df], ignore_index=True)
        current_start_indices[key] = 0
    return in_memory_data, current_start_indices


def iter_intersections[K: StoreKey](
    datasets: dict[K, OrderedParquetDataset],
    start: float | Timestamp | None = None,
    n_prev: int | list[int] = 0,
    end_excl: float | Timestamp | None = None,
) -> Iterator[dict[K, DataFrame]]:
    """
    Iterate over synchronized row groups across multiple datasets in the store.

    This function yields data from multiple datasets (keys) in synchronized
    chunks, ensuring that all returned DataFrames share overlapping spans
    in their 'ordered_on' column. This allows processing 'ordered_on'-aligned
    data from multiple sources.

    Parameters
    ----------
    datasets : dict[K, OrderedParquetDataset]
        Dictionary mapping dataset keys to their corresponding datasets.
    start : Optional[Union[int, float, Timestamp]], default None
        Start value (inclusive) for the 'ordered_on' column range. If None,
        starts from the earliest value across all specified keys.
    n_prev : Union[int, list[int]], default 0
        Number of previous rows (number of values before 'start') to prepend to
        first dataframe yielded for each key.
        If a list, values are used for each key in the same order as 'datasets'.
    end_excl : Optional[Union[int, float, Timestamp]], default None
        End value (exclusive) for the 'ordered_on' column range. If None,
        continues until the latest value across all specified keys.

    Yields
    ------
    dict[K, DataFrame]
        Dictionary mapping each key to its corresponding DataFrame chunk.
        All DataFrames in each yielded dictionary share a common span in their
        'ordered_on' column using [start, end_excl) semantics (start inclusive,
        end exclusive).

    Notes
    -----
    - All datasets must have an 'ordered_on' column with the same name.
    - The iteration is synchronized: each yield contains data from the same
      span across all datasets.
    - Uses [start, end_excl) interval semantics throughout.

    Examples
    --------
    >>> store = Store(...)
    >>> store[key1].write(data1, ordered_on='timestamp')
    >>> store[key2].write(data2, ordered_on='timestamp')
    >>> for data_dict in store.iter_intersections([key1, key2], start="2022-01-01"):
    ...     df1 = data_dict[key1]  # DataFrame for key1
    ...     df2 = data_dict[key2]  # DataFrame for key2
    ...     # Process synchronized data

    """
    # Get and validate ordered_on column name.
    ordered_on_col_name = _get_and_validate_ordered_on_column(datasets)
    if isinstance(n_prev, int):
        n_prev = [n_prev] * len(datasets)
    if any(_n_prev < 0 for _n_prev in n_prev):
        raise ValueError("'n_prev' values must be greater than or equal to 0.")
    # Get row group indices to start iterations with, and intersections.
    rg_idx_starts, prev_rg_idx_ends_excl, intersections = _get_intersections(
        datasets,
        start,
        end_excl,
    )
    # Load initial row groups and initialize start indices, honoring n_prev.
    in_memory_data, current_start_indices = _initialize_first_load(
        datasets=datasets,
        ordered_on_col_name=ordered_on_col_name,
        rg_idx_starts=rg_idx_starts,
        prev_rg_idx_ends_excl=prev_rg_idx_ends_excl,
        start=start,
        n_prev=n_prev,
    )
    current_end_indices = {}
    for current_end_excl, rg_idx_ends_excl in intersections:
        for key, rg_idx_end_excl in rg_idx_ends_excl.items():
            if rg_idx_end_excl != prev_rg_idx_ends_excl[key]:
                in_memory_data[key] = datasets[key][prev_rg_idx_ends_excl[key] : rg_idx_end_excl].to_pandas()
                prev_rg_idx_ends_excl[key] = rg_idx_end_excl
                # Reset start index to 0 for new row group.
                current_start_indices[key] = 0
            # Calculate end indices for current_end_excl.
            current_end_indices[key] = (
                None
                if current_end_excl is None
                else in_memory_data[key]
                .loc[:, ordered_on_col_name]
                .searchsorted(
                    current_end_excl,
                    side=KEY_LEFT,
                )
            )
        # Yield synchronized views [current_start, current_end_excl)
        yield {
            key: df.iloc[current_start_indices[key] : current_end_indices[key], :].reset_index(
                drop=True,
            )
            for key, df in in_memory_data.items()
        }
        # Buffer end indices for next iteration as start indices.
        current_start_indices = current_end_indices.copy()
