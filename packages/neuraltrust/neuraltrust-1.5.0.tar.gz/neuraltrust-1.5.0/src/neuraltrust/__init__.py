from __future__ import annotations

import logging
import os
from typing import TYPE_CHECKING

from .client import TelemetryClient
from .config import TelemetryConfig

LOG_LEVEL = os.getenv("LOG_LEVEL")
if LOG_LEVEL:
    logging.basicConfig(level=getattr(logging, LOG_LEVEL.upper(), logging.INFO))

__all__ = [
    "TelemetryConfig",
    "TelemetryClient",
]

if TYPE_CHECKING:
    from .processors.openai import NeuraltrustTraceProcessor, register_openai_tracing
else:
    try:
        from .processors.openai import NeuraltrustTraceProcessor, register_openai_tracing
    except ModuleNotFoundError:  # pragma: no cover - optional dependency
        NeuraltrustTraceProcessor = None  # type: ignore[assignment]
        register_openai_tracing = None  # type: ignore[assignment]
    else:
        __all__.extend(["NeuraltrustTraceProcessor", "register_openai_tracing"])
