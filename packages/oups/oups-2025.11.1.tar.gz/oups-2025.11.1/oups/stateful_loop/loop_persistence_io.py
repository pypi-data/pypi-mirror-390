#!/usr/bin/env python3
"""
Created on Wed Jun  1 18:35:00 2025.

Loop persistence I/O helpers for the stateful loop.

"""
from pathlib import Path
from typing import Any

from cloudpickle import dump
from cloudpickle import load


KEY_ID = "id"
KEY_VERSION = "version"
KEY_STATES = "states"
PERSISTENCE_ID = "stateful_loop"
PERSISTENCE_VERSION = 1


class LoopPersistenceIO:
    """
    Helper for reading and writing the loop persistence file with schema validation.

    Schema: {"id": "stateful_loop", "version": 1, "states": {...}}.

    """

    @staticmethod
    def load(path: Path) -> dict[str, dict[str, Any]]:
        """
        Load and validate states from ``path``.
        """
        with open(path, "rb") as f:
            payload = load(f)
        if not isinstance(payload, dict):
            raise ValueError("invalid persistence file format.")
        if payload[KEY_ID] != PERSISTENCE_ID:
            raise ValueError("invalid persistence file id.")
        if payload[KEY_VERSION] != PERSISTENCE_VERSION:
            raise ValueError("unsupported persistence file version.")
        states = payload[KEY_STATES]
        if not isinstance(states, dict):
            raise ValueError("invalid 'states' content in persistence file.")
        return states

    @staticmethod
    def save(path: Path, states: dict[str, dict[str, Any]]) -> None:
        """
        Save ``states`` to ``path`` with schema and version.
        """
        payload = {KEY_ID: PERSISTENCE_ID, KEY_VERSION: PERSISTENCE_VERSION, KEY_STATES: states}
        with open(path, "wb") as f:
            dump(payload, f)
