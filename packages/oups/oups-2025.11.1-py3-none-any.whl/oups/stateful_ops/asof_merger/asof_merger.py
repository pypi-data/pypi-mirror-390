#!/usr/bin/env python3
"""
Created on Sat Jun 28 18:35:00 2025.

@author: pierrot

"""

from numpy import concatenate
from numpy import nonzero
from numpy import searchsorted
from numpy import zeros
from numpy.lib.stride_tricks import sliding_window_view
from numpy.typing import DTypeLike
from numpy.typing import NDArray
from pandas import DataFrame

from oups.stateful_ops.asof_merger.get_config import KEY_COLS_DTYPES_SLICES_IN_RES_PER_COL_NAME
from oups.stateful_ops.asof_merger.get_config import KEY_COLS_PER_DTYPE
from oups.stateful_ops.asof_merger.get_config import KEY_COLS_REINDEX_IN_DF
from oups.stateful_ops.asof_merger.get_config import KEY_COLS_SLICES_IN_DF_PER_DTYPE
from oups.stateful_ops.asof_merger.get_config import KEY_COLS_SLICES_IN_RES_PER_JOIN_POS
from oups.stateful_ops.asof_merger.get_config import KEY_SEED_RES_ARRAYS
from oups.stateful_ops.asof_merger.get_config import _get_config
from oups.stateful_ops.asof_merger.get_config import _initialize_fill_values
from oups.stateful_ops.asof_merger.validate_params import _validate_fill_values_init
from oups.stateful_ops.asof_merger.validate_params import _validate_monotonic_increasing
from oups.stateful_ops.asof_merger.validate_params import _validate_n_prev
from oups.stateful_ops.asof_merger.validate_params import _validate_params


RIGHT = "right"
LEFT = "left"


def _resize_res_arrays_length(
    seed_res_arrays: dict[DTypeLike, NDArray],
    n_rows: int,
    copy: bool,
) -> dict[DTypeLike, NDArray]:
    """
    Provide views on ``seed_res_arrays`` sized to ``n_rows``.

    Parameters
    ----------
    seed_res_arrays : dict[DTypeLike, NDArray]
        Mapping of dtype to 2D result arrays. Seed arrays are resized in-place
        only when their current number of rows is smaller than ``n_rows``.
    n_rows : int
        Target number of rows for all result arrays.
    copy : bool
        If True, return a copy of the result arrays.

    Returns
    -------
    dict[DTypeLike, NDArray]
        Mapping of dtype to 2D array views with exactly ``n_rows`` rows.

    Notes
    -----
    Returned arrays are views on the underlying storage and have shape
    ``(n_rows, n_cols)``.

    """
    if copy:
        return {
            res_dtype: zeros((n_rows, res_array.shape[1]), dtype=res_dtype)
            for res_dtype, res_array in seed_res_arrays.items()
        }
    else:
        if n_rows > next(iter(seed_res_arrays.values())).shape[0]:
            for res_array in seed_res_arrays.values():
                res_array.resize((n_rows, res_array.shape[1]), refcheck=False)
        return {res_dtype: res_array[:n_rows] for res_dtype, res_array in seed_res_arrays.items()}


