#!/usr/bin/env python3
"""
Created on Tue Aug 12 18:35:00 2025.

@author: pierrot

"""

from numpy import amax
from numpy import argmax
from numpy import unravel_index
from numpy.typing import NDArray
from pandas import DataFrame


def _validate_n_prev(n_prev: list[int], n_dataframes: int) -> None:
    """
    Validate 'n_prev' parameter.

    Parameters
    ----------
    n_prev : list[int]
        Number of previous values to include for each dataframe.
    n_dataframes : int
        Number of dataframes per group.

    Raises
    ------
    ValueError
        - If 'n_prev' length doesn't match number of dataframes or contains
          invalid values.

    """
    if len(n_prev) != n_dataframes:
        raise ValueError(
            f"'n_prev' must have length '{n_dataframes}' (number of dataframes "
            f"per group), got '{len(n_prev)}'.",
        )
    if any(_n_prev < 0 for _n_prev in n_prev):
        raise ValueError("all values in 'n_prev' must be >= 0.")


def _validate_df_groups(
    n_dfs_per_group: int,
    df_groups: list[list[DataFrame]],
) -> None:
    """
    Validate 'df_groups' parameter.

    Parameters
    ----------
    n_dfs_per_group : int
        Number of dataframes per group.
    df_groups : list[list[DataFrame]]
        The dataframe structure to join.

    Raises
    ------
    ValueError
        - If a group do not have the same number of dataframes as 'n_dfs_per_group'.
        - If dataframes at same position across groups do not share the same
          column names and same dtypes.

    """
    columns_names = [df.columns for df in df_groups[0]]
    columns_dtypes = [df.dtypes for df in df_groups[0]]
    for group_id, group in enumerate(df_groups):
        if len(group) != n_dfs_per_group:
            raise ValueError(
                f"group '{group_id}' must have the same number of "
                f"dataframes as 'n_dfs_per_group' ({n_dfs_per_group}).",
            )
        for df_idx, df in enumerate(group):
            if not df.columns.equals(columns_names[df_idx]):
                raise ValueError(
                    f"dataframe '{df_idx}' in group '{group_id}' "
                    "must have the same columns as the "
                    "corresponding dataframe in the first group.",
                )
            if not df.dtypes.equals(columns_dtypes[df_idx]):
                raise ValueError(
                    f"dataframe '{df_idx}' in group '{group_id}' "
                    "must have the same dtypes as the "
                    "corresponding dataframe in the first group.",
                )


def _validate_combinations(
    main: NDArray,
    df_groups: list[list[DataFrame]],
    combinations: NDArray,
) -> None:
    """
    Validate consistency between 'main', 'df_groups', and 'combinations'.

    Parameters
    ----------
    main : NDArray
        Target values for alignment.
    df_groups : List[List[DataFrame]]
        The nested dataframe structure to join.
    combinations : NDArray
        The combinations array containing group indices to join for each output
        row.
        - 'combinations' must have the same length as 'main'.
        - All output rows must specify the same number of groups (fixed width),
        - Group indices refer to positions in the outer list of `df_groups`,

    Raises
    ------
    ValueError
        - If 'main' and 'combinations' are not of same length.
        - If max value in 'combinations' is greater or equal to length of
          'df_groups'.

    """
    if len(main) != len(combinations):
        raise ValueError(
            "'main' and 'combinations' must have the same length.",
        )
    if amax(combinations) >= len(df_groups):
        max_val = amax(combinations)
        max_idx = unravel_index(
            argmax(combinations, axis=None),
            combinations.shape,
        )
        # Increment back column index.
        max_idx = (int(max_idx[0]), int(max_idx[1]) + 1)
        raise ValueError(
            f"max value '{max_val}' at position '{max_idx}' in 'combinations' "
            "must be less than 'df_groups' length .",
        )


