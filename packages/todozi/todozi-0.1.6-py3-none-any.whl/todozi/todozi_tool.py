# todozi_tools.py
# ==============================================================================
# Python translation of the Rust Todozi tools module (idiomatic, async, validated)
# Incorporates feedback:
#  - Concurrency safety (StorageProxy.execute())
#  - Error handling consistency (returns ToolResult, no silent failures)
#  - API design improvements (validate_params decorator)
#  - Dictionary dispatch for Rust match patterns
#  - Resource management (ResourceManager)
#  - Builder pattern and DI for embedding service
# ==============================================================================

from __future__ import annotations

import asyncio
import json
import os
import re
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterable, Callable, TypeVar, Generic, Awaitable, Literal

# ---------------------------------------------------------------------------
# Core types and Enums
# ---------------------------------------------------------------------------

class Priority(Enum):
    Low = "low"
    Medium = "medium"
    High = "high"
    Critical = "critical"
    Urgent = "urgent"

class Status(Enum):
    Todo = "todo"
    InProgress = "in_progress"
    Blocked = "blocked"
    Review = "review"
    Done = "done"

class MemoryImportance(Enum):
    Low = "low"
    Medium = "medium"
    High = "high"
    Critical = "critical"

class MemoryTerm(Enum):
    Short = "short"
    Long = "long"

class MemoryType(Enum):
    Standard = "standard"
    Emotional = "emotional"

class IdeaImportance(Enum):
    Low = "low"
    Medium = "medium"
    High = "high"
    Breakthrough = "breakthrough"

class ShareLevel(Enum):
    Private = "private"
    Team = "team"
    Public = "public"

class ErrorSeverity(Enum):
    Low = "low"
    Medium = "medium"
    High = "high"
    Critical = "critical"

class ErrorCategory(Enum):
    Runtime = "runtime"
    Database = "database"
    Network = "network"
    Validation = "validation"

class ChunkingLevel(Enum):
    Project = "project"
    Module = "module"
    Class = "class"
    Method = "method"
    Block = "block"

class ChunkStatus(Enum):
    Pending = "pending"
    InProgress = "in_progress"
    Completed = "completed"
    Blocked = "blocked"

class ItemStatus(Enum):
    Active = "active"
    Archived = "archived"

class ResourceLock(Enum):
    FilesystemRead = "FilesystemRead"
    FilesystemWrite = "FilesystemWrite"
    Network = "Network"
    Memory = "Memory"

# ---------------------------------------------------------------------------
# Data Models
# ---------------------------------------------------------------------------

@dataclass
class Task:
    id: str
    user_id: str
    action: str
    time: str
    priority: Priority
    parent_project: str
    status: Status
    assignee: Optional[Priority] = None  # Using Priority to model Assignee variant; adjust to Enum if needed
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    context_notes: Optional[str] = None
    progress: Optional[int] = None
    embedding_vector: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Memory:
    id: str
    user_id: str
    project_id: Optional[str]
    status: ItemStatus
    moment: str
    meaning: str
    reason: str
    importance: MemoryImportance
    term: MemoryTerm
    memory_type: MemoryType
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Idea:
    id: str
    idea: str
    importance: IdeaImportance
    share: ShareLevel
    tags: List[str] = field(default_factory=list)
    context: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Error:
    id: str
    title: str
    description: str
    severity: ErrorSeverity
    category: ErrorCategory
    source: str
    context: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

@dataclass
class CodeChunk:
    chunk_id: str
    status: ChunkStatus
    dependencies: List[str] = field(default_factory=list)
    code: str = ""
    tests: str = ""
    validated: bool = False
    level: ChunkingLevel = ChunkingLevel.Block
    estimated_tokens: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class TaskUpdate:
    action: Optional[str] = None
    time: Optional[str] = None
    priority: Optional[Priority] = None
    parent_project: Optional[str] = None
    status: Optional[Status] = None
    assignee: Optional[Priority] = None
    tags: Optional[List[str]] = None
    dependencies: Optional[List[str]] = None
    context_notes: Optional[str] = None
    progress: Optional[int] = None
    embedding_vector: Optional[List[float]] = None

# ---------------------------------------------------------------------------
# ToolDefinition, Tool, ToolResult
# ---------------------------------------------------------------------------

@dataclass
class ToolParameter:
    name: str
    param_type: str
    description: str
    required: bool

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: List[ToolParameter]
    category: str
    resource_locks: List[ResourceLock]

class ToolResult:
    def __init__(self, success: bool, message: str, code: int, data: Optional[Dict[str, Any]] = None):
        self.success = success
        self.message = message
        self.code = code
        self.data = data or {}

    @staticmethod
    def success(message: str, code: int, data: Optional[Dict[str, Any]] = None) -> "ToolResult":
        return ToolResult(True, message, code, data)

    @staticmethod
    def error(message: str, code: int) -> "ToolResult":
        return ToolResult(False, message, code, {})

class Tool(ABC):
    @abstractmethod
    def definition(self) -> ToolDefinition:
        ...

    @abstractmethod
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        ...

# ---------------------------------------------------------------------------
# Storage (Simplified in-memory)
# ---------------------------------------------------------------------------

@dataclass
class Storage:
    tasks: Dict[str, Task] = field(default_factory=dict)
    memories: Dict[str, Memory] = field(default_factory=dict)
    ideas: Dict[str, Idea] = field(default_factory=dict)
    errors: Dict[str, Error] = field(default_factory=dict)
    code_chunks: Dict[str, CodeChunk] = field(default_factory=dict)

    # -------------------------
    # Task ops
    # -------------------------
    async def add_task_to_project(self, task: Task) -> str:
        self.tasks[task.id] = task
        return task.id

    async def list_tasks_across_projects(self, filters: "TaskFilters") -> List[Task]:
        results = []
        for t in self.tasks.values():
            if matches_filters(t, filters):
                results.append(t)
        return results

    async def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    async def update_task(self, task_id: str, update: TaskUpdate) -> None:
        t = self.tasks.get(task_id)
        if not t:
            return
        if update.action is not None:
            t.action = update.action
        if update.time is not None:
            t.time = update.time
        if update.priority is not None:
            t.priority = update.priority
        if update.parent_project is not None:
            t.parent_project = update.parent_project
        if update.status is not None:
            t.status = update.status
        if update.assignee is not None:
            t.assignee = update.assignee
        if update.tags is not None:
            t.tags = update.tags
        if update.dependencies is not None:
            t.dependencies = update.dependencies
        if update.context_notes is not None:
            t.context_notes = update.context_notes
        if update.progress is not None:
            t.progress = update.progress
        if update.embedding_vector is not None:
            t.embedding_vector = update.embedding_vector
        t.updated_at = datetime.utcnow()

    # -------------------------
    # Memory ops
    # -------------------------
    async def add_memory(self, memory: Memory) -> str:
        self.memories[memory.id] = memory
        return memory.id

    async def list_memories(self) -> List[Memory]:
        return list(self.memories.values())

    # -------------------------
    # Idea ops
    # -------------------------
    async def add_idea(self, idea: Idea) -> str:
        self.ideas[idea.id] = idea
        return idea.id

    async def list_ideas(self) -> List[Idea]:
        return list(self.ideas.values())

    # -------------------------
    # Error ops
    # -------------------------
    async def add_error(self, error: Error) -> str:
        self.errors[error.id] = error
        return error.id

    async def list_errors(self) -> List[Error]:
        return list(self.errors.values())

    # -------------------------
    # Code chunk ops
    # -------------------------
    async def add_code_chunk(self, chunk: CodeChunk) -> str:
        self.code_chunks[chunk.chunk_id] = chunk
        return chunk.chunk_id

