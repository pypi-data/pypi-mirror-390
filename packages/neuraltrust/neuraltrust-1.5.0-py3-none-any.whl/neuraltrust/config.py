from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict

DEFAULT_API_ENDPOINT = "https://data.neuraltrust.ai/v1/traces/batch"


@dataclass(slots=True)
class TelemetryConfig:
    """Configuration for Neuraltrust telemetry export."""

    api_key: str
    endpoint: str = DEFAULT_API_ENDPOINT
    batch_size: int = 25
    flush_interval_seconds: float = 2.0
    timeout_seconds: float = 5.0
    max_retries: int = 3
    metadata: Dict[str, str] = field(default_factory=dict)
    sampling_rate: float = 1.0

    @classmethod
    def from_env(cls, prefix: str = "NEURALTRUST") -> "TelemetryConfig":
        api_key = os.getenv(f"{prefix}_API_KEY")
        if not api_key:
            raise ValueError("Neuraltrust API key not configured")

        endpoint = os.getenv(f"{prefix}_ENDPOINT", DEFAULT_API_ENDPOINT)
        batch_size = int(os.getenv(f"{prefix}_BATCH_SIZE", "25"))
        flush_interval_seconds = float(os.getenv(f"{prefix}_FLUSH_INTERVAL", "2.0"))
        timeout_seconds = float(os.getenv(f"{prefix}_TIMEOUT", "5.0"))
        max_retries = int(os.getenv(f"{prefix}_MAX_RETRIES", "3"))
        sampling_rate = float(os.getenv(f"{prefix}_SAMPLING_RATE", "1.0"))

        metadata: Dict[str, str] = {}
        metadata_prefix = f"{prefix}_METADATA_"
        for key, value in os.environ.items():
            if key.startswith(metadata_prefix):
                metadata_key = key[len(metadata_prefix) :].lower()
                metadata[metadata_key] = value

        return cls(
            api_key=api_key,
            endpoint=endpoint,
            batch_size=batch_size,
            flush_interval_seconds=flush_interval_seconds,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
            metadata=metadata,
            sampling_rate=sampling_rate,
        )
