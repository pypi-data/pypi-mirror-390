"""
Backward-compatibility shim for sweep utilities.

This module re-exports sweep helpers from `autotrain.utils` and provides
compatibility wrappers where older signatures were used.
"""

from typing import Any, Dict, List, Optional

# Re-export core symbols from the consolidated utils module
from autotrain.utils import (  # type: ignore
    SweepBackend as _SweepBackend,
    SweepConfig as _SweepConfig,
    SweepResult as _SweepResult,
    HyperparameterSweep as _HyperparameterSweep,
    run_autotrain_sweep,
    ParameterRange as _NewParameterRange,
)


# Public aliases
SweepBackend = _SweepBackend
SweepConfig = _SweepConfig
SweepResult = _SweepResult
HyperparameterSweep = _HyperparameterSweep


class ParameterRange:  # backward-compatible wrapper
    """Backward compatible ParameterRange wrapper.

    Old signature: ParameterRange(name, param_type, low, high)
    New signature: ParameterRange(low, high, distribution)
    """

    def __init__(
        self,
        name: Optional[str] = None,
        param_type: Optional[str] = None,
        low: float = 0.0,
        high: float = 1.0,
        distribution: Optional[str] = None,
    ):
        # Map old param_type to distribution if not provided
        dist = distribution
        if dist is None and param_type is not None:
            if param_type.lower() in ("int", "int_uniform"):
                dist = "int_uniform"
            elif param_type.lower() in ("log", "log_uniform"):
                dist = "log_uniform"
            else:
                dist = "uniform"
        elif dist is None:
            dist = "uniform"

        self._inner = _NewParameterRange(low=low, high=high, distribution=dist)
        self.name = name

    def sample(self, trial=None, backend: Optional[_SweepBackend] = None):
        # Backend is ignored in the new implementation; we keep the arg for compatibility
        return self._inner.sample(trial=trial)


__all__ = [
    "SweepBackend",
    "SweepConfig",
    "SweepResult",
    "HyperparameterSweep",
    "run_autotrain_sweep",
    "ParameterRange",
]

