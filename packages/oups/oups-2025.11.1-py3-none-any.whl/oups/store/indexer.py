#!/usr/bin/env python3
"""
Created on Wed Dec  1 18:35:00 2021.

@author: pierrot

"""
import sys
from collections.abc import Callable
from collections.abc import Hashable
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import fields
from dataclasses import is_dataclass
from os.path import sep
from pathlib import Path
from typing import Any
from typing import Protocol
from typing import get_type_hints
from typing import runtime_checkable


@runtime_checkable
class StoreKey(Protocol, Hashable):
    def __lt__(self, other: object) -> bool: ...

    def to_path(self) -> Path: ...


@runtime_checkable
class TopLevelIndexer[K: StoreKey](Protocol):
    field_sep: str
    depth: int

    @classmethod
    def from_path(cls, source: str | Path) -> K | None: ...

    @classmethod
    def from_str(cls, source: str) -> K | None: ...


# Float removed to prevent having '.' in field values.
TYPE_ACCEPTED = {int, str}
# Default fields separator, if not modified by user.
DEFAULT_FIELD_SEP = "-"
# Characters forbidden in field value.
# 'field_sep' is also included at runtime before check.
FORBIDDEN_CHARS = (sep, ".")
KEY_FIELD_SEP = "field_sep"
KEY_FROM_PATH = "from_path"
KEY_DEPTH = "depth"


def _is_dataclass_instance(obj: Any) -> bool:
    # Check if a class is an instance of a dataclass and not a dataclass
    # itself, as per
    # https://docs.python.org/3/library/dataclasses.html#dataclasses.is_dataclass
    return is_dataclass(obj) and not isinstance(obj, type)


def _dataclass_instance_to_dict(obj: Any) -> dict:
    # Shallow copy, not possible to use 'asdict()', as per
    # https://docs.python.org/3/library/dataclasses.html#dataclasses.asdict
    return {field.name: getattr(obj, field.name) for field in fields(obj)}


def _dataclass_instance_to_lists(obj: Any) -> Iterator[list[Any]]:
    """
    Yield items as lists of fields values.

    If a new dataclass instance is the last field, its fields values are
    yielded as next item, and so on...

    Parameters
    ----------
    obj : dataclass instance
        Top-level key or nested sublevel dataclass instance. May contain
        nested dataclass instances.

    Returns
    -------
    Iterator[list[Any]]
        Yields list of fields values.

    """
    fields = list(_dataclass_instance_to_dict(obj).values())
    if fields:
        yield fields
        if _is_dataclass_instance(fields[-1]):
            yield from _dataclass_instance_to_lists(fields[-1])


def _validate_toplevel_instance(toplevel: StoreKey):
    """
    Validate a 'toplevel'-decorated data class instance.

    Check field type is only among 'int', 'str' or another dataclass instance.
    Check that there is at most only one dataclass instance per nesting level,
    and if present, it is not the 1st field, nor the last field.
    Raise a TypeError or ValueError if instance is not compliant.

    Parameters
    ----------
    toplevel : StoreKey
        Top-level key instance produced by '@toplevel'.

    """
    forbidden_chars = (toplevel.field_sep, *FORBIDDEN_CHARS)
    for fields_ in _dataclass_instance_to_lists(toplevel):
        number_of_fields = len(fields_)
        for counter, field in enumerate(fields_):
            if _is_dataclass_instance(field):
                # If a dataclass instance.
                if not counter:
                    # A dataclass instance cannot be the only field.
                    # Detecting if it is in last position suffice, except if
                    # there is only one field, in which case it is also in
                    # 1st position.
                    raise TypeError(
                        "a dataclass instance cannot be the only field of a level.",
                    )
                if counter + 1 != number_of_fields:
                    # A dataclass instance cannot be in last position.
                    raise TypeError(
                        "a dataclass instance is only possible in last position.",
                    )
            else:
                # If not a dataclass instance.
                field_as_str = str(field)
                if any(symb in field_as_str for symb in forbidden_chars):
                    raise ValueError(
                        f"use of a forbidden character among {forbidden_chars} "
                        f"is not possible in {field_as_str}.",
                    )
            if not ((type(field) in TYPE_ACCEPTED) or _is_dataclass_instance(field)):
                raise TypeError(f"field type {type(field)} not possible.")
    return


def _dataclass_instance_format(toplevel: StoreKey, to_path: bool = False) -> str | Path:
    """
    Return a key instance formatted as a string or Path object.

    Parameters
    ----------
    toplevel : StoreKey
        Top-level key instance.
    to_path : bool, default False
        If True, return a Path object;
        If False, return a string.

    Returns
    -------
    str | Path
        Formatted representation of the key instance.

    """
    fields_lists = list(_dataclass_instance_to_lists(toplevel))
    # Relying on the fact that only the tail can be a dataclass instance.
    path_parts = [toplevel.field_sep.join(map(str, fields_[:-1])) for fields_ in fields_lists]
    # Handle the last field of the final level
    path_parts[-1] += (
        f"{toplevel.field_sep}{fields_lists[-1][-1]!s}" if path_parts[-1] else str(fields_lists[-1][-1])
    )
    return Path(*path_parts) if to_path else toplevel.field_sep.join(path_parts)


