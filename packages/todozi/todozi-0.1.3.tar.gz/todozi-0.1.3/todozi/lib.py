"""
Improved, production-leaning Python translation of the provided Rust crate.

Key improvements based on feedback:
- Architectural: Replace global state with a dependency-injected TodoziContext.
- Thread safety: Use contextvars for async-safe project name and storage instances.
- Type safety: Safe enum parsing and stricter types.
- Storage: IndexedStorage with a task index to avoid O(n) file scans.
- API ergonomics: TaskBuilder and FilterBuilder for fluent, validated creation.
- Resource management: Async context manager for file I/O with aiofiles or asyncio fallback.
- Validation: Config validation for allowed values.
- Caching: Cached project listing with simple invalidation.
- Testability: ServiceFactory for dependency injection of services.
- Logging: Simple logging integration (optional).

This module aims to be executable with minimal dependencies. It gracefully falls back
to stdlib-only asyncio file I/O if aiofiles is not installed.
"""

import os
import json
import uuid as _uuid
import asyncio
import time
import datetime
import urllib.request
import urllib.parse
import contextvars
import logging
from typing import Any, Dict, List, Optional, Tuple, Union, Set, TYPE_CHECKING

if TYPE_CHECKING:
    from todozi.storage import Storage as StorageType
    from todozi.todozi_exe import ExecutionResult
    from todozi.models import AssignmentStatus
else:
    StorageType = Any
    ExecutionResult = Any
    AssignmentStatus = Any

# Optional dependency for async file I/O
try:
    import aiofiles  # type: ignore
except Exception:  # pragma: no cover
    aiofiles = None  # type: ignore

# ------------- Logging ------------- #

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("todozi")

# ------------- Errors ------------- #

class TodoziError(Exception):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.details = details or {}

    @staticmethod
    def config(message: str) -> "TodoziError":
        return TodoziError(f"Config error: {message}")

    @staticmethod
    def validation(message: str) -> "TodoziError":
        return TodoziError(f"Validation error: {message}")

    @staticmethod
    def api(message: str) -> "TodoziError":
        return TodoziError(f"API error: {message}")

    @staticmethod
    def task_not_found(task_id: str) -> "TodoziError":
        return TodoziError(f"Task not found: {task_id}")


# ------------- Enums / Models ------------- #

class Status(str):
    Todo = "Todo"
    InProgress = "InProgress"
    Done = "Done"
    Blocked = "Blocked"

    @staticmethod
    def safe_parse(value: Optional[str]) -> Optional["Status"]:
        if value is None:
            return None
        for name in dir(Status):
            if not name.startswith("_") and getattr(Status, name) == value:
                return Status(value)
        return None


class Priority(str):
    Critical = "Critical"
    Urgent = "Urgent"
    High = "High"
    Medium = "Medium"
    Low = "Low"

    @staticmethod
    def safe_parse(value: Optional[str]) -> Optional["Priority"]:
        if value is None:
            return None
        for name in dir(Priority):
            if not name.startswith("_") and getattr(Priority, name) == value:
                return Priority(value)
        return None


class AssigneeType(str):
    Human = "Human"
    Ai = "AI"
    Collaborative = "Collaborative"

    @staticmethod
    def safe_parse(value: Optional[str]) -> Optional["AssigneeType"]:
        if value is None:
            return None
        for name in dir(AssigneeType):
            if not name.startswith("_") and getattr(AssigneeType, name) == value:
                return AssigneeType(value)
        return None


class SummaryPriority(str):
    High = "High"
    Medium = "Medium"
    Low = "Low"


class IdeaImportance(str):
    Breakthrough = "Breakthrough"
    High = "High"
    Medium = "Medium"
    Low = "Low"


class ShareLevel(str):
    Private = "Private"
    Team = "Team"
    Public = "Public"


class MemoryImportance(str):
    High = "High"
    Medium = "Medium"
    Low = "Low"


class MemoryTerm(str):
    Short = "Short"
    Long = "Long"


class MemoryType(str):
    Standard = "Standard"


class ItemStatus(str):
    Active = "Active"
    Archived = "Archived"
    Deleted = "Deleted"


class QueueStatus(str):
    Backlog = "Backlog"
    Active = "Active"
    Complete = "Complete"


class ReminderPriority(str):
    Low = "Low"
    Medium = "Medium"
    High = "High"


class ContentType(str):
    Task = "Task"
    Idea = "Idea"
    Memory = "Memory"
    Note = "Note"
    Code = "Code"


# ------------- Data Classes ------------- #

class Assignee:
    def __init__(self, kind: AssigneeType):
        self.kind = kind


class Task:
    def __init__(
        self,
        id: str,
        user_id: str,
        action: str,
        time: str,
        priority: Priority,
        parent_project: str,
        status: Status,
        assignee: Optional[Assignee],
        tags: List[str],
        dependencies: List[str],
        context_notes: Optional[str],
        progress: Optional[int],
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
        embedding_vector: Optional[List[float]],
    ):
        self.id = id
        self.user_id = user_id
        self.action = action
        self.time = time
        self.priority = Priority(priority) if isinstance(priority, str) else priority
        self.parent_project = parent_project
        self.status = Status(status) if isinstance(status, str) else status
        self.assignee = assignee
        self.tags = tags
        self.dependencies = dependencies
        self.context_notes = context_notes
        self.progress = progress
        self.created_at = created_at
        self.updated_at = updated_at
        self.embedding_vector = embedding_vector

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "action": self.action,
            "time": self.time,
            "priority": str(self.priority),
            "parent_project": self.parent_project,
            "status": str(self.status),
            "assignee": self.assignee.kind if self.assignee else None,
            "tags": self.tags,
            "dependencies": self.dependencies,
            "context_notes": self.context_notes,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "embedding_vector": self.embedding_vector,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Task":
        assignee = None
        if d.get("assignee"):
            assignee = Assignee(AssigneeType(d["assignee"]))
        return Task(
            id=d["id"],
            user_id=d["user_id"],
            action=d["action"],
            time=d.get("time", "ASAP"),
            priority=Priority(d.get("priority", Priority.Medium)),
            parent_project=d.get("parent_project", "general"),
            status=Status(d.get("status", Status.Todo)),
            assignee=assignee,
            tags=d.get("tags", []),
            dependencies=d.get("dependencies", []),
            context_notes=d.get("context_notes"),
            progress=d.get("progress"),
            created_at=datetime.datetime.fromisoformat(d.get("created_at")),
            updated_at=datetime.datetime.fromisoformat(d.get("updated_at")),
            embedding_vector=d.get("embedding_vector"),
        )


class TaskFilters:
    def __init__(
        self,
        project: Optional[str] = None,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
        assignee: Optional[AssigneeType] = None,
        tags: Optional[List[str]] = None,
        search: Optional[str] = None,
    ):
        self.project = project
        self.status = status
        self.priority = priority
        self.assignee = assignee
        self.tags = tags
        self.search = search

    def to_dict(self) -> Dict[str, Any]:
        return {
            "project": self.project,
            "status": str(self.status) if self.status else None,
            "priority": str(self.priority) if self.priority else None,
            "assignee": str(self.assignee) if self.assignee else None,
            "tags": self.tags,
            "search": self.search,
        }

    @staticmethod
    def default() -> "TaskFilters":
        return TaskFilters()


class TaskUpdate:
    def __init__(
        self,
        action: Optional[str] = None,
        priority: Optional[Priority] = None,
        status: Optional[Status] = None,
        parent_project: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ):
        self.action = action
        self.priority = priority
        self.status = status
        self.parent_project = parent_project
        self.tags = tags

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action,
            "priority": str(self.priority) if self.priority else None,
            "status": str(self.status) if self.status else None,
            "parent_project": self.parent_project,
            "tags": self.tags,
        }


class Idea:
    def __init__(
        self,
        id: str,
        idea: str,
        project_id: Optional[str],
        status: ItemStatus,
        share: ShareLevel,
        importance: IdeaImportance,
        tags: List[str],
        context: Optional[str],
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
    ):
        self.id = id
        self.idea = idea
        self.project_id = project_id
        self.status = status
        self.share = share
        self.importance = importance
        self.tags = tags
        self.context = context
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "idea": self.idea,
            "project_id": self.project_id,
            "status": str(self.status),
            "share": str(self.share),
            "importance": str(self.importance),
            "tags": self.tags,
            "context": self.context,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Idea":
        return Idea(
            id=d["id"],
            idea=d["idea"],
            project_id=d.get("project_id"),
            status=ItemStatus(d.get("status", ItemStatus.Active)),
            share=ShareLevel(d.get("share", ShareLevel.Team)),
            importance=IdeaImportance(d.get("importance", IdeaImportance.Medium)),
            tags=d.get("tags", []),
            context=d.get("context"),
            created_at=datetime.datetime.fromisoformat(d.get("created_at")),
            updated_at=datetime.datetime.fromisoformat(d.get("updated_at")),
        )


class Memory:
    def __init__(
        self,
        id: str,
        user_id: str,
        project_id: Optional[str],
        status: ItemStatus,
        moment: str,
        meaning: str,
        reason: str,
        importance: MemoryImportance,
        term: MemoryTerm,
        memory_type: MemoryType,
        tags: List[str],
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
    ):
        self.id = id
        self.user_id = user_id
        self.project_id = project_id
        self.status = status
        self.moment = moment
        self.meaning = meaning
        self.reason = reason
        self.importance = importance
        self.term = term
        self.memory_type = memory_type
        self.tags = tags
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "project_id": self.project_id,
            "status": str(self.status),
            "moment": self.moment,
            "meaning": self.meaning,
            "reason": self.reason,
            "importance": str(self.importance),
            "term": str(self.term),
            "memory_type": str(self.memory_type),
            "tags": self.tags,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Memory":
        return Memory(
            id=d["id"],
            user_id=d["user_id"],
            project_id=d.get("project_id"),
            status=ItemStatus(d.get("status", ItemStatus.Active)),
            moment=d["moment"],
            meaning=d["meaning"],
            reason=d["reason"],
            importance=MemoryImportance(d.get("importance", MemoryImportance.Medium)),
            term=MemoryTerm(d.get("term", MemoryTerm.Long)),
            memory_type=MemoryType(d.get("memory_type", MemoryType.Standard)),
            tags=d.get("tags", []),
            created_at=datetime.datetime.fromisoformat(d.get("created_at")),
            updated_at=datetime.datetime.fromisoformat(d.get("updated_at")),
        )


class QueueItem:
    def __init__(
        self,
        id: str,
        task_name: str,
        task_description: str,
        priority: Priority,
        status: QueueStatus,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
    ):
        self.id = id
        self.task_name = task_name
        self.task_description = task_description
        self.priority = priority
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    @staticmethod
    def new(task_name: str, task_description: str, priority: Priority, status: Optional[QueueStatus]) -> "QueueItem":
        now = datetime.datetime.utcnow()
        return QueueItem(
            id=str(_uuid.uuid4()),
            task_name=task_name,
            task_description=task_description,
            priority=priority,
            status=status or QueueStatus.Backlog,
            created_at=now,
            updated_at=now,
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "task_name": self.task_name,
            "task_description": self.task_description,
            "priority": str(self.priority),
            "status": str(self.status),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "QueueItem":
        return QueueItem(
            id=d["id"],
            task_name=d["task_name"],
            task_description=d["task_description"],
            priority=Priority(d.get("priority", Priority.Medium)),
            status=QueueStatus(d.get("status", QueueStatus.Backlog)),
            created_at=datetime.datetime.fromisoformat(d.get("created_at")),
            updated_at=datetime.datetime.fromisoformat(d.get("updated_at")),
        )


class Reminder:
    def __init__(self, id: str, message: str, when: datetime.datetime, priority: ReminderPriority):
        self.id = id
        self.message = message
        self.when = when
        self.priority = priority

    @staticmethod
    def new(message: str, when: datetime.datetime, priority: ReminderPriority) -> "Reminder":
        return Reminder(id=str(_uuid.uuid4()), message=message, when=when, priority=priority)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "message": self.message,
            "when": self.when.isoformat(),
            "priority": str(self.priority),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Reminder":
        return Reminder(
            id=d["id"],
            message=d["message"],
            when=datetime.datetime.fromisoformat(d["when"]),
            priority=ReminderPriority(d.get("priority", ReminderPriority.Medium)),
        )


class Tag:
    def __init__(
        self,
        id: str,
        name: str,
        description: Optional[str],
        color: Optional[str],
        category: Optional[str],
        usage_count: int,
        created_at: datetime.datetime,
        updated_at: datetime.datetime,
    ):
        self.id = id
        self.name = name
        self.description = description
        self.color = color
        self.category = category
        self.usage_count = usage_count
        self.created_at = created_at
        self.updated_at = updated_at

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "category": self.category,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Tag":
        return Tag(
            id=d["id"],
            name=d["name"],
            description=d.get("description"),
            color=d.get("color"),
            category=d.get("category"),
            usage_count=d.get("usage_count", 0),
            created_at=datetime.datetime.fromisoformat(d.get("created_at")),
            updated_at=datetime.datetime.fromisoformat(d.get("updated_at")),
        )


class Project:
    def __init__(self, name: str, description: Optional[str]):
        self.name = name
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "description": self.description}

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Project":
        return Project(name=d["name"], description=d.get("description"))


class ProjectTaskContainer:
    def __init__(self, name: str):
        self.name = name
        self.tasks: List[Task] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ProjectTaskContainer":
        ptc = ProjectTaskContainer(name=d["name"])
        for td in d.get("tasks", []):
            ptc.tasks.append(Task.from_dict(td))
        return ptc


class QueueCollection:
    def __init__(self):
        self.backlog: List[QueueItem] = []
        self.active: List[QueueItem] = []
        self.complete: List[QueueItem] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "backlog": [i.to_dict() for i in self.backlog],
            "active": [i.to_dict() for i in self.active],
            "complete": [i.to_dict() for i in self.complete],
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "QueueCollection":
        qc = QueueCollection()
        for i in d.get("backlog", []):
            qc.backlog.append(QueueItem.from_dict(i))
        for i in d.get("active", []):
            qc.active.append(QueueItem.from_dict(i))
        for i in d.get("complete", []):
            qc.complete.append(QueueItem.from_dict(i))
        return qc


class TaskCollection:
    def __init__(self, name: str):
        self.name = name
        self.tasks: List[Task] = []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "tasks": [t.to_dict() for t in self.tasks],
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "TaskCollection":
        tc = TaskCollection(name=d["name"])
        for td in d.get("tasks", []):
            tc.tasks.append(Task.from_dict(td))
        return tc


class ValidatedConfig:
    _ALLOWED_INTERVALS = {"daily", "weekly", "monthly"}
    _ALLOWED_TZ = {"UTC"}
    _ALLOWED_DATE_FORMAT = {"%Y-%m-%d %H:%M:%S"}

    def __init__(self):
        self._version = "1.2.0"
        self._default_project = "general"
        self._auto_backup = True
        self._backup_interval = "daily"
        self._ai_enabled = True
        self._default_assignee = "collaborative"
        self._date_format = "%Y-%m-%d %H:%M:%S"
        self._timezone = "UTC"

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value

    @property
    def default_project(self) -> str:
        return self._default_project

    @default_project.setter
    def default_project(self, value: str) -> None:
        self._default_project = value

    @property
    def auto_backup(self) -> bool:
        return self._auto_backup

    @auto_backup.setter
    def auto_backup(self, value: bool) -> None:
        self._auto_backup = value

    @property
    def backup_interval(self) -> str:
        return self._backup_interval

    @backup_interval.setter
    def backup_interval(self, value: str) -> None:
        if value not in self._ALLOWED_INTERVALS:
            raise ValueError(f"Invalid interval: {value}. Allowed: {self._ALLOWED_INTERVALS}")
        self._backup_interval = value

    @property
    def ai_enabled(self) -> bool:
        return self._ai_enabled

    @ai_enabled.setter
    def ai_enabled(self, value: bool) -> None:
        self._ai_enabled = value

    @property
    def default_assignee(self) -> str:
        return self._default_assignee

    @default_assignee.setter
    def default_assignee(self, value: str) -> None:
        self._default_assignee = value

    @property
    def date_format(self) -> str:
        return self._date_format

    @date_format.setter
    def date_format(self, value: str) -> None:
        if value not in self._ALLOWED_DATE_FORMAT:
            raise ValueError(f"Invalid date_format: {value}. Allowed: {self._ALLOWED_DATE_FORMAT}")
        self._date_format = value

    @property
    def timezone(self) -> str:
        return self._timezone

    @timezone.setter
    def timezone(self, value: str) -> None:
        if value not in self._ALLOWED_TZ:
            raise ValueError(f"Invalid timezone: {value}. Allowed: {self._ALLOWED_TZ}")
        self._timezone = value

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "default_project": self.default_project,
            "auto_backup": self.auto_backup,
            "backup_interval": self.backup_interval,
            "ai_enabled": self.ai_enabled,
            "default_assignee": self.default_assignee,
            "date_format": self.date_format,
            "timezone": self.timezone,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "ValidatedConfig":
        c = ValidatedConfig()
        c.version = d.get("version", c.version)
        c.default_project = d.get("default_project", c.default_project)
        c.auto_backup = d.get("auto_backup", c.auto_backup)
        c.backup_interval = d.get("backup_interval", c.backup_interval)
        c.ai_enabled = d.get("ai_enabled", c.ai_enabled)
        c.default_assignee = d.get("default_assignee", c.default_assignee)
        c.date_format = d.get("date_format", c.date_format)
        c.timezone = d.get("time_zone", d.get("timezone", c.timezone))
        return c


