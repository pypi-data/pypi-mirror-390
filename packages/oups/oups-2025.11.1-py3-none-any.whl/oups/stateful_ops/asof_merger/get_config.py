#!/usr/bin/env python3
"""
Created on Sat Jun 28 18:35:00 2025.

@author: pierrot

"""
from collections import defaultdict
from typing import TypedDict

from numpy import zeros
from numpy.typing import DTypeLike
from numpy.typing import NDArray
from pandas import DataFrame
from pandas import Index


KEY_COLS_PER_DTYPE = "cols_per_dtype"
KEY_COLS_SLICES_IN_DF_PER_DTYPE = "cols_slices_in_df_per_dtype"
KEY_COLS_REINDEX_IN_DF = "cols_reindex_in_df"
KEY_COLS_SLICES_IN_RES_PER_JOIN_POS = "cols_slices_in_res_per_join_pos"
KEY_COLS_DTYPES_SLICES_IN_RES_PER_COL_NAME = "cols_dtypes_slices_in_res_per_col_name"
KEY_N_RES_COLS_PER_DTYPE = "n_res_cols_per_dtype"
KEY_SEED_RES_ARRAYS = "seed_res_arrays"


class ColsCache(TypedDict):
    """
    Cache of per-dataframe dtype metadata.

    - cols_per_dtype: columns grouped by dtype per dataframe
    - cols_slices_in_df_per_dtype: contiguous column slices per dtype per dataframe
    - cols_reindex_in_df: target column order per dataframe (with filtered keys first)

    """

    cols_per_dtype: list[dict[DTypeLike, list[str]]]
    cols_slices_in_df_per_dtype: list[dict[DTypeLike, slice]]
    cols_reindex_in_df: list[Index]


class ResCache(TypedDict):
    """
    Computed layout for result arrays across join positions.

    - cols_slices_in_res_per_join_pos: for each join position and dataframe, slice per dtype
    - cols_dtypes_slices_in_res_per_col_name: lookup from output column name to (dtype, slice)
    - n_res_cols_per_dtype: total number of result columns per dtype

    """

    cols_slices_in_res_per_join_pos: list[list[dict[DTypeLike, slice]]]
    cols_dtypes_slices_in_res_per_col_name: dict[str, tuple[DTypeLike, slice]]
    n_res_cols_per_dtype: dict[DTypeLike, int]


class Config(TypedDict):
    """
    Final configuration for combine-merge-asof result materialization.

    - cols_slices_in_df_per_dtype: contiguous df column slices per dtype
    - cols_reindex_in_df: target column order per dataframe
    - cols_slices_in_res_per_join_pos: result array slices per join position/df/dtype
    - cols_dtypes_slices_in_res_per_col_name: mapping from output name to (dtype, slice)
    - seed_res_arrays: preallocated empty arrays per dtype, ready to be resized

    """

    cols_slices_in_df_per_dtype: list[dict[DTypeLike, slice]]
    cols_reindex_in_df: list[Index]
    cols_slices_in_res_per_join_pos: list[list[dict[DTypeLike, slice]]]
    cols_dtypes_slices_in_res_per_col_name: dict[str, tuple[DTypeLike, slice]]
    seed_res_arrays: dict[DTypeLike, NDArray]


def _get_cols_cache(
    cols_dtypes_per_df: list[dict[str, DTypeLike]],
    filter_out: list[str],
) -> ColsCache:
    """
    Get list of dicts with columns per dtype for each dataframe in a group.

    Parameters
    ----------
    cols_dtypes_per_df : list[dict[str, DTypeLike]]
        List of dict specifying for each column in a dataframe its dtype.
        One dict per dataframe in a group. Dictionaries are typically obtained
        with ``df.dtypes.to_dict()``.
    filter_out : list[str]
        List of column names to filter out.

    Returns
    -------
    ColsCache
        - 'cols_per_dtype': List of dicts with columns per dtype for each
          dataframe in a group, ``cols_per_dtype[df_idx][col_dtype]``
        - 'cols_slices_in_df_per_dtype': List of dicts with slices per dtype for
          each dataframe in a group, ``cols_slices_in_df_per_dtype[df_idx][col_dtype]``
        - 'cols_reindex_in_df': List[Index] with column order to reindex each
          dataframe in a group, ``cols_reindex_in_df[df_idx]``

    """
    cols_per_dtype: list[dict[DTypeLike, list[str]]] = []
    cols_slices_in_df_per_dtype: list[dict[DTypeLike, slice]] = []
    cols_reindex_in_df: list[Index] = []
    for cols_dtypes_in_df in cols_dtypes_per_df:
        cols_per_dtype_per_df: dict[DTypeLike, list[str]] = defaultdict(list)
        for col, col_dtype in cols_dtypes_in_df.items():
            if col not in filter_out:
                cols_per_dtype_per_df[col_dtype].append(col)
        cols_per_dtype.append(cols_per_dtype_per_df)
        cols_slices_in_df_per_dtype.append(
            {dt: slice(cols[0], cols[-1]) for dt, cols in cols_per_dtype_per_df.items()},
        )
        cols_reindex_in_df.append(
            Index(
                filter_out + [col for cols in cols_per_dtype_per_df.values() for col in cols],
            ),
        )

    return {
        KEY_COLS_PER_DTYPE: cols_per_dtype,
        KEY_COLS_SLICES_IN_DF_PER_DTYPE: cols_slices_in_df_per_dtype,
        KEY_COLS_REINDEX_IN_DF: cols_reindex_in_df,
    }


