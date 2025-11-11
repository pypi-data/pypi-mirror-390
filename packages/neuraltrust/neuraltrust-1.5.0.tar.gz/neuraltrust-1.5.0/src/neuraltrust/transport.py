from __future__ import annotations

import asyncio
import logging
from collections import deque
from typing import Deque, Optional
import contextlib

import httpx

from .config import TelemetryConfig
from .models import TraceEnvelope

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class TelemetryTransport:
    """Background sender that batches trace envelopes."""

    def __init__(self, config: TelemetryConfig) -> None:
        self._config = config
        self._queue: Deque[TraceEnvelope] = deque()
        self._lock = asyncio.Lock()
        self._flush_task: Optional[asyncio.Task[None]] = None
        self._closing = False

    async def start(self) -> None:
        if self._flush_task is None:
            self._flush_task = asyncio.create_task(self._flush_loop())
            logger.debug("Telemetry transport started")

    async def close(self) -> None:
        logger.debug("Telemetry transport closing")
        self._closing = True
        if self._flush_task:
            self._flush_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._flush_task
            self._flush_task = None
        await self._flush(force=True)
        logger.debug("Telemetry transport closed")

    def close_sync(self) -> None:
        """Synchronous close for use during interpreter shutdown."""
        logger.debug("Telemetry transport closing (sync)")
        self._closing = True
        # Get pending items without async lock
        pending: list[TraceEnvelope] = []
        while self._queue:
            pending.append(self._queue.popleft())
        if pending:
            logger.debug(
                "Telemetry flush triggered (sync); batch_size=%s",
                len(pending),
            )
            self._send_batch_sync(pending)
        logger.debug("Telemetry transport closed (sync)")

    async def enqueue(self, envelope: TraceEnvelope) -> None:
        async with self._lock:
            self._queue.append(envelope)
            queue_size = len(self._queue)
        logger.debug("Telemetry envelope queued; queue_size=%s", queue_size)
        if not self._flush_task and not self._closing:
            await self.start()
        if queue_size >= self._config.batch_size:
            logger.debug("Queue reached batch size; flushing immediately")
            await self._flush()

    async def _flush_loop(self) -> None:
        try:
            while not self._closing:
                await asyncio.sleep(self._config.flush_interval_seconds)
                await self._flush()
        except asyncio.CancelledError:  # pragma: no cover - shutdown
            logger.debug("Flush loop cancelled")
            raise

    async def _flush(self, force: bool = False) -> None:
        pending: list[TraceEnvelope] = []
        async with self._lock:
            if not self._queue:
                return
            while self._queue and (force or len(pending) < self._config.batch_size):
                pending.append(self._queue.popleft())
        if not pending:
            return
        logger.debug(
            "Telemetry flush triggered; batch_size=%s force=%s remaining_queue=%s",
            len(pending),
            force,
            len(self._queue),
        )
        await self._send_batch(pending)
        if force and self._queue:
            await self._flush(force=True)

    async def _send_batch(self, batch: list[TraceEnvelope]) -> None:
        payload = [envelope.model_dump(mode="json", by_alias=True) for envelope in batch]
        backoff = 0.5
        for attempt in range(1, self._config.max_retries + 2):
            try:
                async with httpx.AsyncClient(timeout=self._config.timeout_seconds) as client:
                    logger.debug(
                        "Sending telemetry batch; items=%s endpoint=%s attempt=%s",
                        len(batch),
                        self._config.endpoint,
                        attempt,
                    )
                    response = await client.post(
                        self._config.endpoint,
                        json=payload,
                        headers={
                            "Authorization": f"Bearer {self._config.api_key}",
                            "Content-Type": "application/json",
                        },
                    )
                    logger.debug("Telemetry batch response: %s", response.text)
                if response.status_code < 400:
                    logger.debug(
                        "Telemetry batch sent; items=%s status=%s",
                        len(batch),
                        response.status_code,
                    )
                    return

                if response.status_code in {429, 500, 502, 503, 504}:
                    logger.warning(
                        "Retryable telemetry error; status=%s attempt=%s", response.status_code, attempt
                    )
                else:
                    logger.error(
                        "Failed to send telemetry batch; status=%s body=%s",
                        response.status_code,
                        response.text,
                    )
                    return
            except httpx.HTTPError as exc:  # pragma: no cover - network failure
                logger.warning("HTTP error sending telemetry: %s", exc)
            except RuntimeError as exc:  # pragma: no cover - shutdown issues
                logger.warning("Runtime error sending telemetry (may be shutting down): %s", exc)
                return
            except Exception as exc:  # pragma: no cover - unexpected errors
                logger.warning("Unexpected error sending telemetry: %s", exc)

            await asyncio.sleep(backoff)
            backoff *= 2

        logger.error("Telemetry batch exhausted retries; items=%s", len(batch))


    def _send_batch_sync(self, batch: list[TraceEnvelope]) -> None:
        """Synchronous version of _send_batch for shutdown scenarios."""
        payload = [envelope.model_dump(mode="json", by_alias=True) for envelope in batch]
        backoff = 0.5
        for attempt in range(1, self._config.max_retries + 2):
            try:
                with httpx.Client(timeout=self._config.timeout_seconds) as client:
                    logger.debug(
                        "Sending telemetry batch (sync); items=%s endpoint=%s attempt=%s",
                        len(batch),
                        self._config.endpoint,
                        attempt,
                    )
                    response = client.post(
                        self._config.endpoint,
                        json=payload,
                        headers={
                            "Authorization": f"Bearer {self._config.api_key}",
                            "Content-Type": "application/json",
                        },
                    )
                    logger.debug("Telemetry batch response (sync): %s", response.text)
                if response.status_code < 400:
                    logger.debug(
                        "Telemetry batch sent (sync); items=%s status=%s",
                        len(batch),
                        response.status_code,
                    )
                    return

                if response.status_code in {429, 500, 502, 503, 504}:
                    logger.warning(
                        "Retryable telemetry error (sync); status=%s attempt=%s", response.status_code, attempt
                    )
                else:
                    logger.error(
                        "Failed to send telemetry batch (sync); status=%s body=%s",
                        response.status_code,
                        response.text,
                    )
                    return
            except httpx.HTTPError as exc:
                logger.warning("HTTP error sending telemetry (sync): %s", exc)
            except RuntimeError as exc:
                logger.warning("Runtime error sending telemetry (sync, may be shutting down): %s", exc)
                return
            except Exception as exc:
                logger.warning("Unexpected error sending telemetry (sync): %s", exc)

            import time
            time.sleep(backoff)
            backoff *= 2

        logger.error("Telemetry batch exhausted retries (sync); items=%s", len(batch))
