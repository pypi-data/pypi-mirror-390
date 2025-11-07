"""Functions to help tracing the application, i.e. via logging.
"""
import asyncio
import logging
import threading

import humanize

logger = logging.getLogger(__name__)


class DownloadTracer:
    """Log meta-info about any long-running download task.

    Note: This is Thread-safe -- can be used with stdlib "`threading`" module.
        Downloads are I/O bound anyhow, so multithreading works well.
    """

    def __init__(
        self, service_name: str, threshold_bytes: int = 10000,
    ):
        self._name = service_name
        self._threshold = threshold_bytes
        self._total_bytes_downloaded = 0
        self._prior_total_bytes_downloaded = 0
        self._lock = threading.Lock()
        self._asyncio_loop = asyncio.new_event_loop()


    @property
    def total_bytes(self):
        return self._total_bytes_downloaded

    def trace(self, data_len: int):
        """Log message for every  data has been Add data_len to the running total."""
        if self._lock.acquire(blocking=True, timeout=1):
            try:
                self._total_bytes_downloaded += data_len
                if (
                    self._total_bytes_downloaded >   self._threshold 
                                                + self._prior_total_bytes_downloaded
                ):
                    self._prior_total_bytes_downloaded = self._total_bytes_downloaded
                    self._asyncio_loop.run_until_complete(self._log_downloaded_bytes())
            finally:
                self._lock.release()
        else:
            pass
    
    async def _log_downloaded_bytes(self, logger_function = logger.info):
        """Log the total bytes downloaded from this service."""
        logger_function(
            f'Total downloaded from {self._name}: {humanize.naturalsize(self._total_bytes_downloaded)}'
        )