def _validate_fill_values_init(
    *,
    on: str,
    df_groups: list[list[DataFrame]],
    n_prev: list[int],
    fill_values_init: list[list[DataFrame]],
) -> None:
    """
    Validate consistency between 'n_prev', 'fill_values_init', and 'df_groups'.

    Parameters
    ----------
    on : str
        Name of the column to join on. This column is not compulsory in
        dataframes that can be found in 'fill_values_init'.
    df_groups : list[list[DataFrame]]
        The nested dataframe structure
    n_prev : list[int]
        Number of previous values to include for each dataframe.
    fill_values_init : list[list[DataFrame]]
        Fill data for when insufficient previous values exist in original data.
        Structure mirrors `df_groups`. Each group must contain the same number
        of dataframes. Each provided data array must have ``n_prev + 1`` rows:
        the leading extra row is a guard used when the first 'main' value
        precedes the first 'df_on' value. For dataframes with `n_prev = 0`, at
        least 1 row is needed for guard operations during asof merge.

    Raises
    ------
    ValueError
        - If 'fill_values_init' is not of same length than 'df_groups'.
        - If dataframes at same position across the groups in 'df_groups' and
          'fill_values_init' do not share same column names (excluding 'on' column).
        - If the number of dataframes in a group in 'fill_values_init' is different
          than 'n_prev' length.
        - If the number of rows in a dataframe in 'fill_values_init' is not
          equal to 'n_prev' for the corresponding dataframe in a group plus 1.

    """
    # If 'fill_values_init' is a list, check it is consistent with 'n_prev' and
    # 'df_groups'.
    if len(fill_values_init) != len(df_groups):
        raise ValueError(
            "'fill_values_init' must have the same number of groups as 'df_groups'.",
        )
    for group_id, group in enumerate(df_groups):
        if len(fill_values_init[group_id]) != len(n_prev):
            raise ValueError(
                f"'fill_values_init' of group '{group_id}' must have the same number "
                f"of dataframes as specified in 'n_prev' ({len(n_prev)}).",
            )
        for df_idx, n_prev_values in enumerate(n_prev):
            # Validate columns for DataFrame input.
            if (
                not fill_values_init[group_id][df_idx]
                .columns.drop(on, errors="ignore")
                .equals(
                    group[df_idx].columns.drop(on),
                )
            ):
                raise ValueError(
                    f"df '{df_idx}' in group '{group_id}' of 'fill_values_init' must "
                    "have the same columns as corresponding df in 'df_groups'.",
                )
            # Validate row count: each DataFrame must have n_prev + 1 rows
            # (even when n_prev = 0, this means at least 1 row for guard operations)
            if len(fill_values_init[group_id][df_idx]) != n_prev_values + 1:
                raise ValueError(
                    f"df '{df_idx}' in group '{group_id}' of 'fill_values_init' must "
                    f"have {n_prev_values + 1} rows (n_prev + 1).",
                )


def _validate_params(
    *,
    main: NDArray,
    n_dfs_per_group: int,
    df_groups: list[list[DataFrame]],
    combinations: NDArray | None,
) -> None:
    """
    Validate parameters for CombAsofMerger and related functions.

    Parameters
    ----------
    main : NDArray
        Target values for alignment.
    n_dfs_per_group : int
        Number of dataframes per group.
    df_groups : list[list[DataFrame]]
        Nested dataframe structure to join. When ``combinations`` is None,
        callers normalize inputs before invoking this function.
    combinations : Optional[NDArray]
        The combinations array containing group indices to join for each output
        row. If None, only a single join position is allowed.

    Raises
    ------
    ValueError
        - Checks on 'df_groups':
            - If a group do not have the same number of dataframes as
              'n_dfs_per_group'.
            - If dataframes at same position across groups do not share the same
            column names and same dtypes.
        - Checks on 'combinations':
            - If 'main' and 'combinations' are not of same length.
            - If max value in 'combinations' is greater or equal to length of
            'df_groups'.

    """
    _validate_df_groups(n_dfs_per_group=n_dfs_per_group, df_groups=df_groups)
    _validate_combinations(
        main=main,
        df_groups=df_groups,
        combinations=combinations,
    )


def _validate_monotonic_increasing(
    main: NDArray,
    df_groups: list[list[DataFrame]],
    on: str,
) -> None:
    """
    Check that ``main`` and each dataframe's ``on`` columns are increasing.

    Parameters
    ----------
    main : NDArray
        Target values for alignment (must be increasing when checking).
    df_groups : list[list[DataFrame]]
        Nested list of dataframes whose ``on`` columns must be increasing.
    on : str
        Column name to validate in each dataframe.

    Raises
    ------
    ValueError
        If ``main`` or any dataframe ``on`` column is not increasing.

    """
    if len(main) > 1 and not (main[1:] >= main[:-1]).all():
        raise ValueError(
            "'main' must be increasing when 'check_sorted=True'.",
        )
    for group in df_groups:
        for df in group:
            if not df.loc[:, on].is_monotonic_increasing:
                raise ValueError(
                    "all df 'on' columns must be increasing when 'check_sorted=True'.",
                )