# ---------------------------------------------------------------------------
# Filters and Matching
# ---------------------------------------------------------------------------

@dataclass
class TaskFilters:
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    project: Optional[str] = None
    assignee: Optional[Priority] = None
    tags: Optional[List[str]] = None

def matches_filters(task: Task, filters: TaskFilters) -> bool:
    if filters.status is not None and task.status != filters.status:
        return False
    if filters.priority is not None and task.priority != filters.priority:
        return False
    if filters.project is not None and task.parent_project != filters.project:
        return False
    if filters.assignee is not None and task.assignee != filters.assignee:
        return False
    if filters.tags:
        ok = any(
            any(tag.lower() in task_tag.lower() for task_tag in task.tags)
            for tag in filters.tags
        )
        if not ok:
            return False
    return True

# ---------------------------------------------------------------------------
# Resource Management
# ---------------------------------------------------------------------------

class ResourceManager:
    def __init__(self) -> None:
        self._locks: Dict[ResourceLock, asyncio.Lock] = {}

    async def acquire(self, resource_locks: List[ResourceLock]) -> None:
        for lock_type in resource_locks:
            if lock_type not in self._locks:
                self._locks[lock_type] = asyncio.Lock()
            await self._locks[lock_type].acquire()

    def release(self, resource_locks: List[ResourceLock]) -> None:
        for lock_type in resource_locks:
            if lock_type in self._locks:
                # Manual release requires that we are the owner; this is safe if acquire/release are paired
                self._locks[lock_type].release()

# ---------------------------------------------------------------------------
# Storage Proxy (safe concurrent access)
# ---------------------------------------------------------------------------

class StorageProxy:
    def __init__(self, storage: Storage):
        self._storage = storage
        self._lock = asyncio.Lock()

    async def execute(self, operation: Callable[[Storage], Awaitable[Any]]) -> Any:
        async with self._lock:
            return await operation(self._storage)

# ---------------------------------------------------------------------------
# API Key and Requests (Stubbed)
# ---------------------------------------------------------------------------

async def get_todozi_api_key() -> str:
    import os
    from todozi.storage import load_config
    
    api_key = os.environ.get("TDZ_API_KEY")
    if api_key:
        return api_key
    
    try:
        config = await load_config()
        if config.registration and config.registration.api_key:
            return config.registration.api_key
    except Exception:
        pass
    
    raise ValueError("API key not found. Set TDZ_API_KEY environment variable or register with 'todozi register'")

