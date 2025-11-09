#!/usr/bin/env python3
"""
Complete, runnable Python translation of the Rust extraction pipeline.

Key improvements aligned with feedback:
- Consistent error hierarchy (TodoziError, ValidationError, APIError).
- Centralized config management (TodoziConfig).
- API client abstraction (TodoziAPIClient) with async context manager.
- Pydantic models for all extracted data and response validation.
- Structured logging with structlog.
- Dependency injection for embedding service and config.
- Defensive resource management and input validation.

Requirements:
- Python 3.9+
- pip install pydantic==1.10.15 aiohttp aiofiles structlog

Usage:
- python todozi_extract.py extract --content "your text" --format json
- python todozi_extract.py strategy --file path/to/file.txt --format md --human

Note:
- EmbeddingService is implemented to be testable and can be swapped via DI.
- Registry and HLX parts are not included; config is loaded from env and optional tdz.hlx JSON.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import aiofiles
import aiohttp
try:
    import structlog
except ImportError:
    structlog = None
from aiohttp import ClientSession, ClientTimeout
from pydantic import BaseModel, Field as PydField, ValidationError, validator

# ------------------------------
# Logging
# ------------------------------

import logging

if structlog is not None:
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="ISO"),
            structlog.processors.JSONRenderer() if os.environ.get("TODOZI_LOG_JSON") == "1" else structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(20),  # INFO and above by default
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    LOG = structlog.get_logger("todozi.extract")
else:
    LOG = logging.getLogger("todozi.extract")

# ------------------------------
# Error Hierarchy
# ------------------------------

class TodoziError(Exception):
    """Base exception for todozi."""
    pass

class ValidationError(TodoziError):
    """Invalid input or configuration."""
    pass

class APIError(TodoziError):
    """External API or network failures."""
    pass

class ConfigError(TodoziError):
    """Configuration loading error."""
    pass

# ------------------------------
# Constants
# ------------------------------

TODOZI_API_BASE = "https://todozi.com/api/tdz/"
DEFAULT_MODEL = "gpt-oss:120b"
DEFAULT_LANGUAGE = "english"

# ------------------------------
# Config Management
# ------------------------------

@dataclass
class TodoziConfig:
    api_key: str
    user_id: str = ""
    fingerprint: str = ""

    @classmethod
    async def load(cls, cli_api_key: Optional[str] = None, cli_user_id: Optional[str] = None, cli_fingerprint: Optional[str] = None) -> "TodoziConfig":
        # Precedence: CLI > env > HLX config
        api_key = cli_api_key or os.environ.get("TDZ_API_KEY", "")

        # Read HLX (JSON) file at ~/.todozi/tdz.hlx (if present)
        user_id = ""
        fingerprint = ""
        home = os.environ.get("HOME") or os.environ.get("USERPROFILE") or ""
        hlx_path = Path(home) / ".todozi" / "tdz.hlx"
        if hlx_path.exists():
            try:
                async with aiofiles.open(hlx_path, "r", encoding="utf-8") as f:
                    raw = await f.read()
                data = json.loads(raw)
                registration = data.get("registration") if isinstance(data, dict) else None
                if isinstance(registration, dict):
                    uid = registration.get("user_id")
                    fp = registration.get("fingerprint")
                    if isinstance(uid, str):
                        user_id = uid
                    if isinstance(fp, str):
                        fingerprint = fp
            except Exception as e:
                raise ConfigError(f"Failed to read HLX config at {hlx_path}: {e}")

        # Allow CLI overrides to replace missing values
        if cli_user_id:
            user_id = cli_user_id
        if cli_fingerprint:
            fingerprint = cli_fingerprint

        if not api_key:
            raise ValidationError("API key is required. Set TDZ_API_KEY or pass --api-key.")
        if not user_id:
            LOG.warning("user_id is empty; consider setting registration.user_id in tdz.hlx")
        if not fingerprint:
            LOG.warning("fingerprint is empty; consider setting registration.fingerprint in tdz.hlx")

        return cls(api_key=api_key, user_id=user_id, fingerprint=fingerprint)

# ------------------------------
# Pydantic Models
# ------------------------------

class ExtractedTask(BaseModel):
    action: str
    time: str
    priority: str
    project: str
    status: str
    assignee: Optional[str] = None
    tags: List[str] = []

    class Config:
        extra = "ignore"

class ExtractedMemory(BaseModel):
    moment: str
    meaning: str
    reason: str
    importance: str
    term: str

    class Config:
        extra = "ignore"

class ExtractedIdea(BaseModel):
    idea: str
    share: str
    importance: str

    class Config:
        extra = "ignore"

class ExtractedError(BaseModel):
    title: str
    description: str
    severity: str
    category: str

    class Config:
        extra = "ignore"

class ExtractedTrainingData(BaseModel):
    prompt: str
    completion: str
    data_type: str

    class Config:
        extra = "ignore"

class ExtractResponse(BaseModel):
    tasks: List[ExtractedTask] = []
    memories: List[ExtractedMemory] = []
    ideas: List[ExtractedIdea] = []
    errors: List[ExtractedError] = []
    training_data: List[ExtractedTrainingData] = []
    raw_tags: List[str] = []

    class Config:
        arbitrary_types_allowed = True

    def to_json(self, indent: int = 2, ensure_ascii: bool = False) -> str:
        return self.json(indent=indent, ensure_ascii=ensure_ascii)

# ------------------------------
# Utility Functions
# ------------------------------

def hash_project_name(name: str) -> str:
    import hashlib
    return hashlib.sha1(name.encode("utf-8")).hexdigest()

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def format_timestamp_for_filename(dt: Optional[datetime] = None) -> str:
    if dt is None:
        dt = now_utc()
    return dt.strftime("%Y%m%d_%H%M%S")

def format_timestamp_for_display(dt: Optional[datetime] = None) -> str:
    if dt is None:
        dt = now_utc()
    return dt.strftime("%Y-%m-%d %H:%M:%S UTC")

# ------------------------------
# API Client
# ------------------------------

class TodoziAPIClient:
    def __init__(self, session: ClientSession, api_key: str) -> None:
        self._session = session
        self.api_key = api_key

    async def extract_content(
        self,
        endpoint: str,
        content: str,
        user_id: str,
        fingerprint: str,
        model: str = DEFAULT_MODEL,
        language: str = DEFAULT_LANGUAGE,
        extract_all: bool = True,
    ) -> Dict[str, Any]:
        url = f"{TODOZI_API_BASE}{endpoint}"
        payload = {
            "content": content,
            "extract_all": extract_all,
            "model": model,
            "language": language,
            "user_id": user_id,
            "fingerprint": fingerprint,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        LOG.info("Sending request", url=url)
        LOG.debug("Request payload", payload=payload)
        timeout = ClientTimeout(total=120)
        async with self._session.post(url, headers=headers, json=payload, timeout=timeout) as resp:
            if resp.status >= 400:
                text = await resp.text()
                raise APIError(f"API request failed [{resp.status}]: {text}")
            data = await resp.json()
            LOG.debug("API response", data=data)
            return data

@asynccontextmanager
async def get_api_client(config: TodoziConfig):
    async with ClientSession() as session:
        yield TodoziAPIClient(session=session, api_key=config.api_key)

# ------------------------------
# Embedding Service (Testable Interface + Default Implementation)
# ------------------------------

class TaskLike(BaseModel):
    user_id: str
    action: str
    time: str
    priority: str
    parent_project: str
    project_id: str
    status: str
    assignee: Optional[str] = None
    tags: List[str] = []
    dependencies: List[str] = []
    context: Optional[str] = None
    progress: Optional[str] = None

class MemoryLike(BaseModel):
    id: str
    user_id: str
    project_id: str
    status: str = "Active"
    moment: str
    meaning: str
    reason: str
    importance: str
    term: str
    memory_type: str = "Standard"
    tags: List[str] = []

class IdeaLike(BaseModel):
    id: str
    idea: str
    project_id: str
    status: str = "Active"
    share: str
    importance: str
    tags: List[str] = []
    context: Optional[str] = None

class TodoziEmbeddingService:
    def __init__(self) -> None:
        self._tasks: Dict[str, TaskLike] = {}
        self._memories: Dict[str, MemoryLike] = {}
        self._ideas: Dict[str, IdeaLike] = {}

    async def add_task(self, task: TaskLike) -> str:
        tid = task.action.strip() or "task"
        import uuid
        task_id = str(uuid.uuid4())
        self._tasks[task_id] = task
        LOG.info("Saved task", task_id=task_id, action=task.action)
        return task_id

    async def new_memory(self, memory: MemoryLike) -> str:
        mid = memory.id
        self._memories[mid] = memory
        LOG.info("Saved memory", memory_id=mid, moment=memory.moment)
        return mid

    async def new_idea(self, idea: IdeaLike) -> str:
        iid = idea.id
        self._ideas[iid] = idea
        LOG.info("Saved idea", idea_id=iid, idea=idea.idea)
        return iid

# ------------------------------
# Parsing and Serialization
# ------------------------------

def _safe_get_list_of_dicts(d: Dict[str, Any], key: str) -> List[Dict[str, Any]]:
    v = d.get(key)
    if isinstance(v, list):
        out: List[Dict[str, Any]] = []
        for item in v:
            if isinstance(item, dict):
                out.append(item)
        return out
    return []

def parse_extract_response(api_response: Dict[str, Any]) -> ExtractResponse:
    # Defensive parsing into Pydantic models
    try:
        extract_resp = ExtractResponse(
            tasks=[ExtractedTask(**t) for t in _safe_get_list_of_dicts(api_response, "tasks")],
            memories=[ExtractedMemory(**m) for m in _safe_get_list_of_dicts(api_response, "memories")],
            ideas=[ExtractedIdea(**i) for i in _safe_get_list_of_dicts(api_response, "ideas")],
            errors=[ExtractedError(**e) for e in _safe_get_list_of_dicts(api_response, "errors")],
            training_data=[ExtractedTrainingData(**t) for t in _safe_get_list_of_dicts(api_response, "training_data")],
            raw_tags=[str(t) for t in api_response.get("raw_tags", []) if isinstance(t, str)],
        )
        return extract_resp
    except ValidationError as ve:
        raise ValidationError(f"Failed to validate API response: {ve}")

def format_as_csv(response: ExtractResponse) -> str:
    out_lines: List[str] = []
    if response.tasks:
        out_lines.append("Type,Action,Time,Priority,Project,Status,Assignee,Tags")
        for t in response.tasks:
            action = t.action.replace('"', '""')
            assignee = t.assignee if t.assignee else ""
            tags = ", ".join(t.tags)
            out_lines.append(
                f'Task,"{action}","{t.time}",{t.priority},{t.project},{t.status},{assignee},"{tags}"'
            )
    if response.memories:
        if out_lines:
            out_lines.append("")
        out_lines.append("Type,Moment,Meaning,Reason,Importance,Term")
        for m in response.memories:
            moment = m.moment.replace('"', '""')
            meaning = m.meaning.replace('"', '""')
            reason = m.reason.replace('"', '""')
            out_lines.append(
                f'Memory,"{moment}","{meaning}","{reason}",{m.importance},{m.term}'
            )
    if response.ideas:
        if out_lines:
            out_lines.append("")
        out_lines.append("Type,Idea,Share,Importance")
        for i in response.ideas:
            idea = i.idea.replace('"', '""')
            out_lines.append(f'Idea,"{idea}",{i.share},{i.importance}')
    if response.errors:
        if out_lines:
            out_lines.append("")
        out_lines.append("Type,Title,Description,Severity,Category")
        for e in response.errors:
            title = e.title.replace('"', '""')
            desc = e.description.replace('"', '""')
            out_lines.append(f'Error,"{title}","{desc}",{e.severity},{e.category}')
    if response.training_data:
        if out_lines:
            out_lines.append("")
        out_lines.append("Type,Prompt,Completion,DataType")
        for t in response.training_data:
            prompt = t.prompt.replace('"', '""')
            completion = t.completion.replace('"', '""')
            out_lines.append(f'Training,"{prompt}","{completion}",{t.data_type}')
    if response.raw_tags:
        if out_lines:
            out_lines.append("")
        out_lines.append("Type,Tag")
        for tag in response.raw_tags:
            out_lines.append(f'Tag,{tag}')
    return "\n".join(out_lines)

def format_as_markdown(response: ExtractResponse) -> str:
    lines: List[str] = []
    lines.append("# Extracted Content\n")
    if response.tasks:
        lines.append("## Tasks\n")
        for task in response.tasks:
            lines.append(f"- **{task.action}**")
            lines.append(f"  - Time: {task.time}")
            lines.append(f"  - Priority: {task.priority}")
            lines.append(f"  - Project: {task.project}")
            lines.append(f"  - Status: {task.status}")
            if task.assignee:
                lines.append(f"  - Assignee: {task.assignee}")
            if task.tags:
                lines.append(f"  - Tags: {', '.join(task.tags)}")
            lines.append("")
    if response.memories:
        lines.append("## Memories\n")
        for m in response.memories:
            lines.append(f"- **{m.moment}**: {m.meaning}")
            lines.append(f"  - Reason: {m.reason}")
            lines.append(f"  - Importance: {m.importance}")
            lines.append(f"  - Term: {m.term}\n")
    if response.ideas:
        lines.append("## Ideas\n")
        for i in response.ideas:
            lines.append(f"- **{i.idea}** ({i.importance})")
            lines.append(f"  - Share: {i.share}\n")
    if response.errors:
        lines.append("## Errors\n")
        for e in response.errors:
            lines.append(f"- **{e.title}**: {e.description}")
            lines.append(f"  - Severity: {e.severity}")
            lines.append(f"  - Category: {e.category}\n")
    if response.training_data:
        lines.append("## Training Data\n")
        for t in response.training_data:
            lines.append(f"- **{t.prompt}**")
            lines.append(f"  - Type: {t.data_type}")
            lines.append(f"  - Completion: {t.completion}\n")
    if response.raw_tags:
        lines.append("## Raw Tags\n")
        for tag in response.raw_tags:
            lines.append(f"- {tag}\n")