def _get_df_row_idx(
    group_main: NDArray,
    df_on: NDArray,
    allow_exact_matches: bool,
) -> tuple[NDArray, bool]:
    """
    Get 'merge_asof' row indices with respect to 'main' for this dataframe.

    Parameters
    ----------
    group_main : NDArray
        Target values for alignment for this group. Must be sorted ascending.
    df_on : NDArray
        Column to use for merging 'asof'. Must be sorted ascending.
    allow_exact_matches : bool
        If False and an exact match is found, use the previous value in the
        dataframe.

    Returns
    -------
    tuple[NDArray, bool]
        - Row indices (one per ``group_main``) referencing the asof-selected
          current row in this dataframe. When the first index would be -1 (the
          first ``group_main`` precedes the first ``df_on`` with the chosen
          side), indices are incremented by 1 to be non-negative.
        - A boolean flag ``use_guard_row`` indicating whether a guard row must
          be included before dataframe values when creating sliding windows.

    Notes
    -----
    - ``group_main`` is expected to be sorted ascending. Because of this
      monotonicity, checking the first computed index is sufficient to know if
      any index would be negative: if the first is non-negative, all are.
    - When ``use_guard_row`` is True, all returned indices are globally
      incremented by 1 so they align with window indices created over the
      concatenation ``[guard_rows] + ar``. This ensures that index 0 selects
      the guard-only window, index 1 selects the window ending at ``ar[0]``,
      and so forth.
    - When ``use_guard_row`` is True, callers should include the leading guard
      row from their ``fill_values`` (i.e., use the full ``n_prev + 1`` rows).
      When False, callers should drop the guard row (use only the last
      ``n_prev`` rows) to keep window alignment consistent.

    """
    df_row_idx = (
        searchsorted(
            df_on,
            group_main,
            side=RIGHT if allow_exact_matches else LEFT,
        )
        - 1
    )
    if df_row_idx[0] < 0:
        return df_row_idx + 1, True
    else:
        return df_row_idx, False