def _dataclass_instance_format_to_path(toplevel: StoreKey) -> Path:
    """
    Return a key instance formatted as a Path object.

    Parameters
    ----------
    toplevel : StoreKey
        Top-level key instance.

    Returns
    -------
    Path
        Path object representing the key instance.

    """
    return _dataclass_instance_format(toplevel, to_path=True)


def _field_types_for_dataclass(dc_cls: type) -> list[type]:
    # Resolve annotations using the defining module's globals to support
    # cross-module and forward-referenced sublevels.
    module_globals = sys.modules.get(dc_cls.__module__).__dict__
    resolved_hints = get_type_hints(dc_cls, globalns=module_globals)
    # Preserve dataclass field order while pulling resolved types.
    return [resolved_hints.get(field.name, field.type) for field in fields(dc_cls)]


def _resolved_last_field_type(dc_cls: type) -> type:
    module_globals = sys.modules.get(dc_cls.__module__).__dict__
    resolved_hints = get_type_hints(dc_cls, globalns=module_globals)
    # Preserve field order, return last field type if present
    dc_fields = fields(dc_cls)
    return resolved_hints.get(dc_fields[-1].name, dc_fields[-1].type)


def _dataclass_fields_types_to_lists(cls: TopLevelIndexer[StoreKey]) -> list[list[Any]]:
    """
    Type of fields in dataclass returned in lists, resolving forward refs.

    Return the type of each field, one list per level, and all levels in a
    list.

    Parameters
    ----------
    cls : TopLevelIndexer[StoreKey]
        Top-level indexer class produced by '@toplevel'.

    Returns
    -------
    list[list[type]]
        List of field-types lists, one list per level.

    """
    types: list[list[type]] = []
    level_cls: type = cls  # start from toplevel
    while True:
        level_types = _field_types_for_dataclass(level_cls)
        types.append(level_types)
        last_type = level_types[-1]
        if is_dataclass(last_type):
            level_cls = last_type
        else:
            break
    return types


def _dataclass_instance_from_source[K: StoreKey](
    cls: TopLevelIndexer[K],
    source: str | Path,
) -> K | None:
    """
    Return a dataclass instance derived from input string or Path object.

    If dataclass '__init__' fails, `None` is returned.

    Parameters
    ----------
    cls : TopLevelIndexer[K]
        Top-level indexer class to be used for generating a key instance.
    source : str | Path
        String or Path representation of the key instance.

    Returns
    -------
    K | None
        Key instance derived from input, or None if parsing fails.

    """
    types = _dataclass_fields_types_to_lists(cls)
    # Split string into different fields, depending on the type of source.
    field_sep = cls.field_sep
    if isinstance(source, Path):
        # Path case: split each part by field_sep
        strings_as_list = [substring for part in source.parts for substring in part.split(field_sep)]
    else:
        # String case: split only by field_sep (no directory separator).
        strings_as_list = source.split(field_sep)
    # Manages last level first.
    level_types = types.pop()  # remove last element
    level_length = len(level_types)
    try:
        level = [
            field_type(field_as_string)
            for field_type, field_as_string in zip(level_types, strings_as_list[-level_length:], strict=False)
        ]
        while types:
            strings_as_list = strings_as_list[:-level_length]
            level_types = types.pop()  # remove last element
            level_length = len(level_types) - 1
            # Relying on the fact that a dataclass is necessarily the last
            # field.
            level = [
                field_type(field_as_string)
                for field_type, field_as_string in zip(
                    level_types[:-1],
                    strings_as_list[-level_length:],
                    strict=False,
                )
            ] + [level_types[-1](*level)]
        return cls(*level, check=False)
    except (TypeError, ValueError):
        # TypeError if the number of arguments for instantiation of a
        # dataclass is not correct (meaning the split has not been done
        # with the right 'field_sep' character).
        # ValueError if there is a type mismatch, for instance when 'int'
        # is initialized from a string.
        return None


def _get_depth(obj: type) -> int:
    """
    Return number of levels, including 'toplevel'.

    To be decorated with '@property'.

    Parameters
    ----------
    obj : type
        Top-level indexer class.

    Returns
    -------
    int
        Number of levels (including toplevel).

    """
    depth: int = 1
    level_cls: type = obj
    while True:
        last_type = _resolved_last_field_type(level_cls)
        if is_dataclass(last_type):
            depth += 1
            level_cls = last_type
        else:
            break
    return depth


