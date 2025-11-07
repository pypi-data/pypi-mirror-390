"""Configuration management for DataFrame compilation options.

This module provides a flexible configuration system for controlling how DataFrames
are compiled into execution plans. It supports:

- Global defaults via :func:`set_compilation_defaults`
- Scoped overrides via :func:`compilation_config` context manager
- Explicit per-call configuration via :class:`CompilationConfig` objects
- Environment variable overrides

Configuration priority (highest to lowest):
1. Explicit ``config=`` argument to ``DataFrame._compile()``
2. Active context manager config
3. Global defaults
4. Environment variables
5. Built-in fallback defaults
"""

from __future__ import annotations

import contextvars
import os
import threading
from contextlib import contextmanager
from dataclasses import dataclass, field, fields
from typing import Any, Dict, Iterator, Optional

# Context variable to store the stack of active compilation configs
_config_stack: contextvars.ContextVar[Optional[list[CompilationConfig]]] = contextvars.ContextVar(
    "_config_stack", default=None
)

# Global default configuration (thread-safe)
_global_defaults_lock = threading.RLock()
_global_defaults: Optional[CompilationConfig] = None


@dataclass(frozen=True)
class CompilationConfig:
    """Configuration options for DataFrame compilation.

    This class mirrors the C++ ``libchalk::chalktable::CompilationOptions`` struct
    and provides a typed, validated interface for controlling compilation behavior.

    All fields are optional and default to ``None``, which means "use the value from
    the next level in the configuration priority chain".
    """

    skip_runtime_validation: Optional[bool] = None
    """Skip expensive runtime validation (e.g., array/schema integrity checks)."""

    generate_performance_summary: Optional[bool] = None
    """Generate and include a performance summary in the output."""

    update_performance_summary_interval_seconds: Optional[float] = None
    """Interval for updating performance summary (seconds)."""

    log_intermediate_batches: Optional[bool] = None
    """Log intermediate batches after each plan node (debug level)."""

    query_memory_limit_bytes: Optional[int] = None
    """Maximum RAM a query can use before spilling to disk (0 = unlimited)."""

    spill_directory: Optional[str] = None
    """Parent directory for spilling outputs when memory-bound."""

    num_threads: Optional[int] = None
    """Number of threads to use (Velox only)."""

    unbuffered_hash_probe: Optional[bool] = None
    """Disable buffering of hash probe pipeline."""

    apply_backpressure_to_replay: Optional[bool] = None
    """Apply backpressure to replay writes for better streaming."""

    enable_combine_aggregation_optimization: Optional[bool] = None
    """Enable combine aggregation optimization."""

    enable_filter_pushdown_optimization: Optional[bool] = None
    """Push symbolic filters down into SQL UDFs."""

    add_libchalk_timeline_traces: Optional[bool] = None
    """Add timeline tracer nodes to the plan."""

    velox_use_filtered_joins: Optional[bool] = None
    """Use filters during joins rather than immediately after."""

    use_online_hash_join: Optional[bool] = None
    """Use OnlineHashJoin for single-threaded plans."""

    use_velox_parquet_reader: Optional[bool] = None
    """Use the Velox Parquet reader implementation."""

    extra_options: Optional[Dict[str, str]] = field(default=None)
    """Additional unstructured options passed to the execution engine."""

    record_all_plan_rewrites: Optional[bool] = None
    """Record all plan rewrites for debugging."""

    def merge(self, other: Optional[CompilationConfig]) -> CompilationConfig:
        """Merge this config with another, preferring non-None values from self.

        :param other: Configuration to merge with (lower priority).
        :return: New merged configuration.
        """
        if other is None:
            return self

        merged_values = {}
        for f in fields(self):
            self_val = getattr(self, f.name)
            other_val = getattr(other, f.name)

            # Special handling for extra_options dict
            if f.name == "extra_options":
                if self_val is not None and other_val is not None:
                    merged_values[f.name] = {**other_val, **self_val}
                else:
                    merged_values[f.name] = self_val if self_val is not None else other_val
            else:
                merged_values[f.name] = self_val if self_val is not None else other_val

        return CompilationConfig(**merged_values)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary, excluding None values.

        :return: Dictionary of non-None configuration values.
        """
        return {f.name: getattr(self, f.name) for f in fields(self) if getattr(self, f.name) is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> CompilationConfig:
        """Create a CompilationConfig from a dictionary.

        :param data: Dictionary of configuration values.
        :return: New CompilationConfig instance.
        """
        valid_fields = {f.name for f in fields(cls)}
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)


def get_compilation_defaults() -> CompilationConfig:
    """Get the current global default compilation configuration.

    :return: Global default configuration (or empty config if none set).
    """
    with _global_defaults_lock:
        return _global_defaults or CompilationConfig()


def set_compilation_defaults(**kwargs: Any) -> None:
    """Set global default compilation options.

    These defaults apply to all DataFrame compilations unless overridden by
    a context manager or explicit config argument.

    Example:
        >>> import chalkdf
        >>> chalkdf.set_compilation_defaults(num_threads=20, enable_filter_pushdown_optimization=True)
        >>> df.run()  # Uses 20 threads with filter pushdown enabled

    :param kwargs: Configuration options to set as defaults.
    """
    global _global_defaults
    with _global_defaults_lock:
        new_config = CompilationConfig(**kwargs)
        if _global_defaults is None:
            _global_defaults = new_config
        else:
            _global_defaults = new_config.merge(_global_defaults)


def reset_compilation_defaults() -> None:
    """Reset global defaults to empty configuration."""
    global _global_defaults
    with _global_defaults_lock:
        _global_defaults = None


@contextmanager
def compilation_config(**kwargs: Any) -> Iterator[None]:
    """Context manager for scoped compilation configuration overrides.

    Configuration set within this context applies to all DataFrame compilations
    within the context, overriding global defaults but not explicit config arguments.

    Context managers can be nested, with inner contexts taking precedence.

    Example:
        >>> import chalkdf
        >>> with chalkdf.compilation_config(num_threads=5):
        ...     df.run()  # Uses 5 threads
        ...     with chalkdf.compilation_config(num_threads=1):
        ...         df2.run()  # Uses 1 thread
        ...     df.run()  # Uses 5 threads again

    :param kwargs: Configuration options to apply within this context.
    """
    config = CompilationConfig(**kwargs)

    # Get current stack and push new config
    stack = _config_stack.get() or []
    new_stack = stack + [config]
    token = _config_stack.set(new_stack)

    try:
        yield
    finally:
        # Restore previous stack
        _config_stack.reset(token)


def get_active_config() -> CompilationConfig:
    """Get the current active configuration based on context and defaults.

    This merges configurations in priority order:
    1. Active context manager configs (innermost first)
    2. Global defaults
    3. Built-in fallback defaults

    :return: Merged active configuration.
    """
    # Start with global defaults
    config = get_compilation_defaults()

    # Apply context stack from outermost to innermost
    stack = _config_stack.get() or []
    for ctx_config in stack:
        config = ctx_config.merge(config)

    return config


# Built-in fallback defaults
_FALLBACK_DEFAULTS = CompilationConfig(
    skip_runtime_validation=True,
    generate_performance_summary=False,
    update_performance_summary_interval_seconds=0.0,
    log_intermediate_batches=False,
    query_memory_limit_bytes=0,
    spill_directory="",
    num_threads=10,
    unbuffered_hash_probe=False,
    apply_backpressure_to_replay=False,
    enable_combine_aggregation_optimization=False,
    enable_filter_pushdown_optimization=True,
    add_libchalk_timeline_traces=False,
    velox_use_filtered_joins=False,
    use_online_hash_join=False,
    use_velox_parquet_reader=False,
    extra_options={},
    record_all_plan_rewrites=False,
)


def _config_from_env() -> CompilationConfig:
    """Read configuration from environment variables.

    Currently supported environment variables:
    - CHALK_USE_VELOX_PARQUET_READER: Set to "1", "true", or "yes" to enable Velox Parquet reader.

    :return: Configuration derived from environment variables.
    """
    env_config = {}

    # Handle CHALK_USE_VELOX_PARQUET_READER
    env_flag = os.getenv("CHALK_USE_VELOX_PARQUET_READER")
    if env_flag is not None:
        env_config["use_velox_parquet_reader"] = env_flag.lower() not in ("0", "false", "no")

    return CompilationConfig(**env_config) if env_config else CompilationConfig()


def resolve_config(explicit_config: Optional[CompilationConfig] = None) -> CompilationConfig:
    """Resolve final configuration from all sources.

    Priority order (highest to lowest):
    1. explicit_config argument
    2. Active context manager configs
    3. Global defaults
    4. Environment variables
    5. Built-in fallback defaults

    :param explicit_config: Explicitly provided configuration (highest priority).
    :return: Fully resolved configuration with all None values replaced.
    """
    # Start with fallback defaults
    config = _FALLBACK_DEFAULTS

    # Apply environment variables
    config = _config_from_env().merge(config)

    # Apply global defaults
    config = get_compilation_defaults().merge(config)

    # Apply context stack
    stack = _config_stack.get() or []
    for ctx_config in stack:
        config = ctx_config.merge(config)

    # Apply explicit config (highest priority)
    if explicit_config is not None:
        config = explicit_config.merge(config)

    return config
