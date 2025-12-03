import time
import os
import uuid
import asyncio
import json
from pydantic import BaseModel
from typing import Any, Literal, Dict
from app.types import DICT_PARAMS
from app.logger import get_logger

logger = get_logger(__name__)

EVALUATE_FOLDER = "/evaluate"
EVALUATE_DATASET_FORMAT = Literal["auto", "conversational", "text"]
EVALUATE_TASK_STATUS = Literal["queued", "running", "done", "error"]


class EVALUATE_TASK(BaseModel):
    id: str
    status: EVALUATE_TASK_STATUS | None = None
    queued_at: float
    running_at: float | None = None
    done_at: float | None = None
    result: Any | None = None
    progress: int | None = 0
    error: str | None = None


class EVALUATE_TASKS_STORE:

    def __init__(self):
        self._store: Dict[str, EVALUATE_TASK] = {}
        self._lock = asyncio.Lock()
        self._save_on_dir = EVALUATE_FOLDER
        if not os.path.isdir(EVALUATE_FOLDER):
            logger.warning("⚠️ TaskStore saving directory not found: saving to disk disabled")
            self._save_on_dir = None

    async def _update(self, task_id: str, **kwargs):
        async with self._lock:
            task = self._store.get(task_id)
            if not task:
                raise KeyError(f"Evaluate task {task_id} not found")
            updated = task.model_copy(update=kwargs)
            self._store[task_id] = updated

    async def create(self) -> str:
        async with self._lock:
            task_id = str(uuid.uuid4())
            self._store[task_id] = EVALUATE_TASK(
                id=task_id,
                status="queued",
                queued_at=time.time(),
            )
            return task_id

    async def set_error(self, task_id: str, error: str):
        await self._update(task_id, status="error", error=error)

    async def set_running(self, task_id: str):
        await self._update(task_id, status="running", running_at=time.time())

    async def set_done(self, task_id: str, result: Any):
        await self._update(task_id, status="done", done_at=time.time(), result=result)
        if self._save_on_dir:
            file_path = f"{self._save_on_dir}/{task_id}.json"
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(result, file)
            logger.debug(f"{os.listdir(EVALUATE_FOLDER)}")
            logger.debug(f"💾 Task {task_id} completions saved to {file_path}")

    async def get(self, task_id: str) -> EVALUATE_TASK:
        async with self._lock:
            task = self._store.get(task_id)
            if not task:
                raise KeyError(f"Task {task_id} not found")
            return task

    async def dict(self) -> list[EVALUATE_TASK]:
        async with self._lock:
            return [task.model_dump() for task in self._store.values()]

    async def cleanup(self, older_than_secs: int = 60 * 10):
        async with self._lock:
            now = time.time()
            expired = [tid for tid, t in self._store.items() if t.done_at and (now - t.done_at) > older_than_secs]
            for tid in expired:
                del self._store[tid]
                logger.debug(f"🗑️ Task {tid} expired and removed.")


class EVALUATE_INPUTS(BaseModel):
    dataset_name: str
    model_id: str | None = None
    container: str | None = None
    experiment_project: str | None = None