def _reduce(obj: TopLevelIndexer[StoreKey]) -> tuple[Callable, tuple[str]]:
    """
    Reduce function for making 'Indexer' serializable.

    Parameters
    ----------
    obj : TopLevelIndexer[StoreKey]
        Top-level indexer class.

    Returns
    -------
    tuple[Callable, tuple[str]]
        See '__reduce' standard interface.
        https://docs.python.org/3/library/pickle.html#object.__reduce__

    """
    return obj.from_str, (str(obj),)


class TopLevel(type):
    """
    Metaclass defining class properties of '@toplevel'-decorated class.
    """

    @property
    def field_sep(cls) -> str:
        """
        Return field separator.
        """
        return cls._field_sep

    @property
    def depth(cls) -> int:
        """
        Return depth, i.e. number of levels.
        """
        return cls._depth


def toplevel(index_class=None, *, field_sep: str = DEFAULT_FIELD_SEP) -> type | Callable:
    """
    Turn decorated class into an indexing schema.

    Decorated class is equipped with methods and attributes to use with a
    ``Store`` instance.
    It has to be defined as one would define a class decorated by
    ``@dataclass``.

    Parameters
    ----------
    field_sep : str, default '-'
        Character to use as separator between fields of the dataclass.

    Returns
    -------
    type
        Decorated class (a toplevel indexer class).

    Attributes
    ----------
    field_sep: str
        Fields separator (can't assign).
    depth: int
        Number of levels, including 'toplevel' (can't assign).

    Notes
    -----
    ``@dataclass`` is actually called when decorating with ``@toplevel`` with
    parameters set to:

      - ``order=True``,
      - ``frozen=True``

    When class is instantiated, a validation step is conducted on attributes
    types and values.

      - An instance can only be composed with ``int``, ``str`` or a dataclass
        object coming in last position;
      - Value of attribute can not incorporate forbidden characters like ``/``
        and ``self.field_sep``.

    """

    def create_toplevel_class(index_class):
        # Re-create 'index_class' as a 'TopLevel'-inheriting class to equip it
        # with class properties 'depth' and 'field_sep'
        # (as per https://stackoverflow.com/questions/5120688)
        # Explicitly add property to OtherClass.__dict__
        # (as per https://stackoverflow.com/questions/70233891)
        d = dict(index_class.__dict__)
        d.update({KEY_FIELD_SEP: TopLevel.field_sep, KEY_DEPTH: TopLevel.depth})
        index_class = TopLevel(index_class.__name__, index_class.__bases__, d)
        # Wrap with `@dataclass`.
        # TODO: when python 3.10 is more wide spread, set 'slot=True' to save
        # RAM.
        index_class = dataclass(index_class, order=True, frozen=True)

        # Equip 'index_class' with what is needed to be a 'toplevel'.
        # Dunders: modified '__init__', modified '__str__'
        # Copy of original __init__ to call it without recursion.
        index_class_init = index_class.__init__

        def __init__(self, *args, check: bool = True, **kws):
            #            object.__setattr__(self, "_field_sep", field_sep)
            index_class_init(self, *args, **kws)
            if check:
                # Validate dataclass instance.
                _validate_toplevel_instance(self)

        index_class.__init__ = __init__
        index_class.__str__ = _dataclass_instance_format

        # Class properties: 'field_sep', 'depth'
        index_class._field_sep = field_sep
        index_class._depth = _get_depth(index_class)

        # Class instance method: 'to_path'
        index_class.to_path = _dataclass_instance_format_to_path

        # Classmethods: 'from_str', 'from_path'.
        index_class.from_path = classmethod(_dataclass_instance_from_source)
        index_class.from_str = classmethod(_dataclass_instance_from_source)

        # Serialization.
        index_class.__reduce__ = _reduce

        return index_class

    if index_class:
        # Calling decorator without other parameters.
        return create_toplevel_class(index_class)
    # Calling decorator with other parameters.
    return create_toplevel_class


def is_toplevel(toplevel: Any) -> bool:
    """
    Return `True` if `toplevel`-decorated class.

    Returns 'True' if 'toplevel' (class or instance) has been decorated with
    '@toplevel'. It checks presence 'field_sep' attribute and 'from_path' method.

    """
    return hasattr(toplevel, KEY_FIELD_SEP) and callable(getattr(toplevel, KEY_FROM_PATH, None))


def sublevel(index_class):
    """
    Define a subdirectory level.

    This decorator really is an alias of ``@dataclass`` decorator, with
    parameters set to:

        - ``order=True``,
        - ``frozen=True``

    """
    # Wrap with `@dataclass`.
    return dataclass(index_class, order=True, frozen=True, slots=True)


# TODO: deep copy of an Indexer is currently not possible. Work this out.