def _comb_merge_asof(
    main: NDArray,
    on: str,
    df_groups: list[list[DataFrame]],
    cols_slices_in_df_per_dtype: list[dict[DTypeLike, slice]],
    combinations: NDArray,
    allow_exact_matches: list[bool],
    n_prev: list[int],
    fill_values: list[list[dict[DTypeLike, NDArray]]],
    res_arrays: dict[DTypeLike, NDArray],
    cols_slices_in_res_per_join_pos: list[list[dict[DTypeLike, slice]]],
) -> None:
    """
    Core combine and asof merge implementation for groups of dataframes.

    This function performs the actual asof join logic by iterating through
    groups, dataframes, and data types to populate the pre-allocated result
    structure. It handles sliding window views for previous values and maps
    results to the correct output positions. When previous values are
    requested, each window is ordered earliest-to-latest as
    [prev_n, ..., prev1, current].

    Parameters
    ----------
    main : NDArray
        Array of target values for alignment. Same length as ``combinations``.
    on : str
        Column name used for asof joining (key column).
    df_groups : list[list[DataFrame]]
        Nested list of dataframes:
        - Outer list: Different groups of dataframes
        - Inner lists: Dataframes within each group
        All dataframes must contain the 'on' column.
    cols_slices_in_df_per_dtype : list[dict[DTypeLike, slice]]
        List with one dict per dataframe in a group. Each dict maps
        dtype -> slice of column names (excluding 'on' column).
        Structure: [{dtype1: slice(col1, col2), dtype2: slice(col3, col4)}, ...]
    combinations : NDArray
        Integer array of shape ``(n_output_rows, n_join_positions)`` where
        each element is a group index for the corresponding join position.
    allow_exact_matches : list[bool]
        List of booleans, one per dataframe in a group. If False and an
        exact match is found, uses previous value instead.
    n_prev : list[int]
        List of integers, one per dataframe in a group. Number of previous
        values to include for each dataframe (0 = current value only).
    fill_values : list[list[dict[DTypeLike, NDArray]]]
        Fill data for insufficient previous values. Structure matches
        ``df_groups`` and inner lists contain one dict per dataframe in a group.
        These arrays have ``n_prev + 1`` rows: the leading extra row is a guard
        used when the first 'main' value precedes the first 'df_on' value.
    res_arrays : dict[DTypeLike, NDArray]
        Pre-allocated result arrays to populate in-place, one array per dtype
        with shape (n_output_rows, n_columns_for_this_dtype).
    cols_slices_in_res_per_join_pos : list[list[dict[DTypeLike, slice]]]
        List of lists of dicts, one per join position, one per dataframe,
        one per dtype. For each join position and dataframe, slice per dtype

    Notes
    -----
    - This function modifies 'res_arrays' in-place.
    - The algorithm uses three nested loops:
        1. Loop over groups of dataframes
           - Build `group_mask = (combinations == group_idx)`
           - `output_row_indices_for_group = nonzero(group_mask.any(axis=1))[0]`
           - `main_values_for_group = main[output_row_indices_for_group]`
           - For each join position where this group appears, compute
             `group_main_indices_per_join_pos[j]` which are the local row
             indices within `main_values_for_group` to materialize for that
             join position

        2. Loop over dataframes within the group
           - Compute `df_row_idx, use_guard_row = _get_df_row_idx(
             main_values_for_group, df[on], allow_exact_matches[df_idx])
           - `df_row_idx` gives, for each value in `main_values_for_group`, the
             window end index in the extended df values (guard already accounted
             for)
           - Concatenate guard rows (from `fill_values`) with df values depending on
             `use_guard_row`, then update `fill_values` in-place with the last
             `n_prev + 1` rows for reuse

        3. Loop over dtypes within the dataframe
           - If `n_prev > 0`, create sliding windows so each row selects a
             window of shape `(n_prev + 1, n_cols)` ordered from earliest to
             current
           - For each join position, select only the local subset of rows using
             `group_main_indices_per_join_pos`, map to global output rows via
             `output_row_indices_for_group`, then write into the correct result
             array slice for this dtype

    """
    # Loop 1: Over groups of dataframes.
    for group_idx, group in enumerate(df_groups):
        group_mask = combinations == group_idx
        # Join positions where this group appears (column indices in
        # combinations, excluding main).
        join_positions_for_group = nonzero(group_mask.any(axis=0))[0].tolist()
        # Output row indices that use this group at any join position.
        output_row_indices_for_group = nonzero(group_mask.any(axis=1))[0]
        # Subset of main values for output rows that use this group.
        main_values_for_group = main[output_row_indices_for_group]
        # For each join position, get indices within main_values_for_group.
        group_main_indices_per_join_pos = [
            nonzero((group_mask[:, join_pos])[output_row_indices_for_group])[0]
            for join_pos in join_positions_for_group
        ]
        # Loop 2: Over dataframes in a group.
        for df_idx, df in enumerate(group):
            # Get asof row indices (same length as 'main_values_for_group').
            # These will be filtered by 'group_main_indices_per_join_pos'
            # depending on join position when assembling results.
            df_row_idx, use_guard_row = _get_df_row_idx(
                main_values_for_group,
                df.loc[:, on].to_numpy(),
                allow_exact_matches[df_idx],
            )
            # Loop 3: Over data types in a dataframe.
            n_prev_plus_one = n_prev[df_idx] + 1
            for cols_dtype, cols_slice in cols_slices_in_df_per_dtype[df_idx].items():
                val_array = df.loc[:, cols_slice].to_numpy(copy=False)
                # Prepare per-dtype fill values.
                fill_values_for_dtype = fill_values[group_idx][df_idx][cols_dtype]
                # Concatenate fill values with original data.
                extended_val_array = (
                    concatenate([fill_values_for_dtype, val_array], axis=0)
                    if use_guard_row
                    else concatenate([fill_values_for_dtype[1:], val_array], axis=0)
                )
                # Reset fill values in place with last n_prev+1 rows from the extended array.
                fill_values_for_dtype[:] = extended_val_array[-n_prev_plus_one:]
                if n_prev_plus_one > 1:
                    # 'n_prev' values requested.
                    # Create sliding window view: (len(ar), n_prev+1, n_cols).
                    extended_val_array = sliding_window_view(
                        extended_val_array,
                        n_prev_plus_one,
                        axis=0,
                    )
                # Map results to output positions for each join position
                for join_pos_idx, join_pos in enumerate(join_positions_for_group):
                    relevant_row_indices_in_group_main = group_main_indices_per_join_pos[join_pos_idx]
                    relevant_row_indices_in_df = df_row_idx[relevant_row_indices_in_group_main]
                    # 'reshape' is only needed for n_prev > 0, in which case
                    # 'extended_val_array' is a windowed view with shape
                    # (n_prev+1, n_cols).
                    # For performance reason, 'reshape' is after the indexing
                    # operation with 'relevant_row_indices_in_df'.
                    # Having the reshaping before the indexing would lead to
                    # creation of a large temporary copy of all windows.
                    selected_values = extended_val_array[relevant_row_indices_in_df].reshape(
                        len(relevant_row_indices_in_group_main),
                        -1,
                    )
                    col_slice_in_res = cols_slices_in_res_per_join_pos[join_pos][df_idx][cols_dtype]
                    res_arrays[cols_dtype][
                        output_row_indices_for_group[relevant_row_indices_in_group_main],
                        col_slice_in_res,
                    ] = selected_values