def _get_res_cache(
    cols_per_dtype: list[dict[DTypeLike, list[str]]],
    n_join_positions: int,
    prefixes: list[list[str]] | None,
    n_prev: list[int],
    n_prev_suffix_start: int,
) -> ResCache:
    """
    Compute column layout metadata for result arrays from ``comb_merge_asof``.

    This function pre-computes the column slicing information needed to
    place results from different dataframes into the final result arrays.
    Results of precomputations can be accessed using an indexed structure
    organized by:
     - join position,
     -> dataframe index in group,
     -> dtype,
     -> column_slices.

    Parameters
    ----------
    cols_per_dtype : list[dict[DTypeLike, list[str]]]
        List of dicts mapping dtype to column lists for each dataframe in a
        group. Example:
        [{dtype('int64'): ['col1', 'col2']}, {dtype('float64'): ['col3']}]
    n_join_positions : int
        Number of join positions (``combinations.shape[1]``).
    prefixes : list[list[str]] | None
        Nested list of column prefixes for each dataframe at each join position.
        Shape: ``[n_join_positions][n_dataframes]``
        Example for 2 join positions, 2 dfs each:
        ``[['left_', 'right_'], ['left_', 'right_']]``
    n_prev : list[int]
        Number of previous values to include for each dataframe.
        Length must equal ``len(cols_per_dtype)``, one per dataframe in a group.
    n_prev_suffix_start : int
        Starting index for previous value suffixes in column names.
        If ``n_prev_suffix_start=0`` and ``n_prev[i]=2``, suffixes will be
        ``'_0'``, ``'_1'``, ``'_2'``.

    Returns
    -------
    ResCache
        Dictionary with keys:
        - 'cols_slices_in_res_per_join_pos': List[List[Dict[dtype, slice]]]
          Column slices organized as [join_pos][df_idx][dtype] = slice(start, end)
        - 'cols_dtypes_slices_in_res_per_col_name': dict[str, tuple[dtype, slice]]
          Individual column name to dtype and slice mapping for quick lookups.
        - 'n_res_cols_per_dtype': Dict[dtype, int]
          Total expected number of columns per dtype in the result array.

    """
    if prefixes is None:
        prefixes = [[""] * len(cols_per_dtype) for _ in range(n_join_positions)]
    # Indexing in res is made by
    # join_pos -> df_idx -> dtype -> col_name -> slice in res
    cols_slices_in_res_per_join_pos: list[list[dict[DTypeLike, slice]]] = []
    # Without parameter, 'int()' returns 0.
    dtype_offsets: dict[DTypeLike, int] = defaultdict(int)
    cols_dtypes_slices_in_res_per_col_name: dict[str, tuple[DTypeLike, slice]] = {}
    # Create range for values: [current] if n_prev=0, [prev_values + current]
    # if n_prev>0.
    # When expanded, previous values are ordered from earliest to latest.
    value_range = [
        range(
            n_prev_suffix_start + n_prev[df_idx],
            n_prev_suffix_start - 1,
            -1,
        )
        for df_idx in range(len(cols_per_dtype))
    ]
    for join_pos_idx in range(n_join_positions):
        slices_by_df: list[dict[DTypeLike, slice]] = []
        for df_idx, cols_per_df_per_dtype in enumerate(cols_per_dtype):
            slices_by_dtype: dict[DTypeLike, slice] = {}
            n_prev_for_current_df = n_prev[df_idx]
            for col_dtype, cols in cols_per_df_per_dtype.items():
                # Store current offset before updating (needed for individual column slices)
                current_dtype_offset = dtype_offsets[col_dtype]
                new_offset_with_current_df = (n_prev_for_current_df + 1) * len(
                    cols,
                ) + current_dtype_offset
                slices_by_dtype[col_dtype] = slice(current_dtype_offset, new_offset_with_current_df)
                dtype_offsets[col_dtype] = new_offset_with_current_df
                for col_idx, col in enumerate(cols):
                    for value_idx, n_prev_idx in enumerate(value_range[df_idx]):
                        # Column name: add suffix only for n_prev > 0. For
                        # dataframes with previous values, expanded columns
                        # for a given source column are ordered from earliest
                        # previous to current.
                        col_name = f"{prefixes[join_pos_idx][df_idx]}{col}" + (
                            f"_{n_prev_idx}" if n_prev_for_current_df > 0 else ""
                        )
                        # Calculate global position within this dtype's result array
                        global_col_position = (
                            current_dtype_offset + col_idx * (n_prev_for_current_df + 1) + value_idx
                        )
                        cols_dtypes_slices_in_res_per_col_name[col_name] = (
                            col_dtype,
                            slice(global_col_position, global_col_position + 1),
                        )
            slices_by_df.append(slices_by_dtype)
        cols_slices_in_res_per_join_pos.append(slices_by_df)
    return {
        KEY_COLS_SLICES_IN_RES_PER_JOIN_POS: cols_slices_in_res_per_join_pos,
        KEY_COLS_DTYPES_SLICES_IN_RES_PER_COL_NAME: cols_dtypes_slices_in_res_per_col_name,
        KEY_N_RES_COLS_PER_DTYPE: dtype_offsets,
    }


