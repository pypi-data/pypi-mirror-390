"""
Author: Vasiliy Zdanovskiy
email: vasilyvz@gmail.com

Simple in-memory job manager for long-running demo commands.
Not for production use.
"""

import asyncio
import uuid
from typing import Any, Dict, Optional, Awaitable


class JobRecord:
    def __init__(self, task: asyncio.Task):
        self.task = task
        self.status = "running"
        self.result: Optional[Any] = None
        self.error: Optional[str] = None


_jobs: Dict[str, JobRecord] = {}


def enqueue_coroutine(coro: Awaitable[Any]) -> str:
    job_id = str(uuid.uuid4())
    task = asyncio.create_task(_run_job(job_id, coro))
    _jobs[job_id] = JobRecord(task)
    return job_id


async def _run_job(job_id: str, coro):
    rec = _jobs[job_id]
    try:
        rec.result = await coro
        rec.status = "completed"
    except Exception as exc:  # noqa: BLE001
        rec.error = str(exc)
        rec.status = "failed"


def get_job_status(job_id: str) -> Dict[str, Any]:
    rec = _jobs.get(job_id)
    if not rec:
        return {"exists": False}
    return {
        "exists": True,
        "status": rec.status,
        "done": rec.task.done(),
        "result": rec.result,
        "error": rec.error,
    }


