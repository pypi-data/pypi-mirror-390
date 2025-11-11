from __future__ import annotations

import asyncio
import logging
from typing import Optional

from .config import TelemetryConfig
from .models import TraceEnvelope
from .transport import TelemetryTransport

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TelemetryClient:
    """High-level client for sending telemetry to Neuraltrust."""

    def __init__(
        self,
        config: TelemetryConfig,
        transport: Optional[TelemetryTransport] = None,
    ) -> None:
        self._config = config
        self._transport = transport or TelemetryTransport(config)
        self._started = False
        self._start_lock = asyncio.Lock()

    @classmethod
    def from_env(cls, prefix: str = "NEURALTRUST") -> "TelemetryClient":
        config = TelemetryConfig.from_env(prefix=prefix)
        return cls(config)

    async def start(self) -> None:
        async with self._start_lock:
            if self._started:
                return
            await self._transport.start()
            self._started = True
            logger.debug("Telemetry client started")

    async def close(self) -> None:
        async with self._start_lock:
            if not self._started:
                return
            await self._transport.close()
            self._started = False
            logger.debug("Telemetry client closed")

    def close_sync(self) -> None:
        """Synchronous close for use during interpreter shutdown."""
        if not self._started:
            return
        self._transport.close_sync()
        self._started = False
        logger.debug("Telemetry client closed (sync)")

    async def send_envelope(self, envelope: TraceEnvelope) -> None:
        if self._config.sampling_rate < 1.0:
            import random

            if random.random() > self._config.sampling_rate:
                logger.debug(
                    "Telemetry envelope sampled out; sampling_rate=%s trace_ids=%s",
                    self._config.sampling_rate,
                    [trace.trace_id for trace in envelope.traces],
                )
                return

        await self.start()
        logger.debug(
            "Telemetry envelope accepted; trace_ids=%s",
            [trace.trace_id for trace in envelope.traces],
        )
        await self._transport.enqueue(envelope)

    def emit_envelope(self, envelope: TraceEnvelope) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            asyncio.run(self.send_envelope(envelope))
        else:
            loop.create_task(self.send_envelope(envelope))
