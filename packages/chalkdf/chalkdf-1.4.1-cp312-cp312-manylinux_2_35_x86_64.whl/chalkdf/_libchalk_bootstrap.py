"""Helpers to locate and load the external ``libchalk`` shared library.

This module is used by ``libchalk`` to support the "headless" wheel
variant where the compiled extension is supplied by the environment instead of
being bundled inside the package.  The loader searches a small, well-defined
set of locations so that users can control where the binary lives without
modifying ``sys.path`` manually.
"""

from __future__ import annotations

import importlib.machinery
import importlib.util
import os
import sys
from pathlib import Path
from types import ModuleType
from typing import Iterable, Iterator, NamedTuple, Sequence

__all__ = [
    "ENV_PATH_OVERRIDE",
    "collect_candidates",
    "load_libchalk_extension",
]

ENV_PATH_OVERRIDE = "CHALKDF_LIBCHALK_PATH"

# Normal CPython exposes several suffixes for extension modules (per platform).
_EXTENSION_SUFFIXES: tuple[str, ...] = tuple(
    dict.fromkeys(importlib.machinery.EXTENSION_SUFFIXES + [".so", ".dylib", ".pyd"])
)
_CANDIDATE_BASENAMES = set("libchalk")


class _CandidateCollection(NamedTuple):
    candidates: list[Path]
    search_log: list[str]
    search_summary: str


class LibchalkNotFoundError(ImportError):
    """Raised when the loader cannot locate a suitable shared library."""


def _looks_like_extension(path: Path) -> bool:
    name = path.name
    return any(name.endswith(suffix) for suffix in _EXTENSION_SUFFIXES)


def _iter_directory_candidates(directory: Path) -> Iterator[Path]:
    if not directory.is_dir():
        return

    seen: set[Path] = set()
    for base in _CANDIDATE_BASENAMES:
        for suffix in _EXTENSION_SUFFIXES:
            candidate = (directory / f"{base}{suffix}").resolve()
            if candidate.is_file() and candidate not in seen:
                seen.add(candidate)
                yield candidate

    # Fallback for filenames that inject build metadata (e.g. ``libchalk.cpython...so``).
    for child in directory.glob("libchalk*"):
        resolved = child.resolve()
        if resolved in seen or not resolved.is_file():
            continue
        if _looks_like_extension(resolved):
            seen.add(resolved)
            yield resolved


def _is_site_packages_path(path: Path) -> bool:
    return any(part.lower() in {"site-packages", "dist-packages"} for part in path.parts)


def _split_os_path(value: str) -> list[str]:
    return [chunk for chunk in value.split(os.pathsep) if chunk]


def _resolve_path(candidate: Path | str) -> Path | None:
    try:
        return Path(candidate).expanduser().resolve()
    except (TypeError, ValueError, OSError):
        return None


def _iter_search_directories(
    env: os._Environ[str],
    package_dir: Path,
    sys_path: Iterable[str] | None = None,
) -> Iterator[tuple[str, Path]]:
    path_entries = list(sys.path if sys_path is None else sys_path)
    site_sys_entries: list[Path] = []
    other_sys_entries: list[Path] = []

    for entry in path_entries:
        resolved = _resolve_path(entry)
        if resolved is None:
            continue
        container = site_sys_entries if _is_site_packages_path(resolved) else other_sys_entries
        container.append(resolved)

    seen: set[Path] = set()

    def _record(label: str, candidate: Path | str) -> Path | None:
        resolved = _resolve_path(candidate)
        if resolved is None or resolved in seen:
            return None
        seen.add(resolved)
        return resolved

    # 1. Prefer system/virtualenv site-packages directories.
    for directory in site_sys_entries:
        if directory in seen:
            continue
        seen.add(directory)
        yield ("sys.path", directory)

    # 2. Look adjacent to the package.
    for label, candidate in (
        ("package", package_dir),
        ("package_parent", package_dir.parent),
        ("package_extra", package_dir / "_lib"),
        ("package_extra", package_dir.parent / "_lib"),
    ):
        resolved = _record(label, candidate)
        if resolved is not None:
            yield (label, resolved)

    # 3. Standard dynamic library search paths.
    for var in ("LD_LIBRARY_PATH", "DYLD_LIBRARY_PATH"):
        value = env.get(var)
        if not value:
            continue
        for chunk in _split_os_path(value):
            resolved = _record(var, chunk)
            if resolved is not None:
                yield (var, resolved)

    # 4. Finally, fall back to ``sys.path`` entries so virtualenv/site-packages
    # directories are covered without a dedicated override.
    for directory in other_sys_entries:
        if directory in seen:
            continue
        seen.add(directory)
        yield ("sys.path", directory)