def _initialize_fill_values(
    n_df_groups: int,
    cols_per_dtype: list[dict[DTypeLike, list[str]]],
    n_prev: list[int],
    fill_values_init: list[list[DataFrame]] | None,
) -> list[list[dict[DTypeLike, NDArray]]]:
    """
    Initialize 'fill_values' parameter.

    Parameters
    ----------
    n_df_groups : int
        Number of groups of dataframes.
    cols_per_dtype : list[dict[DTypeLike, list[str]]]
        List of dict with list of columns per dtype, one dict per dataframe in a
        group, omitting 'on' column.
    n_prev : list[int]
        Number of previous values to include for each dataframe.
    fill_values_init : list[list[DataFrame]] | None
        When a list of list of dataframes, each dataframe has to provide
        ``n_prev + 1`` rows: the leading extra row is a guard used when the
        first 'main' value precedes the first 'df_on' value.

    Returns
    -------
    list[list[dict[DTypeLike, NDArray]]]
        If 'fill_values_init' is None, return a list of list of dicts
        with arrays initialized to 0 and shaped (n_prev + 1, n_cols) per dtype.
        If 'fill_values_init' is a list of list of dataframes, arrays returned
        contain values from dataframes in initial 'fill_values_init'.
        Only columns present in 'cols_per_dtype' are included in resulting
        array. 'on' column is thus filtered out from result arrays.

    """
    if fill_values_init is None:
        # Initialize 'fill_values_init' if None.
        return [
            [
                {
                    dtype: zeros((n_prev[df_id] + 1, len(cols)), dtype=dtype)
                    for dtype, cols in cols_per_dtype_per_df.items()
                }
                for df_id, cols_per_dtype_per_df in enumerate(cols_per_dtype)
            ]
            for _ in range(n_df_groups)
        ]
    elif isinstance(fill_values_init[0][0], DataFrame):
        # If a list of list of DataFrames, transform into a list of list of
        # dicts with arrays (per dtype).
        return [
            [
                {
                    col_dtype: fill_value_df[cols].to_numpy()
                    for col_dtype, cols in cols_per_dtype[df_idx].items()
                }
                for df_idx, fill_value_df in enumerate(fill_value_group)
            ]
            for fill_value_group in fill_values_init
        ]


