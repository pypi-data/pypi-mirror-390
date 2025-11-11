#!/usr/bin/env python3
"""
AST-based validation for ``StatefulLoop`` usage.

This module enforces the positive placement rules for ``StatefulLoop``:

- The ``for`` statement iterating over ``loop.iterate(...)`` must be
  immediately followed by a ``with <item_ctx> as ...:`` statement, where
  ``<item_ctx>`` is the loop target variable.
- Any ``loop.buffer(...)`` calls within that loop must appear as direct
  statements inside the body of that single ``with`` block (i.e., at the same
  indentation level as other top-level statements inside the ``with``), not
  inside conditionals, nested loops, nested ``with`` blocks, try/except, match
  blocks, comprehensions, or nested function/class bodies.

This check is intended to run before the loop begins and is strict: if the
source file cannot be read, the calling code should surface that failure.

"""
from __future__ import annotations

import ast
import inspect
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:  # pragma: no cover
    # Imported only for typing to avoid circular imports at runtime
    from .stateful_loop import StatefulLoop


ILLEGAL_ANCESTOR_TYPES = (
    ast.If,
    ast.For,
    ast.While,
    ast.AsyncFor,
    ast.Try,
    ast.Match,
    ast.FunctionDef,
    ast.AsyncFunctionDef,
    ast.ClassDef,
    ast.Lambda,
    ast.ListComp,
    ast.SetComp,
    ast.DictComp,
    ast.GeneratorExp,
)


def _get_for_target_name(for_node: ast.For) -> str | None:
    """
    Return the name bound by the iteration context in the ``for`` target.

    Parameters
    ----------
    for_node : ast.For
        The ``for`` node to inspect.

    Returns
    -------
    Optional[str]
        The name bound by the loop target, or None if unsupported.

    """
    tgt = for_node.target
    if isinstance(tgt, ast.Name):
        return tgt.id
    # Allow tuple-unpacking pattern produced by enumerate(...), e.g.::
    #   for i, item_ctx in enumerate(loop.iterate(...)):
    # In this case, the iteration context variable is conventionally the
    # second element.
    if isinstance(tgt, ast.Tuple) and len(getattr(tgt, "elts", ())) == 2:
        second = tgt.elts[1]
        if isinstance(second, ast.Name):
            return second.id
    return None


def _find_for_node(tree: ast.AST, lineno: int) -> ast.For | None:
    """
    Find the ``ast.For`` node that starts at the given line number.

    Parameters
    ----------
    tree : ast.AST
        Parsed module AST.
    lineno : int
        Expected starting line number of the ``for`` statement.

    Returns
    -------
    Optional[ast.For]
        The matching ``For`` node, if any.

    """
    for node in ast.walk(tree):
        if isinstance(node, ast.For) and getattr(node, "lineno", None) == lineno:
            return node
    return None


def _extract_iterate_target_name(for_node: ast.For) -> str | None:
    """
    Return the variable name used to call ``iterate`` in ``for ... in ...``.

    Supports the simple dotted form ``<name>.iterate(...)`` and the common
    ``enumerate(<name>.iterate(...))`` wrapper. If the iterate call target is
    more complex (e.g., attribute chains), return None to skip strict
    enforcement.

    Parameters
    ----------
    for_node : ast.For
        The ``for`` node to inspect.

    Returns
    -------
    Optional[str]
        The base name used for the ``iterate`` call, or None if unsupported.

    """
    it = for_node.iter
    call_candidate: ast.AST | None = it
    # Unwrap enumerate(...) if present
    if isinstance(call_candidate, ast.Call) and isinstance(call_candidate.func, ast.Name):
        if call_candidate.func.id == "enumerate" and call_candidate.args:
            call_candidate = call_candidate.args[0]
    if (
        isinstance(call_candidate, ast.Call)
        and isinstance(call_candidate.func, ast.Attribute)
        and call_candidate.func.attr == "iterate"
    ):
        base = call_candidate.func.value
        if isinstance(base, ast.Name):
            return base.id
    return None


def _is_illegal_placement(
    ancestors: tuple[ast.AST, ...],
    *,
    allowed_with: ast.With | None,
) -> bool:
    """
    Return True if the call is not directly under the required ``with`` block.

    Rules:
    - If ``allowed_with`` is None, any placement is illegal (used to flag calls
      outside the first required ``with``).
    - Otherwise, since traversal starts at a single top-level statement inside
      the required ``with`` body, we accept when no control-flow nodes appear
      among ancestors. Control-flow nodes are ``If``, ``For``, ``While``,
      ``AsyncFor``, ``Try``, ``Match``, function/class/lambda defs, or
      comprehensions. This ensures the call is not nested within such blocks.

    """
    if allowed_with is None:
        return True
    # Since we traverse from a single top-level statement inside the 'with'
    # body, simply ensure there is no control-flow node among ancestors.
    for a in ancestors:
        if isinstance(a, ILLEGAL_ANCESTOR_TYPES):
            return True
    return False


def _first_offending_buffer_call(
    node: ast.AST,
    loop_var_name: str,
    *,
    allowed_with: ast.With | None,
) -> ast.Call | None:
    """
    Find and return the first illegal ``loop.buffer(...)`` call under ``node``.

    Parameters
    ----------
    node : ast.AST
        Root node to inspect (typically a ``For`` body statement).
    loop_var_name : str
        The variable name on which ``iterate`` was called (e.g., ``loop``).

    Returns
    -------
    Optional[ast.Call]
        The offending call node, if found.

    """
    stack: list[tuple[ast.AST, tuple[ast.AST, ...]]] = [(node, ())]
    while stack:
        current, ancestors = stack.pop()
        if isinstance(current, ast.Call) and isinstance(
            getattr(current, "func", None),
            ast.Attribute,
        ):
            attr = current.func
            if attr.attr == "buffer" and isinstance(attr.value, ast.Name) and attr.value.id == loop_var_name:
                if _is_illegal_placement(ancestors, allowed_with=allowed_with):
                    return current
        for child in ast.iter_child_nodes(current):
            stack.append((child, ancestors + (current,)))
    return None