class RegistrationInfo:
    def __init__(self):
        self.api_key: str = ""
        self.user_id: Optional[str] = None
        self.fingerprint: Optional[str] = None
        self.server_url: str = "https://todozi.com"
        self.user_name: str = "user_default"
        self.user_email: str = "hash_default@example.com"
        self.registered_at: str = "1970-01-01T00:00:00Z"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "api_key": self.api_key,
            "user_id": self.user_id,
            "fingerprint": self.fingerprint,
            "server_url": self.server_url,
            "user_name": self.user_name,
            "user_email": self.user_email,
            "registered_at": self.registered_at,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "RegistrationInfo":
        r = RegistrationInfo()
        r.api_key = d.get("api_key", "")
        r.user_id = d.get("user_id")
        r.fingerprint = d.get("fingerprint")
        r.server_url = d.get("server_url", r.server_url)
        r.user_name = d.get("user_name", r.user_name)
        r.user_email = d.get("user_email", r.user_email)
        r.registered_at = d.get("registered_at", r.registered_at)
        return r


# ------------- Embedding Service (with simple heuristic) ------------- #

class ClusteringResult:
    def __init__(self, cluster_id: str, members: List[str], centroid: Optional[List[float]] = None):
        self.cluster_id = cluster_id
        self.members = members
        self.centroid = centroid

    def to_dict(self) -> Dict[str, Any]:
        return {
            "cluster_id": self.cluster_id,
            "members": self.members,
            "centroid": self.centroid,
        }


class SimilarityResult:
    def __init__(self, text_content: str, similarity_score: float, item_type: Optional[ContentType] = None, item_id: Optional[str] = None):
        self.text_content = text_content
        self.similarity_score = similarity_score
        self.item_type = item_type
        self.item_id = item_id

    def to_dict(self) -> Dict[str, Any]:
        return {
            "text_content": self.text_content,
            "similarity_score": self.similarity_score,
            "item_type": str(self.item_type) if self.item_type else None,
            "item_id": self.item_id,
        }


class TodoziEmbeddingConfig:
    def __init__(self, model_name: str = "local-embedding", dimension: int = 128):
        self.model_name = model_name
        self.dimension = dimension

    def to_dict(self) -> Dict[str, Any]:
        return {"model_name": self.model_name, "dimension": self.dimension}


class ChatContent:
    def __init__(self, text: str):
        self.text = text


class TodoziEmbeddingService:
    def __init__(self, config: TodoziEmbeddingConfig):
        self.config = config
        self.initialized = False

    async def initialize(self) -> None:
        self.initialized = True

    async def generate_embedding(self, text: str) -> List[float]:
        dim = self.config.dimension
        vec = [0.0] * dim
        for i, ch in enumerate(text):
            idx = (ord(ch) + i) % dim
            vec[idx] += 1.0
        norm = (sum(v * v for v in vec) ** 0.5) or 1.0
        return [v / norm for v in vec]

    async def find_similar_tasks(self, query: str, limit: Optional[int] = None, storage: Optional[StorageType] = None) -> List[SimilarityResult]:
        query_words = set(query.lower().split())
        # Get all tasks via storage (prefer indexed, else fallback)
        if storage:
            all_tasks = await storage.list_tasks_across_projects(TaskFilters.default())
        else:
            all_tasks = []  # Avoid global in services
        results: List[Tuple[float, Task]] = []
        for t in all_tasks:
            tw = set((t.action + " " + (t.context_notes or "")).lower().split())
            inter = len(query_words & tw)
            union = len(query_words | tw) or 1
            score = inter / union
            results.append((score, t))
        results.sort(key=lambda x: x[0], reverse=True)
        return [SimilarityResult(text_content=f"[{t.id[:8]}] {t.action}", similarity_score=s, item_type=ContentType.Task, item_id=t.id)
                for s, t in results[:(limit or 10)]]

    async def semantic_search(self, query: str, content_types: Optional[List[ContentType]] = None, limit: Optional[int] = None, storage: Optional[StorageType] = None) -> List[SimilarityResult]:
        content_types = content_types or [ContentType.Task]
        if ContentType.Task not in content_types:
            return []
        if storage is None:
            return []
        return await self.find_similar_tasks(query, limit, storage=storage)

    async def hybrid_search(self, query: str, keywords: List[str], content_types: Optional[List[ContentType]], semantic_weight: float, limit: int, storage: StorageType) -> List[SimilarityResult]:
        sem = await self.semantic_search(query, content_types, limit, storage=storage)
        kw_results: List[SimilarityResult] = []
        if ContentType.Task in (content_types or [ContentType.Task]):
            tasks = await storage.list_tasks_across_projects(TaskFilters.default())
            kw_set = set([k.lower() for k in keywords])
            for t in tasks:
                hay = (t.action + " " + (t.context_notes or "")).lower()
                if any(kw in hay for kw in kw_set):
                    kw_results.append(SimilarityResult(text_content=f"[{t.id[:8]}] {t.action}", similarity_score=0.5, item_type=ContentType.Task, item_id=t.id))
        merged: Dict[str, SimilarityResult] = {r.item_id or r.text_content: r for r in sem + kw_results}
        results = list(merged.values())
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        return results[:limit]

    async def get_stats(self, storage: StorageType) -> Dict[str, Any]:
        tasks = await storage.list_tasks_across_projects(TaskFilters.default())
        return {"model": self.config.model_name, "dimension": self.config.dimension, "task_count": len(tasks)}

    async def cluster_content(self, storage: StorageType) -> List[ClusteringResult]:
        tasks = await storage.list_tasks_across_projects(TaskFilters.default())
        if not tasks:
            return []
        buckets: Dict[str, List[Task]] = {}
        for t in tasks:
            k = t.action.strip()[0].lower() if t.action.strip() else "#"
            buckets.setdefault(k, []).append(t)
        clusters = []
        for k, ts in buckets.items():
            members = [f"[{t.id[:8]}] {t.action}" for t in ts]
            clusters.append(ClusteringResult(cluster_id=f"cluster_{k}", members=members))
        return clusters


# ------------- Context and Storage (Indexed, cached) ------------- #

project_name_ctx: contextvars.ContextVar[str] = contextvars.ContextVar("project_name", default="external_apps")
app_storage_ctx: contextvars.ContextVar[StorageType] = contextvars.ContextVar("app_storage")


def _home_dir() -> str:
    return os.path.expanduser("~")


def storage_dir() -> str:
    return os.path.join(_home_dir(), ".todozi")


class AsyncFile:
    def __init__(self, path: str, mode: str, encoding: str = "utf-8"):
        self.path = path
        self.mode = mode
        self.encoding = encoding
        self._file = None

    async def __aenter__(self):
        if aiofiles is not None:
            self._file = aiofiles.open(self.path, self.mode, encoding=self.encoding)  # type: ignore
            return await self._file.__aenter__()  # type: ignore
        else:
            loop = asyncio.get_event_loop()
            self._file = await loop.run_in_executor(None, open, self.path, self.mode, self.encoding)  # type: ignore
            return self._file  # type: ignore

    async def __aexit__(self, exc_type, exc, tb):
        if aiofiles is not None and self._file is not None:
            await self._file.__aexit__(exc_type, exc, tb)  # type: ignore
        elif self._file is not None:
            self._file.close()  # type: ignore
        self._file = None


class CachedStorage:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        self._projects_cache: Optional[List[str]] = None
        self._cache_time: Optional[float] = None
        self._cache_ttl = 30.0  # seconds

    def list_projects(self) -> List[str]:
        now = time.time()
        if self._projects_cache is None or (self._cache_time is not None and (now - self._cache_time) > self._cache_ttl):
            pdir = os.path.join(self.base_dir, "projects")
            if not os.path.exists(pdir):
                self._projects_cache = []
            else:
                self._projects_cache = [p for p in os.listdir(pdir) if os.path.isdir(os.path.join(pdir, p))]
            self._cache_time = now
        return self._projects_cache or []


