"""Public entry points for the :mod:`chalkdf` library.

This module exposes the :class:`~chalkdf.dataframe.DataFrame` type along with
expression helpers and testing utilities so that users can simply ``import
chalkdf`` and access the core API.
"""

from __future__ import annotations

import sys

from ._libchalk_bootstrap import LibchalkNotFoundError, load_libchalk_extension

try:
    load_libchalk_extension("chalkdf.libchalk", aliases=("libchalk",))
except (LibchalkNotFoundError, ImportError) as exc:  # pragma: no cover - depends on optional binary
    raise ImportError(
        "libchalk failed to load. Install a libchalk shared library built for Python "
        f'{sys.version_info.major}.{sys.version_info.minor} (e.g. `pip install "chalkdf"` (non-headless)).'
    ) from exc

from libchalk.chalktable import AggExpr, Expr, WindowExpr

from .config import (
    CompilationConfig,
    compilation_config,
    get_compilation_defaults,
    reset_compilation_defaults,
    set_compilation_defaults,
)
from .dataframe import DataFrame
from .lazyframe import LazyFrame
from .schema import Schema
from .testing import Testing

try:
    from ._version import version as __version__
except ImportError:  # pragma: no cover - best-effort fallback
    __version__ = "0.0.0.dev0"

__all__ = [
    "DataFrame",
    "LazyFrame",
    "Schema",
    "Expr",
    "AggExpr",
    "WindowExpr",
    "Testing",
    "CompilationConfig",
    "compilation_config",
    "get_compilation_defaults",
    "set_compilation_defaults",
    "reset_compilation_defaults",
    "__version__",
]