class AsofMerger:
    """
    A class for combine and asof merge operations on groups of dataframes.

    The class is designed to be used iteratively.

    Attributes
    ----------
    on : str
        Column name to use for joining. This column should contain ordered
        values (typically timestamps or sequential numbers), and has to exist
        in all dataframes.
    n_dfs_per_group : int
        Number of dataframes per group.
    prefixes : list[list[str]]
        Column name prefixes for each join position in 'combinations'.
        Outer list length must match number of join positions (width of
        'combinations').
        Inner list length must match number of dataframes in a group.
    allow_exact_matches : list[bool]
        List of booleans of same length as the inner list in `df_groups`
        If False, and an exact match is found, the previous value in the
        dataframe is used.
    n_prev : list[int]
        List of length ``len(df_groups[0])``, where each value indicates the
        number of previous values to include for the corresponding dataframe.
        This configuration applies identically to all groups.
    n_prev_suffix_start : int
        Start index for suffixing column names for dataframes with previous
        values.
    _fill_values : list[list[dict[DTypeLike, NDArray]]]
        Fill data for when insufficient previous values exist in data of current
        iteration.
        Structure mirrors `df_groups`. Each inner list corresponds to a group
        and contains a dict per dataframe in the group, in the same order as
        in the corresponding group. Each dict stores one numpy array per
        dtype in the corresponding dataframe, 'on' column being omitted.
        Each array has ``n_prev + 1`` rows. The leading extra row is a guard
        used when the first 'main' value precedes the first value in 'on'
        column.
        For dataframes with `n_prev = 0`, at least 1 row is used for guard
        operations during asof merge.
        During execution, ``_fill_values`` is updated in-place with the last
        ``n_prev + 1`` rows to be reused in the next call.
        This attribute is internal and lazily initialized on the first call to
        ``merge`` based on the configured ``n_prev`` and optional
        ``fill_values_init`` provided at initialization. It is not required to
        be bound as state for resumability. Binding ``_conf`` alone may be
        sufficient for stateful usage; ``_fill_values`` will be re-initialized
        automatically on resume if needed (zeros when no ``fill_values_init`` is
        provided). In particular, if input chunks already include at least
        ``n_prev[i]`` rows preceding the earliest value of ``main`` for each
        dataframe ``i`` (for example, by using ``Store.iter_intersections`` with
        its ``n_prev`` parameter), then persisting ``_fill_values`` is
        unnecessary because previous windows can be rebuilt from the loaded
        rows.
    _conf : dict
        Internal configuration cached on first merge. Contains arrays, slices,
        and layout metadata returned by ``_get_config``. Intended to be bound
        as object state with ``StatefulLoop.bind_object_state(...)``.
        - cols_per_dtype: list[dict[DTypeLike, list[str]]]
          List of dicts, one per dataframe in a group.
          Each dict maps dtype -> list of column names (excluding 'on' column).
          Structure: [{dtype1: [col1, col2], dtype2: [col3, col4]}, ...]
        - cols_reindex_in_df: list[Index]
          List of pandas Index objects, one per dataframe in a group.
          Each Index object contains the column names of the corresponding
          dataframe, starting with 'on' column, and re-ordered per dtype.
          Reindexing with this Index object enables selecting columns of same
          dtype by using slices.
        - cols_slices_in_df_per_dtype: list[dict[DTypeLike, slice]]
          List of dicts, one per dataframe in a group.
          Each dict maps dtype -> slice of column names (excluding 'on' column).
          Structure: [{dtype1: slice(col1, col2), dtype2: slice(col3, col4)}, ...]
        - seed_res_arrays: dict[DTypeLike, NDArray]
          Dictionary with one numpy array per dtype, used to store the result of
          the asof merge for each dtype.
        - cols_slices_in_res_per_join_pos: list[list[dict[DTypeLike, slice]]]
          List of lists of dicts, one per join position, one per dataframe in a
          group, one per dtype. For each join position, dataframe and dtype,
          slice in corresponding result array where to paste the result.
        - cols_dtypes_slices_in_res_per_col_name: dict[str, tuple[DTypeLike, slice]]
          Dictionary with one tuple per column name, mapping column name in
          result to its dtype and its position in the result array (using
          slices).

    Methods
    -------
    merge(
        main: NDArray,
        df_groups: list[list[DataFrame]],
        combinations: NDArray,
        copy: bool,
        check_sorted: bool,
    ) -> DataFrame
        Perform simultaneously an as-of merge and combine operations on multiple
        groups of dataframes vs an ordered key.

    """

    def __init__(
        self,
        on: str,
        *,
        n_dfs_per_group: int,
        prefixes: list[list[str]] | list[str] | None = None,
        allow_exact_matches: list[bool] | None = None,
        n_prev: list[int] | None = None,
        n_prev_suffix_start: int = 0,
        fill_values_init: list[list[DataFrame]] | None = None,
    ) -> None:
        """
        Initialize the merger.

        Parameters
        ----------
        on : str
            Column name to use for joining. This column should contain ordered
            values (typically timestamps or sequential numbers), and has to
            exist in all dataframes.
        *,
        n_dfs_per_group : int
            Number of dataframes expected in each group.
        prefixes : list[list[str]] | list[str] | None
            Column name prefixes per join position (nested), or for single join
            position as a flat list, or None.
            - Nested form: outer length == number of join positions; inner
              length == number of dataframes per group.
            - Flat form: treated as a single join position.
            - None: prefixes will be generated at first merge using empty
              strings with shape [n_join_positions][n_df_per_group].
        allow_exact_matches : Optional[list[bool]], default None
            List of booleans of same length as the inner list in `df_groups`
            Per dataframe, if False, and an exact match is found, the previous
            value in the dataframe is used.
            If None, ``allow_exact_matches`` is False for any dataframe.
        n_prev : Optional[list[int]], default None
            List of length ``len(df_groups[0])``, where each value indicates the
            number of previous values to include for the corresponding
            dataframe.
            If 'n_prev' is specified, all values must be >= 0.
            This configuration applies identically to all groups.
            If None, only the current asof value is included for each dataframe.
            If set, column names in result dataframe are those of input
            dataframes with column names for previous values suffixed by the
            position of the previous values, starting at 'n_prev_suffix_start'.
        n_prev_suffix_start : int, default 0
            Start index for suffixing column names for dataframes with previous
            values.
        fill_values_init : Optional[list[list[DataFrame]]], default None
            Fill data for when insufficient previous values exist in data at
            first iteration.
            Structure mirrors `df_groups`. Each group must contain the same
            number of dataframes.  Each inner list corresponds to a group in the
            same order as `df_groups`, with one dataframe per dataframe in the
            corresponding group, without the 'on' column.
            If None, missing previous values are filled with ``0``.

        Examples
        --------
        >>> # Define prefixes for each join position (2 positions, 2 dataframes per
        >>> # group)
        >>> prefixes = [
        ...     ['left_df1_', 'left_df2_'],   # Prefixes for first join position
        ...     ['right_df1_', 'right_df2_'], # Prefixes for second join position
        ... ]
        >>>
        >>> # Basic merger initialization (current values only)
        >>> merger = AsofMerger(
        ...     on='timestamp',
        ...     prefixes=prefixes
        ... )
        >>>
        >>> # Advanced merger with previous values
        >>> n_prev = [3, 1]  # df0: +3 previous, df1: +1 previous
        >>> merger = AsofMerger(
        ...     on='timestamp',
        ...     prefixes=prefixes,
        ...     n_prev=n_prev
        ... )
        >>>
        >>> # Advanced merger with custom fill values
        >>> n_prev = [3, 0]  # df0: +3 previous, df1: +0 previous (but guard row needed)
        >>> fill_values_init = [
        ...     [df0_fill_g0, df1_guard_g0],  # Fill data for df0 + guard for df1 in group 0
        ...     [df0_fill_g1, df1_guard_g1],  # Fill data for df0 + guard for df1 in group 1
        ...     [df0_fill_g2, df1_guard_g2],  # Fill data for df0 + guard for df1 in group 2
        ... ]
        >>> merger = AsofMerger(
        ...     on='timestamp',
        ...     prefixes=prefixes,
        ...     n_prev=n_prev,
        ...     fill_values_init=fill_values_init
        ... )

        """
        self.on = on
        self.n_dfs_per_group = n_dfs_per_group
        # Normalize prefixes to nested form and set join positions.
        if prefixes is not None:
            if isinstance(prefixes[0], str):
                prefixes = [prefixes]
            if any((len(group) != n_dfs_per_group) for group in prefixes):
                raise ValueError("each group must be of length 'n_dfs_per_group' in 'prefixes'.")
        self.prefixes = prefixes
        self.allow_exact_matches = (
            [False] * self.n_dfs_per_group if allow_exact_matches is None else allow_exact_matches
        )
        if len(self.allow_exact_matches) != self.n_dfs_per_group:
            raise ValueError("'allow_exact_matches' length must match 'n_dfs_per_group'.")
        if n_prev is None:
            self.n_prev = [0] * self.n_dfs_per_group
        else:
            self.n_prev = n_prev
            _validate_n_prev(self.n_prev, self.n_dfs_per_group)
        self.n_prev_suffix_start = n_prev_suffix_start
        self.fill_values_init = fill_values_init
        # These parameters require the first group of dataframes to be passed.
        # They will be initialized at first call of 'merge' method.
        self._conf = None
        self._fill_values = None

    def merge(
        self,
        main: NDArray,
        *,
        df_groups: list[list[DataFrame]] | list[DataFrame],
        combinations: NDArray | None = None,
        copy: bool = True,
        check_sorted: bool = False,
    ) -> DataFrame:
        """
        Perform an as-of join and combine on multiple groups of dataframes.

        This function aligns rows from multiple dataframes based on the nearest
        preceding value in the key column.
        This method is similar to pandas 'merge_asof' function but supports
        multiple dataframes and multiple group of dataframes simultaneously.

        Parameters
        ----------
        main : NDArray
            Target values for alignment. The asof join will find the nearest
            preceding value in each dataframe's key column for each value in main.
            A value can be referenced multiple times in 'main'.
        *,
        df_groups : list[list[DataFrame]] | list[DataFrame]
            Dataframe groups to join.
            - When ``combinations`` is provided: nested list structure where
              the outer list contains groups (length ``n_groups``) and each
              inner list contains dataframes for that group (length
              ``n_dfs_per_group``). Each dataframe at position i across all
              groups must have identical column structure (name and dtype).
            - When ``combinations`` is None (single join position): requires a
              flat list of DataFrames. Inputs are normalized internally to a
              single-group nested list.
            - All dataframes must contain the specified 'on' column.

        combinations : Optional[NDArray[int]]
            Integer array of shape ``(n_output_rows, n_join_positions)`` where:
            - Column indices represent join positions (combinations of fixed
              width),
            - Values are group indices referring to positions in ``df_groups``'s
              outer list,
            - The same group can be referenced multiple times per row at
              different join positions.

            If None, a single join position is required and a default array of
            zeros of shape ``(len(main), 1)`` is used (selecting group ``0`` at
            the sole join position).
        copy : bool, default True
            If True, return a copy of the result arrays.
            If False, return views on the result arrays.
            Returning views will result in faster processing time if `merge` is
            called iteratively (result array won't be re-initialized across
            iterations). This requires however the caller to ensure the result
            arrays to make copy of the results before the next call to `merge`.
            In particular, if `merge` is called in successive iterations, along
            with result accumulation across iterations without any copy of the
            results, it is recommended to keep `copy` to True.
        check_sorted : bool, default False
            If True, validate that 'main' is increasing and that each
            dataframe's 'on' column is increasing. This is an O(N) pass per
            array/Series and is intended for debugging or defensive runs.

        Returns
        -------
        DataFrame
            Joined dataframe where each row corresponds to a row in
            ``combinations``.
            The first column contains the `main` values named after `on`.
            Then columns follow join position order, dataframe order, dtype
            order, and previous values order (if any).

        Examples
        --------
        >>> # Three groups of dataframes, each group has 2 dataframes
        >>> df_groups = [
        ...     [df1_g0, df2_g0],  # Group 0
        ...     [df1_g1, df2_g1],  # Group 1
        ...     [df1_g2, df2_g2],  # Group 2
        ... ]
        >>> main_times = np.array([10, 20, 30])
        >>>
        >>> # Create output rows, each with 2 join positions selecting different groups:
        >>> combinations = np.array([
        ...     [0, 1],  # main[0] (10): pos0 -> group0, pos1 -> group1
        ...     [0, 2],  # main[0] (10): pos0 -> group0, pos1 -> group2
        ...     [1, 2],  # main[1] (20): pos0 -> group1, pos1 -> group2
        ...     [2, 1],  # main[2] (30): pos0 -> group2, pos1 -> group1
        ... ])
        >>>
        >>> # Initialize merger
        >>> prefixes = [
        ...     ['left_df1_', 'left_df2_'],   # Prefixes for first join position
        ...     ['right_df1_', 'right_df2_'], # Prefixes for second join position
        ... ]
        >>> merger = AsofMerger(on='timestamp', prefixes=prefixes)
        >>>
        >>> # Basic join (current values only)
        >>> result = merger.merge(main_times, df_groups, combinations)
        >>> # Result has 4 rows, each with 5 columns (2 join positions × 2 dataframes × 1
        >>> # value + 1 main)
        >>>
        >>> # Advanced join with previous values
        >>> n_prev = [3, 1]  # df0: +3 previous, df1: +1 previous
        >>> merger_prev = AsofMerger(on='timestamp', prefixes=prefixes, n_prev=n_prev)
        >>> result = merger_prev.merge(main_times, df_groups, combinations)
        >>> # Result has 4 rows, each with 11 columns (2 join positions × (4+2)
        >>> # columns + 1 main)
        >>>
        >>> # Advanced join with custom fill values
        >>> n_prev = [3, 0]  # df0: +3 previous, df1: +0 previous (but guard row needed)
        >>> fill_values_init = [
        ...     [df0_fill_g0, df1_guard_g0],  # Fill data for df0 + guard for df1 in group 0
        ...     [df0_fill_g1, df1_guard_g1],  # Fill data for df0 + guard for df1 in group 1
        ...     [df0_fill_g2, df1_guard_g2],  # Fill data for df0 + guard for df1 in group 2
        ... ]
        >>> merger_fill = AsofMerger(on='timestamp', prefixes=prefixes,
        ...                         n_prev=n_prev, fill_values_init=fill_values_init)
        >>> result = merger_fill.merge(main_times, df_groups, combinations)
        >>> # Result has 4 rows, each with 9 columns (2 join positions × (4+1)
        >>> # columns + 1 main)

        Notes
        -----
        - All dataframes must have their 'on' column sorted in ascending order.
        - The asof join uses backward search (nearest preceding value).
        - Columns in output are re-ordered per dtype, for improved performance.
        - For dataframes with previous values, within each dtype the expanded
          columns for a given source column are ordered from earliest previous
          on the left to the current value on the right.
        - ``main`` must be monotonically increasing. The algorithm relies on
          monotonic ``main`` for efficient asof index computation and for the
          correctness of the first-entry negative-index guard.
        - When ``n_prev`` is all zeros and ``fill_values`` is None, a single
          guard row of zeros per dtype is synthesized internally so that early
          ``main`` values produce correct guard windows.
        - When ``merge`` is called a first time, ``fill_values_init`` provided
          in initialization is deleted.The internal state is managed
          automatically across iterations. The ``_fill_values`` attribute is
          internal and does not necessarily need to be bound for resumability;
          binding ``_conf`` alone may be sufficient. On resume, ``_fill_values``
          is synthesized from zeros (or rebuilt from ``fill_values_init`` when
          provided).
        - Iterative usage guidance:
          * The internal state (``fill_values``, and other configuration
            parameters) is managed automatically.
          * If you set ``copy=False`` across iterations, take a copy of each
            returned result DataFrame before invoking the next iteration to
            avoid overwriting via shared underlying buffers.

        """
        if combinations is None:
            # Normalize inputs up-front when combinations is None (single join
            # position).
            if not isinstance(df_groups[0], DataFrame):
                raise ValueError(
                    "when 'combinations' is None, 'df_groups' must be a flat " "list of DataFrames.",
                )
            df_groups = [df_groups]
            combinations = zeros((len(main), 1), dtype=int)
        n_join_positions = combinations.shape[1]
        # Optional monotonicity checks.
        if check_sorted:
            _validate_monotonic_increasing(main, df_groups, self.on)
        if self._conf is None:
            # First use of function, validate consistency of input data.
            _validate_params(
                main=main,
                n_dfs_per_group=self.n_dfs_per_group,
                df_groups=df_groups,
                combinations=combinations,
            )
            self._conf = _get_config(
                cols_dtypes_per_df=[df.dtypes.to_dict() for df in df_groups[0]],
                filter_out=[self.on],
                n_join_positions=n_join_positions,
                prefixes=self.prefixes,
                n_prev=self.n_prev,
                n_prev_suffix_start=self.n_prev_suffix_start,
            )
        if self._fill_values is None:
            if isinstance(self.fill_values_init, list):
                _validate_fill_values_init(
                    on=self.on,
                    df_groups=df_groups,
                    n_prev=self.n_prev,
                    fill_values_init=self.fill_values_init,
                )
            self._fill_values = _initialize_fill_values(
                n_df_groups=len(df_groups),
                cols_per_dtype=self._conf[KEY_COLS_PER_DTYPE],
                n_prev=self.n_prev,
                fill_values_init=self.fill_values_init,
            )
            # 'fill_values_init' no longer needed after transformation, free
            # memory.
            del self.fill_values_init
        # Reindex dfs to ensure columns are in the same order per dtype.
        # (make use of slices safe in '_comb_merge_asof')
        for group in df_groups:
            for df_idx in range(len(group)):
                group[df_idx] = group[df_idx].reindex(
                    columns=self._conf[KEY_COLS_REINDEX_IN_DF][df_idx],
                    copy=False,
                )
        # Resize result arrays to match the number of output rows.
        res_arrays = _resize_res_arrays_length(
            seed_res_arrays=self._conf[KEY_SEED_RES_ARRAYS],
            n_rows=len(main),
            copy=copy,
        )
        # Set 'res_arrays' in-place.
        _comb_merge_asof(
            main=main,
            on=self.on,
            df_groups=df_groups,
            cols_slices_in_df_per_dtype=self._conf[KEY_COLS_SLICES_IN_DF_PER_DTYPE],
            combinations=combinations,
            allow_exact_matches=self.allow_exact_matches,
            n_prev=self.n_prev,
            fill_values=self._fill_values,
            res_arrays=res_arrays,
            cols_slices_in_res_per_join_pos=self._conf[KEY_COLS_SLICES_IN_RES_PER_JOIN_POS],
        )
        return DataFrame(
            {self.on: main}
            | {
                col_name: res_arrays[col_dtype][:, col_slice].reshape(-1)
                for col_name, (
                    col_dtype,
                    col_slice,
                ) in self._conf[KEY_COLS_DTYPES_SLICES_IN_RES_PER_COL_NAME].items()
            },
        )