def _get_config(
    cols_dtypes_per_df: list[dict[str, DTypeLike]],
    filter_out: list[str],
    n_join_positions: int,
    prefixes: list[list[str]] | None,
    n_prev: list[int],
    n_prev_suffix_start: int,
) -> Config:
    """
    Get configuration for combine-asof-merge result materialization.

    Parameters
    ----------
    cols_dtypes_per_df : list[dict[str, DTypeLike]]
        List of dict specifying for each column in a dataframe its dtype.
        One dict per dataframe in a group. Dictionaries are typically obtained
        with ``df.dtypes.to_dict()``.
    filter_out : list[str]
        List of column names to filter out (will not be accounted for in result
        arrays).
    n_join_positions : int
        Number of join positions (``combinations.shape[1]``).
    prefixes : list[list[str]] | None
        Nested list of column prefixes for each dataframe at each join position.
        Shape: ``[n_join_positions][n_dataframes]``. If None, empty prefixes are
        generated downstream by callers.
    n_prev : list[int]
        Number of previous values to include for each dataframe in a join
        position. Length must equal ``len(cols_dtypes_per_df)``.
    n_prev_suffix_start : int
        Starting index for previous value suffixes in column names.
        If ``n_prev_suffix_start=0`` and ``n_prev[i]=2``, suffixes will be
        ``'_0'``, ``'_1'``, ``'_2'``.

    Returns
    -------
    Config
        Dictionary with keys:
        - 'cols_per_dtype': list[dict[DTypeLike, list[str]]]
        - 'cols_reindex_in_df': list[Index]
        - 'cols_slices_in_df_per_dtype': list[dict[DTypeLike, slice]]
        - 'seed_res_arrays': dict[DTypeLike, ndarray], one result array for each
          dtype.
        - 'cols_slices_in_res_per_join_pos': list[list[dict[DTypeLike, slice]]]
        - 'cols_dtypes_slices_in_res_per_col_name': dict[str, tuple[DTypeLike, slice]]

    Notes
    -----
    Target usage of these dicts are to iterate over them to set result arrays
    in-place as follows:

    ```python
    # Reindex all dataframes to make sure creating views by column slicing
    # is possible. 'on' column will be in first position.
    for group in groups:
        for df_idx, df in enumerate(group):
            df = df.reindex(columns=cols_reindex_in_df[df_idx])

    # Appropriately resize result arrays.
    for array in seed_res_arrays.values():
        array.resize((expected_n_rows, array.shape[1]))

    # Get row indices appropriately per join positions for each dataframe.
    row_indices = [[...], [...]]  # Shape: [n_join_positions][n_dataframes]

    # Set result arrays in-place.
    for join_pos in range(n_join_positions):
        for group in groups:
            for df_idx, df in enumerate(group):
                for col_dtype, cols_slice in cols_slices_in_df_per_dtype[df_idx].items():
                    seed_res_arrays[col_dtype][
                        cols_slices_in_res_per_join_pos[join_pos][df_idx][col_dtype]
                    ] = (
                        df.iloc[row_indices[join_pos][df_idx]][cols_slice]

    # Later on, assemble result arrays into a single dataframe.
    res = DataFrame({col_name: seed_res_arrays[col_dtype][_slice]
                     for col_name, (col_dtype, _slice)
                     in cols_dtypes_slices_in_res_per_col_name.items()})

    ```

    """
    cols_cache = _get_cols_cache(cols_dtypes_per_df, filter_out)
    res_cache = _get_res_cache(
        cols_per_dtype=cols_cache[KEY_COLS_PER_DTYPE],
        n_join_positions=n_join_positions,
        prefixes=prefixes,
        n_prev=n_prev,
        n_prev_suffix_start=n_prev_suffix_start,
    )
    return {
        KEY_COLS_PER_DTYPE: cols_cache[KEY_COLS_PER_DTYPE],
        KEY_COLS_REINDEX_IN_DF: cols_cache[KEY_COLS_REINDEX_IN_DF],
        KEY_COLS_SLICES_IN_DF_PER_DTYPE: cols_cache[KEY_COLS_SLICES_IN_DF_PER_DTYPE],
        # Initialize a dict of arrays with the correct dtype {dtype: array}.
        KEY_SEED_RES_ARRAYS: {
            col_dtype: zeros((0, n_cols), dtype=col_dtype)
            for col_dtype, n_cols in res_cache[KEY_N_RES_COLS_PER_DTYPE].items()
        },
        KEY_COLS_SLICES_IN_RES_PER_JOIN_POS: res_cache[KEY_COLS_SLICES_IN_RES_PER_JOIN_POS],
        KEY_COLS_DTYPES_SLICES_IN_RES_PER_COL_NAME: res_cache[KEY_COLS_DTYPES_SLICES_IN_RES_PER_COL_NAME],
    }
