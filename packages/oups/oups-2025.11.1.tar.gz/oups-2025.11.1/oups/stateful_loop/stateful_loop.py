#!/usr/bin/env python3
"""
Created on Wed Jun  1 18:35:00 2025.

@author: pierrot

"""
from collections import defaultdict
from collections.abc import Callable
from collections.abc import Hashable
from collections.abc import Iterable
from collections.abc import Iterator
from functools import partial
from inspect import signature
from pathlib import Path
from types import TracebackType
from typing import Any
from typing import TypeVar

from pandas import DataFrame
from pandas import concat

from oups.stateful_loop.loop_persistence_io import LoopPersistenceIO
from oups.stateful_loop.validate_loop_usage import validate_loop_usage


T = TypeVar("T")


class Skip(Exception):
    """
    Exception used to skip downstream processing for the current item.

    In this stateful loop context, ``Skip`` signals that the current iteration
    should continue without executing downstream code for the current data item.
    It is typically raised by accumulating operations when memory limits are not
    yet reached.

    """


class IterationContext:
    """
    Per-item context manager that swallows ``Skip`` and yields the item.

    The ``__enter__`` method returns the current item. If a ``Skip``
    exception is raised inside the ``with`` block, it is swallowed to
    proceed to the next iteration without running downstream code.

    """

    def __init__(self, current: Any):
        """
        Initialize the IterationContext.

        Parameters
        ----------
        current : Any
            The current item to be yielded.

        """
        self._current = current

    def __enter__(self):
        """
        Return the current item.
        """
        return self._current

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        _exc: BaseException | None,
        _tb: TracebackType | None,
    ) -> bool:
        """
        Exit the IterationContext.

        Swallow ``Skip`` exceptions to proceed to the next iteration without
        running downstream code.

        """
        if exc_type is Skip:
            return True
        return False


def _raise_invalid_state_keys(
    invalid_keys: Iterable[str],
) -> None:
    """
    Raise a ValueError if the invalid keys are not empty.

    Parameters
    ----------
    invalid_keys : Iterable[str]
        Keys that are not present in the stateful function/object.

    Raises
    ------
    ValueError
        If the invalid keys are not empty.

    """
    if invalid_keys:
        raise ValueError(
            "state contains keys not present in stateful function/object: " + ", ".join(sorted(invalid_keys)),
        )


