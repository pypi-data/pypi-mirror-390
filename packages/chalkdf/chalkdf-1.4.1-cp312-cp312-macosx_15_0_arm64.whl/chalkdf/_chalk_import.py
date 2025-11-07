from __future__ import annotations

import importlib
from typing import Any

CHALK_IMPORT_MESSAGE = (
    'chalkpy is required for this functionality. Install the optional dependency with `pip install "chalkdf[chalkpy]"`.'
)


def require_chalk_module(module: str):
    """
    Import a chalk module, raising a helpful error if the dependency is missing.
    """

    try:
        return importlib.import_module(module)
    except ImportError as exc:  # pragma: no cover - dependent on optional dependency
        raise ImportError(CHALK_IMPORT_MESSAGE) from exc


def require_chalk_attrs(module: str, *names: str) -> Any:
    """
    Import specific attributes from a chalk module with a friendly error message.
    """

    mod = require_chalk_module(module)
    try:
        attrs = tuple(getattr(mod, name) for name in names)
    except AttributeError as exc:  # pragma: no cover - dependent on optional dependency
        requested = ", ".join(names)
        raise ImportError(f"Failed to import {requested} from {module}. {CHALK_IMPORT_MESSAGE}") from exc
    return attrs[0] if len(attrs) == 1 else attrs