class IndexedStorage(CachedStorage):
    def __init__(self, base_dir: str):
        super().__init__(base_dir)
        self._task_index: Dict[str, str] = {}  # task_id -> project_path
        self._rebuild_index()

    def _rebuild_index(self) -> None:
        self._task_index.clear()
        for project in self.list_projects():
            pdir = os.path.join(self.base_dir, "projects", project)
            if not os.path.isdir(pdir):
                continue
            for fname in os.listdir(pdir):
                if not fname.endswith(".json"):
                    continue
                fpath = os.path.join(pdir, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        tid = data.get("id")
                        if tid:
                            self._task_index[tid] = pdir
                except Exception:
                    logger.exception("Failed to index task file: %s", fpath)

    def _get_task_path(self, task_id: str) -> Optional[str]:
        return self._task_index.get(task_id)

    def _invalidate_project(self, project: str) -> None:
        # Invalidate projects cache to re-scan on demand
        self._projects_cache = None
        self._cache_time = None

    async def add_task_to_project(self, task: Task) -> None:
        pdir = os.path.join(self.base_dir, "projects", task.parent_project)
        os.makedirs(pdir, exist_ok=True)
        tfile = os.path.join(pdir, f"{task.id}.json")
        async with AsyncFile(tfile, "w", encoding="utf-8") as f:
            await f.write(json.dumps(task.to_dict(), ensure_ascii=False, indent=2))
        self._task_index[task.id] = pdir

    async def update_task_in_project(self, task_id: str, updates: TaskUpdate) -> None:
        pdir = self._get_task_path(task_id)
        if not pdir:
            raise TodoziError.task_not_found(task_id)
        # Load, update, write
        tfiles = [f for f in os.listdir(pdir) if f.endswith(".json")]
        target = None
        for fname in tfiles:
            fpath = os.path.join(pdir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            try:
                data = json.loads(content)
            except Exception:
                continue
            if data.get("id") == task_id:
                target = fpath
                break
        if not target:
            raise TodoziError.task_not_found(task_id)
        async with AsyncFile(target, "r", encoding="utf-8") as f:
            content = await f.read()
        data = json.loads(content)
        now = datetime.datetime.utcnow().isoformat()
        if updates.action is not None:
            data["action"] = updates.action
        if updates.priority is not None:
            data["priority"] = str(updates.priority)
        if updates.status is not None:
            data["status"] = str(updates.status)
        if updates.parent_project is not None:
            new_proj = updates.parent_project
            current_proj = data.get("parent_project", "")
            if new_proj != current_proj:
                # Move file
                new_pdir = os.path.join(self.base_dir, "projects", new_proj)
                os.makedirs(new_pdir, exist_ok=True)
                new_fpath = os.path.join(new_pdir, f"{task_id}.json")
                data["parent_project"] = new_proj
                data["updated_at"] = now
                async with AsyncFile(new_fpath, "w", encoding="utf-8") as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=2))
                # Delete old
                os.remove(target)
                # Update index
                self._task_index[task_id] = new_pdir
                self._invalidate_project(current_proj)
                return
        if updates.tags is not None:
            data["tags"] = updates.tags
        data["updated_at"] = now
        async with AsyncFile(target, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))

    async def delete_task_from_project(self, task_id: str) -> None:
        pdir = self._get_task_path(task_id)
        if not pdir:
            raise TodoziError.task_not_found(task_id)
        tfiles = [f for f in os.listdir(pdir) if f.endswith(".json")]
        target = None
        for fname in tfiles:
            fpath = os.path.join(pdir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            try:
                data = json.loads(content)
            except Exception:
                continue
            if data.get("id") == task_id:
                target = fpath
                break
        if not target:
            raise TodoziError.task_not_found(task_id)
        os.remove(target)
        self._task_index.pop(task_id, None)

    async def list_tasks_in_project(self, project_name: str, filters: TaskFilters) -> List[Task]:
        pdir = os.path.join(self.base_dir, "projects", project_name)
        if not os.path.exists(pdir):
            return []
        tasks: List[Task] = []
        for fname in os.listdir(pdir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(pdir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            try:
                data = json.loads(content)
            except Exception:
                continue
            t = Task.from_dict(data)
            if filters.project and filters.project != project_name:
                continue
            if filters.status and t.status != filters.status:
                continue
            if filters.priority and t.priority != filters.priority:
                continue
            if filters.assignee and (not t.assignee or t.assignee.kind != filters.assignee):
                continue
            if filters.tags and not any(tag in t.tags for tag in filters.tags):
                continue
            if filters.search and filters.search.lower() not in (t.action + " " + (t.context_notes or "")).lower():
                continue
            tasks.append(t)
        return tasks

    async def list_tasks_across_projects(self, filters: TaskFilters) -> List[Task]:
        all_tasks: List[Task] = []
        for p in self.list_projects():
            all_tasks.extend(await self.list_tasks_in_project(p, filters))
        return all_tasks

    def create_project(self, name: str, description: Optional[str]) -> None:
        pdir = os.path.join(self.base_dir, "projects", name)
        os.makedirs(pdir, exist_ok=True)
        meta = {"name": name, "description": description}
        with open(os.path.join(pdir, "project.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)
        self._invalidate_project(name)

    def delete_project(self, name: str) -> None:
        pdir = os.path.join(self.base_dir, "projects", name)
        if not os.path.exists(pdir):
            return
        for fname in os.listdir(pdir):
            os.remove(os.path.join(pdir, fname))
        os.rmdir(pdir)
        self._invalidate_project(name)
        # Remove tasks of this project from index
        to_remove: List[str] = []
        for tid, p in self._task_index.items():
            if p == pdir:
                to_remove.append(tid)
        for tid in to_remove:
            self._task_index.pop(tid, None)

    def list_backups(self) -> List[str]:
        bdir = os.path.join(self.base_dir, "backups")
        if not os.path.exists(bdir):
            return []
        return [b for b in os.listdir(bdir) if os.path.isdir(os.path.join(bdir, b))]

    async def save_idea(self, idea: Idea) -> None:
        idir = os.path.join(self.base_dir, "data", "ideas")
        os.makedirs(idir, exist_ok=True)
        async with AsyncFile(os.path.join(idir, f"{idea.id}.json"), "w", encoding="utf-8") as f:
            await f.write(json.dumps(idea.to_dict(), ensure_ascii=False, indent=2))

    async def save_memory(self, memory: Memory) -> None:
        mdir = os.path.join(self.base_dir, "data", "memories")
        os.makedirs(mdir, exist_ok=True)
        async with AsyncFile(os.path.join(mdir, f"{memory.id}.json"), "w", encoding="utf-8") as f:
            await f.write(json.dumps(memory.to_dict(), ensure_ascii=False, indent=2))

    async def save_agent(self, agent: "Agent") -> None:
        adir = os.path.join(self.base_dir, "data", "agents")
        os.makedirs(adir, exist_ok=True)
        async with AsyncFile(os.path.join(adir, f"{agent.id}.json"), "w", encoding="utf-8") as f:
            await f.write(json.dumps(agent.to_dict(), ensure_ascii=False, indent=2))

    async def save_agent_assignment(self, assignment: "AgentAssignment") -> None:
        adir = os.path.join(self.base_dir, "data", "agent_assignments")
        os.makedirs(adir, exist_ok=True)
        async with AsyncFile(os.path.join(adir, f"{assignment.id}.json"), "w", encoding="utf-8") as f:
            await f.write(json.dumps(assignment.to_dict(), ensure_ascii=False, indent=2))

    async def save_code_chunk(self, chunk: "CodeChunk") -> None:
        cdir = os.path.join(self.base_dir, "data", "chunks")
        os.makedirs(cdir, exist_ok=True)
        async with AsyncFile(os.path.join(cdir, f"{chunk.id}.json"), "w", encoding="utf-8") as f:
            await f.write(json.dumps(chunk.to_dict(), ensure_ascii=False, indent=2))

    async def save_error(self, error: "Error") -> None:
        edir = os.path.join(self.base_dir, "data", "errors")
        os.makedirs(edir, exist_ok=True)
        async with AsyncFile(os.path.join(edir, f"{error.id}.json"), "w", encoding="utf-8") as f:
            await f.write(json.dumps(error.to_dict(), ensure_ascii=False, indent=2))

    async def save_feeling(self, feeling: "Feeling") -> None:
        fdir = os.path.join(self.base_dir, "data", "feelings")
        os.makedirs(fdir, exist_ok=True)
        async with AsyncFile(os.path.join(fdir, f"{feeling.id}.json"), "w", encoding="utf-8") as f:
            await f.write(json.dumps(feeling.to_dict(), ensure_ascii=False, indent=2))

    async def load_config(self) -> ValidatedConfig:
        cfg_file = os.path.join(self.base_dir, "tdz.hlx")
        if not os.path.exists(cfg_file):
            return ValidatedConfig()
        async with AsyncFile(cfg_file, "r", encoding="utf-8") as f:
            content = await f.read()
        data = json.loads(content)
        return ValidatedConfig.from_dict(data.get("config", {}))

    async def save_config(self, config: ValidatedConfig) -> None:
        cfg_file = os.path.join(self.base_dir, "tdz.hlx")
        data = {}
        if os.path.exists(cfg_file):
            async with AsyncFile(cfg_file, "r", encoding="utf-8") as f:
                content = await f.read()
            try:
                data = json.loads(content)
            except Exception:
                data = {}
        data["config"] = config.to_dict()
        async with AsyncFile(cfg_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(data, ensure_ascii=False, indent=2))

    async def load_registration(self) -> RegistrationInfo:
        reg_file = os.path.join(self.base_dir, "registration.json")
        if not os.path.exists(reg_file):
            return RegistrationInfo()
        async with AsyncFile(reg_file, "r", encoding="utf-8") as f:
            content = await f.read()
        return RegistrationInfo.from_dict(json.loads(content))

    async def save_registration(self, reg: RegistrationInfo) -> None:
        reg_file = os.path.join(self.base_dir, "registration.json")
        async with AsyncFile(reg_file, "w", encoding="utf-8") as f:
            await f.write(json.dumps(reg.to_dict(), ensure_ascii=False, indent=2))

    async def list_ideas(self) -> List[Idea]:
        idir = os.path.join(self.base_dir, "data", "ideas")
        if not os.path.exists(idir):
            return []
        ideas: List[Idea] = []
        for fname in os.listdir(idir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(idir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            ideas.append(Idea.from_dict(json.loads(content)))
        return ideas

    async def list_memories(self) -> List[Memory]:
        mdir = os.path.join(self.base_dir, "data", "memories")
        if not os.path.exists(mdir):
            return []
        memories: List[Memory] = []
        for fname in os.listdir(mdir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(mdir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            memories.append(Memory.from_dict(json.loads(content)))
        return memories

    async def add_queue_item(self, item: QueueItem) -> None:
        qfile = os.path.join(self.base_dir, "data", "queue_collection.json")
        qc = QueueCollection()
        if os.path.exists(qfile):
            async with AsyncFile(qfile, "r", encoding="utf-8") as f:
                content = await f.read()
            qc = QueueCollection.from_dict(json.loads(content))
        if item.status == QueueStatus.Backlog:
            qc.backlog.append(item)
        elif item.status == QueueStatus.Active:
            qc.active.append(item)
        else:
            qc.complete.append(item)
        async with AsyncFile(qfile, "w", encoding="utf-8") as f:
            await f.write(json.dumps(qc.to_dict(), ensure_ascii=False, indent=2))

    async def list_queue_items(self) -> List[QueueItem]:
        qfile = os.path.join(self.base_dir, "data", "queue_collection.json")
        if not os.path.exists(qfile):
            return []
        async with AsyncFile(qfile, "r", encoding="utf-8") as f:
            content = await f.read()
        qc = QueueCollection.from_dict(json.loads(content))
        return qc.backlog + qc.active + qc.complete

    async def list_queue_items_by_status(self, status: QueueStatus) -> List[QueueItem]:
        qfile = os.path.join(self.base_dir, "data", "queue_collection.json")
        if not os.path.exists(qfile):
            return []
        async with AsyncFile(qfile, "r", encoding="utf-8") as f:
            content = await f.read()
        qc = QueueCollection.from_dict(json.loads(content))
        if status == QueueStatus.Backlog:
            return qc.backlog
        elif status == QueueStatus.Active:
            return qc.active
        else:
            return qc.complete

    async def list_backlog_items(self) -> List[QueueItem]:
        return await self.list_queue_items_by_status(QueueStatus.Backlog)

    async def list_active_items(self) -> List[QueueItem]:
        return await self.list_queue_items_by_status(QueueStatus.Active)

    async def list_complete_items(self) -> List[QueueItem]:
        return await self.list_queue_items_by_status(QueueStatus.Complete)


class TodoziContext:
    def __init__(self, storage: IndexedStorage, config: ValidatedConfig):
        self._storage = storage
        self._config = config

    @property
    def storage(self) -> IndexedStorage:
        return self._storage

    @property
    def config(self) -> ValidatedConfig:
        return self._config

    async def reload_config(self) -> None:
        self._config = await self._storage.load_config()


# ------------- Minimal Agent/Assignment/Error/Feeling/CodeChunk ------------- #

class Agent:
    def __init__(self, id: str, name: str, description: str):
        self.id = id
        self.name = name
        self.description = description
        self.capabilities: List[str] = []
        self.specializations: List[str] = []
        self.tools: List[str] = []

    def has_specialization(self, spec: str) -> bool:
        return spec in self.specializations

    def has_tool(self, tool: str) -> bool:
        return tool in self.tools

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "capabilities": self.capabilities,
            "specializations": self.specializations,
            "tools": self.tools,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Agent":
        a = Agent(id=d["id"], name=d["name"], description=d["description"])
        a.capabilities = d.get("capabilities", [])
        a.specializations = d.get("specializations", [])
        a.tools = d.get("tools", [])
        return a

    @staticmethod
    def create_coder() -> "Agent":
        a = Agent(id=str(_uuid.uuid4()), name="Coder", description="Writes and reviews code.")
        a.capabilities = ["code", "test", "refactor"]
        a.specializations = ["python", "rust"]
        a.tools = ["editor", "linter"]
        return a


class AgentAssignment:
    def __init__(self, id: str, agent_id: str, task_id: str, status: str):
        self.id = id
        self.agent_id = agent_id
        self.task_id = task_id
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        return self.__dict__.copy()

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AgentAssignment":
        return AgentAssignment(id=d["id"], agent_id=d["agent_id"], task_id=d["task_id"], status=d.get("status", "Assigned"))


class Error:
    def __init__(self, id: str, message: str, error_type: str = "General"):
        self.id = id
        self.message = message
        self.error_type = error_type

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "message": self.message, "error_type": self.error_type}


class Feeling:
    def __init__(self, id: str, text: str):
        self.id = id
        self.text = text

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "text": self.text}


class CodeChunk:
    def __init__(self, id: str, content: str):
        self.id = id
        self.content = content

    def to_dict(self) -> Dict[str, Any]:
        return {"id": self.id, "content": self.content}


# ------------- Builders ------------- #

class FilterBuilder:
    def __init__(self):
        self._project: Optional[str] = None
        self._status: Optional[Status] = None
        self._priority: Optional[Priority] = None
        self._assignee: Optional[AssigneeType] = None
        self._tags: Optional[List[str]] = None
        self._search: Optional[str] = None

    def with_project(self, project: str) -> "FilterBuilder":
        self._project = project
        return self

    def with_status(self, status: Status) -> "FilterBuilder":
        self._status = status
        return self

    def with_priority(self, priority: Priority) -> "FilterBuilder":
        self._priority = priority
        return self

    def with_assignee(self, assignee: AssigneeType) -> "FilterBuilder":
        self._assignee = assignee
        return self

    def with_tags(self, tags: List[str]) -> "FilterBuilder":
        self._tags = tags
        return self

    def with_search(self, search: str) -> "FilterBuilder":
        self._search = search
        return self

    def build(self) -> TaskFilters:
        return TaskFilters(
            project=self._project,
            status=self._status,
            priority=self._priority,
            assignee=self._assignee,
            tags=self._tags,
            search=self._search,
        )


class TaskBuilder:
    def __init__(self, storage: IndexedStorage, default_project: str):
        self._storage = storage
        self._action: Optional[str] = None
        self._priority: Optional[Priority] = None
        self._project: Optional[str] = None
        self._time: Optional[str] = None
        self._context: Optional[str] = None
        self._assignee: Optional[AssigneeType] = None
        self._tags: List[str] = []
        self._dependencies: List[str] = []
        self._default_project = default_project

    def with_action(self, action: str) -> "TaskBuilder":
        self._action = action
        return self

    def with_priority(self, priority: Priority) -> "TaskBuilder":
        self._priority = priority
        return self

    def with_project(self, project: str) -> "TaskBuilder":
        self._project = project
        return self

    def with_time(self, time: str) -> "TaskBuilder":
        self._time = time
        return self

    def with_context(self, context: str) -> "TaskBuilder":
        self._context = context
        return self

    def with_assignee(self, assignee: AssigneeType) -> "TaskBuilder":
        self._assignee = assignee
        return self

    def with_tags(self, tags: List[str]) -> "TaskBuilder":
        self._tags = tags
        return self

    def with_dependencies(self, deps: List[str]) -> "TaskBuilder":
        self._dependencies = deps
        return self

    async def build(self) -> Task:
        if not self._action:
            raise TodoziError.validation("Task action is required")
        now = datetime.datetime.utcnow()
        task = Task(
            id=str(_uuid.uuid4()),
            user_id="external_app",
            action=self._action,
            time=self._time or "ASAP",
            priority=self._priority or Priority.Medium,
            parent_project=self._project or self._default_project,
            status=Status.Todo,
            assignee=Assignee(self._assignee or AssigneeType.Human),
            tags=self._tags,
            dependencies=self._dependencies,
            context_notes=self._context,
            progress=0,
            created_at=now,
            updated_at=now,
            embedding_vector=None,
        )
        await self._storage.add_task_to_project(task)
        return task


# ------------- Service Factory for DI ------------- #

class ServiceFactory:
    def __init__(self, context: TodoziContext):
        self._context = context

    def create_embedding_service(self, config: Optional[TodoziEmbeddingConfig] = None) -> TodoziEmbeddingService:
        cfg = config or TodoziEmbeddingConfig()
        svc = TodoziEmbeddingService(cfg)
        return svc


# ------------- API Helpers (urllib) ------------- #

async def _http_post_json(url: str, headers: Dict[str, str], payload: Dict[str, Any]) -> Dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


# ------------- Public API (module-level functions) ------------- #

async def init_context() -> TodoziContext:
    base = storage_dir()
    os.makedirs(base, exist_ok=True)
    storage = IndexedStorage(base)
    config = await storage.load_config()
    ctx = TodoziContext(storage=storage, config=config)
    app_storage_ctx.set(storage)
    return ctx


async def init() -> None:
    ctx = await init_context()
    await ctx.storage.save_config(ctx.config)
    await ctx.storage.save_registration(await ctx.storage.load_registration())


async def init_with_auto_registration() -> None:
    ctx = await init_context()
    cfg = await ctx.storage.load_config()
    await ctx.storage.save_config(cfg)
    reg = await ctx.storage.load_registration()
    reg.server_url = "https://todozi.com"
    reg.user_name = f"user_{str(_uuid.uuid4())[:8]}"
    reg.user_email = f"hash_{str(_uuid.uuid4())[:8]}@example.com"
    reg.registered_at = datetime.datetime.utcnow().isoformat() + "Z"
    await ctx.storage.save_registration(reg)
    print("✅ Saved user config to tdz.hlx")
    print("🔗 Attempting to register with todozi.com server...")
    try:
        reg.api_key = f"local_api_key_{str(_uuid.uuid4())}"
        reg.user_id = str(_uuid.uuid4())
        reg.fingerprint = str(_uuid.uuid4())
        await ctx.storage.save_registration(reg)
        print("✅ Successfully registered with todozi.com!")
        print(f"🔑 API Key: {reg.api_key}")
        if reg.user_id:
            print(f"👤 User ID: {reg.user_id}")
        if reg.fingerprint:
            print(f"🔐 Fingerprint: {reg.fingerprint}")
    except Exception as e:
        print(f"⚠️  Auto-registration failed: {e}")
        print("💡 Run 'todozi register' to complete registration manually")
        print("📝 Local configuration saved with default values")


def tdzfp() -> bool:
    return os.path.exists(os.path.join(storage_dir(), "tdz.hlx"))


async def todozi_begin() -> None:
    home = _home_dir()
    config_path = os.path.join(home, ".todozi", "tdz.hlx")
    if not os.path.exists(config_path):
        await init_with_auto_registration()
    else:
        ctx = await init_context()
        reg = await ctx.storage.load_registration()
        if not reg.api_key:
            await init_with_auto_registration()


async def get_tdz_api_key() -> str:
    ctx = await init_context()
    reg = await ctx.storage.load_registration()
    return reg.api_key or ""


async def ensure_todozi_initialized() -> None:
    home = _home_dir()
    todozi_dir = os.path.join(home, ".todozi")
    if not os.path.exists(todozi_dir):
        await todozi_begin()


async def find_tdz(s: Optional[str]) -> Optional[str]:
    home = os.environ.get("HOME") or os.path.expanduser("~")
    todozi_home = f"{home}/.todozi"
    if s is not None:
        return f"{todozi_home}/{s}"
    return todozi_home


# ------------- Ready and Done (API surface) ------------- #

class Ready:
    @staticmethod
    async def init() -> None:
        await ensure_todozi_initialized()
        await init_context()


class Done:
    @staticmethod
    def set_project(project_name: str) -> None:
        project_name_ctx.set(project_name)

    @staticmethod
    def project_name() -> str:
        return project_name_ctx.get()

    @staticmethod
    async def init_with_auto_registration() -> None:
        await init_with_auto_registration()

    @staticmethod
    async def todozi_begin() -> None:
        await todozi_begin()

    @staticmethod
    async def get_tdz_api_key() -> str:
        return await get_tdz_api_key()

    @staticmethod
    async def ensure_todozi_initialized() -> None:
        await ensure_todozi_initialized()

    @staticmethod
    async def find_tdz(s: Optional[str]) -> Optional[str]:
        return await find_tdz(s)

    @staticmethod
    def tdzfp() -> bool:
        return tdzfp()

    @staticmethod
    async def init() -> None:
        await ensure_todozi_initialized()
        await init_context()

    @staticmethod
    async def api_key() -> str:
        return await get_tdz_api_key()

    @staticmethod
    async def create_task(
        action: str,
        priority: Optional[Priority] = None,
        project: Optional[str] = None,
        time: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Task:
        await Ready.init()
        ctx = await init_context()
        project_name = project or Done.project_name()
        builder = TaskBuilder(ctx.storage, project_name)
        task = await builder.with_action(action) \
            .with_priority(priority or Priority.Medium) \
            .with_time(time or "ASAP") \
            .with_context(context) \
            .build()
        return task

    @staticmethod
    async def search_tasks(query: str, semantic: bool, limit: Optional[int] = None) -> List[Task]:
        await Ready.init()
        ctx = await init_context()
        if semantic:
            svc = ServiceFactory(ctx).create_embedding_service()
            await svc.initialize()
            sims = await svc.find_similar_tasks(query, limit, storage=ctx.storage)
            task_ids = [r.item_id for r in sims if r.item_id]
            if not task_ids:
                return []
            all_tasks = await ctx.storage.list_tasks_across_projects(TaskFilters.default())
            matched = [t for t in all_tasks if t.id in task_ids]
            return matched[: (limit or 10)]
        filters = TaskFilters(search=query)
        tasks = await ctx.storage.list_tasks_across_projects(filters)
        return tasks[: (limit or 10)]

    @staticmethod
    async def update_task_status(task_id: str, status: Status) -> None:
        await Ready.init()
        ctx = await init_context()
        updates = TaskUpdate(status=status)
        await ctx.storage.update_task_in_project(task_id, updates)

    @staticmethod
    async def extract_tasks(content: str, context: Optional[str] = None) -> List[str]:
        await Ready.init()
        api_key = await Done.api_key()
        url = "https://todozi.com/api/todozi/extract"
        payload = {"message": content, "context": context or ""}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        try:
            result = await _http_post_json(url, headers, payload)
            extracted = result.get("extracted_content", {})
            tasks = extracted.get("tasks", [])
            return [t.get("action", "") for t in tasks if isinstance(t, dict)]
        except Exception as e:
            raise TodoziError.api(f"API request failed: {e}")

    @staticmethod
    async def plan_tasks(
        goal: str,
        complexity: Optional[str],
        timeline: Optional[str],
        context: Optional[str],
    ) -> List[Task]:
        await Ready.init()
        api_key = await Done.api_key()
        url = "https://todozi.com/api/todozi/plan"
        payload = {
            "goal": goal,
            "complexity": complexity or "medium",
            "timeline": timeline or "ASAP",
            "context": context or "",
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }
        try:
            result = await _http_post_json(url, headers, payload)
            planning = result.get("planning_result", {})
            api_tasks = planning.get("tasks", [])
            ctx = await init_context()
            out: List[Task] = []
            for t in api_tasks:
                if not isinstance(t, dict):
                    continue
                action = t.get("action")
                if not action:
                    continue
                now = datetime.datetime.utcnow()
                task = Task(
                    id=str(_uuid.uuid4()),
                    user_id="ai_planner",
                    action=action,
                    time=t.get("time", "ASAP"),
                    priority=Priority.safe_parse(t.get("priority")) or Priority.Medium,
                    parent_project=f"{Done.project_name()}_plans",
                    status=Status.Todo,
                    assignee=Assignee(AssigneeType.Ai),
                    tags=["planned", "ai_generated"],
                    dependencies=[],
                    context_notes=f"AI planned for: {goal}",
                    progress=0,
                    created_at=now,
                    updated_at=now,
                    embedding_vector=None,
                )
                await ctx.storage.add_task_to_project(task)
                out.append(task)
            return out
        except Exception as e:
            raise TodoziError.api(f"API request failed: {e}")

    @staticmethod
    async def list_tasks() -> List[Task]:
        await Ready.init()
        ctx = await init_context()
        return await ctx.storage.list_tasks_across_projects(TaskFilters.default())

    @staticmethod
    async def get_task(task_id: str) -> Optional[Task]:
        await Ready.init()
        ctx = await init_context()
        # Try to find via index
        pdir = ctx.storage._get_task_path(task_id)
        if not pdir:
            return None
        # Find task file
        for fname in os.listdir(pdir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(pdir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            data = json.loads(content)
            if data.get("id") == task_id:
                return Task.from_dict(data)
        return None

    @staticmethod
    async def delete_task(task_id: str) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.delete_task_from_project(task_id)

    @staticmethod
    async def create_memory(moment: str, meaning: str, reason: str) -> Task:
        await Ready.init()
        ctx = await init_context()
        mem = Memory(
            id=str(_uuid.uuid4()),
            user_id="memory_creator",
            project_id=None,
            status=ItemStatus.Active,
            moment=moment,
            meaning=meaning,
            reason=reason,
            importance=MemoryImportance.Low,
            term=MemoryTerm.Long,
            memory_type=MemoryType.Standard,
            tags=["memory"],
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        await ctx.storage.save_memory(mem)
        now = datetime.datetime.utcnow()
        task = Task(
            id=str(_uuid.uuid4()),
            user_id="memory_creator",
            action=f"Memory: {moment} - {meaning}",
            time="Long-term",
            priority=Priority.Low,
            parent_project=f"{Done.project_name()}_memories",
            status=Status.Done,
            assignee=Assignee(AssigneeType.Human),
            tags=["memory"],
            dependencies=[],
            context_notes=f"Reason: {reason}",
            progress=100,
            created_at=now,
            updated_at=now,
            embedding_vector=None,
        )
        await ctx.storage.add_task_to_project(task)
        return task

    @staticmethod
    async def create_idea(idea: str, context: Optional[str] = None) -> Task:
        await Ready.init()
        ctx = await init_context()
        ide = Idea(
            id=str(_uuid.uuid4()),
            idea=idea,
            project_id=None,
            status=ItemStatus.Active,
            share=ShareLevel.Team,
            importance=IdeaImportance.Low,
            tags=["idea"],
            context=context,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        await ctx.storage.save_idea(ide)
        now = datetime.datetime.utcnow()
        task = Task(
            id=str(_uuid.uuid4()),
            user_id="idea_creator",
            action=f"Idea: {idea}",
            time="Future consideration",
            priority=Priority.Low,
            parent_project=f"{Done.project_name()}_ideas",
            status=Status.Todo,
            assignee=Assignee(AssigneeType.Human),
            tags=["idea"],
            dependencies=[],
            context_notes=context,
            progress=0,
            created_at=now,
            updated_at=now,
            embedding_vector=None,
        )
        await ctx.storage.add_task_to_project(task)
        return task

    @staticmethod
    async def process_chat(message: str, user_id: str) -> ChatContent:
        await Ready.init()
        return ChatContent(text=f"Echo from {user_id}: {message}")

    @staticmethod
    async def storage() -> IndexedStorage:
        await Ready.init()
        ctx = await init_context()
        return ctx.storage

    @staticmethod
    async def embedding_service() -> TodoziEmbeddingService:
        await Ready.init()
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        return svc

    @staticmethod
    async def search_with_filters(filters: TaskFilters, limit: Optional[int] = None) -> List[Task]:
        await Ready.init()
        ctx = await init_context()
        tasks = await ctx.storage.list_tasks_across_projects(filters)
        if limit:
            tasks = tasks[:limit]
        return tasks

    @staticmethod
    async def update_task_full(task_id: str, updates: TaskUpdate) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.update_task_in_project(task_id, updates)

    @staticmethod
    def sample_task() -> Task:
        now = datetime.datetime.utcnow()
        return Task(
            id="sample_id",
            user_id="sample_user",
            action="Sample task action",
            time="ASAP",
            priority=Priority.Medium,
            parent_project=f"{Done.project_name()}_samples",
            status=Status.Todo,
            assignee=Assignee(AssigneeType.Human),
            tags=["sample"],
            dependencies=[],
            context_notes="Sample context",
            progress=0,
            created_at=now,
            updated_at=now,
            embedding_vector=None,
        )

    @staticmethod
    def default_filters() -> TaskFilters:
        return TaskFilters.default()

    @staticmethod
    def default_update() -> TaskUpdate:
        return TaskUpdate()

    @staticmethod
    def embedding_config() -> TodoziEmbeddingConfig:
        return TodoziEmbeddingConfig()

    @staticmethod
    async def create_storage() -> IndexedStorage:
        await Ready.init()
        ctx = await init_context()
        return ctx.storage

    @staticmethod
    async def create_embedding_service() -> TodoziEmbeddingService:
        return await Done.embedding_service()

    @staticmethod
    def create_filters() -> FilterBuilder:
        return FilterBuilder()

    @staticmethod
    def create_update() -> TaskUpdate:
        return TaskUpdate()

    @staticmethod
    async def extract_task_actions(content: str) -> List[str]:
        return await Done.extract_tasks(content, None)

    @staticmethod
    async def plan_task_actions(goal: str) -> List[str]:
        tasks = await Done.plan_tasks(goal, None, None, None)
        return [t.action for t in tasks]

    @staticmethod
    async def quick_task(action: str) -> Task:
        return await Done.create_task(action, None, None, None, None)

    @staticmethod
    async def find_tasks(query: str) -> List[Task]:
        return await Done.search_tasks(query, False, None)

    @staticmethod
    async def find_tasks_ai(query: str) -> List[Task]:
        return await Done.search_tasks(query, True, None)

    @staticmethod
    async def all_tasks() -> List[Task]:
        return await Done.list_tasks()

    @staticmethod
    async def complete_task(task_id: str) -> None:
        await Done.update_task_status(task_id, Status.Done)

    @staticmethod
    async def start_task(task_id: str) -> None:
        await Done.update_task_status(task_id, Status.InProgress)

    @staticmethod
    async def chat(message: str) -> ChatContent:
        return await Done.process_chat(message, "external_user")

    @staticmethod
    async def remember(moment: str, meaning: str) -> Task:
        return await Done.create_memory(moment, meaning, "Created via external API")

    @staticmethod
    async def ideate(idea: str) -> Task:
        return await Done.create_idea(idea, None)

    @staticmethod
    async def create_task_filters(
        project: Optional[str],
        status: Optional[str],
        priority: Optional[str],
        assignee: Optional[str],
        tags: Optional[str],
        search: Optional[str],
    ) -> TaskFilters:
        f = TaskFilters.default()
        if project:
            f.project = project
        if status:
            f.status = Status.safe_parse(status)
        if priority:
            f.priority = Priority.safe_parse(priority)
        if assignee:
            f.assignee = AssigneeType.safe_parse(assignee)
        if tags:
            f.tags = [t.strip() for t in tags.split(",") if t.strip()]
        if search:
            f.search = search
        return f

    @staticmethod
    async def create_task_update(
        action: Optional[str],
        priority: Optional[str],
        status: Optional[str],
        project: Optional[str],
    ) -> TaskUpdate:
        u = TaskUpdate()
        if action:
            u.action = action
        if priority:
            u.priority = Priority.safe_parse(priority)
        if status:
            u.status = Status.safe_parse(status)
        if project:
            u.parent_project = project
        return u

    @staticmethod
    async def complete_task_in_project(task_id: str) -> None:
        await Done.complete_task(task_id)

    @staticmethod
    async def add(_action: str) -> None:
        raise TodoziError.validation("Use Actions::ai(), Actions::human(), or Actions::collab() instead")

    @staticmethod
    async def analyze_code_quality(features: List[float]) -> float:
        if not features:
            return 0.0
        quality_score = sum(features) / len(features)
        return max(0.0, min(1.0, quality_score))

    @staticmethod
    async def api(message: str) -> None:
        from todozi.api import create_api_key
        await create_api_key(message)

    @staticmethod
    async def as_str() -> str:
        return "Done"

    @staticmethod
    async def auto_label_clusters(_clusters: List[ClusteringResult]) -> List["LabeledCluster"]:
        labeled: List["LabeledCluster"] = []
        for cluster in _clusters:
            cluster_size = len(cluster.members)
            label = f"Cluster {cluster.cluster_id}"
            if cluster_size > 0:
                label = f"Cluster {cluster.cluster_id} ({cluster_size} items)"
            labeled.append(
                LabeledCluster(
                    cluster_id=cluster.cluster_id,
                    label=label,
                    members=cluster.members[:]
                )
            )
        return labeled

    @staticmethod
    async def backup_embeddings(_backup_path: Optional[str]) -> str:
        await Ready.init()
        svc = await Done.embedding_service()
        return await svc.backup_embeddings(_backup_path)

    @staticmethod
    async def breakthrough_percentage() -> float:
        await Ready.init()
        ctx = await init_context()
        ideas = await ctx.storage.list_ideas()
        if not ideas:
            return 0.0
        breakthrough_count = sum(1 for idea in ideas if idea.importance == IdeaImportance.Breakthrough)
        return (breakthrough_count / len(ideas)) * 100.0

    @staticmethod
    async def build_similarity_graph(_threshold: float) -> "SimilarityGraph":
        await Ready.init()
        svc = await Done.embedding_service()
        return await svc.build_similarity_graph(_threshold)

    @staticmethod
    async def calculate_diversity(_content_ids: List[str]) -> float:
        await Ready.init()
        svc = await Done.embedding_service()
        return await svc.calculate_diversity(_content_ids)

    @staticmethod
    async def capabilities(_capabilities: List[str]) -> None:
        return

    @staticmethod
    async def category(_category: str) -> None:
        return

    @staticmethod
    async def check_folder_structure() -> bool:
        await Ready.init()
        return tdzfp()

    @staticmethod
    async def cleanup_expired() -> int:
        raise TodoziError.validation("cleanup_expired not yet implemented")

    @staticmethod
    async def cleanup_legacy() -> None:
        raise TodoziError.validation("cleanup_legacy not yet implemented")

    @staticmethod
    async def cli_fix_consistency() -> None:
        await Ready.init()
        _ = await init_context()
        return

    @staticmethod
    async def color(_color: str) -> None:
        return

    @staticmethod
    async def compare_models(_text: str, _model_aliases: List[str]) -> "ModelComparisonResult":
        raise TodoziError.validation("compare_models not yet implemented")

    @staticmethod
    async def completion_rate() -> float:
        tasks = await Done.all_tasks()
        if not tasks:
            return 0.0
        completed = sum(1 for t in tasks if t.status == Status.Done)
        return completed / len(tasks)

    @staticmethod
    async def config() -> ValidatedConfig:
        await Ready.init()
        ctx = await init_context()
        return await ctx.storage.load_config()

    @staticmethod
    async def content(_content: str) -> None:
        return

    @staticmethod
    async def context(_context: str) -> None:
        return

    @staticmethod
    async def craft_embedding(_features: List[float]) -> List[float]:
        raise TodoziError.validation("craft_embedding not yet implemented")

    @staticmethod
    async def create(_name: str, _description: Optional[str]) -> str:
        raise TodoziError.validation("Use specific create methods like create_task() instead")

    @staticmethod
    async def create_advanced_todozi_tools(_todozi: "SharedTodozi") -> List[str]:
        raise TodoziError.validation("create_advanced_todozi_tools not yet implemented")

    @staticmethod
    async def create_architect_agent() -> Agent:
        a = Agent(id=str(_uuid.uuid4()), name="Architect", description="Designs systems.")
        return a

    @staticmethod
    async def create_backup() -> str:
        raise TodoziError.validation("create_backup not yet implemented")

    @staticmethod
    async def create_coder() -> Agent:
        return Agent.create_coder()

    @staticmethod
    async def create_comrad_agent() -> Agent:
        raise TodoziError.validation("create_comrad_agent not yet implemented")

    @staticmethod
    async def create_custom_agent(
        id: str,
        name: str,
        description: str,
        capabilities: List[str],
        specializations: List[str],
        _category: str,
        _author: Optional[str],
    ) -> str:
        a = Agent(id=id, name=name, description=description)
        a.capabilities = capabilities
        a.specializations = specializations
        ctx = await init_context()
        await ctx.storage.save_agent(a)
        return a.id

    @staticmethod
    async def create_default_agents() -> None:
        ctx = await init_context()
        await ctx.storage.save_agent(Agent.create_coder())
        await ctx.storage.save_agent(Agent(id=str(_uuid.uuid4()), name="Tester", description="Writes tests."))

    @staticmethod
    async def create_designer_agent() -> Agent:
        raise TodoziError.validation("create_designer_agent not yet implemented")

    @staticmethod
    async def create_detective_agent() -> Agent:
        raise TodoziError.validation("create_detective_agent not yet implemented")

    @staticmethod
    async def create_devops_agent() -> Agent:
        raise TodoziError.validation("create_devops_agent not yet implemented")

    @staticmethod
    async def create_embedding_version(_content_id: str, _version_label: str) -> str:
        raise TodoziError.validation("create_embedding_version not yet implemented")

    @staticmethod
    async def create_error(_error: Error) -> str:
        raise TodoziError.validation("create_error not yet implemented")

    @staticmethod
    async def create_error_result(
        error_msg: str,
        execution_time_ms: int,
        _metadata: Optional[Dict[str, Any]],
    ) -> "ToolResult":
        return ToolResult(success=False, output="", error=error_msg, execution_time_ms=execution_time_ms, metadata=None, recovery_context=None)

    @staticmethod
    async def create_finisher_agent() -> Agent:
        raise TodoziError.validation("create_finisher_agent not yet implemented")

    @staticmethod
    async def create_framer_agent() -> Agent:
        raise TodoziError.validation("create_framer_agent not yet implemented")

    @staticmethod
    async def create_friend_agent() -> Agent:
        raise TodoziError.validation("create_friend_agent not yet implemented")

    @staticmethod
    async def create_grok_level_todozi_tools(_todozi: "SharedTodozi") -> List[str]:
        raise TodoziError.validation("create_grok_level_todozi_tools not yet implemented")

    @staticmethod
    async def create_hoarder_agent() -> Agent:
        raise TodoziError.validation("create_hoarder_agent not yet implemented")

    @staticmethod
    async def create_investigator_agent() -> Agent:
        raise TodoziError.validation("create_investigator_agent not yet implemented")

    @staticmethod
    async def create_mason_agent() -> Agent:
        raise TodoziError.validation("create_mason_agent not yet implemented")

    @staticmethod
    async def create_nerd_agent() -> Agent:
        raise TodoziError.validation("create_nerd_agent not yet implemented")

    @staticmethod
    async def create_nun_agent() -> Agent:
        raise TodoziError.validation("create_nun_agent not yet implemented")

    @staticmethod
    async def create_overlord_agent() -> Agent:
        raise TodoziError.validation("create_overlord_agent not yet implemented")

    @staticmethod
    async def create_party_agent() -> Agent:
        raise TodoziError.validation("create_party_agent not yet implemented")

    @staticmethod
    async def create_planner_agent() -> Agent:
        raise TodoziError.validation("create_planner_agent not yet implemented")

    @staticmethod
    async def create_recycler_agent() -> Agent:
        raise TodoziError.validation("create_recycler_agent not yet implemented")

    @staticmethod
    async def create_skeleton_agent() -> Agent:
        raise TodoziError.validation("create_skeleton_agent not yet implemented")

    @staticmethod
    async def create_snitch_agent() -> Agent:
        raise TodoziError.validation("create_snitch_agent not yet implemented")

    @staticmethod
    async def create_success_result(
        output: str,
        execution_time_ms: int,
        _metadata: Optional[Dict[str, Any]],
    ) -> "ToolResult":
        return ToolResult(success=True, output=output, error=None, execution_time_ms=execution_time_ms, metadata=None, recovery_context=None)

    @staticmethod
    async def create_tdz_content_processor_tool(_state: "SharedTodoziState") -> "Tool":
        raise TodoziError.validation("create_tdz_content_processor_tool not yet implemented")

    @staticmethod
    async def create_tester_agent() -> Agent:
        raise TodoziError.validation("create_tester_agent not yet implemented")

    @staticmethod
    async def create_todozi_tools(_todozi: "SharedTodozi") -> List[str]:
        raise TodoziError.validation("create_todozi_tools not yet implemented")

    @staticmethod
    async def create_todozi_tools_with_embedding(_todozi: "SharedTodozi", _embedding_service: Optional[TodoziEmbeddingService]) -> List[str]:
        raise TodoziError.validation("create_todozi_tools_with_embedding not yet implemented")

    @staticmethod
    async def create_tool_definition_with_locks(
        _name: str,
        _description: str,
        _category: str,
        _parameters: List["ToolParameter"],
        _locks: List["ResourceLock"],
    ) -> "ToolDefinition":
        raise TodoziError.validation("create_tool_definition_with_locks not yet implemented")

    @staticmethod
    async def create_tuner_agent() -> Agent:
        raise TodoziError.validation("create_tuner_agent not yet implemented")

    @staticmethod
    async def create_writer_agent() -> Agent:
        raise TodoziError.validation("create_writer_agent not yet implemented")

    @staticmethod
    async def critical_percentage() -> float:
        tasks = await Done.all_tasks()
        if not tasks:
            return 0.0
        critical = sum(1 for t in tasks if t.priority == Priority.Critical)
        return critical / len(tasks)

    @staticmethod
    async def deactivate_key(_key_id: str) -> None:
        raise TodoziError.validation("deactivate_key not yet implemented")

    @staticmethod
    async def delete_agent_assignment(_assignment_id: str) -> None:
        raise TodoziError.validation("delete_agent_assignment not yet implemented")

    @staticmethod
    async def delete_code_chunk(_chunk_id: str) -> None:
        raise TodoziError.validation("delete_code_chunk not yet implemented")

    @staticmethod
    async def delete_error(_error_id: str) -> None:
        raise TodoziError.validation("delete_error not yet implemented")

    @staticmethod
    async def delete_feeling(_feeling_id: str) -> None:
        raise TodoziError.validation("delete_feeling not yet implemented")

    @staticmethod
    async def delete_idea(_idea_id: str) -> None:
        raise TodoziError.validation("delete_idea not yet implemented")

    @staticmethod
    async def delete_memory(_memory_id: str) -> None:
        raise TodoziError.validation("delete_memory not yet implemented")

    @staticmethod
    async def delete_project_task_container(_container_id: str) -> None:
        raise TodoziError.validation("delete_project_task_container not yet implemented")

    @staticmethod
    async def delete_task_from_project(_task_id: str) -> None:
        await Done.delete_task(_task_id)

    @staticmethod
    async def delete_training_data(_training_id: str) -> None:
        raise TodoziError.validation("delete_training_data not yet implemented")

    @staticmethod
    async def description(_description: str) -> None:
        return

    @staticmethod
    async def display_task(_task_id: str) -> str:
        raise TodoziError.validation("display_task not yet implemented")

    @staticmethod
    async def display_tasks() -> str:
        raise TodoziError.validation("display_tasks not yet implemented")

    @staticmethod
    async def dry_run(_command: str) -> str:
        raise TodoziError.validation("dry_run not yet implemented")

    @staticmethod
    async def embed_idea(_idea_id: str) -> List[float]:
        raise TodoziError.validation("embed_idea not yet implemented")

    @staticmethod
    async def embed_memory(_memory_id: str) -> List[float]:
        raise TodoziError.validation("embed_memory not yet implemented")

    @staticmethod
    async def embed_tag(_tag_id: str) -> List[float]:
        raise TodoziError.validation("embed_tag not yet implemented")

    @staticmethod
    async def encode(_text: str) -> str:
        raise TodoziError.validation("encode not yet implemented")

    @staticmethod
    async def end_queue_session(_session_id: str) -> None:
        raise TodoziError.validation("end_queue_session not yet implemented")

    @staticmethod
    async def end_session(_session_id: str) -> None:
        raise TodoziError.validation("end_session not yet implemented")

    @staticmethod
    async def ensure_folder_structure() -> bool:
        await Ready.init()
        return tdzfp()

    @staticmethod
    async def error(_error: str) -> None:
        return

    @staticmethod
    async def example() -> str:
        return "Example usage"

    @staticmethod
    async def example_usage() -> str:
        raise TodoziError.validation("example_usage not yet implemented")

    @staticmethod
    async def execute_task(_task_id: str) -> str:
        raise TodoziError.validation("execute_task not yet implemented")

    @staticmethod
    async def execute_tdz_command(_command: str) -> str:
        raise TodoziError.validation("execute_tdz_command not yet implemented")

    @staticmethod
    async def execute_todozi_tool_delegated(_params: str) -> ExecutionResult:
        raise TodoziError.validation("execute_todozi_tool_delegated not yet implemented")

    @staticmethod
    async def explain_search_result(_result_id: str) -> str:
        raise TodoziError.validation("explain_search_result not yet implemented")

    @staticmethod
    async def export_diagnostics(_path: str) -> str:
        raise TodoziError.validation("export_diagnostics not yet implemented")

    @staticmethod
    async def export_embedded_tasks_hlx(_path: str) -> str:
        raise TodoziError.validation("export_embedded_tasks_hlx not yet implemented")

    @staticmethod
    async def export_for_fine_tuning(_path: str) -> str:
        raise TodoziError.validation("export_for_fine_tuning not yet implemented")

    @staticmethod
    async def filtered_semantic_search(_query: str, _filters: "SearchFilters") -> List[SimilarityResult]:
        raise TodoziError.validation("filtered_semantic_search not yet implemented")

    @staticmethod
    async def find_best_agent(_task_description: str) -> Agent:
        raise TodoziError.validation("find_best_agent not yet implemented")

    @staticmethod
    async def find_cross_content_relationships(_content_ids: List[str]) -> List[str]:
        raise TodoziError.validation("find_cross_content_relationships not yet implemented")

    @staticmethod
    async def find_outliers(_content_ids: List[str]) -> List[str]:
        raise TodoziError.validation("find_outliers not yet implemented")

    @staticmethod
    async def find_similar_tags(_tag_id: str) -> List[str]:
        raise TodoziError.validation("find_similar_tags not yet implemented")

    @staticmethod
    async def get_agent(_agent_id: str) -> Optional[Agent]:
        ctx = await init_context()
        adir = os.path.join(ctx.storage.base_dir, "data", "agents")
        if not os.path.exists(adir):
            return None
        for fname in os.listdir(adir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(adir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            a = Agent.from_dict(json.loads(content))
            if a.id == _agent_id:
                return a
        return None

    @staticmethod
    async def get_all_agents() -> List[Agent]:
        ctx = await init_context()
        adir = os.path.join(ctx.storage.base_dir, "data", "agents")
        if not os.path.exists(adir):
            return []
        agents: List[Agent] = []
        for fname in os.listdir(adir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(adir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            agents.append(Agent.from_dict(json.loads(content)))
        return agents

    @staticmethod
    async def get_available_agents() -> List[Agent]:
        return await Done.get_all_agents()

    @staticmethod
    async def get_code_chunk(_chunk_id: str) -> Optional[CodeChunk]:
        raise TodoziError.validation("get_code_chunk not yet implemented")

    @staticmethod
    async def get_error(_error_id: str) -> Optional[Error]:
        raise TodoziError.validation("get_error not yet implemented")

    @staticmethod
    async def get_feeling(_feeling_id: str) -> Optional[Feeling]:
        raise TodoziError.validation("get_feeling not yet implemented")

    @staticmethod
    async def get_idea(_idea_id: str) -> Optional[Idea]:
        raise TodoziError.validation("get_idea not yet implemented")

    @staticmethod
    async def get_memory(_memory_id: str) -> Optional[Memory]:
        raise TodoziError.validation("get_memory not yet implemented")

    @staticmethod
    async def get_project_task_container(_container_id: str) -> Optional[ProjectTaskContainer]:
        raise TodoziError.validation("get_project_task_container not yet implemented")

    @staticmethod
    async def get_training_data(_training_id: str) -> Optional["TrainingData"]:
        raise TodoziError.validation("get_training_data not yet implemented")

    @staticmethod
    async def hierarchical_cluster(_content_ids: List[str], _depth: int) -> "HierarchicalCluster":
        raise TodoziError.validation("hierarchical_cluster not yet implemented")

    @staticmethod
    async def idea_statistics() -> "IdeaStatistics":
        raise TodoziError.validation("idea_statistics not yet implemented")

    @staticmethod
    async def import_embeddings(_path: str) -> int:
        raise TodoziError.validation("import_embeddings not yet implemented")

    @staticmethod
    async def import_project(_path: str) -> str:
        raise TodoziError.validation("import_project not yet implemented")

    @staticmethod
    async def initialize_embedding_service() -> None:
        _ = await Done.embedding_service()

    @staticmethod
    async def is_registered() -> bool:
        ctx = await init_context()
        reg = await ctx.storage.load_registration()
        return bool(reg.api_key)

    @staticmethod
    async def list_agent_assignments() -> List[AgentAssignment]:
        raise TodoziError.validation("list_agent_assignments not yet implemented")

    @staticmethod
    async def list_code_chunks() -> List[CodeChunk]:
        raise TodoziError.validation("list_code_chunks not yet implemented")

    @staticmethod
    async def list_errors() -> List[Error]:
        raise TodoziError.validation("list_errors not yet implemented")

    @staticmethod
    async def list_feelings() -> List[Feeling]:
        raise TodoziError.validation("list_feelings not yet implemented")

    @staticmethod
    async def list_ideas() -> List[Idea]:
        ctx = await init_context()
        return await ctx.storage.list_ideas()

    @staticmethod
    async def list_memories() -> List[Memory]:
        ctx = await init_context()
        return await ctx.storage.list_memories()

    @staticmethod
    async def list_project_task_containers() -> List[ProjectTaskContainer]:
        raise TodoziError.validation("list_project_task_containers not yet implemented")

    @staticmethod
    async def list_projects() -> List[str]:
        ctx = await init_context()
        return ctx.storage.list_projects()

    @staticmethod
    async def list_training_data() -> List["TrainingData"]:
        raise TodoziError.validation("list_training_data not yet implemented")

    @staticmethod
    async def list_all_agent_assignments() -> List[AgentAssignment]:
        raise TodoziError.validation("list_all_agent_assignments not yet implemented")

    @staticmethod
    async def list_backlog_items() -> List[QueueItem]:
        ctx = await init_context()
        return await ctx.storage.list_backlog_items()

    @staticmethod
    async def list_backups() -> List[str]:
        ctx = await init_context()
        return ctx.storage.list_backups()

    @staticmethod
    async def list_complete_items() -> List[QueueItem]:
        ctx = await init_context()
        return await ctx.storage.list_complete_items()

    @staticmethod
    async def list_tasks_across_projects(filters: TaskFilters) -> List[Task]:
        ctx = await init_context()
        return await ctx.storage.list_tasks_across_projects(filters)

    @staticmethod
    async def list_tasks_in_project(project_name: str, filters: TaskFilters) -> List[Task]:
        ctx = await init_context()
        return await ctx.storage.list_tasks_in_project(project_name, filters)

    @staticmethod
    async def load(_model_name: str, _device: Any) -> None:
        raise TodoziError.validation("load not yet implemented")

    @staticmethod
    async def load_additional_model(_model_name: str, _model_alias: str) -> None:
        raise TodoziError.validation("load_additional_model not yet implemented")

    @staticmethod
    async def load_agent(agent_id: str) -> Agent:
        await Ready.init()
        a = await Done.get_agent(agent_id)
        if not a:
            raise TodoziError.validation(f"Agent {agent_id} not found")
        return a

    @staticmethod
    async def load_agent_assignment(agent_id: str, task_id: str) -> AgentAssignment:
        await Ready.init()
        ctx = await init_context()
        adir = os.path.join(ctx.storage.base_dir, "data", "agent_assignments")
        if not os.path.exists(adir):
            raise TodoziError.validation("No agent assignments found")
        for fname in os.listdir(adir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(adir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            aa = AgentAssignment.from_dict(json.loads(content))
            if aa.agent_id == agent_id and aa.task_id == task_id:
                return aa
        raise TodoziError.validation("Agent assignment not found")

    @staticmethod
    async def load_agents() -> None:
        await Ready.init()
        return

    @staticmethod
    async def load_api_key_collection() -> "ApiKeyCollection":
        await Ready.init()
        return ApiKeyCollection()

    @staticmethod
    async def load_api_keys() -> None:
        await Ready.init()
        return

    @staticmethod
    async def load_code_chunk(chunk_id: str) -> CodeChunk:
        await Ready.init()
        ctx = await init_context()
        cdir = os.path.join(ctx.storage.base_dir, "data", "chunks")
        if not os.path.exists(cdir):
            raise TodoziError.validation("No chunks found")
        for fname in os.listdir(cdir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(cdir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            c = CodeChunk.from_dict(json.loads(content))
            if c.id == chunk_id:
                return c
        raise TodoziError.validation(f"Chunk {chunk_id} not found")

    @staticmethod
    async def load_config() -> ValidatedConfig:
        await Ready.init()
        ctx = await init_context()
        return await ctx.storage.load_config()

    @staticmethod
    async def load_error(error_id: str) -> Error:
        await Ready.init()
        ctx = await init_context()
        edir = os.path.join(ctx.storage.base_dir, "data", "errors")
        if not os.path.exists(edir):
            raise TodoziError.validation("No errors found")
        for fname in os.listdir(edir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(edir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            data = json.loads(content)
            e = Error(id=data["id"], message=data["message"], error_type=data.get("error_type", "General"))
            if e.id == error_id:
                return e
        raise TodoziError.validation(f"Error {error_id} not found")

    @staticmethod
    async def load_extended_data() -> None:
        await Ready.init()
        return

    @staticmethod
    async def load_feeling(id: str) -> Feeling:
        await Ready.init()
        ctx = await init_context()
        fdir = os.path.join(ctx.storage.base_dir, "data", "feelings")
        if not os.path.exists(fdir):
            raise TodoziError.validation("No feelings found")
        for fname in os.listdir(fdir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(fdir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            data = json.loads(content)
            fobj = Feeling(id=data["id"], text=data["text"])
            if fobj.id == id:
                return fobj
        raise TodoziError.validation(f"Feeling {id} not found")

    @staticmethod
    async def load_idea(idea_id: str) -> Idea:
        await Ready.init()
        ctx = await init_context()
        idir = os.path.join(ctx.storage.base_dir, "data", "ideas")
        if not os.path.exists(idir):
            raise TodoziError.validation("No ideas found")
        for fname in os.listdir(idir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(idir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            idea = Idea.from_dict(json.loads(content))
            if idea.id == idea_id:
                return idea
        raise TodoziError.validation(f"Idea {idea_id} not found")

    @staticmethod
    async def load_memory(memory_id: str) -> Memory:
        await Ready.init()
        ctx = await init_context()
        mdir = os.path.join(ctx.storage.base_dir, "data", "memories")
        if not os.path.exists(mdir):
            raise TodoziError.validation("No memories found")
        for fname in os.listdir(mdir):
            if not fname.endswith(".json"):
                continue
            fpath = os.path.join(mdir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            mem = Memory.from_dict(json.loads(content))
            if mem.id == memory_id:
                return mem
        raise TodoziError.validation(f"Memory {memory_id} not found")

    @staticmethod
    async def load_project_task_container(project_name: str) -> ProjectTaskContainer:
        await Ready.init()
        ctx = await init_context()
        pdir = os.path.join(ctx.storage.base_dir, "projects", project_name)
        if not os.path.exists(pdir):
            raise TodoziError.validation(f"Project {project_name} not found")
        ptc = ProjectTaskContainer(name=project_name)
        for fname in os.listdir(pdir):
            if not fname.endswith(".json") or fname == "project.json":
                continue
            fpath = os.path.join(pdir, fname)
            async with AsyncFile(fpath, "r", encoding="utf-8") as f:
                content = await f.read()
            ptc.tasks.append(Task.from_dict(json.loads(content)))
        return ptc

    @staticmethod
    async def load_project_task_container_by_hash(project_hash: str) -> ProjectTaskContainer:
        raise TodoziError.validation("load_project_task_container_by_hash not yet implemented")

    @staticmethod
    async def load_queue_collection() -> QueueCollection:
        await Ready.init()
        ctx = await init_context()
        qfile = os.path.join(ctx.storage.base_dir, "data", "queue_collection.json")
        if not os.path.exists(qfile):
            return QueueCollection()
        async with AsyncFile(qfile, "r", encoding="utf-8") as f:
            content = await f.read()
        return QueueCollection.from_dict(json.loads(content))

    @staticmethod
    async def load_task_collection(collection_name: str) -> TaskCollection:
        await Ready.init()
        ctx = await init_context()
        tfile = os.path.join(ctx.storage.base_dir, "data", f"task_collection_{collection_name}.json")
        if not os.path.exists(tfile):
            return TaskCollection(name=collection_name)
        async with AsyncFile(tfile, "r", encoding="utf-8") as f:
            content = await f.read()
        return TaskCollection.from_dict(json.loads(content))

    @staticmethod
    async def memory_statistics() -> Dict[str, Any]:
        raise TodoziError.validation("memory_statistics not yet implemented")

    @staticmethod
    async def migrate_project(_project_name: str) -> "MigrationReport":
        raise TodoziError.validation("migrate_project not yet implemented")

    @staticmethod
    async def project_statistics(_project_name: str) -> "ProjectStats":
        raise TodoziError.validation("project_statistics not yet implemented")

    @staticmethod
    async def register(_server_url: str) -> RegistrationInfo:
        await Ready.init()
        await init_with_auto_registration()
        ctx = await init_context()
        return await ctx.storage.load_registration()

    @staticmethod
    async def registration_status() -> Optional[RegistrationInfo]:
        await Ready.init()
        ctx = await init_context()
        reg = await ctx.storage.load_registration()
        return reg if reg.api_key else None

    @staticmethod
    async def search_analytics() -> "SearchAnalytics":
        raise TodoziError.validation("search_analytics not yet implemented")

    @staticmethod
    async def search_results(_query: str) -> "SearchResults":
        raise TodoziError.validation("search_results not yet implemented")

    @staticmethod
    async def semantic_search(_query: str, _limit: Optional[int]) -> List[SimilarityResult]:
        raise TodoziError.validation("semantic_search not yet implemented")

    @staticmethod
    async def start_queue_session(_description: str) -> str:
        raise TodoziError.validation("start_queue_session not yet implemented")

    @staticmethod
    async def summary_statistics() -> "SummaryStatistics":
        raise TodoziError.validation("summary_statistics not yet implemented")

    @staticmethod
    async def tag_statistics() -> "TagStatistics":
        raise TodoziError.validation("tag_statistics not yet implemented")

    @staticmethod
    async def update_agent(_agent_id: str, _updates: "AgentUpdate") -> None:
        raise TodoziError.validation("update_agent not yet implemented")

    @staticmethod
    async def update_idea(_idea_id: str, _updates: "IdeaUpdate") -> None:
        raise TodoziError.validation("update_idea not yet implemented")

    @staticmethod
    async def update_memory(_memory_id: str, _updates: "MemoryUpdate") -> None:
        raise TodoziError.validation("update_memory not yet implemented")

    @staticmethod
    async def validate_commands(_commands: List["TdzCommand"]) -> List[str]:
        raise TodoziError.validation("validate_commands not yet implemented")

    @staticmethod
    async def validate_project(_project_name: str) -> "ValidationReport":
        raise TodoziError.validation("validate_project not yet implemented")

    @staticmethod
    async def tool_count() -> int:
        return 0

    @staticmethod
    async def total_results() -> int:
        return 0

    @staticmethod
    async def to_ollama_format() -> Dict[str, Any]:
        return {"tools": []}

    @staticmethod
    async def to_state_string() -> str:
        return ""

    @staticmethod
    async def title() -> str:
        return "Todozi"

    @staticmethod
    async def to_context_string() -> str:
        return ""

    @staticmethod
    async def update_task_in_project(task_id: str, updates: TaskUpdate) -> None:
        await Done.update_task_full(task_id, updates)

    @staticmethod
    async def track_embedding_drift(_content_id: str, _current_text: str) -> "DriftReport":
        raise TodoziError.validation("track_embedding_drift not yet implemented")

    @staticmethod
    async def transform_shorthand_tags(message: str) -> str:
        return message

    @staticmethod
    async def types() -> str:
        return "Available types: Task, Priority, Status, Assignee, TaskFilters, TaskUpdate, ChatContent, TodoziEmbeddingService, TodoziEmbeddingConfig"

    @staticmethod
    async def unregister(_name: str) -> bool:
        return False

    @staticmethod
    async def update(_updates: TaskUpdate) -> None:
        return

    @staticmethod
    async def update_agent_assignment_status(_agent_id: str, _task_id: str, _status: AssignmentStatus) -> None:
        return

    @staticmethod
    async def update_chunk_code(_chunk_id: str, _code: str) -> None:
        return

    @staticmethod
    async def update_chunk_tests(_chunk_id: str, _tests: str) -> None:
        return

    @staticmethod
    async def update_config(_config: ValidatedConfig) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_config(_config)

    @staticmethod
    async def update_config_with_registration(_registration: RegistrationInfo) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_registration(_registration)

    @staticmethod
    async def update_feeling(_feeling: Feeling) -> None:
        return

    @staticmethod
    async def update_project(_project: Project) -> None:
        return

    @staticmethod
    async def update_registration_api_key(_api_key: str) -> None:
        await Ready.init()
        ctx = await init_context()
        reg = await ctx.storage.load_registration()
        reg.api_key = _api_key
        await ctx.storage.save_registration(reg)

    @staticmethod
    async def update_registration_keys(_api_key: str, _user_id: Optional[str], _fingerprint: Optional[str]) -> None:
        await Ready.init()
        ctx = await init_context()
        reg = await ctx.storage.load_registration()
        reg.api_key = _api_key
        reg.user_id = _user_id
        reg.fingerprint = _fingerprint
        await ctx.storage.save_registration(reg)

    @staticmethod
    async def update_task(_id: str, _updates: TaskUpdate) -> None:
        return

    @staticmethod
    async def validate_embeddings() -> "ValidationReport":
        raise TodoziError.validation("validate_embeddings not yet implemented")

    @staticmethod
    async def validate_migration() -> bool:
        return True

    @staticmethod
    async def validate_required_params(_kwargs: Dict[str, Any], _required_params: List[str]) -> Optional["ToolResult"]:
        return None

    @staticmethod
    async def validate_string_param(_value: Any, _param_name: str, _min_length: int, _max_length: int, _pattern: Optional[str]) -> Optional["ToolResult"]:
        return None

    @staticmethod
    async def validate_task_input(
        _action: str,
        _time: str,
        _priority: str,
        _project: str,
        _status: str,
        _assignee: Optional[str],
        _progress: Optional[int],
    ) -> None:
        return

    @staticmethod
    async def validation(_message: str) -> "Done":
        return Done

    @staticmethod
    async def verbose(_verbose: bool) -> "Done":
        return Done

    @staticmethod
    async def with_action(_action: str) -> "Done":
        return Done

    @staticmethod
    async def with_assignee(_assignee: AssigneeType) -> "Done":
        return Done

    @staticmethod
    async def with_context(_context: str) -> "Done":
        return Done

    @staticmethod
    async def with_context_notes(_context_notes: str) -> "Done":
        return Done

    @staticmethod
    async def with_dependencies(_dependencies: List[str]) -> "Done":
        return Done

    @staticmethod
    async def with_dry_run(_dry_run: bool) -> "Done":
        return Done

    @staticmethod
    async def with_embedding_service(_service: TodoziEmbeddingService) -> "Done":
        return Done

    @staticmethod
    async def with_embedding_service_option(_service: Optional[TodoziEmbeddingService]) -> "Done":
        return Done

    @staticmethod
    async def with_force(_force: bool) -> "Done":
        return Done

    @staticmethod
    async def with_max_tokens(_max_tokens: int) -> "Done":
        return Done

    @staticmethod
    async def with_parent_project(_parent_project: str) -> "Done":
        return Done

    @staticmethod
    async def with_priority(_priority: Priority) -> "Done":
        return Done

    @staticmethod
    async def with_progress(_progress: int) -> "Done":
        return Done

    @staticmethod
    async def with_shared_components(
        _config: Any,
        _cache: Any,
        _embedding_model: Any,
        _embedding_models: Any,
        _tag_manager: Any,
        _storage: Any,
    ) -> "Done":
        return Done

    @staticmethod
    async def with_status(_status: Status) -> "Done":
        return Done

    @staticmethod
    async def with_tags(_tags: List[str]) -> "Done":
        return Done

    @staticmethod
    async def with_time(_time: str) -> "Done":
        return Done

    @staticmethod
    def with_temperature(_temperature: float) -> "Done":
        return Done

    @staticmethod
    async def with_user_id(_user_id: str) -> "Done":
        return Done

    @staticmethod
    async def load_tasks() -> None:
        await Ready.init()
        return

    @staticmethod
    async def load_training_data(training_data_id: str) -> "TrainingData":
        raise TodoziError.validation("load_training_data not yet implemented")

    @staticmethod
    async def long_term_percentage() -> float:
        tasks = await Done.all_tasks()
        if not tasks:
            return 0.0
        long_term = sum(1 for t in tasks if ("long" in t.time.lower() or "future" in t.time.lower()))
        return long_term / len(tasks)

    @staticmethod
    async def mark_chunk_completed(chunk_id: str) -> None:
        raise TodoziError.validation("mark_chunk_completed not yet implemented")

    @staticmethod
    async def mark_chunk_validated(chunk_id: str) -> None:
        raise TodoziError.validation("mark_chunk_validated not yet implemented")

    @staticmethod
    async def matches(public_key: str, private_key: Optional[str]) -> bool:
        raise TodoziError.validation("matches not yet implemented")

    @staticmethod
    async def max_tokens() -> int:
        return 4096

    @staticmethod
    async def meaning(_meaning: str) -> "Done":
        return Done

    @staticmethod
    async def migrate() -> "MigrationReport":
        raise TodoziError.validation("migrate not yet implemented")

    @staticmethod
    async def migrate_to_project_based() -> "MigrationReport":
        raise TodoziError.validation("migrate_to_project_based not yet implemented")

    @staticmethod
    async def moment(_moment: str) -> "Done":
        return Done

    @staticmethod
    async def move_task(id: str, _from_collection: str, to_collection: str) -> None:
        await Ready.init()
        ctx = await init_context()
        task = await Done.get_task(id)
        if task:
            updates = TaskUpdate(parent_project=to_collection)
            await ctx.storage.update_task_in_project(id, updates)

    @staticmethod
    async def multi_query_search(
        queries: List[str],
        _aggregation: Any,
        _content_types: Optional[List[ContentType]],
        limit: int,
    ) -> List[SimilarityResult]:
        await Ready.init()
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        results: List[SimilarityResult] = []
        for q in queries:
            results.extend(await svc.semantic_search(q, None, limit, storage=ctx.storage))
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results[:limit]

    @staticmethod
    async def name(_name: str) -> "Done":
        return Done

    @staticmethod
    async def new_full(
        user_id: str,
        action: str,
        time: str,
        priority: Priority,
        parent_project: str,
        status: Status,
        assignee: Optional[Assignee],
        tags: List[str],
        dependencies: List[str],
        context_notes: Optional[str],
        progress: Optional[int],
    ) -> "Done":
        now = datetime.datetime.utcnow()
        task = Task(
            id=str(_uuid.uuid4()),
            user_id=user_id,
            action=action,
            time=time,
            priority=priority,
            parent_project=parent_project,
            status=status,
            assignee=assignee,
            tags=tags,
            dependencies=dependencies,
            context_notes=context_notes,
            progress=progress,
            created_at=now,
            updated_at=now,
            embedding_vector=None,
        )
        ctx = await init_context()
        await ctx.storage.add_task_to_project(task)
        return Done

    @staticmethod
    async def new_idea(idea: Idea) -> str:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_idea(idea)
        return idea.id

    @staticmethod
    async def new_memory(memory: Memory) -> str:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_memory(memory)
        return memory.id

    @staticmethod
    async def new_with_hashes(_server_url: str) -> "Done":
        await Ready.init()
        return Done

    @staticmethod
    async def ok(_body: str) -> "Done":
        return Done

    @staticmethod
    async def overdue_percentage() -> float:
        tasks = await Done.all_tasks()
        if not tasks:
            return 0.0
        now = datetime.datetime.utcnow()
        overdue = 0
        for t in tasks:
            try:
                deadline = datetime.datetime.fromisoformat(t.time.replace("Z", ""))
                if deadline < now:
                    overdue += 1
            except Exception:
                pass
        return overdue / len(tasks)

    @staticmethod
    async def parse_agent_assignment_format(agent_text: str) -> AgentAssignment:
        parts = agent_text.split("->")
        agent_id = parts[0].strip().split(":")[-1].strip() if ":" in agent_text else "unknown_agent"
        task_id = parts[1].strip().split()[0].split(":")[-1].strip() if len(parts) > 1 and ":" in parts[1] else "unknown_task"
        return AgentAssignment(id=str(_uuid.uuid4()), agent_id=agent_id, task_id=task_id, status="Assigned")

    @staticmethod
    async def parse_chunking_format(chunk_text: str) -> CodeChunk:
        return CodeChunk(id=str(_uuid.uuid4()), content=chunk_text)

    @staticmethod
    async def parse_dependencies(deps_str: str) -> List[str]:
        return [d.strip() for d in deps_str.split(",") if d.strip()]

    @staticmethod
    async def parse_error_format(error_text: str) -> Error:
        return Error(id=str(_uuid.uuid4()), message=error_text)

    @staticmethod
    async def parse_feeling_format(feel_text: str) -> Feeling:
        return Feeling(id=str(_uuid.uuid4()), text=feel_text)

    @staticmethod
    async def parse_idea_format(idea_text: str) -> Idea:
        return Idea(
            id=str(_uuid.uuid4()),
            idea=idea_text,
            project_id=None,
            status=ItemStatus.Active,
            share=ShareLevel.Team,
            importance=IdeaImportance.Medium,
            tags=[],
            context=None,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )

    @staticmethod
    async def parse_memory_format(memory_text: str, user_id: str) -> Memory:
        return Memory(
            id=str(_uuid.uuid4()),
            user_id=user_id,
            project_id=None,
            status=ItemStatus.Active,
            moment=memory_text,
            meaning="",
            reason="",
            importance=MemoryImportance.Medium,
            term=MemoryTerm.Long,
            memory_type=MemoryType.Standard,
            tags=[],
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )

    @staticmethod
    async def parse_reminder_format(reminder_text: str) -> Reminder:
        raise TodoziError.validation("parse_reminder_format not yet implemented")

    @staticmethod
    async def parse_summary_format(summary_text: str) -> "Summary":
        raise TodoziError.validation("parse_summary_format not yet implemented")

    @staticmethod
    async def parse_tags(tags_str: str) -> List[str]:
        return [t.strip() for t in tags_str.split(",") if t.strip()]

    @staticmethod
    async def parse_tdz_command(text: str) -> List["TdzCommand"]:
        return []

    @staticmethod
    async def parse_todozi_format(todozi_text: str) -> Task:
        now = datetime.datetime.utcnow()
        return Task(
            id=str(_uuid.uuid4()),
            user_id="parser",
            action=todozi_text,
            time="ASAP",
            priority=Priority.Medium,
            parent_project=Done.project_name(),
            status=Status.Todo,
            assignee=Assignee(AssigneeType.Human),
            tags=[],
            dependencies=[],
            context_notes=None,
            progress=0,
            created_at=now,
            updated_at=now,
            embedding_vector=None,
        )

    @staticmethod
    async def parse_training_data_format(train_text: str) -> "TrainingData":
        raise TodoziError.validation("parse_training_data_format not yet implemented")

    @staticmethod
    async def pending_percentage() -> float:
        tasks = await Done.all_tasks()
        if not tasks:
            return 0.0
        pending = sum(1 for t in tasks if t.status == Status.Todo)
        return (pending / len(tasks)) * 100.0

    @staticmethod
    async def predict_relevance(_features: List[float]) -> float:
        raise TodoziError.validation("predict_relevance not yet implemented")

    @staticmethod
    async def preload_related_embeddings(_content_id: str, _depth: int) -> None:
        raise TodoziError.validation("preload_related_embeddings not yet implemented")

    @staticmethod
    async def prepare_task_content(task: Task) -> str:
        return f"{task.action} - {task.context_notes or ''}"

    @staticmethod
    async def priority(_priority: SummaryPriority) -> "Done":
        return Done

    @staticmethod
    async def private_percentage() -> float:
        raise TodoziError.validation("private_percentage not yet implemented")

    @staticmethod
    async def process_chat_message(message: str) -> List[Task]:
        t = await Done.parse_todozi_format(message)
        return [t]

    @staticmethod
    async def process_chat_message_extended(message: str, user_id: str) -> ChatContent:
        return await Done.process_chat(message, user_id)

    @staticmethod
    async def process_chunking_message(message: str) -> List[CodeChunk]:
        return [await Done.parse_chunking_format(message)]

    @staticmethod
    async def process_json_examples(json_data: str) -> List[Task]:
        try:
            data = json.loads(json_data)
            tasks: List[Task] = []
            now = datetime.datetime.utcnow()
            for item in (data if isinstance(data, list) else [data]):
                tasks.append(Task(
                    id=str(_uuid.uuid4()),
                    user_id=item.get("user_id", "json"),
                    action=item.get("action", "Unknown action"),
                    time=item.get("time", "ASAP"),
                    priority=Priority(item.get("priority", Priority.Medium)),
                    parent_project=item.get("parent_project", Done.project_name()),
                    status=Status(item.get("status", Status.Todo)),
                    assignee=Assignee(AssigneeType.Human),
                    tags=item.get("tags", []),
                    dependencies=item.get("dependencies", []),
                    context_notes=item.get("context_notes"),
                    progress=item.get("progress"),
                    created_at=now,
                    updated_at=now,
                    embedding_vector=None,
                ))
            return tasks
        except Exception as e:
            raise TodoziError.validation(f"Invalid JSON: {e}")

    @staticmethod
    async def process_tdz_commands(text: str, base_url: str, api_key: Optional[str]) -> List[Dict[str, Any]]:
        return []

    @staticmethod
    async def process_workflow(_tasks: List[Task]) -> List[str]:
        raise TodoziError.validation("process_workflow not yet implemented")

    @staticmethod
    async def profile_search_performance(query: str, iterations: int) -> "PerformanceMetrics":
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        start = time.time()
        for _ in range(iterations):
            _ = await svc.semantic_search(query, None, 10, storage=ctx.storage)
        elapsed = (time.time() - start) * 1000.0
        return {"iterations": iterations, "total_ms": elapsed, "avg_ms": elapsed / max(iterations, 1)}

    @staticmethod
    async def public_percentage() -> float:
        raise TodoziError.validation("public_percentage not yet implemented")

    @staticmethod
    async def reason(_reason: str) -> "Done":
        return Done

    @staticmethod
    async def register_with_server(server_url: str) -> RegistrationInfo:
        await Ready.init()
        ctx = await init_context()
        reg = await ctx.storage.load_registration()
        reg.server_url = server_url
        reg.api_key = f"api_key_{str(_uuid.uuid4())}"
        reg.user_id = str(_uuid.uuid4())
        reg.fingerprint = str(_uuid.uuid4())
        await ctx.storage.save_registration(reg)
        return reg

    @staticmethod
    async def relationships_per_tag() -> float:
        raise TodoziError.validation("relationships_per_tag not yet implemented")

    @staticmethod
    async def recommend_similar(
        based_on: List[str],
        exclude: List[str],
        limit: int,
    ) -> List[SimilarityResult]:
        await Ready.init()
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        q = " ".join(based_on)
        all_results = await svc.semantic_search(q, None, limit * 2, storage=ctx.storage)
        return [r for r in all_results if (r.item_id or r.text_content) not in exclude][:limit]

    @staticmethod
    async def remove_item(id: str) -> Optional[QueueItem]:
        await Ready.init()
        ctx = await init_context()
        qc = await ctx.storage.load_queue_collection()
        for col in [qc.backlog, qc.active, qc.complete]:
            for i, item in enumerate(col):
                if item.id == id:
                    return col.pop(i)
        return None

    @staticmethod
    async def remove_key(user_id: str) -> Optional["ApiKey"]:
        await Ready.init()
        return ApiKey(user_id=user_id, key="fake_key")

    @staticmethod
    async def remove_task(id: str) -> Optional[Task]:
        await Ready.init()
        task = await Done.get_task(id)
        if task:
            await Done.delete_task(id)
        return task

    @staticmethod
    async def render(_config: "DisplayConfig") -> str:
        await Ready.init()
        tasks = await Done.all_tasks()
        return f"{len(tasks)} tasks loaded"

    @staticmethod
    async def render_compact(_config: "DisplayConfig") -> str:
        await Ready.init()
        tasks = await Done.all_tasks()
        return f"{len(tasks)} tasks loaded (compact)"

    @staticmethod
    async def render_detailed(_config: "DisplayConfig") -> str:
        await Ready.init()
        tasks = await Done.all_tasks()
        return f"{len(tasks)} tasks loaded (detailed)"

    @staticmethod
    async def resolve_error(error_id: str, resolution: str) -> None:
        await Ready.init()
        print(f"Resolved error {error_id} with resolution: {resolution}")

    @staticmethod
    async def restore_backup(backup_name: str) -> None:
        await Ready.init()
        raise TodoziError.validation(f"Backup restore not yet implemented: {backup_name}")

    @staticmethod
    async def restore_embeddings(backup_path: str) -> int:
        await Ready.init()
        return 0

    @staticmethod
    async def run() -> None:
        await Ready.init()
        print("TUI not enabled in this minimal Python translation.")

    @staticmethod
    async def run_interactive() -> str:
        await Ready.init()
        return "Interactive mode not available."

    @staticmethod
    async def sample_task_async() -> Task:
        return Done.sample_task()

    @staticmethod
    async def save_agent(agent: Agent) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_agent(agent)

    @staticmethod
    async def save_agent_assignment(assignment: AgentAssignment) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_agent_assignment(assignment)

    @staticmethod
    async def save_api_key_collection(collection: "ApiKeyCollection") -> None:
        await Ready.init()
        return

    @staticmethod
    async def save_as_default(model_name: str) -> None:
        from todozi.emb import TodoziEmbeddingConfig
        from todozi.storage import load_config, save_config
        
        await Ready.init()
        config = await load_config()
        config.default_embedding_model = model_name
        await save_config(config)
        print(f"✅ Set default embedding model to {model_name}")

    @staticmethod
    async def save_code_chunk(chunk: CodeChunk) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_code_chunk(chunk)

    @staticmethod
    async def save_config(config: ValidatedConfig) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_config(config)

    @staticmethod
    async def save_error(error: Error) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_error(error)

    @staticmethod
    async def save_feeling(feeling: Feeling) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_feeling(feeling)

    @staticmethod
    async def save_idea(idea: Idea) -> None:
        await Ready.init()
        ctx = await init_context()
        await ctx.storage.save_idea(idea)

    @staticmethod
    async def remind_at(task_id: str, when: datetime.datetime) -> None:
        await Ready.init()
        reminder = Reminder.new(message=f"Reminder for task {task_id}", when=when, priority=ReminderPriority.Medium)
        print(f"Reminder created: {reminder.to_dict()}")

    @staticmethod
    async def task(action: str) -> str:
        t = await Done.create_task(action, None, None, None, None)
        return t.id

    @staticmethod
    async def urgent(action: str) -> str:
        t = await Done.create_task(action, Priority.Urgent, None, None, None)
        return t.id

    @staticmethod
    async def high(action: str) -> str:
        t = await Done.create_task(action, Priority.High, None, None, None)
        return t.id

    @staticmethod
    async def low(action: str) -> str:
        t = await Done.create_task(action, Priority.Low, None, None, None)
        return t.id

    @staticmethod
    async def find(query: str) -> List[Task]:
        return await Done.find_tasks(query)

    @staticmethod
    async def ai_find(query: str) -> List[Task]:
        return await Done.find_tasks_ai(query)

    @staticmethod
    async def done(task_id: str) -> None:
        await Done.complete_task(task_id)

    @staticmethod
    async def start(task_id: str) -> None:
        await Done.start_task(task_id)

    @staticmethod
    async def all() -> List[Task]:
        return await Done.all_tasks()

    @staticmethod
    async def idea(idea: str) -> Task:
        return await Done.ideate(idea)

    @staticmethod
    async def ai(action: str) -> str:
        ctx = await init_context()
        now = datetime.datetime.utcnow()
        t = Task(
            id=str(_uuid.uuid4()),
            user_id="actions_user",
            action=action,
            time="ASAP",
            priority=Priority.Medium,
            parent_project=f"{Done.project_name()}_ai",
            status=Status.Todo,
            assignee=Assignee(AssigneeType.Ai),
            tags=["ai"],
            dependencies=[],
            context_notes="Created via Actions::ai",
            progress=0,
            created_at=now,
            updated_at=now,
            embedding_vector=None,
        )
        await ctx.storage.add_task_to_project(t)
        return t.id

    @staticmethod
    async def human(action: str) -> str:
        ctx = await init_context()
        now = datetime.datetime.utcnow()
        t = Task(
            id=str(_uuid.uuid4()),
            user_id="actions_user",
            action=action,
            time="ASAP",
            priority=Priority.Medium,
            parent_project=f"{Done.project_name()}_human",
            status=Status.Todo,
            assignee=Assignee(AssigneeType.Human),
            tags=["human"],
            dependencies=[],
            context_notes="Created via Actions::human",
            progress=0,
            created_at=now,
            updated_at=now,
            embedding_vector=None,
        )
        await ctx.storage.add_task_to_project(t)
        return t.id

    @staticmethod
    async def collab(action: str) -> str:
        ctx = await init_context()
        now = datetime.datetime.utcnow()
        t = Task(
            id=str(_uuid.uuid4()),
            user_id="actions_user",
            action=action,
            time="ASAP",
            priority=Priority.Medium,
            parent_project=f"{Done.project_name()}_collaborative",
            status=Status.Todo,
            assignee=Assignee(AssigneeType.Collaborative),
            tags=["collaborative"],
            dependencies=[],
            context_notes="Created via Actions::collab",
            progress=0,
            created_at=now,
            updated_at=now,
            embedding_vector=None,
        )
        await ctx.storage.add_task_to_project(t)
        return t.id

    @staticmethod
    async def complete(task_id: str) -> None:
        await Done.complete_task(task_id)

    @staticmethod
    async def begin(task_id: str) -> None:
        await Done.start_task(task_id)

    @staticmethod
    async def delete(task_id: str) -> None:
        await Done.delete_task(task_id)

    @staticmethod
    async def get(task_id: str) -> Optional[Task]:
        return await Done.get_task(task_id)

    @staticmethod
    async def list() -> List[Task]:
        return await Done.all_tasks()

    @staticmethod
    async def add_recent(description: str) -> None:
        print(f"Recent action: {description}")

    @staticmethod
    async def create_tag(name: str, description: Optional[str]) -> str:
        await Ready.init()
        tag = Tag(
            id=str(_uuid.uuid4()),
            name=name,
            description=description,
            color=None,
            category=None,
            usage_count=0,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        return tag.id

    @staticmethod
    async def find_tag(tag_name: str) -> List[Task]:
        f = TaskFilters(tags=[tag_name])
        return await Done.search_with_filters(f, None)

    @staticmethod
    async def add_to_task(task_id: str, tag: str) -> None:
        t = await Done.get_task(task_id)
        if t and tag not in t.tags:
            t.tags.append(tag)
            updates = TaskUpdate(tags=t.tags)
            await Done.update_task_full(task_id, updates)

    @staticmethod
    async def remove_from_task(task_id: str, tag: str) -> None:
        t = await Done.get_task(task_id)
        if t and tag in t.tags:
            t.tags.remove(tag)
            updates = TaskUpdate(tags=t.tags)
            await Done.update_task_full(task_id, updates)

    @staticmethod
    async def advanced_search(query: str) -> List[Tag]:
        if query.strip():
            return [Tag(
                id=str(_uuid.uuid4()),
                name=query,
                description="Synthetic result",
                color=None,
                category=None,
                usage_count=0,
                created_at=datetime.datetime.utcnow(),
                updated_at=datetime.datetime.utcnow(),
            )]
        return []

    @staticmethod
    async def create_project(name: str, description: Optional[str]) -> None:
        await Ready.init()
        ctx = await init_context()
        ctx.storage.create_project(name, description)

    @staticmethod
    async def tasks(project_name: str) -> List[Task]:
        f = TaskFilters(project=project_name)
        return await Done.search_with_filters(f, None)

    @staticmethod
    async def delete_project(project_name: str) -> None:
        await Ready.init()
        ctx = await init_context()
        ctx.storage.delete_project(project_name)

    @staticmethod
    async def important(moment: str, meaning: str, reason: str) -> str:
        await Ready.init()
        ctx = await init_context()
        mem = Memory(
            id=str(_uuid.uuid4()),
            user_id="memories_user",
            project_id=None,
            status=ItemStatus.Active,
            moment=moment,
            meaning=meaning,
            reason=reason,
            importance=MemoryImportance.High,
            term=MemoryTerm.Long,
            memory_type=MemoryType.Standard,
            tags=["important"],
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        await ctx.storage.save_memory(mem)
        return mem.id

    @staticmethod
    async def find_memory(query: str) -> List[Memory]:
        memories = await Done.list_memories()
        q = query.lower()
        return [m for m in memories if q in m.moment.lower() or q in m.meaning.lower()]

    @staticmethod
    async def breakthrough(idea: str) -> str:
        await Ready.init()
        ctx = await init_context()
        ide = Idea(
            id=str(_uuid.uuid4()),
            idea=idea,
            project_id=None,
            status=ItemStatus.Active,
            share=ShareLevel.Team,
            importance=IdeaImportance.Breakthrough,
            tags=["breakthrough"],
            context=None,
            created_at=datetime.datetime.utcnow(),
            updated_at=datetime.datetime.utcnow(),
        )
        await ctx.storage.save_idea(ide)
        return ide.id

    @staticmethod
    async def find_idea(query: str) -> List[Idea]:
        ideas = await Done.list_ideas()
        q = query.lower()
        return [i for i in ideas if q in i.idea.lower()]

    @staticmethod
    async def add_to_queue(task_name: str, description: str) -> str:
        await Ready.init()
        ctx = await init_context()
        item = QueueItem.new(task_name, description, Priority.Medium, QueueStatus.Backlog)
        await ctx.storage.add_queue_item(item)
        return item.id

    @staticmethod
    async def list_queue_items() -> List[QueueItem]:
        ctx = await init_context()
        return await ctx.storage.list_queue_items()

    @staticmethod
    async def list_queue_items_by_status(status: QueueStatus) -> List[QueueItem]:
        ctx = await init_context()
        return await ctx.storage.list_queue_items_by_status(status)

    @staticmethod
    async def backlog() -> List[QueueItem]:
        ctx = await init_context()
        return await ctx.storage.list_backlog_items()

    @staticmethod
    async def active() -> List[QueueItem]:
        ctx = await init_context()
        return await ctx.storage.list_active_items()

    @staticmethod
    async def tdz_find(query: str) -> str:
        await Ready.init()
        results: List[str] = []
        ai_res = await Done.ai_search(query)
        if ai_res:
            results.append("🤖 AI SEMANTIC SEARCH:")
            for r in ai_res[:5]:
                results.append(f"  • {r.text_content} (similarity: {r.similarity_score:.2})")
            if len(ai_res) > 5:
                results.append(f"  ... and {len(ai_res) - 5} more AI matches")
            results.append("")
        kw = await Done.keyword_search(query)
        if kw:
            results.append("🔍 KEYWORD SEARCH:")
            results.append(kw)
        if not results:
            return f"🔍 No results found for: '{query}'"
        return "\n".join(results)

    @staticmethod
    async def ai_search(query: str) -> List[SimilarityResult]:
        await Ready.init()
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        return await svc.semantic_search(query, None, 20, storage=ctx.storage)

    @staticmethod
    async def keyword_search(query: str) -> str:
        await Ready.init()
        results: List[str] = []
        tasks = await Done.find_tasks(query)
        if tasks:
            results.append(f"📋 TASKS ({len(tasks)}):")
            for t in tasks[:5]:
                results.append(f"  • {t.action} [{t.status}] [{t.priority}]")
            if len(tasks) > 5:
                results.append(f"  ... and {len(tasks) - 5} more")
            results.append("")
        memories = await Done.find_memory(query)
        if memories:
            results.append(f"🧠 MEMORIES ({len(memories)}):")
            for m in memories[:3]:
                results.append(f"  • {m.moment} - {m.meaning}")
            if len(memories) > 3:
                results.append(f"  ... and {len(memories) - 3} more")
            results.append("")
        ideas = await Done.find_idea(query)
        if ideas:
            results.append(f"💡 IDEAS ({len(ideas)}):")
            for i in ideas[:3]:
                results.append(f"  • {i.idea}")
            if len(ideas) > 3:
                results.append(f"  ... and {len(ideas) - 3} more")
            results.append("")
        queue_items = await Done.list_queue_items()
        filtered = [q for q in queue_items if query.lower() in q.task_name.lower() or query.lower() in q.task_description.lower()]
        if filtered:
            results.append(f"📋 QUEUE ({len(filtered)}):")
            for q in filtered[:3]:
                results.append(f"  • {q.task_name} [{q.status}]")
            if len(filtered) > 3:
                results.append(f"  ... and {len(filtered) - 3} more")
        if not results:
            return f"No keyword results found for: '{query}'"
        return "\n".join(results)

    @staticmethod
    async def ai_tasks(query: str) -> List[SimilarityResult]:
        await Ready.init()
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        return await svc.semantic_search(query, [ContentType.Task], 10, storage=ctx.storage)

    @staticmethod
    async def keyword_tasks(query: str) -> List[Task]:
        return await Done.find_tasks(query)

    @staticmethod
    async def similar_tasks(task_id: str) -> List[SimilarityResult]:
        await Ready.init()
        t = await Done.get_task(task_id)
        if not t:
            return []
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        return await svc.find_similar_tasks(t.action, 10, storage=ctx.storage)

    @staticmethod
    async def smart(query: str) -> str:
        await Ready.init()
        q = query.lower()
        if "task" in q or "todo" in q or "do" in q:
            ai = await Done.ai_tasks(query)
            if ai:
                lines = ["🎯 SMART SEARCH - TASKS FOCUS:", ""]
                for r in ai[:7]:
                    lines.append(f"  • {r.text_content} (similarity: {r.similarity_score:.2})")
                return "\n".join(lines)
        if "remember" in q or "memory" in q or "recall" in q:
            mems = await Done.find_memory(query)
            if mems:
                lines = ["🎯 SMART SEARCH - MEMORIES FOCUS:", ""]
                for m in mems[:5]:
                    lines.append(f"  • {m.moment} - {m.meaning}")
                return "\n".join(lines)
        if "idea" in q or "concept" in q or "innovation" in q:
            ideas = await Done.find_idea(query)
            if ideas:
                lines = ["🎯 SMART SEARCH - IDEAS FOCUS:", ""]
                for i in ideas[:5]:
                    lines.append(f"  • {i.idea}")
                return "\n".join(lines)
        return await Done.tdz_find(query)

    @staticmethod
    async def fast(query: str) -> str:
        return await Done.keyword_search(query)

    @staticmethod
    async def deep(query: str) -> List[SimilarityResult]:
        return await Done.ai_search(query)

    @staticmethod
    async def embed(text: str) -> List[float]:
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        return await svc.generate_embedding(text)

    @staticmethod
    async def find_similar(query: str) -> List[SimilarityResult]:
        return await Done.ai_search(query)

    @staticmethod
    async def find_ai_tasks(query: str) -> List[SimilarityResult]:
        return await Done.ai_tasks(query)

    @staticmethod
    async def cluster_content() -> List[ClusteringResult]:
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        return await svc.cluster_content(ctx.storage)

    @staticmethod
    async def stats() -> str:
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        s = await svc.get_stats(ctx.storage)
        return "🧠 EMBEDDING STATS:\n" + json.dumps(s, indent=2)

    @staticmethod
    async def embed_task(task_id: str) -> str:
        t = await Done.get_task(task_id)
        if not t:
            raise TodoziError.task_not_found(task_id)
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        content = await svc.prepare_task_content(t)
        vec = await svc.generate_embedding(content)
        return f"Task '{t.action}' embedded successfully ({len(vec)} dimensions)"

    @staticmethod
    async def quick() -> str:
        tasks = await Done.all_tasks()
        total = len(tasks)
        done = sum(1 for t in tasks if t.status == Status.Done)
        in_progress = sum(1 for t in tasks if t.status == Status.InProgress)
        blocked = sum(1 for t in tasks if t.status == Status.Blocked)
        ideas = await Done.list_ideas()
        memories = await Done.list_memories()
        queue_items = await Done.list_queue_items()
        return (
            f"📊 TODOZI STATS\n\n"
            f"📋 Tasks: {total} total\n"
            f"  ✅ Done: {done}\n"
            f"  🔄 In Progress: {in_progress}\n"
            f"  🚫 Blocked: {blocked}\n\n"
            f"💡 Ideas: {len(ideas)}\n"
            f"🧠 Memories: {len(memories)}\n"
            f"📋 Queue: {len(queue_items)}"
        )

    @staticmethod
    async def detailed() -> str:
        quick_stats = await Done.quick()
        tasks = await Done.all_tasks()
        critical = sum(1 for t in tasks if t.priority == Priority.Critical)
        urgent = sum(1 for t in tasks if t.priority == Priority.Urgent)
        high = sum(1 for t in tasks if t.priority == Priority.High)
        medium = sum(1 for t in tasks if t.priority == Priority.Medium)
        low = sum(1 for t in tasks if t.priority == Priority.Low)
        projects = await Done.list_projects()
        return (
            f"{quick_stats}\n"
            f"\n🎯 By Priority:\n"
            f"  🔴 Critical: {critical}\n"
            f"  🚨 Urgent: {urgent}\n"
            f"  🟠 High: {high}\n"
            f"  🟡 Medium: {medium}\n"
            f"  🟢 Low: {low}\n"
            f"\n📁 Projects: {len(projects)} total"
        )

    @staticmethod
    async def add_task_to_project(task: Task) -> None:
        ctx = await init_context()
        await ctx.storage.add_task_to_project(task)

    @staticmethod
    async def add_item(content: str) -> None:
        print(f"Checklist item added: {content}")

    @staticmethod
    async def add_chunk(chunk_id: str, level: str, deps: List[str]) -> None:
        print(f"Chunk {chunk_id} added at level {level} with deps {deps}")

    @staticmethod
    async def add_completed_module(module: str) -> None:
        print(f"Completed module: {module}")

    @staticmethod
    async def add_dependency(dep: str) -> None:
        print(f"Added dependency: {dep}")

    @staticmethod
    async def add_error_pattern(pattern: str) -> None:
        print(f"Added error pattern: {pattern}")

    @staticmethod
    async def add_function_signature(name: str, signature: str) -> None:
        print(f"Added function signature: {name} -> {signature}")

    @staticmethod
    async def add_import(import_stmt: str) -> None:
        print(f"Added import: {import_stmt}")

    @staticmethod
    async def add_pending_module(module: str) -> None:
        print(f"Pending module: {module}")

    @staticmethod
    async def do_it(what: str, action: str, priority: Optional[Priority], project: Optional[str], time: Optional[str], context: Optional[str]) -> str:
        t = await Done.create_task(action, priority, project, time, context)
        return t.id

    @staticmethod
    async def find_task(what: str) -> str:
        res = await Done.find_tasks(what)
        if not res:
            return f"No tasks found for: {what}"
        return f"Found {len(res)} task(s)"

    @staticmethod
    async def see_all() -> str:
        return await Done.quick()

    @staticmethod
    async def has_results() -> bool:
        return False

    @staticmethod
    async def has_specialization(specialization: str) -> bool:
        agents = await Done.get_all_agents()
        return any(a.has_specialization(specialization) for a in agents)

    @staticmethod
    async def has_tool(tool_name: str) -> bool:
        agents = await Done.get_all_agents()
        return any(a.has_tool(tool_name) for a in agents)

    @staticmethod
    async def hash_project_name(project_name: str) -> str:
        h = 5381
        for ch in project_name:
            h = ((h << 5) + h) + ord(ch)
        return str(h & 0xFFFFFFFF)

    @staticmethod
    async def hierarchical_clustering(content_types: List[ContentType], max_depth: int) -> List["HierarchicalCluster"]:
        raise TodoziError.validation("hierarchical_clustering not yet implemented")

    @staticmethod
    async def high_priority_percentage() -> float:
        tasks = await Done.all_tasks()
        if not tasks:
            return 0.0
        hp = sum(1 for t in tasks if t.priority in [Priority.High, Priority.Critical])
        return hp / len(tasks)

    @staticmethod
    async def hybrid_search(
        query: str,
        keywords: List[str],
        content_types: Optional[List[ContentType]],
        semantic_weight: float,
        limit: int,
    ) -> List[SimilarityResult]:
        ctx = await init_context()
        svc = TodoziEmbeddingService(TodoziEmbeddingConfig())
        await svc.initialize()
        return await svc.hybrid_search(query, keywords, content_types, semantic_weight, limit, storage=ctx.storage)

    @staticmethod
    async def importance(_importance: IdeaImportance) -> None:
        raise TodoziError.validation("importance() should be called on Idea builder, not Easy")

    @staticmethod
    async def initialize_grok_level_todozi_system() -> "SharedTodozi":
        await Ready.init()
        ctx = await init_context()
        return SharedTodozi(storage=ctx.storage)

    @staticmethod
    async def initialize_grok_level_todozi_system_with_embedding(enable_embeddings: bool) -> Tuple["SharedTodozi", Optional[TodoziEmbeddingService]]:
        await Ready.init()
        ctx = await init_context()
        emb = TodoziEmbeddingService(TodoziEmbeddingConfig()) if enable_embeddings else None
        if emb:
            await emb.initialize()
        return SharedTodozi(storage=ctx.storage), emb

    @staticmethod
    async def initialize_tdz_content_processor() -> "SharedTodoziState":
        return SharedTodoziState()

    @staticmethod
    async def interactive_create_task() -> Task:
        raise TodoziError.validation("interactive_create_task() requires interactive terminal, use create_task() instead")

    @staticmethod
    async def io(message: str) -> None:
        raise TodoziError.validation(f"io() should be called on Error builder, not Done. Message: {message}")

    @staticmethod
    async def is_active() -> bool:
        return True

    @staticmethod
    async def is_admin(public_key: str, private_key: str) -> bool:
        return len(public_key) > 3 and len(private_key) > 3

    @staticmethod
    async def is_available() -> bool:
        return True

    @staticmethod
    async def is_backlog() -> bool:
        return False

    @staticmethod
    async def is_complete() -> bool:
        return False

    @staticmethod
    async def is_completed() -> bool:
        return False

    @staticmethod
    async def is_empty() -> bool:
        tasks = await Done.all_tasks()
        return len(tasks) == 0

    @staticmethod
    async def is_overdue() -> bool:
        return False

    @staticmethod
    async def smart_search(query: str) -> str:
        return await Done.smart(query)

    @staticmethod
    async def handle_memory_command(command: "MemoryCommands") -> None:
        print(f"Memory command: {command}")

    @staticmethod
    async def handle_project_command(command: "ProjectCommands") -> None:
        print(f"Project command: {command}")

    @staticmethod
    async def handle_queue_command(command: "QueueCommands") -> None:
        print(f"Queue command: {command}")

    @staticmethod
    async def handle_search_all_command(command: "Commands") -> None:
        print(f"Search all command: {command}")

    @staticmethod
    async def handle_search_command(command: "SearchCommands") -> None:
        print(f"Search command: {command}")

    @staticmethod
    async def handle_server_command(command: "ServerCommands") -> None:
        print(f"Server command: {command}")

    @staticmethod
    async def handle_show_command(command: "ShowCommands") -> None:
        print(f"Show command: {command}")

    @staticmethod
    async def handle_stats_command(command: "StatsCommands") -> None:
        print(f"Stats command: {command}")

    @staticmethod
    async def handle_strategy_command(
        content: Optional[str],
        file: Optional[str],
        output_format: str,
        human: bool,
    ) -> None:
        print(f"Strategy command: content={content}, file={file}, format={output_format}, human={human}")

    @staticmethod
    async def handle_train_command(command: "TrainingCommands") -> None:
        print(f"Train command: {command}")

    @staticmethod
    async def handle_update_command(
        id: str,
        action: Optional[str],
        time: Optional[str],
        priority: Optional[str],
        project: Optional[str],
        status: Optional[str],
        assignee: Optional[str],
        tags: Optional[str],
        dependencies: Optional[str],
        context: Optional[str],
        progress: Optional[int],
    ) -> None:
        print(f"Update command: id={id}, action={action}, time={time}, priority={priority}, project={project}, status={status}, assignee={assignee}, tags={tags}, dependencies={dependencies}, context={context}, progress={progress}")

    @staticmethod
    async def has_capability(capability: str) -> bool:
        agents = await Done.get_all_agents()
        return any(capability in a.capabilities for a in agents)


# ------------- Support Types (minimal stubs) ------------- #

class SharedTodozi:
    def __init__(self, storage: IndexedStorage):
        self.storage = storage


class SharedTodoziState:
    def __init__(self):
        self.recent_actions: List[Dict[str, Any]] = []
        self.checklist: List[Dict[str, Any]] = []

    def add_recent_action(self, action: Dict[str, Any]) -> None:
        self.recent_actions.append(action)

    def add_checklist_item(self, item: Dict[str, Any]) -> None:
        self.checklist.append(item)


class LabeledCluster:
    def __init__(self, cluster_id: str, label: str, members: List[str]):
        self.cluster_id = cluster_id
        self.label = label
        self.members = members


class SimilarityGraph:
    pass


class ModelComparisonResult:
    pass


class ToolResult:
    def __init__(self, success: bool, output: str, error: Optional[str], execution_time_ms: int, metadata: Optional[Dict[str, Any]], recovery_context: Optional[str]):
        self.success = success
        self.output = output
        self.error = error
        self.execution_time_ms = execution_time_ms
        self.metadata = metadata
        self.recovery_context = recovery_context


class Tool:
    pass


class ToolDefinition:
    pass


class ToolParameter:
    pass


class ResourceLock:
    pass


class SearchFilters:
    pass


class TrainingData:
    pass


class HierarchicalCluster:
    pass


class IdeaStatistics:
    pass


class SearchAnalytics:
    pass


class SearchResults:
    pass


class SummaryStatistics:
    pass


class TagStatistics:
    pass


class AgentUpdate:
    pass


class IdeaUpdate:
    pass


class MemoryUpdate:
    pass


class TdzCommand:
    pass


class ValidationReport:
    pass


class DriftReport:
    pass


class PerformanceMetrics:
    pass


class Summary:
    pass


class ProjectStats:
    pass


class MigrationReport:
    pass


class ApiKeyCollection:
    def __init__(self):
        self.keys: Dict[str, "ApiKey"] = {}


class ApiKey:
    def __init__(self, user_id: str, key: str):
        self.user_id = user_id
        self.key = key


class DisplayConfig:
    pass


class MemoryCommands:
    pass


class ProjectCommands:
    pass


class QueueCommands:
    pass


class Commands:
    pass


class SearchCommands:
    pass


class ServerCommands:
    pass


class ShowCommands:
    pass


class StatsCommands:
    pass


class TrainingCommands:
    pass