class StatefulLoop:
    """
    Main orchestrator for stateful loop execution.

    The StatefulLoop class provides the core functionality wrapping a
    lightweight data-processing ``for`` loop, including iteration control, state
    management, and DataFrame buffering with memory-triggered concatenation.

    If the provided ``filepath`` already exists at instantiation time,
    its content is loaded and used to initialize the internal state store. In
    that case, any initial values given later via ``bind_function_state`` or
    ``bind_object_state`` are ignored for the corresponding bindings, because
    previously recorded state takes precedence. This enables resuming a
    stateful loop by re-running the same function that declares the loop,
    bindings, and iteration.

    Targeted usage is:

    - define a function that receives a data iterable/generator as a parameter.
    - instantiate ``StatefulLoop`` inside the function, providing a stable
      loop persistence ``filepath``.
    - bind stateful functions/objects with ``bind_function_state`` and
      ``bind_object_state``.
    - iterate using ``for item_ctx in loop.iterate(source):``.

    On subsequent calls of the same function, the stored state is loaded from
    the loop persistence ``filepath`` at construction time, so stateful
    functions resume from their last recorded state and ignore newly provided
    initial values. State is persisted when the loop completes (after the last
    item).

    Attributes
    ----------
    default_memory_limit_mb : float
        Default memory limit in megabytes used by accumulation when
        no per-call override is provided.
    default_memory_limit_bytes : int
        Default memory limit in bytes used by accumulation when
        no per-call override is provided.
    is_last_iteration : bool
        Flag indicating if this is the last iteration of the stateful loop.
    iteration_count : int
        Current iteration count (0-based).
        Value is '-1' till the loop starts.
    filepath : Path
        Path of the loop persistence file: serialized states for stateful
        functions/objects and a run-flag used by loop validation and buffering
        behavior.
    _persistence_loaded : bool
        Whether a persistence file existed and was loaded at construction time.
        Used to decide default behavior of the buffer placement validation.
    _data_buffer : dict[int, defaultdict[Hashable, list[DataFrame]]]
        Nested buffer for buffering DataFrames.
        First level keys are buffer IDs (call position within iteration),
        second level keys are user-provided keys, values are lists of
        DataFrames.
    _iteration_buffer_current : int
        Tracks the iteration index for which the current buffer position
        counter is valid. Used to reset the counter at each new iteration.
    _iteration_buffer_count : int
        Tracks the 0-based call position of ``buffer()`` within the current
        iteration.
    _memory_usage_bytes : dict[int, int]
        Memory usage tracking per buffer ID in bytes.
    _state_key_counts : dict[str, int]
        Counter per base state reference used to generate stable unique keys
        for stateful functions and objects (e.g., ``func:name#1``,
        ``obj:name#1``).
    _state_store : dict[str, dict[str, Any]]
        In-memory state storage (persisted on disk when stateful loop finishes).
        For stateful functions: stores parameter name -> value mappings.
        For stateful objects: stores last persisted attribute values.
    _object_bindings : dict[str, tuple[Any, list[str]]]
        Registry of object bindings keyed by namespaced state reference
        (e.g., ``obj:Counter#1``) to a tuple of the bound object and the list
        of attribute names to snapshot on save.

    Methods
    -------
    iterate(iterable: Iterable[Any], *, check_loop_usage: Optional[bool] = None)
        -> Iterator[IterationContext]
        Wrap an iterable to control loop flow in stateful loop context. Optionally
        runs a strict AST validation that enforces legal buffer placement.
    buffer(
        data: dict[Hashable, DataFrame],
        memory_limit_mb: Optional[float] = None,
        concat_func: Callable[[list[DataFrame]], DataFrame] = pandas.concat,
    ) -> Optional[dict[Hashable, DataFrame]]
        Buffer DataFrames in memory and track memory usage.
    bind_function_state(func: Callable[..., Any], *, state: dict[str, Any],
                        name: Optional[str] = None) -> Callable[..., Any]
        Wrap a function to bind specified parameters as state across iterations.
    bind_object_state(obj: T, *, state: list[str], name: Optional[str] = None) -> T
        Register a stateful object for state binding.

    """

    def __init__(
        self,
        filepath: Path,
        *,
        default_memory_limit_mb: float = 300.0,
    ):
        """
        Initialize the StatefulLoop.

        Parameters
        ----------
        filepath : Path
            File path for storing the loop persistence. If this file
            already exists when the instance is created, its content is loaded
            to initialize the internal state store, allowing stateful loops to
            resume from a prior run. This also flags that a successful prior run
            occurred, allowing the loop validation to be skipped on subsequent
            runs if 'check_loop_usage' is ``None``.
        default_memory_limit_mb : float, default 300.0
            Default memory limit in megabytes used by delayed concatenation when
            no per-instance/per-site override is provided.

        """
        self._filepath = filepath
        self._default_memory_limit_bytes = int(default_memory_limit_mb * 1024 * 1024)
        # Simple iteration context attributes
        self.is_last_iteration = False
        # 'iteration_count' will be set to 0 at first iteration.
        self.iteration_count: int = -1
        # In-memory state storage (persisted when the stateful loop finishes).
        # If a loop persistence file exists, load it to resume previous states;
        # otherwise start empty.
        self._state_store: dict[str, dict[str, Any]] = {}
        self._persistence_loaded = Path(self._filepath).exists()
        if self._persistence_loaded:
            self._state_store = LoopPersistenceIO.load(self._filepath)
        # Track counts for state references to ensure stable, unique keys
        self._state_key_counts: dict[str, int] = defaultdict(int)
        # Registry for object bindings (strong refs during loop lifetime)
        self._object_bindings: dict[str, tuple[Any, list[str]]] = {}
        # Track buffer call order within each iteration
        self._iteration_buffer_current = -1
        self._iteration_buffer_count = 0
        # Data buffer for buffering: buffer_id -> user_key -> list[DataFrame]
        self._data_buffer: dict[int, defaultdict[Hashable, list[DataFrame]]] = {}
        # Track memory usage per buffer_id in bytes
        self._memory_usage_bytes: dict[int, int] = {}

    def __repr__(self):
        """
        Return string representation of the StatefulLoop.
        """
        return (
            f"StatefulLoop(filepath={self.filepath}, "
            f"default_memory_limit_mb={self.default_memory_limit_mb})"
        )

    @property
    def filepath(self):
        """
        Return loop persistence file path.
        """
        return self._filepath

    @property
    def default_memory_limit_mb(self):
        """
        Return default memory limit in megabytes.
        """
        return self._default_memory_limit_bytes / (1024 * 1024)

    @property
    def default_memory_limit_bytes(self):
        """
        Return default memory limit in bytes.
        """
        return self._default_memory_limit_bytes

    def bind_function_state(
        self,
        func: Callable[..., Any],
        *,
        state: dict[str, Any],
        name: str | None = None,
    ) -> Callable[..., Any]:
        """
        Create a partial callable that binds specified parameters as state.

        The binding is by reference. For it to work, the parameters bound as
        state must be mutable (e.g., ``dict`` or ``list``) and updated in place
        by the stateful function.

        Parameters
        ----------
        func : callable
            Function to wrap. The partial callable publishes a reduced
            signature that hides state-managed parameters. There is no runtime
            guard: if callers pass those parameters, they will override the
            bound values for that call.
        state : dict[str, Any]
            Mapping of state parameter names to initial values used only if no
            stored state exists yet for this binding. Values should be mutable
            (e.g., ``dict`` or ``list``) and updated in place by the stateful
            function.
        name : Optional[str]
            Optional base name used to generate a stable, unique state key
            (e.g., ``name#1``). Declare stateful functions in a consistent
            order to keep keys stable across runs. Defaults to
            the function's ``__name__``.

        Returns
        -------
        callable
            A partial callable compatible with ``func`` with state references
            pre-bound and a reduced public signature.

        """
        # Initialize or reuse stored state references.
        base_ref = name or getattr(func, "__name__", None)
        if base_ref is None:
            raise ValueError("function has no name.")
        sig = signature(func)
        _raise_invalid_state_keys(set(state) - set(sig.parameters))
        _, stored_state = self._get_or_init_state(
            "func",
            base_ref,
            initial_state=state,
        )
        partial_func = partial(func, **stored_state)
        # Publish reduced signature so callers see only non-state parameters.
        public_params = [p for p in sig.parameters.values() if p.name not in state]
        partial_func.__signature__ = sig.replace(parameters=public_params)
        return partial_func

    # --- Stateful object support ---
    def bind_object_state(
        self,
        obj: T,
        *,
        state: list[str],
        name: str | None = None,
    ) -> T:
        """
        Register a stateful object for state binding.

        At bind time, if a stored persisted state exists for this object binding,
        the listed attributes are restored on ``obj``. Otherwise, the current
        values of those attributes are stored into the internal state store.
        The loop keeps a registry of bound objects and attribute names, and on
        persistence it records the latest attribute values via
        ``getattr``. Both in-place mutation and reassignment are supported.

        Parameters
        ----------
        obj : T
            The object to bind.
        state : list[str]
            List of attribute names to bind as state. Attributes must exist on
            ``obj`` at bind time and their values must be serializable by the
            configured loop persistence I/O.
        name : Optional[str], default None
            Base name used to build a stable state reference for this object.
            If None, the object's name or its class name is used.

        Returns
        -------
        T
            The same object instance provided in ``obj``.

        Examples
        --------
        Pre-initialized attribute (mutation):

        >>> class PreInitCounter:
        ...     def __init__(self):
        ...         self.state1 = {"count": 0}
        ...     def process(self, x):
        ...         self.state1["count"] += 1
        ...         return x
        >>> obj = PreInitCounter()
        >>> loop.bind_object_state(obj, state=["state1"])

        Lazy initialization with reassignment:

        >>> class ReassigningCounter:
        ...     def __init__(self, start=0):
        ...         self.state1 = None
        ...         self._start = start
        ...     def process(self, x):
        ...         if self.state1 is None:
        ...             self.state1 = {"count": self._start}
        ...         self.state1["count"] += 1
        ...         return x
        >>> obj2 = ReassigningCounter()
        >>> loop.bind_object_state(obj2, state=["state1"])

        """
        base_ref = name or getattr(obj, "__name__", None) or obj.__class__.__name__
        if base_ref is None:
            raise ValueError("object has no name.")
        _raise_invalid_state_keys({attr for attr in state if not hasattr(obj, attr)})
        state_ref, stored_state = self._get_or_init_state(
            "obj",
            base_ref,
            initial_state={attr: getattr(obj, attr) for attr in state},
        )
        for attr in state:
            setattr(obj, attr, stored_state[attr])
        # Register binding for persistence-on-save using strong reference.
        self._object_bindings[state_ref] = (obj, list(state))
        return obj

    def buffer(
        self,
        data: dict[Hashable, DataFrame],
        memory_limit_mb: float | None = None,
        concat_func: Callable[[list[DataFrame]], DataFrame] = concat,
    ) -> dict[Hashable, DataFrame] | None:
        """
        Buffer DataFrames in memory and track memory usage.

        This method automatically creates unique buffer spaces for each
        ``buffer()`` call within an iteration, preventing data from different
        ``buffer()`` calls from interfering with each other, even when using the
        same user-provided keys.

        ``buffer()`` cannot be placed within a nested loop. The unique
        identifier is based on call order within each iteration.

        Placement rules
        ---------------
        Calls to ``buffer()`` are intended to be used directly as top-level
        statements inside the first ``with item_ctx as ...:`` block inside the
        body of ``for item_ctx in loop.iterate(...):``. A strict AST validation
        can enforce these rules when ``iterate(..., check_loop_usage=...)``
        enables it (see ``iterate`` docstring for details).

        Parameters
        ----------
        data : dict[Hashable, DataFrame]
            Dictionary mapping keys to DataFrames to be buffered.
            Keys can be reused across different ``buffer()`` calls without
            conflict.
        memory_limit_mb : Optional[float], default None
            Memory limit in megabytes. If None, uses default memory limit.
            When exceeded, triggers concatenation and returns results.
        concat_func : Callable[[list[DataFrame]], DataFrame], default ``pandas.concat``
            Function to concatenate a non-empty list of DataFrames when the
            memory limit is reached.

        Returns
        -------
        Optional[dict[Hashable, DataFrame]]
            Returns concatenated DataFrames when memory limit is exceeded or on
            last iteration.

        Raises
        ------
        Skip
            Raised when memory limit is not exceeded and not on last iteration
            to signal the caller to skip downstream processing and continue to
            the next iteration.

        """
        # Generate unique iteration-based identifier.
        buffer_id = self._get_buffer_id()
        # Ensure buffer_id exists in buffer and memory tracker.
        if buffer_id not in self._data_buffer:
            self._data_buffer[buffer_id] = defaultdict(list)
            self._memory_usage_bytes[buffer_id] = 0
        # Append data to buffer and track memory usage.
        for user_key, df in data.items():
            self._data_buffer[buffer_id][user_key].append(df)
            # Increment memory usage for this buffer_id
            self._memory_usage_bytes[buffer_id] += df.memory_usage(deep=True).sum()
        # Check if we need to concat current buffer.
        memory_limit_bytes = int(
            (
                memory_limit_mb * 1024 * 1024
                if memory_limit_mb is not None
                else self._default_memory_limit_bytes
            ),
        )
        if self.is_last_iteration or self._memory_usage_bytes[buffer_id] >= memory_limit_bytes:
            concat_res = {}
            for user_key, df_list in self._data_buffer[buffer_id].items():
                if df_list:
                    # Concatenate all DataFrames for this user_key.
                    concat_res[user_key] = concat_func(df_list)
                    # Free memory on the way to prevent buffering data
                    # twice along the concatenation chain.
                    self._data_buffer[buffer_id][user_key].clear()
            self._memory_usage_bytes[buffer_id] = 0
            return concat_res
        else:
            raise Skip

    def iterate(
        self,
        iterable: Iterable[Any],
        *,
        check_loop_usage: bool | None = None,
    ) -> Iterator[IterationContext]:
        """
        Wrap an iterable to control loop flow using context-managed steps.

        This method provides the fundamental pattern for stateful loops: a
        for-loop that processes data iteratively while managing iteration
        context flags. It uses lookahead to detect the last element without
        emitting a sentinel value.

        ``Skip`` exceptions raised inside the ``with item_ctx`` block (e.g., by
        ``buffer()`` while still under the memory limit) are swallowed by the
        ``IterationContext``, skipping downstream code and continuing to the
        next iteration.

        Parameters
        ----------
        iterable : Iterable[Any]
            The iterable to wrap and process
        check_loop_usage : Optional[bool], default None
            If True, always run the strict validation that enforces:
            - the first statement in the loop body is ``with item_ctx as ...:``
            - any ``loop.buffer(...)`` calls are direct statements at the top
              level inside that ``with`` body (not in conditionals/loops/nested
              blocks).
              File read failures will raise immediately.
            If False, never run the validation.
            If None, run the validation only if the loop persistence file was
            not loaded at construction time (i.e., first run for this stateful
            loop). If a loop persistence file existed and was loaded, skip the
            validation.

        Yields
        ------
        IterationContext
            A context manager that yields the current item and swallows
            ``Skip``.

        Examples
        --------
        >>> from pathlib import Path
        >>> loop = StatefulLoop(Path("state.pkl"))
        >>> out = []
        >>> for item_ctx in loop.iterate([10, 20]):
        ...     with item_ctx as item:
        ...         out.append(item)
        >>> out
        [10, 20]

        """
        # Optional strict validation to fail fast on illegal buffer placement.
        if check_loop_usage is True or (check_loop_usage is None and not self._persistence_loaded):
            validate_loop_usage(self)
        it = iter(iterable)
        try:
            try:
                next_item = next(it)
            except StopIteration:
                # Empty iterable, exit.
                # No state to persist since no iterations occurred.
                return

            while True:
                self.iteration_count += 1
                current = next_item
                try:
                    next_item = next(it)
                except StopIteration:
                    self.is_last_iteration = True
                    yield IterationContext(current)
                    break

                yield IterationContext(current)

        finally:
            if self.is_last_iteration:
                # Persist object-bound attributes just before saving state.
                if self._object_bindings:
                    for state_ref, (obj, attrs) in self._object_bindings.items():
                        self._state_store[state_ref] = {attr: getattr(obj, attr) for attr in attrs}
                # After yielding last element, persist state and stop.
                # The file is created even if there is no state to persist
                # (no bindings). The file is still used as a flag to indicate
                # the stateful loop has been run once (see 'check_loop_usage').
                LoopPersistenceIO.save(self.filepath, self._state_store)
                # Clear strong references so objects can be GC'ed after save.
                self._object_bindings.clear()

    # --- Iteration-based buffer ID generation ---
    def _get_buffer_id(self) -> int:
        """
        Generate buffer id depending on its call order in the iteration.

        This approach is valid if all ``buffer()`` calls are at same level
        in the code, within the stateful loop.

        Returns
        -------
        int
            The call position (0, 1, 2, ...) of this buffer within the
            iteration. Same position across different iterations gets the same
            ID.

        """
        # Reset counter when we enter a new iteration
        if self.iteration_count != self._iteration_buffer_current:
            self._iteration_buffer_current = self.iteration_count
            self._iteration_buffer_count = 0
        else:
            self._iteration_buffer_count += 1
        return self._iteration_buffer_count

    def _get_or_init_state(
        self,
        namespace: str,
        base_ref: str,
        *,
        initial_state: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        """
        Validate states, initialize if needed, and return state ref and values.

        Parameters
        ----------
        namespace : str
            Either ``"func"`` or ``"obj"``. Used to namespace state keys.
        base_ref : str
            Base name for the state reference; a unique counter is appended and
            prefixed by the namespace (e.g., ``func:base#1``, ``obj:base#1``).
        initial_state : dict[str, Any]
            Initial mapping to use when creating a new state entry.

        Returns
        -------
        tuple[str, dict[str, Any]]
            The namespaced state reference and the stored state mapping.

        """
        # Generate unique state reference and initialize if needed
        namespaced_ref = f"{namespace}:{base_ref}"
        self._state_key_counts[namespaced_ref] += 1
        state_ref = f"{namespaced_ref}#{self._state_key_counts[namespaced_ref]}"
        if state_ref not in self._state_store:
            # Initialize new state entry with initial state.
            self._state_store[state_ref] = initial_state
        return state_ref, self._state_store[state_ref]