def collect_candidates(
    *,
    env: os._Environ[str] | None = None,
    sys_path: Iterable[str] | None = None,
) -> _CandidateCollection:
    """Collect candidate shared libraries and the locations that were searched."""

    env = os.environ if env is None else env
    package_dir = Path(__file__).resolve().parent
    sys_path_iterable = list(sys.path if sys_path is None else sys_path)

    def _summarise(log: list[str]) -> str:
        return ", ".join(log) if log else "<none>"

    override_value = env.get(ENV_PATH_OVERRIDE)
    if override_value:
        override_path = Path(override_value).expanduser()
        if override_path.is_file():
            if not _looks_like_extension(override_path):
                raise LibchalkNotFoundError(
                    f"{ENV_PATH_OVERRIDE}={override_value!r} is not a recognised libchalk shared object"
                )
            resolved_file = override_path.resolve()
            search_log = [f"{ENV_PATH_OVERRIDE} file: {resolved_file}"]
            return _CandidateCollection(
                candidates=[resolved_file],
                search_log=search_log,
                search_summary=_summarise(search_log),
            )
        if override_path.is_dir():
            matches = list(_iter_directory_candidates(override_path))
            if matches:
                resolved_dir = override_path.resolve()
                search_log = [f"{ENV_PATH_OVERRIDE} directory: {resolved_dir}"]
                return _CandidateCollection(
                    candidates=matches,
                    search_log=search_log,
                    search_summary=_summarise(search_log),
                )
            raise LibchalkNotFoundError(
                f"{ENV_PATH_OVERRIDE} directory {override_path!s} does not contain a libchalk shared object"
            )
        raise LibchalkNotFoundError(f"{ENV_PATH_OVERRIDE}={override_value!r} does not exist")

    seen_dirs: set[Path] = set()
    search_queue: list[tuple[str, Path]] = []

    for label, directory in _iter_search_directories(env, package_dir, sys_path_iterable):
        if directory in seen_dirs:
            continue
        seen_dirs.add(directory)
        search_queue.append((label, directory))

    candidate_files: list[Path] = []
    for _, directory in search_queue:
        if directory.is_file():
            if _looks_like_extension(directory):
                candidate_files.append(directory)
            continue
        candidate_files.extend(_iter_directory_candidates(directory))

    search_log = [f"{label}: {directory}" for label, directory in search_queue]
    return _CandidateCollection(
        candidates=candidate_files,
        search_log=search_log,
        search_summary=_summarise(search_log),
    )


def load_libchalk_extension(fullname: str, *, aliases: Sequence[str] = ()) -> ModuleType:
    """Load the ``libchalk`` extension module located by :func:`_collect_candidates`.

    Parameters
    ----------
    fullname:
        Canonical module name to register the extension under.
    aliases:
        Additional import names that should resolve to the same module object.  This allows
        the binary to be exposed both as a top-level package (``libchalk``) and as a submodule
        (``chalkdf.libchalk``) without duplicating initialisation.
    """

    def _coerce_existing(name: str) -> ModuleType | None:
        candidate = sys.modules.get(name)
        if not isinstance(candidate, ModuleType):
            return None

        spec = getattr(candidate, "__spec__", None)
        if spec is not None and isinstance(getattr(spec, "loader", None), importlib.machinery.ExtensionFileLoader):
            return candidate

        loader = getattr(candidate, "__loader__", None)
        if isinstance(loader, importlib.machinery.ExtensionFileLoader):
            return candidate

        module_file = getattr(candidate, "__file__", None)
        if isinstance(module_file, str) and any(module_file.endswith(suffix) for suffix in _EXTENSION_SUFFIXES):
            return candidate
        return None

    def _bind_aliases(module: ModuleType) -> ModuleType:
        module_names = (fullname, *aliases)
        for alias in aliases:
            sys.modules[alias] = module

        registered = list(sys.modules.items())
        for registered_name, registered_module in registered:
            source_prefix = None
            for candidate in module_names:
                if registered_name == candidate or registered_name.startswith(f"{candidate}."):
                    source_prefix = candidate
                    break
            if source_prefix is None:
                continue
            suffix = registered_name[len(source_prefix) :]
            for target in module_names:
                if target == source_prefix:
                    continue
                target_name = f"{target}{suffix}"
                sys.modules[target_name] = registered_module
        return module

    existing = _coerce_existing(fullname)
    if existing is not None:
        return _bind_aliases(existing)

    for alias in aliases:
        alias_module = _coerce_existing(alias)
        if alias_module is not None:
            sys.modules[fullname] = alias_module
            return _bind_aliases(alias_module)

    collection = collect_candidates()
    candidates = collection.candidates
    loader_errors: list[str] = []

    if not candidates:
        raise ImportError(
            (
                "Unable to load libchalk; no shared library candidates were discovered. "
                f"Searched: {collection.search_summary}. "
                f"Set {ENV_PATH_OVERRIDE} to point to the libchalk shared object."
            ),
            name=fullname,
        )

    for shared_object in candidates:
        spec = importlib.util.spec_from_file_location(fullname, shared_object)
        if spec is None or not isinstance(spec.loader, importlib.machinery.ExtensionFileLoader):
            loader_errors.append(f"{shared_object} is not a valid extension module")
            continue

        placeholders: list[str] = []
        try:
            module = importlib.util.module_from_spec(spec)
            sys.modules[fullname] = module

            for alias in aliases:
                if alias in sys.modules:
                    continue
                sys.modules[alias] = module
                placeholders.append(alias)

            spec.loader.exec_module(module)
        except ImportError as exc:  # pragma: no cover - depends on local interpreter
            loader_errors.append(f"{shared_object}: {exc}")
            sys.modules.pop(fullname, None)
            for alias in placeholders:
                sys.modules.pop(alias, None)
            continue
        else:
            break
    else:
        searched = ", ".join(str(path) for path in candidates) or "<none>"
        details = "; ".join(loader_errors) if loader_errors else "no suitable shared object found"
        raise ImportError(
            (f"Unable to load libchalk. Tried: {searched}. Errors: {details}. Searched: {collection.search_summary}."),
            name=fullname,
        )

    # Ensure that Python treats the module as a package so that submodules
    # provided by the binary remain importable.
    package_paths: list[str] = []
    parent_dir = shared_object.parent
    if parent_dir.is_dir():
        package_paths.append(str(parent_dir))
    module.__dict__.setdefault("__path__", package_paths)

    return _bind_aliases(module)