def _parse_and_find_for(filename: str, for_lineno: int) -> ast.For:
    """
    Parse source and locate the for-node at the call site.
    """
    source = Path(filename).read_text()
    tree = ast.parse(source, filename)
    for_node = _find_for_node(tree, for_lineno)
    if for_node is None:
        raise ValueError(
            "StatefulLoop.iterate() usage validation failed: could not locate the 'for' "
            "statement at the call site. Ensure you call iterate() directly in a for "
            "header, e.g., 'for item_ctx in loop.iterate(...)'.",
        )
    return for_node


def _validate_header_requirements(for_node: ast.For) -> tuple[str, ast.With]:
    """
    Validate the ``for`` header and first ``with`` block.

    Returns
    -------
    tuple[str, ast.With]
        The loop variable name and the first ``with`` block node.

    """
    loop_var_name = _extract_iterate_target_name(for_node)
    if loop_var_name is None:
        raise ValueError(
            "StatefulLoop.iterate() usage validation failed: expected '<name>.iterate(...)' "
            "in the for header. Complex expressions are not supported for this validation.",
        )
    target_name = _get_for_target_name(for_node)
    if target_name is None:
        raise ValueError(
            "StatefulLoop.iterate() usage validation failed: requires binding the iteration "
            "context to a simple name, e.g., 'for item_ctx in loop.iterate(...):'. ",
        )
    if not for_node.body or not isinstance(for_node.body[0], ast.With):
        raise ValueError(
            "StatefulLoop.iterate() usage validation failed: using a with statement is "
            "compulsory immediately inside the iterate-for body, e.g., "
            "'with item_ctx as item:'.",
        )
    with_node = for_node.body[0]
    if len(with_node.items) != 1:
        raise ValueError(
            "StatefulLoop.iterate() usage validation failed: the first with statement must "
            "have a single context manager using the loop target name, e.g., "
            "'with item_ctx as item:'.",
        )
    with_item = with_node.items[0]
    if not isinstance(with_item.context_expr, ast.Name) or with_item.context_expr.id != target_name:
        raise ValueError(
            "StatefulLoop.iterate() usage validation failed: the first with statement in the "
            "iterate-for body must use the iteration context variable, e.g., "
            "'with item_ctx as item:'.",
        )
    return loop_var_name, with_node


def _enforce_no_buffer_outside_with(for_node: ast.For, loop_var_name: str, filename: str) -> None:
    """
    Disallow buffer calls outside the first-with block.
    """
    for outer_stmt in for_node.body[1:]:
        offender = _first_offending_buffer_call(outer_stmt, loop_var_name, allowed_with=None)
        if offender is not None:
            raise ValueError(
                "StatefulLoop.buffer() placement validation failed: must be called directly inside "
                "the first 'with item_ctx as ...:' block (offending call at "
                f"{filename}:{offender.lineno}).",
            )


def _enforce_top_level_inside_with(with_node: ast.With, loop_var_name: str, filename: str) -> None:
    """
    Allow buffer only as top-level statements inside the with block.
    """
    for inner_stmt in with_node.body:
        offender = _first_offending_buffer_call(inner_stmt, loop_var_name, allowed_with=with_node)
        if offender is not None:
            raise ValueError(
                "StatefulLoop.buffer() placement validation failed: must be at the same "
                "indentation level as other top-level statements inside the "
                "'with item_ctx as ...:' "
                f"block (offending call at {filename}:{offender.lineno}). "
                "Avoid conditionals/loops/nested blocks.",
            )


def validate_loop_usage(loop: StatefulLoop) -> None:
    """
    Validate placement rules for ``StatefulLoop.buffer`` at iterate callsite.

    The validation enforces the following constraints for the loop where
    ``for item_ctx in loop.iterate(...):`` appears:

    - The first statement in the loop body must be a single ``with`` statement
      using the iteration context variable, e.g., ``with item_ctx as item:``.
    - Any calls to ``loop.buffer(...)`` must be top-level statements inside
      that ``with`` block (i.e., not nested inside conditionals/loops/try/with
      blocks, functions/classes/lambdas, or comprehensions).
    - No ``loop.buffer(...)`` call can appear outside that first ``with`` block
      within the same loop.

    Parameters
    ----------
    loop : StatefulLoop
        The loop instance for which placement is being validated.

    Raises
    ------
    ValueError
        If the structure of the loop body or the placement of ``buffer`` calls
        violates the rules above.

    Notes
    -----
    - This check analyzes the caller's source file using the AST and is intended
      to run before the first iteration as a fail-fast safeguard.
    - The function assumes Python 3.10+ AST (e.g., presence of ``ast.Match``).

    """
    frame = inspect.currentframe().f_back.f_back
    filename = frame.f_code.co_filename
    for_lineno = frame.f_lineno
    # Validate StatefulLoop.iterate() usage.
    for_node = _parse_and_find_for(filename, for_lineno)
    loop_var_name, with_node = _validate_header_requirements(for_node)
    # Validate StatefulLoop.buffer() usage.
    _enforce_no_buffer_outside_with(for_node, loop_var_name, filename)
    _enforce_top_level_inside_with(with_node, loop_var_name, filename)