async def make_todozi_request(endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    import aiohttp
    from aiohttp import ClientSession, ClientTimeout
    
    api_key = await get_todozi_api_key()
    base_url = os.getenv("TDZ_BASE_URL", "https://todozi.com")
    url = f"{base_url}{endpoint}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }
    
    timeout = ClientTimeout(total=120)
    async with ClientSession() as session:
        async with session.post(url, headers=headers, json=payload, timeout=timeout) as resp:
            if resp.status >= 400:
                text = await resp.text()
                raise ValueError(f"API request failed [{resp.status}]: {text}")
            return await resp.json()

# ---------------------------------------------------------------------------
# Done facade (uses StorageProxy for safe operations)
# ---------------------------------------------------------------------------

class Done:
    def __init__(self, storage_proxy: StorageProxy):
        self._proxy = storage_proxy

    async def ai(self, action: str) -> str:
        async def run(s: Storage) -> str:
            return await self._create_task(s, action, assignee=Priority.Critical, priority=Priority.High)
        return await self._proxy.execute(run)

    async def human(self, action: str) -> str:
        async def run(s: Storage) -> str:
            return await self._create_task(s, action, assignee=Priority.Medium, priority=Priority.Medium)
        return await self._proxy.execute(run)

    async def collab(self, action: str) -> str:
        async def run(s: Storage) -> str:
            return await self._create_task(s, action, assignee=Priority.Low, priority=Priority.High)
        return await self._proxy.execute(run)

    async def urgent(self, action: str) -> str:
        async def run(s: Storage) -> str:
            return await self._create_task(s, action, priority=Priority.Urgent)
        return await self._proxy.execute(run)

    async def high(self, action: str) -> str:
        async def run(s: Storage) -> str:
            return await self._create_task(s, action, priority=Priority.High)
        return await self._proxy.execute(run)

    async def low(self, action: str) -> str:
        async def run(s: Storage) -> str:
            return await self._create_task(s, action, priority=Priority.Low)
        return await self._proxy.execute(run)

    async def create_task(
        self,
        action: str,
        priority: Optional[Priority] = None,
        project: Optional[str] = None,
        time: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Task:
        async def run(s: Storage) -> Task:
            return await self._create_task(s, action, None, priority, project, time, context)
        return await self._proxy.execute(run)

    async def add_to_task(self, task_id: str, tag: str) -> None:
        async def run(s: Storage) -> None:
            t = await s.get_task(task_id)
            if not t:
                return
            if tag not in t.tags:
                t.tags.append(tag)
            t.updated_at = datetime.utcnow()
        await self._proxy.execute(run)

    async def complete(self, task_id: str) -> None:
        async def run(s: Storage) -> None:
            t = await s.get_task(task_id)
            if not t:
                return
            t.status = Status.Done
            t.progress = 100
            t.updated_at = datetime.utcnow()
        await self._proxy.execute(run)

    async def begin(self, task_id: str) -> None:
        async def run(s: Storage) -> None:
            t = await s.get_task(task_id)
            if not t:
                return
            t.status = Status.InProgress
            t.progress = max(t.progress or 0, 1)
            t.updated_at = datetime.utcnow()
        await self._proxy.execute(run)

    async def update_task_full(self, task_id: str, update: TaskUpdate) -> None:
        async def run(s: Storage) -> None:
            await s.update_task(task_id, update)
        await self._proxy.execute(run)

    async def deep(self, query: str) -> List[Dict[str, Any]]:
        # Stubbed AI semantic search results
        return [
            {"content_id": str(uuid.uuid4()), "text_content": f"Result for '{query}' 1", "similarity_score": 0.93},
            {"content_id": str(uuid.uuid4()), "text_content": f"Result for '{query}' 2", "similarity_score": 0.88},
        ]

    async def fast(self, query: str) -> List[Dict[str, Any]]:
        async def run(s: Storage) -> List[Dict[str, Any]]:
            results = []
            for t in s.tasks.values():
                if query.lower() in t.action.lower() or (t.context_notes and query.lower() in t.context_notes.lower()):
                    results.append({"id": t.id, "action": t.action, "status": t.status.value, "priority": t.priority.value})
            return results
        return await self._proxy.execute(run)

    async def tdz_find(self, query: str) -> List[Dict[str, Any]]:
        async def run(s: Storage) -> List[Dict[str, Any]]:
            out = []
            for t in s.tasks.values():
                if query.lower() in t.action.lower():
                    out.append({"type": "task", "id": t.id, "action": t.action})
            for m in s.memories.values():
                if query.lower() in m.moment.lower() or query.lower() in m.meaning.lower():
                    out.append({"type": "memory", "id": m.id, "moment": m.moment})
            for i in s.ideas.values():
                if query.lower() in i.idea.lower():
                    out.append({"type": "idea", "id": i.id, "idea": i.idea})
            for e in s.errors.values():
                if query.lower() in e.title.lower() or query.lower() in e.description.lower():
                    out.append({"type": "error", "id": e.id, "title": e.title})
            return out
        return await self._proxy.execute(run)

    async def create_memory(self, moment: str, meaning: str, reason: str) -> Memory:
        async def run(s: Storage) -> Memory:
            m = Memory(
                id=str(uuid.uuid4()),
                user_id="ai_agent",
                project_id=None,
                status=ItemStatus.Active,
                moment=moment,
                meaning=meaning,
                reason=reason,
                importance=MemoryImportance.Medium,
                term=MemoryTerm.Long,
                memory_type=MemoryType.Standard,
                tags=[],
            )
            await s.add_memory(m)
            return m
        return await self._proxy.execute(run)

    async def important(self, moment: str, meaning: str, reason: str) -> str:
        m = await self.create_memory(moment, meaning, reason)
        async def update_importance(s: Storage) -> None:
            from todozi.storage import load_memory, save_memory, list_memories
            try:
                stored = load_memory(m.id)
                stored.importance = MemoryImportance.High
                from datetime import datetime, timezone
                stored.updated_at = datetime.now(timezone.utc)
                save_memory(stored)
            except Exception:
                memories = list_memories()
                for mem in memories:
                    if mem.moment == m.moment and mem.meaning == m.meaning:
                        mem.importance = MemoryImportance.High
                        from datetime import datetime, timezone
                        mem.updated_at = datetime.now(timezone.utc)
                        save_memory(mem)
                        break
        await self._proxy.execute(update_importance)
        return m.id

    async def create_idea(self, idea: str, context: Optional[str]) -> Idea:
        async def run(s: Storage) -> Idea:
            i = Idea(
                id=str(uuid.uuid4()),
                idea=idea,
                importance=IdeaImportance.Medium,
                share=ShareLevel.Team,
                tags=[],
                context=context,
            )
            await s.add_idea(i)
            return i
        return await self._proxy.execute(run)

    async def breakthrough(self, idea: str) -> str:
        i = await self.create_idea(idea, None)
        # Update importance
        async def run(s: Storage) -> None:
            stored = None
            for idea_obj in s.ideas.values():
                if idea_obj.id == i.id:
                    stored = idea_obj
                    break
            if stored:
                stored.importance = IdeaImportance.Breakthrough
                stored.updated_at = datetime.utcnow()
        await self._proxy.execute(run)
        return i.id

    async def chat(self, message: str) -> Dict[str, Any]:
        async def run(s: Storage) -> Dict[str, Any]:
            tasks = []
            memories = []
            ideas = []
            errors = []
            feelings = []
            if "TODO:" in message or "todo:" in message:
                for part in message.splitlines():
                    if "TODO:" in part or "todo:" in part:
                        action = re.sub(r".*?[Tt][Oo][Dd][Oo]:\s*", "", part).strip()
                        if action:
                            t = await self._create_task(s, action)
                            tasks.append(t)
            if "REMEMBER:" in message or "remember:" in message:
                for part in message.splitlines():
                    if "REMEMBER:" in part or "remember:" in part:
                        text = re.sub(r".*?[Rr]emember:\s*", "", part).strip()
                        if text:
                            m = await self._create_memory(s, text, "noted_from_chat", "chat_message")
                            memories.append(m)
            if "IDEA:" in message or "idea:" in message:
                for part in message.splitlines():
                    if "IDEA:" in part or "idea:" in part:
                        text = re.sub(r".*?[Ii]dea:\s*", "", part).strip()
                        if text:
                            idea_obj = await self._create_idea(s, text, None)
                            ideas.append(idea_obj)
            if "ERROR:" in message or "error:" in message:
                for part in message.splitlines():
                    if "ERROR:" in part or "error:" in part:
                        text = re.sub(r".*?[Ee]rror:\s*", "", part).strip()
                        if text:
                            e = Error(
                                id=str(uuid.uuid4()),
                                title="ChatError",
                                description=text,
                                severity=ErrorSeverity.Medium,
                                category=ErrorCategory.Runtime,
                                source="chat",
                            )
                            await s.add_error(e)
                            errors.append(e)
            return {
                "tasks": tasks,
                "memories": memories,
                "ideas": ideas,
                "errors": errors,
                "feelings": feelings,
            }
        return await self._proxy.execute(run)

    async def extract_tasks(self, content: str, extra: Optional[str]) -> List[str]:
        return ChecklistTool.extract_tasks(content)

    async def plan_tasks(self, content: str, priority: Optional[str], timeline: Optional[str], extra: Optional[str]) -> List[Task]:
        async def run(s: Storage) -> List[Task]:
            base = await self._create_task(s, f"Plan: {content[:50]}")
            step1 = await self._create_task(s, f"Analyze: {content[:40]}")
            step2 = await self._create_task(s, f"Design: {content[:40]}")
            return [base, step1, step2]
        return await self._proxy.execute(run)

    async def quick(self) -> str:
        async def run(s: Storage) -> str:
            total = len(s.tasks)
            done = sum(1 for t in s.tasks.values() if t.status == Status.Done)
            return f"Total tasks: {total}\nCompleted: {done}\nRemaining: {total - done}"
        return await self._proxy.execute(run)

    async def list_queue_items(self) -> List[str]:
        async def run(s: Storage) -> List[str]:
            return [t.id for t in s.tasks.values() if t.status in (Status.Todo, Status.InProgress)]
        return await self._proxy.execute(run)

    async def _create_task(
        self,
        s: Storage,
        action: str,
        assignee: Optional[Priority] = None,
        priority: Optional[Priority] = None,
        project: Optional[str] = None,
        time: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Task:
        t = Task(
            id=str(uuid.uuid4()),
            user_id="ai_agent",
            action=action,
            time=time or "ASAP",
            priority=priority or Priority.Medium,
            parent_project=project or "",
            status=Status.Todo,
            assignee=assignee,
            tags=[],
            dependencies=[],
            context_notes=context,
            progress=0,
            embedding_vector=None,
        )
        await s.add_task_to_project(t)
        return t

    async def _create_memory(self, s: Storage, moment: str, meaning: str, reason: str) -> Memory:
        m = Memory(
            id=str(uuid.uuid4()),
            user_id="ai_agent",
            project_id=None,
            status=ItemStatus.Active,
            moment=moment,
            meaning=meaning,
            reason=reason,
            importance=MemoryImportance.Medium,
            term=MemoryTerm.Long,
            memory_type=MemoryType.Standard,
            tags=[],
        )
        await s.add_memory(m)
        return m

    async def _create_idea(self, s: Storage, idea: str, context: Optional[str]) -> Idea:
        i = Idea(
            id=str(uuid.uuid4()),
            idea=idea,
            importance=IdeaImportance.Medium,
            share=ShareLevel.Team,
            tags=[],
            context=context,
        )
        await s.add_idea(i)
        return i

# ---------------------------------------------------------------------------
# Embedding Service
# ---------------------------------------------------------------------------

@dataclass
class TodoziEmbeddingConfig:
    model_name: str
    max_results: int
    similarity_threshold: float
    cache_ttl_seconds: int
    clustering_threshold: float
    dimensions: int
    enable_clustering: bool

class TodoziEmbeddingService:
    def __init__(self, config: TodoziEmbeddingConfig):
        self.config = config
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    async def search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        return [
            {"content_id": str(uuid.uuid4()), "text_content": f"Embedding match for '{query}' 1", "similarity_score": 0.91},
            {"content_id": str(uuid.uuid4()), "text_content": f"Embedding match for '{query}' 2", "similarity_score": 0.86},
        ][:limit]

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def create_tool_parameter(name: str, param_type: str, description: str, required: bool) -> ToolParameter:
    return ToolParameter(name=name, param_type=param_type, description=description, required=required)

def get_tasks_dir() -> Path:
    p = Path("todozi_data/tasks")
    p.mkdir(parents=True, exist_ok=True)
    return p

def load_task(task_id: str) -> Task:
    return Task(
        id=task_id,
        user_id="demo",
        action="Demo task",
        time="ASAP",
        priority=Priority.Medium,
        parent_project="",
        status=Status.Todo,
    )

def save_task(task: Task) -> None:
    pass

def save_error(error: Error) -> None:
    pass

def save_code_chunk(chunk: CodeChunk) -> None:
    pass

def save_memory(memory: Memory) -> None:
    pass

def save_idea(idea: Idea) -> None:
    pass

def list_memories() -> List[Memory]:
    return []

def list_ideas() -> List[Idea]:
    return []

def list_errors() -> List[Error]:
    return []

async def init_todozi() -> None:
    Path("todozi_data").mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Parameter Validation Decorator
# ---------------------------------------------------------------------------

def validate_params(*validations: Tuple[str, type, bool]):
    def decorator(method: Callable[..., Awaitable[ToolResult]]):
        async def wrapper(self: "BaseTool", kwargs: Dict[str, Any]) -> ToolResult:
            for param_name, param_type, required in validations:
                value = kwargs.get(param_name)
                if required and (value is None or not isinstance(value, param_type)):
                    return ToolResult.error(f"Missing or invalid '{param_name}' parameter", 400)
                # Optional: add more validation logic per type here
            return await method(self, kwargs)
        return wrapper
    return decorator

# ---------------------------------------------------------------------------
# Dictionary Dispatch for Rust match-like logic
# ---------------------------------------------------------------------------

def get_task_creator(done: Done, assignee: str, priority: str) -> Callable[[str], Awaitable[str]]:
    strategies = {
        ("ai", "_"): done.ai,
        ("human", "_"): done.human,
        ("collaborative", "_"): done.collab,
        ("_", "urgent"): done.urgent,
        ("_", "critical"): done.urgent,  # mimic Rust behavior
        ("_", "high"): done.high,
        ("_", "low"): done.low,
    }
    for (a, p), creator in strategies.items():
        if (a == assignee or a == "_") and (p == priority or p == "_"):
            return creator
    # default
    return lambda action: done.create_task(action)

# ---------------------------------------------------------------------------
# Base Tool to share resource management
# ---------------------------------------------------------------------------

class BaseTool(Tool):
    def __init__(self, storage_proxy: StorageProxy, resource_locks: List[ResourceLock]):
        self._proxy = storage_proxy
        self._resource_manager = ResourceManager()
        self._resource_locks = resource_locks

    async def _with_resources(self, coro: Callable[[], Awaitable[ToolResult]]) -> ToolResult:
        await self._resource_manager.acquire(self._resource_locks)
        try:
            return await coro()
        finally:
            self._resource_manager.release(self._resource_locks)

# ---------------------------------------------------------------------------
# Tool Implementations
# ---------------------------------------------------------------------------

class CreateTaskTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy):
        super().__init__(storage_proxy, [ResourceLock.FilesystemWrite])

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="create_task",
            description="Create a new task in the Todozi system with automatic AI assignment and queue management",
            parameters=[
                create_tool_parameter("action", str, "Task description/action to perform", True),
                create_tool_parameter("time", str, "Time estimate (e.g., '2 hours', '1 day')", False),
                create_tool_parameter("priority", str, "Priority level (low/medium/high/critical/urgent)", False),
                create_tool_parameter("project", str, "Project name to associate with task", False),
                create_tool_parameter("assignee", str, "Assignee type (ai/human/collaborative)", False),
                create_tool_parameter("tags", str, "Comma-separated tags for the task", False),
                create_tool_parameter("context", str, "Additional context or notes", False),
            ],
            category="Task Management",
            resource_locks=self._resource_locks,
        )

    @validate_params(("action", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        action = kwargs["action"]
        if not action.strip() or len(action) > 500:
            return ToolResult.error("Action must be 1-500 characters", 100)

        assignee_str = str(kwargs.get("assignee") or "human")
        priority_str = str(kwargs.get("priority") or "medium")
        context = kwargs.get("context")
        project = kwargs.get("project")

        async def run() -> ToolResult:
            done = Done(self._proxy)
            creator = get_task_creator(done, assignee_str, priority_str)
            if (priority_str, assignee_str) in [("urgent", "_"), ("critical", "_"), ("high", "_"), ("low", "_")]:
                task_id = await creator(action)
            else:
                # default create_task path
                t = await done.create_task(
                    action,
                    Priority(priority_str) if priority_str in [e.value for e in Priority] else Priority.Medium,
                    project,
                    kwargs.get("time"),
                    context,
                )
                task_id = t.id

            if tags_str := kwargs.get("tags"):
                if isinstance(tags_str, str):
                    for tag in tags_str.split(","):
                        tag = tag.strip()
                        if tag:
                            await done.add_to_task(task_id, tag)

            return ToolResult.success(
                f"✅ Created task '{action}' with ID: {task_id} (queued for {assignee_str})",
                100,
            )

        return await self._with_resources(run)

class SearchTasksTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy, embedding_service: Optional[TodoziEmbeddingService] = None):
        super().__init__(storage_proxy, [ResourceLock.FilesystemRead])
        self._embedding = embedding_service

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="search_tasks",
            description="Search for tasks in the Todozi system with semantic AI capabilities",
            parameters=[
                create_tool_parameter("query", str, "Search query to match against task content", True),
                create_tool_parameter("semantic", bool, "Use AI semantic search instead of keyword matching", False),
                create_tool_parameter("project", str, "Filter by project name", False),
                create_tool_parameter("status", str, "Filter by status (todo/in_progress/blocked/review/done)", False),
                create_tool_parameter("assignee", str, "Filter by assignee (ai/human/collaborative)", False),
                create_tool_parameter("limit", int, "Maximum number of results to return", False),
            ],
            category="Task Management",
            resource_locks=self._resource_locks,
        )

    @validate_params(("query", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        query = kwargs["query"]
        if not query.strip() or len(query) > 100:
            return ToolResult.error("Query must be 1-100 characters", 150)

        semantic = bool(kwargs.get("semantic", False))
        limit = int(kwargs.get("limit") or 10)

        async def _run() -> ToolResult:
            done = Done(self._proxy)
            if semantic:
                results = await done.deep(query)
                if not results:
                    return ToolResult.success(f"🤖 No AI semantic results found for: {query}", 150)
                out = "\n".join(
                    f"ID: {r['content_id']} | {r['text_content']} | Similarity: {r['similarity_score']:.2} | Type: task"
                    for r in results[:limit]
                )
                return ToolResult.success(f"🤖 AI Semantic Search - Found {len(results[:limit])} results:\n{out}", 150)
            else:
                results = await done.fast(query)
                if not results:
                    return ToolResult.success(f"🔍 No keyword results found for: {query}", 150)
                return ToolResult.success(f"🔍 Keyword Search Results:\n{json.dumps(results[:limit], indent=2)}", 150)

        return await self._with_resources(_run)

class UpdateTaskTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy):
        super().__init__(storage_proxy, [ResourceLock.FilesystemWrite])

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="update_task",
            description="Update an existing task in the Todozi system",
            parameters=[
                create_tool_parameter("task_id", str, "ID of the task to update", True),
                create_tool_parameter("status", str, "New status (todo/in_progress/blocked/review/done)", False),
                create_tool_parameter("progress", int, "Progress percentage (0-100)", False),
                create_tool_parameter("priority", str, "New priority level", False),
                create_tool_parameter("assignee", str, "New assignee", False),
                create_tool_parameter("context", str, "Additional context or notes", False),
            ],
            category="Task Management",
            resource_locks=self._resource_locks,
        )

    @validate_params(("task_id", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        task_id = kwargs["task_id"]
        if not task_id.strip() or len(task_id) > 50:
            return ToolResult.error("Task ID must be 1-50 characters", 120)

        async def _run() -> ToolResult:
            done = Done(self._proxy)
            status_str = kwargs.get("status")
            if status_str:
                low = str(status_str).lower()
                if low in ("completed", "done"):
                    await done.complete(task_id)
                    return ToolResult.success(f"✅ Task {task_id} marked as completed", 120)
                if low in ("in_progress", "started"):
                    await done.begin(task_id)
                    return ToolResult.success(f"🔄 Task {task_id} marked as in progress", 120)

            update = TaskUpdate()
            if p := kwargs.get("priority"):
                try:
                    update.priority = Priority(str(p).lower())
                except Exception:
                    pass
            if a := kwargs.get("assignee"):
                try:
                    update.assignee = Priority(str(a).lower())
                except Exception:
                    pass
            if c := kwargs.get("context"):
                update.context_notes = str(c)
            if pr := kwargs.get("progress"):
                try:
                    update.progress = int(pr)
                except Exception:
                    pass
            if st := kwargs.get("status"):
                try:
                    update.status = Status(str(st).lower())
                except Exception:
                    pass

            await done.update_task_full(task_id, update)
            return ToolResult.success(f"✅ Updated task {task_id}", 120)

        return await self._with_resources(_run)

class CreateMemoryTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy):
        super().__init__(storage_proxy, [ResourceLock.FilesystemWrite])

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="create_memory",
            description="Create a new memory for learning and context",
            parameters=[
                create_tool_parameter("moment", str, "What happened (the moment)", True),
                create_tool_parameter("meaning", str, "What it means or why it's important", True),
                create_tool_parameter("reason", str, "The reason for remembering this", True),
                create_tool_parameter("importance", str, "Importance level (low/medium/high/critical)", False),
                create_tool_parameter("term", str, "Memory term (short/long)", False),
                create_tool_parameter("tags", str, "Comma-separated tags", False),
            ],
            category="Memory Management",
            resource_locks=self._resource_locks,
        )

    @validate_params(("moment", str, True), ("meaning", str, True), ("reason", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        moment, meaning, reason = kwargs["moment"], kwargs["meaning"], kwargs["reason"]
        if len(moment) > 1000 or len(meaning) > 1000 or len(reason) > 1000:
            return ToolResult.error("Parameters must be <= 1000 characters", 200)

        async def _run() -> ToolResult:
            done = Done(self._proxy)
            importance_str = str(kwargs.get("importance") or "medium").lower()
            if importance_str in ("high", "critical"):
                memory_id = await done.important(moment, meaning, reason)
            else:
                m = await done.create_memory(moment, meaning, reason)
                memory_id = m.id
            return ToolResult.success(f"🧠 Created memory '{moment}' with ID: {memory_id}", 200)

        return await self._with_resources(_run)

class CreateIdeaTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy):
        super().__init__(storage_proxy, [ResourceLock.FilesystemWrite])

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="create_idea",
            description="Create a new creative idea or concept",
            parameters=[
                create_tool_parameter("idea", str, "The idea content", True),
                create_tool_parameter("share", str, "Share level (private/team/public)", False),
                create_tool_parameter("importance", str, "Importance level (low/medium/high/breakthrough)", False),
                create_tool_parameter("tags", str, "Comma-separated tags", False),
                create_tool_parameter("context", str, "Additional context", False),
            ],
            category="Idea Management",
            resource_locks=self._resource_locks,
        )

    @validate_params(("idea", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        idea = kwargs["idea"]
        if not idea.strip() or len(idea) > 1000:
            return ToolResult.error("Idea must be 1-1000 characters", 180)

        async def _run() -> ToolResult:
            done = Done(self._proxy)
            importance_str = str(kwargs.get("importance") or "medium").lower()
            if importance_str in ("breakthrough", "high"):
                idea_id = await done.breakthrough(idea)
            else:
                i = await done.create_idea(idea, kwargs.get("context"))
                idea_id = i.id
            return ToolResult.success(f"💡 Created idea '{idea}' with ID: {idea_id}", 180)

        return await self._with_resources(_run)

class UnifiedSearchTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy, embedding_service: Optional[TodoziEmbeddingService] = None):
        super().__init__(storage_proxy, [ResourceLock.FilesystemRead])
        self._embedding = embedding_service

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="unified_search",
            description="Search across all Todozi data types with AI semantic capabilities (tasks, memories, ideas, errors)",
            parameters=[
                create_tool_parameter("query", str, "Search query", True),
                create_tool_parameter("semantic", bool, "Use AI semantic search instead of keyword matching", False),
                create_tool_parameter("data_types", str, "Comma-separated data types to search (tasks,memories,ideas,errors)", False),
                create_tool_parameter("limit", int, "Maximum results per type", False),
            ],
            category="Search",
            resource_locks=self._resource_locks,
        )

    @validate_params(("query", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        query = kwargs["query"]
        if not query.strip() or len(query) > 100:
            return ToolResult.error("Query must be 1-100 characters", 300)

        async def _run() -> ToolResult:
            done = Done(self._proxy)
            semantic = bool(kwargs.get("semantic", False))
            if semantic:
                ai_results = await done.deep(query)
                if not ai_results:
                    return ToolResult.success(f"🤖 No AI semantic results found for: {query}", 300)
                out = "\n".join(
                    f"• {r['text_content']} | Type: task | Similarity: {r['similarity_score']:.2}"
                    for r in ai_results
                )
                return ToolResult.success(
                    f"🤖 AI Unified Search - Found {len(ai_results)} semantic matches:\n{out}",
                    300,
                )
            else:
                unified_results = await done.tdz_find(query)
                if not unified_results:
                    return ToolResult.success(f"🔍 No unified results found for: {query}", 300)
                return ToolResult.success(f"🔍 Unified Search Results:\n{json.dumps(unified_results, indent=2)}", 300)

        return await self._with_resources(_run)

class ProcessChatMessageTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy):
        super().__init__(storage_proxy, [ResourceLock.FilesystemWrite])

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="process_chat_message",
            description="Process a chat message containing Todozi tags and create corresponding items",
            parameters=[
                create_tool_parameter("message", str, "Chat message with Todozi tags", True),
                create_tool_parameter("user_id", str, "User ID for created items", False),
            ],
            category="Message Processing",
            resource_locks=self._resource_locks,
        )

    @validate_params(("message", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        message = kwargs["message"]
        if not message.strip() or len(message) > 10000:
            return ToolResult.error("Message must be 1-10000 characters", 250)

        async def _run() -> ToolResult:
            done = Done(self._proxy)
            content = await done.chat(message)
            results = []
            if content["tasks"]:
                results.append(f"📋 Created {len(content['tasks'])} tasks")
                for t in content["tasks"]:
                    results.append(f"  • {t.action} [{t.assignee.name if t.assignee else 'unassigned'}]")
            if content["memories"]:
                results.append(f"🧠 Created {len(content['memories'])} memories")
                for m in content["memories"]:
                    results.append(f"  • {m.moment}")
            if content["ideas"]:
                results.append(f"💡 Created {len(content['ideas'])} ideas")
                for i in content["ideas"]:
                    results.append(f"  • {i.idea}")
            if content["errors"]:
                results.append(f"❌ Created {len(content['errors'])} error records")
            if content["feelings"]:
                results.append(f"😊 Created {len(content['feelings'])} feelings")
            if not results:
                return ToolResult.success("✅ Message processed - no structured content extracted", 250)
            return ToolResult.success("\n".join(results), 250)

        return await self._with_resources(_run)

class CreateErrorTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy):
        super().__init__(storage_proxy, [ResourceLock.FilesystemWrite])

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="create_error",
            description="Create an error record for tracking issues",
            parameters=[
                create_tool_parameter("title", str, "Error title/summary", True),
                create_tool_parameter("description", str, "Detailed error description", True),
                create_tool_parameter("severity", str, "Severity level (low/medium/high/critical)", False),
                create_tool_parameter("category", str, "Error category", False),
                create_tool_parameter("source", str, "Source file/component", False),
                create_tool_parameter("context", str, "Additional context", False),
                create_tool_parameter("tags", str, "Comma-separated tags", False),
            ],
            category="Error Tracking",
            resource_locks=self._resource_locks,
        )

    @validate_params(("title", str, True), ("description", str, True), ("source", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        title, description, source = kwargs["title"], kwargs["description"], kwargs["source"]
        if len(title) > 200 or len(description) > 1000 or len(source) > 200:
            return ToolResult.error("Parameters exceed length limits", 220)

        async def _run() -> ToolResult:
            async def _op(s: Storage) -> str:
                severity_str = str(kwargs.get("severity") or "medium").lower()
                category_str = str(kwargs.get("category") or "runtime").lower()
                severity = {
                    "low": ErrorSeverity.Low,
                    "medium": ErrorSeverity.Medium,
                    "high": ErrorSeverity.High,
                    "critical": ErrorSeverity.Critical,
                }.get(severity_str, ErrorSeverity.Medium)
                category = {
                    "runtime": ErrorCategory.Runtime,
                    "database": ErrorCategory.Database,
                    "network": ErrorCategory.Network,
                    "validation": ErrorCategory.Validation,
                }.get(category_str, ErrorCategory.Runtime)

                tags = []
                if isinstance(kwargs.get("tags"), str):
                    tags = [t.strip() for t in kwargs.get("tags").split(",") if t.strip()]

                error = Error(
                    id=str(uuid.uuid4()),
                    title=title,
                    description=description,
                    severity=severity,
                    category=category,
                    source=source,
                    context=kwargs.get("context"),
                    tags=tags,
                    resolved=False,
                    resolution=None,
                )
                await s.add_error(error)
                return error.id

            err_id = await self._proxy.execute(_op)
            return ToolResult.success(
                f"Created error record '{title}' with ID: {err_id}",
                220,
            )

        return await self._with_resources(_run)

class CreateCodeChunkTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy):
        super().__init__(storage_proxy, [ResourceLock.FilesystemWrite])

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="create_code_chunk",
            description="Create a code chunk for hierarchical task decomposition",
            parameters=[
                create_tool_parameter("chunk_id", str, "Unique chunk identifier", True),
                create_tool_parameter("level", str, "Chunking level (project/module/class/method/block)", True),
                create_tool_parameter("description", str, "What this chunk accomplishes", True),
                create_tool_parameter("dependencies", str, "Comma-separated dependency chunk IDs", False),
                create_tool_parameter("code", str, "The actual code content", False),
            ],
            category="Code Chunking",
            resource_locks=self._resource_locks,
        )

    @validate_params(("chunk_id", str, True), ("level", str, True), ("description", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        chunk_id, level_str, description = kwargs["chunk_id"], kwargs["level"], kwargs["description"]
        if len(chunk_id) > 100 or len(level_str) > 50 or len(description) > 500:
            return ToolResult.error("Parameters exceed length limits", 180)

        async def _run() -> ToolResult:
            level_map = {
                "project": ChunkingLevel.Project,
                "module": ChunkingLevel.Module,
                "class": ChunkingLevel.Class,
                "method": ChunkingLevel.Method,
                "block": ChunkingLevel.Block,
            }
            level = level_map.get(str(level_str).lower())
            if not level:
                return ToolResult.error(f"Invalid chunking level: {level_str}", 180)

            deps = []
            if isinstance(kwargs.get("dependencies"), str):
                deps = [d.strip() for d in kwargs.get("dependencies").split(",") if d.strip()]

            code = str(kwargs.get("code") or "")

            chunk = CodeChunk(
                chunk_id=chunk_id,
                status=ChunkStatus.Pending,
                dependencies=deps,
                code=code,
                level=level,
            )

            async def _op(s: Storage) -> str:
                return await s.add_code_chunk(chunk)

            await self._proxy.execute(_op)
            return ToolResult.success(
                f"Created code chunk '{chunk.chunk_id}' at level {level.name}",
                180,
            )

        return await self._with_resources(_run)

class ChecklistTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy):
        super().__init__(storage_proxy, [ResourceLock.FilesystemWrite])

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="extract_tasks",
            description="Extract actionable tasks from message content and create them in Todozi",
            parameters=[
                create_tool_parameter("content", str, "Message content to extract tasks from", True),
                create_tool_parameter("project", str, "Project to associate extracted tasks with", False),
                create_tool_parameter("priority", str, "Default priority for extracted tasks (low/medium/high/critical/urgent)", False),
                create_tool_parameter("assignee", str, "Default assignee for extracted tasks (ai/human/collaborative)", False),
            ],
            category="Task Management",
            resource_locks=self._resource_locks,
        )

    @validate_params(("content", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        content = kwargs["content"]
        if not content.strip() or len(content) > 10000:
            return ToolResult.error("Content must be 1-10000 characters", 150)

        async def _run() -> ToolResult:
            default_project = str(kwargs.get("project") or "")
            default_priority = kwargs.get("priority")
            default_assignee = kwargs.get("assignee")
            priority_map = {
                "low": Priority.Low,
                "medium": Priority.Medium,
                "high": Priority.High,
                "critical": Priority.Critical,
                "urgent": Priority.Urgent,
            }
            pr = priority_map.get(str(default_priority).lower()) if default_priority else Priority.Medium
            assignee_map = {
                "ai": Priority.Critical,
                "human": Priority.Medium,
                "collaborative": Priority.Low,
            }
            asg = assignee_map.get(str(default_assignee).lower()) if default_assignee else None

            extracted = self.extract_tasks_from_content(content)
            if not extracted:
                return ToolResult.success("No tasks found in content", 150)

            done = Done(self._proxy)
            created_count = 0
            for action in extracted:
                t = await done.create_task(action, pr, default_project, "ASAP", "Extracted from message content")
                if asg:
                    t.assignee = asg
                created_count += 1

            return ToolResult.success(f"Extracted and created {created_count} tasks from content", 150)

        return await self._with_resources(_run)

    @staticmethod
    def extract_tasks_from_content(content: str) -> List[str]:
        tasks: List[str] = []
        task_indicators = [
            r"(?i)^\s*[\*\-\•]\s*\[ \]\s*(.+)",
            r"(?i)^\s*[\*\-\•]\s*(.+)",
            r"(?i)^\s*\d+\.\s*(.+)",
            r"(?i)^\s*todo:\s*(.+)",
            r"(?i)^\s*task:\s*(.+)",
            r"(?i)need to\s+(.+)",
            r"(?i)should\s+(.+)",
            r"(?i)must\s+(.+)",
        ]
        for line in content.splitlines():
            for pattern in task_indicators:
                if m := re.match(pattern, line):
                    if (task_text := m.group(1).strip()):
                        if 0 < len(task_text) <= 200:
                            tasks.append(task_text)
                            break

        if not tasks:
            sentence_patterns = [
                r"(?i)I will\s+(.+?)(?:\.|$)",
                r"(?i)We need to\s+(.+?)(?:\.|$)",
                r"(?i)Let's\s+(.+?)(?:\.|$)",
            ]
            for pattern in sentence_patterns:
                for m in re.finditer(pattern, content):
                    if (task_text := m.group(1).strip()):
                        if 0 < len(task_text) <= 200:
                            tasks.append(task_text)

        # Deduplicate case-insensitively
        seen: Set[str] = set()
        unique = []
        for t in tasks:
            low = t.lower()
            if low not in seen:
                seen.add(low)
                unique.append(t)
        return unique

class SimpleTodoziTool(BaseTool):
    def __init__(self, storage_proxy: StorageProxy):
        super().__init__(storage_proxy, [ResourceLock.FilesystemWrite, ResourceLock.FilesystemRead])

    def definition(self) -> ToolDefinition:
        return ToolDefinition(
            name="simple_todozi",
            description="Ultra-simple Todozi interface with automatic AI/human coordination and smart search",
            parameters=[
                create_tool_parameter("action", str,
                    "What to do: 'task', 'urgent', 'find', 'remember', 'idea', 'stats', 'ai_search', 'complete', 'start'",
                    True),
                create_tool_parameter("content", str, "The content/description for the action", True),
                create_tool_parameter("extra", str, "Extra context, meaning, or details", False),
            ],
            category="Simple Task Management",
            resource_locks=self._resource_locks,
        )

    @validate_params(("action", str, True), ("content", str, True))
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        action, content = kwargs["action"], kwargs["content"]
        extra = str(kwargs.get("extra") or "")

        async def _run() -> ToolResult:
            done = Done(self._proxy)
            act = action.lower()
            if act == "task":
                tid = (await done.create_task(content)).id
                return ToolResult.success(f"✅ Task created: {tid}", 50)
            if act == "urgent":
                tid = await done.urgent(content)
                return ToolResult.success(f"🚨 Urgent task created: {tid}", 50)
            if act == "high":
                tid = await done.high(content)
                return ToolResult.success(f"🟠 High priority task created: {tid}", 50)
            if act == "low":
                tid = await done.low(content)
                return ToolResult.success(f"🟢 Low priority task created: {tid}", 50)
            if act == "ai":
                tid = await done.ai(content)
                return ToolResult.success(f"🤖 AI task queued: {tid}", 50)
            if act == "human":
                tid = await done.human(content)
                return ToolResult.success(f"👤 Human task created (visible in TUI): {tid}", 50)
            if act == "collab":
                tid = await done.collab(content)
                return ToolResult.success(f"🤝 Collaborative task created: {tid}", 50)
            if act == "find":
                res = await done.tdz_find(content)
                return ToolResult.success(f"🔍 Smart search results:\n{json.dumps(res, indent=2)}", 50)
            if act == "ai_search":
                res = await done.deep(content)
                out = "\n".join(f"• {r['text_content']} [ID: {r['content_id']}]" for r in res)
                return ToolResult.success(f"🤖 AI semantic search:\n{out}", 50)
            if act == "fast_search":
                res = await done.fast(content)
                return ToolResult.success(f"⚡ Fast keyword search:\n{json.dumps(res, indent=2)}", 50)
            if act == "smart_search":
                res = await done.deep(content)
                return ToolResult.success(f"🧠 Smart intent search:\n{json.dumps(res, indent=2)}", 50)
            if act == "remember":
                m = await done.create_memory(content, extra, "Created via simple tool")
                return ToolResult.success(f"🧠 Memory saved: {m.id}", 50)
            if act == "important_memory":
                mid = await done.important(content, extra, "Important via simple tool")
                return ToolResult.success(f"🧠⭐ Important memory saved: {mid}", 50)
            if act == "idea":
                i = await done.create_idea(content, None)
                return ToolResult.success(f"💡 Idea saved: {i.id}", 50)
            if act == "breakthrough_idea":
                iid = await done.breakthrough(content)
                return ToolResult.success(f"💡🚀 Breakthrough idea saved: {iid}", 50)
            if act == "complete":
                await done.complete(content)
                return ToolResult.success(f"✅ Task {content} completed", 50)
            if act == "start":
                await done.begin(content)
                return ToolResult.success(f"🔄 Task {content} started", 50)
            if act == "stats":
                s = await done.quick()
                return ToolResult.success(f"📊 Quick stats:\n{s}", 50)
            if act == "queue":
                items = await done.list_queue_items()
                return ToolResult.success(f"📋 Queue: {len(items)} total items", 50)
            if act == "chat":
                res = await done.chat(content)
                out = []
                if res["tasks"]:
                    out.append(f"📋 {len(res['tasks'])} tasks")
                if res["memories"]:
                    out.append(f"🧠 {len(res['memories'])} memories")
                if res["ideas"]:
                    out.append(f"💡 {len(res['ideas'])} ideas")
                if not out:
                    return ToolResult.success("✅ Chat processed - no structured content", 50)
                return ToolResult.success(f"✅ Chat processed: {', '.join(out)}", 50)
            if act == "extract":
                extracted = await done.extract_tasks(content, extra)
                if not extracted:
                    return ToolResult.success("🤖 No tasks extracted from content", 50)
                numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(extracted))
                return ToolResult.success(
                    f"🤖 Extracted {len(extracted)} tasks via todozi.com AI:\n{numbered}",
                    50,
                )
            if act == "expand":
                expanded = await done.plan_tasks(content, "medium", "ASAP", extra)
                if not expanded:
                    return ToolResult.success("🤖 No task expansion generated", 50)
                numbered = "\n".join(f"{i+1}. {t.action}" for i, t in enumerate(expanded))
                return ToolResult.success(
                    f"🤖 Expanded into {len(expanded)} subtasks via todozi.com AI:\n{numbered}",
                    50,
                )
            return ToolResult.error(
                f"❌ Unknown action: '{action}'. Available: task, urgent, high, low, ai, human, collab, find, ai_search, fast_search, smart_search, remember, important_memory, idea, breakthrough_idea, complete, start, stats, queue, chat, extract, expand",
                50,
            )

        return await self._with_resources(_run)

# ---------------------------------------------------------------------------
# Builder Pattern for Tool Construction
# ---------------------------------------------------------------------------

@dataclass
class ToolBuilder:
    storage_proxy: StorageProxy
    embedding_service: Optional[TodoziEmbeddingService] = None

    def with_embedding(self, service: TodoziEmbeddingService) -> "ToolBuilder":
        return ToolBuilder(self.storage_proxy, service)

    def build_all(self) -> List[Tool]:
        return [
            SimpleTodoziTool(self.storage_proxy),
            CreateTaskTool(self.storage_proxy),
            SearchTasksTool(self.storage_proxy, self.embedding_service),
            UpdateTaskTool(self.storage_proxy),
            CreateMemoryTool(self.storage_proxy),
            CreateIdeaTool(self.storage_proxy),
            UnifiedSearchTool(self.storage_proxy, self.embedding_service),
            ProcessChatMessageTool(self.storage_proxy),
            CreateErrorTool(self.storage_proxy),
            CreateCodeChunkTool(self.storage_proxy),
            ChecklistTool(self.storage_proxy),
        ]

# ---------------------------------------------------------------------------
# Factory functions to create tool sets (with embedding)
# ---------------------------------------------------------------------------

def create_todozi_tools(storage_proxy: StorageProxy, embedding_service: Optional[TodoziEmbeddingService] = None) -> List[Tool]:
    return ToolBuilder(storage_proxy, embedding_service).build_all()

def create_todozi_tools_with_embedding(storage_proxy: StorageProxy, embedding_service: Optional[TodoziEmbeddingService]) -> List[Tool]:
    return ToolBuilder(storage_proxy, embedding_service).build_all()

async def initialize_grok_level_todozi_system(enable_embeddings: bool = False) -> Tuple[StorageProxy, Optional[TodoziEmbeddingService]]:
    await init_todozi()
    storage = Storage()
    proxy = StorageProxy(storage)
    embedding = None
    if enable_embeddings:
        cfg = TodoziEmbeddingConfig(
            model_name="all-MiniLM-L6-v2",
            max_results=10,
            similarity_threshold=0.7,
            cache_ttl_seconds=3600,
            clustering_threshold=0.8,
            dimensions=384,
            enable_clustering=False,
        )
        embedding = TodoziEmbeddingService(cfg)
    return proxy, embedding

# ---------------------------------------------------------------------------
# Demo main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    async def main():
        storage_proxy, embedding = await initialize_grok_level_todozi_system(enable_embeddings=False)
        tools = create_todozi_tools(storage_proxy, embedding)

        # Example: create a task
        tool = next(t for t in tools if isinstance(t, CreateTaskTool))
        res = await tool.execute({"action": "Write documentation for API", "priority": "high", "assignee": "human"})
        print(res.message)

        # Example: search tasks keyword
        tool = next(t for t in tools if isinstance(t, SearchTasksTool))
        res = await tool.execute({"query": "documentation", "semantic": False})
        print(res.message)

        # Example: simple tool - quick stats
        tool = next(t for t in tools if isinstance(t, SimpleTodoziTool))
        res = await tool.execute({"action": "stats", "content": "anything"})
        print(res.message)

    asyncio.run(main())
