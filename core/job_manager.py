"""
Asynchrones Job-Handling für Tool-Ausführung.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass, field
from datetime import datetime, timezone
import threading
import time
import uuid
from typing import Any, Callable, Dict, Optional


@dataclass
class JobResult:
    job_id: str
    status: str
    created_at: str
    updated_at: str
    retries: int = 0
    timeout_seconds: int = 300
    progress: int = 0
    error: Optional[str] = None
    result: Any = None
    cancelled: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class JobManager:
    def __init__(self, max_workers: int = 4):
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.jobs: Dict[str, JobResult] = {}
        self.futures = {}
        self.cancel_flags: Dict[str, threading.Event] = {}
        self.lock = threading.Lock()

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def _run_with_retry(
        self,
        job_id: str,
        callback: Callable[..., Any],
        retries: int,
        args: tuple,
        kwargs: dict,
    ):
        job = self.jobs[job_id]
        for attempt in range(retries + 1):
            if self.cancel_flags[job_id].is_set():
                job.status = "cancelled"
                job.cancelled = True
                job.updated_at = self._now()
                return None
            try:
                job.status = "running"
                job.retries = attempt
                job.updated_at = self._now()
                result = callback(*args, **kwargs)
                job.status = "completed"
                job.progress = 100
                job.result = result
                job.updated_at = self._now()
                return result
            except Exception as exc:
                job.error = str(exc)
                job.updated_at = self._now()
                if attempt >= retries:
                    job.status = "failed"
                    raise
                time.sleep(0.1)
        return None

    def submit(
        self,
        callback: Callable[..., Any],
        *args,
        timeout_seconds: int = 300,
        retries: int = 1,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> str:
        job_id = str(uuid.uuid4())
        created_at = self._now()
        with self.lock:
            self.jobs[job_id] = JobResult(
                job_id=job_id,
                status="queued",
                created_at=created_at,
                updated_at=created_at,
                timeout_seconds=timeout_seconds,
                metadata=metadata or {},
            )
            self.cancel_flags[job_id] = threading.Event()
            self.futures[job_id] = self.executor.submit(
                self._run_with_retry,
                job_id,
                callback,
                retries,
                args,
                kwargs,
            )
        return job_id

    def set_progress(self, job_id: str, progress: int) -> None:
        with self.lock:
            job = self.jobs.get(job_id)
            if not job:
                return
            job.progress = max(0, min(100, int(progress)))
            job.updated_at = self._now()

    def cancel(self, job_id: str) -> bool:
        with self.lock:
            if job_id not in self.jobs:
                return False
            self.cancel_flags[job_id].set()
            future = self.futures.get(job_id)
            cancelled = future.cancel() if future else False
            job = self.jobs[job_id]
            job.status = "cancelled"
            job.cancelled = True
            job.updated_at = self._now()
            return cancelled or True

    def wait(self, job_id: str) -> JobResult:
        future = self.futures.get(job_id)
        job = self.jobs[job_id]
        if not future:
            return job
        try:
            future.result(timeout=job.timeout_seconds)
        except FutureTimeoutError:
            self.cancel(job_id)
            job.status = "timeout"
            job.error = f"Timed out after {job.timeout_seconds}s"
            job.updated_at = self._now()
        except Exception as exc:
            job.status = "failed"
            job.error = str(exc)
            job.updated_at = self._now()
        return job

    def status(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.jobs.get(job_id)
        if not job:
            return None
        return {
            "job_id": job.job_id,
            "status": job.status,
            "progress": job.progress,
            "retries": job.retries,
            "error": job.error,
            "cancelled": job.cancelled,
            "created_at": job.created_at,
            "updated_at": job.updated_at,
            "metadata": job.metadata,
        }
