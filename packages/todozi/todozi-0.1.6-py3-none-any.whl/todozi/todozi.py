# Fix imports when running directly or when package isn't properly set up
import sys
from pathlib import Path
_todozi_file = Path(__file__)
if _todozi_file.exists():
    parent_dir = _todozi_file.parent.parent
    if str(parent_dir) not in sys.path:
        sys.path.insert(0, str(parent_dir))

import re
import uuid
import json
import copy
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import List, Optional, Dict, Any, Tuple, Union
try:
    from .models import Ok
except ImportError:
    try:
        from todozi.models import Ok
    except ImportError:
        # Last resort: try importing models directly if we're in the same directory
        import importlib.util
        models_path = _todozi_file.parent / "models.py"
        if models_path.exists():
            spec = importlib.util.spec_from_file_location("models", models_path)
            if spec and spec.loader:
                models_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(models_module)
                Ok = models_module.Ok
        else:
            raise ImportError("Cannot import Ok from todozi.models")


# ========== Configuration / Constants ==========

def get_emotion_list() -> List[str]:
    return [
        "happy", "sad", "angry", "fearful", "surprised", "disgusted", "excited",
        "anxious", "confident", "frustrated", "motivated", "overwhelmed", "curious",
        "satisfied", "disappointed", "grateful", "proud", "ashamed", "hopeful",
        "resigned",
    ]


def validation_error(message: str) -> "ValidationError":
    return ValidationError(message)


# ========== Pattern Cache (compiled regex once) ==========

class PatternCache:
    _patterns: Dict[str, re.Pattern] = {}

    @classmethod
    def get(cls, pattern: str, flags: int = 0) -> re.Pattern:
        key = f"{pattern}|{flags}"
        if key not in cls._patterns:
            cls._patterns[key] = re.compile(pattern, flags)
        return cls._patterns[key]


# ========== Enums and Parsing ==========

class Priority(Enum):
    Low = auto()
    Medium = auto()
    High = auto()
    Critical = auto()

    @staticmethod
    def _str_to_enum() -> Dict[str, "Priority"]:
        return {
            "low": Priority.Low,
            "medium": Priority.Medium,
            "high": Priority.High,
            "critical": Priority.Critical,
        }

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, value: str) -> "Priority":
        v = value.strip().lower()
        mapping = cls._str_to_enum()
        if v not in mapping:
            raise ValueError(f"Invalid priority: {value}")
        return mapping[v]


class Status(Enum):
    Todo = auto()
    InProgress = auto()
    Done = auto()
    Blocked = auto()
    Deferred = auto()

    def __str__(self) -> str:
        return self.name

    @classmethod
    def from_str(cls, value: str) -> "Status":
        v = value.strip().lower()
        mapping = {
            "todo": Status.Todo,
            "inprogress": Status.InProgress,
            "in progress": Status.InProgress,
            "done": Status.Done,
            "blocked": Status.Blocked,
            "deferred": Status.Deferred,
        }
        if v not in mapping:
            raise ValueError(f"Invalid status: {value}")
        return mapping[v]


class AssigneeType(Enum):
    Ai = auto()
    Human = auto()
    Collaborative = auto()
    Agent = auto()


@dataclass
class Assignee:
    kind: AssigneeType
    name: Optional[str] = None  # only used for Agent

    @staticmethod
    def ai() -> "Assignee":
        return Assignee(AssigneeType.Ai)

    @staticmethod
    def human() -> "Assignee":
        return Assignee(AssigneeType.Human)

    @staticmethod
    def collaborative() -> "Assignee":
        return Assignee(AssigneeType.Collaborative)

    @staticmethod
    def agent(agent_name: str) -> "Assignee":
        return Assignee(AssigneeType.Agent, agent_name)

    @staticmethod
    def parse(value: str) -> "Assignee":
        v = value.strip().lower()
        if v == "ai":
            return Assignee.ai()
        if v in ("human", "assignee=human"):
            return Assignee.human()
        if v in ("collaborative", "collab"):
            return Assignee.collaborative()
        if v.startswith("agent=") or v.startswith("assignee=agent="):
            name = v.split("=", 1)[1].strip()
            return Assignee.agent(name)
        # default fallback
        return Assignee.human()

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Assignee):
            return False
        return self.kind == other.kind and self.name == other.name

    def __repr__(self) -> str:
        if self.kind == AssigneeType.Agent:
            return f"Assignee.agent({self.name!r})"
        return f"Assignee.{self.kind.name}()"


class MemoryImportance(Enum):
    Low = auto()
    Medium = auto()
    High = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def parse(value: str) -> "MemoryImportance":
        v = value.strip().lower()
        mapping = {
            "low": MemoryImportance.Low,
            "medium": MemoryImportance.Medium,
            "high": MemoryImportance.High,
        }
        if v not in mapping:
            raise ValueError(f"Invalid memory importance: {value}")
        return mapping[v]

    @classmethod
    def from_str(cls, value: str) -> "MemoryImportance":
        return cls.parse(value)


class MemoryTerm(Enum):
    Short = auto()
    Long = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def parse(value: str) -> "MemoryTerm":
        v = value.strip().lower()
        if v == "short":
            return MemoryTerm.Short
        if v == "long":
            return MemoryTerm.Long
        raise ValueError(f"Invalid memory term: {value}")

    @classmethod
    def from_str(cls, value: str) -> "MemoryTerm":
        return cls.parse(value)


class MemoryType(Enum):
    Standard = auto()
    Secret = auto()
    Human = auto()
    Short = auto()
    Long = auto()
    Emotional = auto()  # for emotions, value is stored separately in Memory.emotion

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def parse(value: str) -> "MemoryType":
        v = value.strip().lower()
        mapping = {
            "standard": MemoryType.Standard,
            "secret": MemoryType.Secret,
            "human": MemoryType.Human,
            "short": MemoryType.Short,
            "long": MemoryType.Long,
        }
        return mapping.get(v) or MemoryType.Standard

    @classmethod
    def from_str(cls, value: str) -> "MemoryType":
        return cls.parse(value)


class ItemStatus(Enum):
    Active = auto()
    Archived = auto()

    def __str__(self) -> str:
        return self.name


class ShareLevel(Enum):
    Private = auto()
    Public = auto()
    Team = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def parse(value: str) -> "ShareLevel":
        v = value.strip().lower()
        if v in ("public", "share"):
            return ShareLevel.Public
        if v in ("private", "dont share", "don't share"):
            return ShareLevel.Private
        if v == "team":
            return ShareLevel.Team
        raise ValueError(f"Invalid share level: {value}")

    @classmethod
    def from_str(cls, value: str) -> "ShareLevel":
        return cls.parse(value)


class IdeaImportance(Enum):
    Low = auto()
    Medium = auto()
    High = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def parse(value: str) -> "IdeaImportance":
        v = value.strip().lower()
        mapping = {
            "low": IdeaImportance.Low,
            "medium": IdeaImportance.Medium,
            "high": IdeaImportance.High,
        }
        if v not in mapping:
            raise ValueError(f"Invalid idea importance: {value}")
        return mapping[v]

    @classmethod
    def from_str(cls, value: str) -> "IdeaImportance":
        return cls.parse(value)


class ErrorSeverity(Enum):
    Low = auto()
    Medium = auto()
    High = auto()
    Critical = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def parse(value: str) -> "ErrorSeverity":
        v = value.strip().lower()
        mapping = {
            "low": ErrorSeverity.Low,
            "medium": ErrorSeverity.Medium,
            "high": ErrorSeverity.High,
            "critical": ErrorSeverity.Critical,
        }
        if v not in mapping:
            raise ValueError(f"Invalid error severity: {value}")
        return mapping[v]

    @classmethod
    def from_str(cls, value: str) -> "ErrorSeverity":
        return cls.parse(value)


class ErrorCategory(Enum):
    Network = auto()
    Database = auto()
    Logic = auto()
    General = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def parse(value: str) -> "ErrorCategory":
        v = value.strip().lower()
        mapping = {
            "network": ErrorCategory.Network,
            "database": ErrorCategory.Database,
            "logic": ErrorCategory.Logic,
            "general": ErrorCategory.General,
        }
        return mapping.get(v) or ErrorCategory.General

    @classmethod
    def from_str(cls, value: str) -> "ErrorCategory":
        return cls.parse(value)


class TrainingDataType(Enum):
    Instruction = auto()
    Completion = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def parse(value: str) -> "TrainingDataType":
        v = value.strip().lower()
        if v == "instruction":
            return TrainingDataType.Instruction
        if v == "completion":
            return TrainingDataType.Completion
        raise ValueError(f"Invalid training data type: {value}")

    @classmethod
    def from_str(cls, value: str) -> "TrainingDataType":
        return cls.parse(value)


class AssignmentStatus(Enum):
    Assigned = auto()


# ========== Errors ==========

class TodoziError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        return f"TodoziError: {self.message}"


class ValidationError(TodoziError):
    def __init__(self, message: str):
        super().__init__(message)


# ========== Domain Models ==========

@dataclass
class Task:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = "anonymous"
    action: str = ""
    time: str = ""
    priority: Priority = Priority.Medium
    parent_project: str = ""
    status: Status = Status.Todo
    assignee: Optional[Assignee] = None
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    context_notes: Optional[str] = None
    progress: Optional[int] = None
    embedding_vector: Optional[List[float]] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Memory:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    project_id: Optional[str] = None
    status: ItemStatus = ItemStatus.Active
    moment: str = ""
    meaning: str = ""
    reason: str = ""
    importance: MemoryImportance = MemoryImportance.Medium
    term: MemoryTerm = MemoryTerm.Short
    memory_type: MemoryType = MemoryType.Standard
    emotion: Optional[str] = None  # populated if memory_type == Emotional
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Idea:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    idea: str = ""
    project_id: Optional[str] = None
    status: ItemStatus = ItemStatus.Active
    share: ShareLevel = ShareLevel.Private
    importance: IdeaImportance = IdeaImportance.Medium
    tags: List[str] = field(default_factory=list)
    context: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class AgentAssignment:
    agent_id: str = ""
    task_id: str = ""
    project_id: str = ""
    assigned_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: AssignmentStatus = AssignmentStatus.Assigned


@dataclass
class CodeChunk:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    code: str = ""
    language: str = ""
    source_file: Optional[str] = None
    summary: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Error:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    severity: ErrorSeverity = ErrorSeverity.Medium
    category: ErrorCategory = ErrorCategory.General
    source: str = ""
    context: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None


@dataclass
class TrainingData:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data_type: TrainingDataType = TrainingDataType.Instruction
    prompt: str = ""
    completion: str = ""
    context: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    quality_score: Optional[float] = None
    source: str = "unknown"
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Feeling:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    emotion: str = ""
    intensity: int = 1
    description: str = ""
    context: str = "general"
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Summary:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    importance: IdeaImportance = IdeaImportance.Medium
    context: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class Reminder:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    due_at: Optional[datetime] = None
    priority: Priority = Priority.Medium
    status: Status = Status.Todo
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class ChatContent:
    tasks: List[Task] = field(default_factory=list)
    memories: List[Memory] = field(default_factory=list)
    ideas: List[Idea] = field(default_factory=list)
    agent_assignments: List[AgentAssignment] = field(default_factory=list)
    code_chunks: List[CodeChunk] = field(default_factory=list)
    errors: List[Error] = field(default_factory=list)
    training_data: List[TrainingData] = field(default_factory=list)
    feelings: List[Feeling] = field(default_factory=list)
    summaries: List[Summary] = field(default_factory=list)
    reminders: List[Reminder] = field(default_factory=list)


# ========== Storage abstraction and queue item ==========

@dataclass
class QueueItem:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    priority: Priority = Priority.Medium
    project_id: Optional[str] = None


class TaskResult:
    def __init__(self, task: Task, score: float):
        self.task = task
        self.score = score


class Storage:
    _instance: Optional["Storage"] = None

    def __init__(self) -> None:
        # In real implementations, initialize your DB/connection here
        pass

    @classmethod
    async def get_instance(cls) -> "Storage":
        if cls._instance is None:
            cls._instance = Storage()
        return cls._instance

    async def search_tasks_semantic(self, action: str, limit: int) -> List[TaskResult]:
        from todozi.storage import Storage as StorageImpl
        from todozi.models import TaskFilters
        
        storage = StorageImpl.new()
        tasks = storage.list_tasks_across_projects(TaskFilters(search=action))
        return [TaskResult(task=t, score=1.0) for t in tasks[:limit]]

    async def add_queue_item(self, item: QueueItem) -> None:
        from todozi.storage import add_queue_item as _add_queue_item
        _add_queue_item(item)

    async def save_agent_assignment(self, assignment: AgentAssignment) -> None:
        from todozi.storage import save_agent_assignment as _save_assignment
        _save_assignment(assignment)

    async def update_task_in_project(self, task_id: str, update: "TaskUpdate") -> None:
        from todozi.storage import Storage as StorageImpl
        from todozi.models import TaskUpdate as StorageTaskUpdate, Priority, Status
        
        storage = StorageImpl.new()
        storage_updates = StorageTaskUpdate()
        if update.action:
            storage_updates.action = update.action
        if update.status:
            status_result = Status.from_str(update.status.value if hasattr(update.status, 'value') else str(update.status))
            if isinstance(status_result, Ok):
                storage_updates.status = status_result.value
        storage.update_task_in_project(task_id, storage_updates)


@dataclass
class TaskUpdate:
    action: Optional[str] = None
    status: Optional[Status] = None


# ========== Helper functions ==========

def parse_date_robust(date_str: str) -> Optional[datetime]:
    # Try isoformat first
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
    except Exception:
        pass
    # Try dateutil if available
    try:
        from dateutil.parser import parse
        return parse(date_str)
    except Exception:
        return None


def transform_shorthand_tags(message: str) -> str:
    transformed = message
    mappings = [
        ("<tz>", "<todozi>"), ("</tz>", "</todozi>"), ("<mm>", "<memory>"), ("</mm>", "</memory>"),
        ("<id>", "<idea>"), ("</id>", "</idea>"), ("<ch>", "<chunk>"), ("</ch>", "</chunk>"),
        ("<fe>", "<feel>"), ("</fe>", "</feel>"), ("<tn>", "<train>"), ("</tn>", "</train>"),
        ("<er>", "<error>"), ("</er>", "</error>"), ("<sm>", "<summary>"), ("</sm>", "</summary>"),
        ("<rd>", "<reminder>"), ("</rd>", "</reminder>"), ("<tdz>", "<tdz>"), ("</tdz>", "</tdz>"),
    ]
    for shorthand, longhand in mappings:
        transformed = transformed.replace(shorthand, longhand)
    return transformed


def _extract_content(text: str, start_tag: str, end_tag: str) -> str:
    start = text.find(start_tag)
    if start == -1:
        raise validation_error(f"Missing {start_tag} start tag")
    end = text.find(end_tag, start + len(start_tag))
    if end == -1:
        raise validation_error(f"Missing {end_tag} end tag")
    return text[start + len(start_tag):end]


def _split_parts(content: str) -> List[str]:
    return [p.strip() for p in content.split(";") if p.strip() != ""]


def _extract_value(part: str, key: Optional[str] = None) -> str:
    """Extract value from key=value format or return part as-is if no '=' found."""
    if "=" in part:
        _, value = part.split("=", 1)
        return value.strip()
    return part.strip()


# ========== Parsers ==========

def parse_todozi_format(todozi_text: str) -> Task:
    content = _extract_content(todozi_text, "<todozi>", "</todozi>")
    parts = _split_parts(content)
    if len(parts) < 5:
        raise validation_error(
            "Invalid todozi format: need at least 5 parts (action; time; priority; parent_project; status)"
        )

    action = parts[0]
    time_ = parts[1]
    priority = Priority.from_str(parts[2])
    parent_project = parts[3]
    status = Status.from_str(parts[4])

    assignee: Optional[Assignee] = None
    if len(parts) > 5 and parts[5]:
        assignee_value = _extract_value(parts[5], "assignee")
        assignee = Assignee.parse(assignee_value)

    tags: List[str] = []
    if len(parts) > 6 and parts[6]:
        tags_value = _extract_value(parts[6], "tags")
        tags = [t.strip() for t in tags_value.split(",") if t.strip()]

    dependencies: List[str] = []
    if len(parts) > 7 and parts[7]:
        deps_value = _extract_value(parts[7], "dependencies")
        dependencies = [t.strip() for t in deps_value.split(",") if t.strip()]

    context_notes: Optional[str] = None
    if len(parts) > 8 and parts[8]:
        context_notes = _extract_value(parts[8], "context_notes")

    progress: Optional[int] = None
    if len(parts) > 9 and parts[9]:
        try:
            prog_value = _extract_value(parts[9], "progress")
            prog = prog_value.replace("%", "").strip()
            progress = int(prog)
        except Exception:
            raise validation_error("Invalid progress percentage")

    return Task(
        id=str(uuid.uuid4()),
        user_id="anonymous",
        action=action,
        time=time_,
        priority=priority,
        parent_project=parent_project,
        status=status,
        assignee=assignee,
        tags=tags,
        dependencies=dependencies,
        context_notes=context_notes,
        progress=progress,
        embedding_vector=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def parse_memory_format(memory_text: str, user_id: str) -> Memory:
    content = _extract_content(memory_text, "<memory>", "</memory>")
    parts = _split_parts(content)
    if len(parts) < 6:
        raise validation_error(
            "Invalid memory format: need at least 6 parts (type; moment; meaning; reason; importance; term)"
        )
    memory_type_str = parts[0]
    emotion_list = get_emotion_list()
    memory_type: MemoryType
    emotion: Optional[str] = None
    if memory_type_str.strip().lower() in emotion_list:
        memory_type = MemoryType.Emotional
        emotion = memory_type_str.strip()
    else:
        memory_type = MemoryType.from_str(memory_type_str)

    tags: List[str] = []
    if len(parts) > 6 and parts[6]:
        tags = [t.strip() for t in parts[6].split(",")]

    importance = MemoryImportance.from_str(parts[4])
    term = MemoryTerm.from_str(parts[5])

    return Memory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        project_id=None,
        status=ItemStatus.Active,
        moment=parts[1],
        meaning=parts[2],
        reason=parts[3],
        importance=importance,
        term=term,
        memory_type=memory_type,
        emotion=emotion,
        tags=tags,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def parse_idea_format(idea_text: str) -> Idea:
    content = _extract_content(idea_text, "<idea>", "</idea>")
    parts = _split_parts(content)
    if len(parts) < 3:
        raise validation_error(
            "Invalid idea format: need at least 3 parts (idea; share; importance)"
        )
    share_str = parts[1].lower()
    share = ShareLevel.parse(share_str)
    importance = IdeaImportance.from_str(parts[2])

    context: Optional[str] = None
    if len(parts) > 3 and parts[3]:
        context = parts[3]

    tags: List[str] = []
    if len(parts) > 4 and parts[4]:
        tags = [t.strip() for t in parts[4].split(",") if t.strip()]

    return Idea(
        id=str(uuid.uuid4()),
        idea=parts[0],
        project_id=None,
        status=ItemStatus.Active,
        share=share,
        importance=importance,
        tags=tags,
        context=context,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def parse_agent_assignment_format(agent_text: str) -> AgentAssignment:
    content = _extract_content(agent_text, "<todozi_agent>", "</todozi_agent>")
    parts = _split_parts(content)
    if len(parts) < 3:
        raise validation_error(
            "Invalid agent assignment format: need at least 3 parts (task_id; agent_id; project_id)"
        )
    return AgentAssignment(
        task_id=parts[0],
        agent_id=parts[1],
        project_id=parts[2],
        assigned_at=datetime.now(timezone.utc),
        status=AssignmentStatus.Assigned,
    )


def parse_error_format(error_text: str) -> Error:
    # Handle both <error> and <e> tags
    if "<e>" in error_text and "</e>" in error_text:
        content = _extract_content(error_text, "<e>", "</e>")
    else:
        content = _extract_content(error_text, "<error>", "</error>")
    parts = _split_parts(content)
    if len(parts) < 5:
        raise validation_error(
            "Invalid error format: need at least 5 parts (title; description; severity; category; source)"
        )

    tags: List[str] = []
    if len(parts) > 6 and parts[6]:
        tags = [t.strip() for t in parts[6].split(",")]

    severity = ErrorSeverity.from_str(parts[2])
    category = ErrorCategory.from_str(parts[3])

    context = parts[5] if len(parts) > 5 and parts[5] else None

    return Error(
        id=str(uuid.uuid4()),
        title=parts[0],
        description=parts[1],
        severity=severity,
        category=category,
        source=parts[4],
        context=context,
        tags=tags,
        resolved=False,
        resolution=None,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        resolved_at=None,
    )


def parse_training_data_format(train_text: str) -> TrainingData:
    content = _extract_content(train_text, "<train>", "</train>")
    parts = _split_parts(content)
    if len(parts) < 4:
        raise validation_error(
            "Invalid training data format: need at least 4 parts (data_type; prompt; completion; source)"
        )

    tags: List[str] = []
    if len(parts) > 4 and parts[4]:
        tags = [t.strip() for t in parts[4].split(",")]

    quality_score: Optional[float] = None
    if len(parts) > 5 and parts[5]:
        try:
            quality_score = float(parts[5])
        except Exception:
            raise validation_error("Invalid quality score")

    data_type = TrainingDataType.from_str(parts[0])
    source = parts[6] if len(parts) > 6 else "unknown"

    return TrainingData(
        id=str(uuid.uuid4()),
        data_type=data_type,
        prompt=parts[1],
        completion=parts[2],
        context=parts[3] if len(parts) > 3 and parts[3] else None,
        tags=tags,
        quality_score=quality_score,
        source=source,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def parse_feeling_format(feel_text: str) -> Feeling:
    content = _extract_content(feel_text, "<feel>", "</feel>")
    parts = _split_parts(content)
    if len(parts) < 3:
        raise validation_error("Feeling format requires at least emotion; intensity; description")

    try:
        intensity = int(parts[1])
    except Exception:
        raise validation_error("Invalid intensity format")

    if intensity < 1 or intensity > 10:
        raise validation_error("Intensity must be between 1 and 10")

    tags: List[str] = []
    if len(parts) > 4 and parts[4]:
        tags = [t.strip() for t in parts[4].split(",")]

    context = parts[3] if len(parts) > 3 else "general"

    return Feeling(
        id=str(uuid.uuid4()),
        emotion=parts[0],
        intensity=intensity,
        description=parts[2],
        context=context,
        tags=tags,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def parse_chunking_format(chunk_text: str) -> CodeChunk:
    content = _extract_content(chunk_text, "<chunk>", "</chunk>")
    parts = _split_parts(content)
    code = parts[0] if len(parts) > 0 else ""
    language = parts[1] if len(parts) > 1 else ""
    summary = parts[2] if len(parts) > 2 else None
    source_file = parts[3] if len(parts) > 3 else None
    tags = []
    if len(parts) > 4 and parts[4]:
        tags = [t.strip() for t in parts[4].split(",")]
    return CodeChunk(
        id=str(uuid.uuid4()),
        code=code,
        language=language,
        source_file=source_file,
        summary=summary,
        tags=tags,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def parse_summary_format(summary_text: str) -> Summary:
    content = _extract_content(summary_text, "<summary>", "</summary>")
    parts = _split_parts(content)
    content_str = parts[0] if len(parts) > 0 else content
    importance = IdeaImportance.Medium
    if len(parts) > 1:
        try:
            importance = IdeaImportance.from_str(parts[1])
        except Exception:
            pass
    context = parts[2] if len(parts) > 2 else None
    tags = []
    if len(parts) > 3 and parts[3]:
        tags = [t.strip() for t in parts[3].split(",")]
    return Summary(
        id=str(uuid.uuid4()),
        content=content_str,
        importance=importance,
        context=context,
        tags=tags,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


def parse_reminder_format(reminder_text: str) -> Reminder:
    content = _extract_content(reminder_text, "<reminder>", "</reminder>")
    parts = _split_parts(content)
    content_str = parts[0] if len(parts) > 0 else content
    due_at: Optional[datetime] = None
    if len(parts) > 1 and parts[1]:
        due_at = parse_date_robust(parts[1])
    priority = Priority.Medium
    if len(parts) > 2:
        try:
            priority = Priority.from_str(parts[2])
        except Exception:
            pass
    status = Status.Todo
    if len(parts) > 3:
        try:
            status = Status.from_str(parts[3])
        except Exception:
            pass
    tags = []
    if len(parts) > 4 and parts[4]:
        tags = [t.strip() for t in parts[4].split(",")]
    return Reminder(
        id=str(uuid.uuid4()),
        content=content_str,
        due_at=due_at,
        priority=priority,
        status=status,
        tags=tags,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )


# ========== Message Processing ==========

def process_chat_message(message: str) -> List[Task]:
    tasks: List[Task] = []
    pattern = PatternCache.get(r"<todozi>.*?</todozi>", re.DOTALL)
    for m in pattern.finditer(message):
        todozi_text = m.group(0)
        try:
            task = parse_todozi_format(todozi_text)
            tasks.append(task)
        except Exception as e:
            print(f"Warning: Failed to parse todozi task: {e}")
    return tasks


def process_chat_message_extended(message: str, user_id: str) -> ChatContent:
    transformed_message = transform_shorthand_tags(message)
    content = ChatContent()

    def extract_all(pattern: str, parser):
        compiled = PatternCache.get(pattern, re.DOTALL)
        for m in compiled.finditer(transformed_message):
            text = m.group(0)
            try:
                obj = parser(text)
                yield obj
            except Exception as e:
                print(f"Warning: {e}")

    # todozi
    for task in extract_all(r"<todozi>.*?</todozi>", parse_todozi_format):
        content.tasks.append(task)

    # memory
    for mem in extract_all(r"<memory>.*?</memory>", lambda t: parse_memory_format(t, user_id)):
        content.memories.append(mem)

    # idea
    for idea in extract_all(r"<idea>.*?</idea>", parse_idea_format):
        content.ideas.append(idea)

    # agent assignment
    for ag in extract_all(r"<todozi_agent>.*?</todozi_agent>", parse_agent_assignment_format):
        content.agent_assignments.append(ag)

    # code chunks
    for ch in extract_all(r"<chunk>.*?</chunk>", parse_chunking_format):
        content.code_chunks.append(ch)

    # errors (<error> and shorthand <er> and <e>)
    for err in extract_all(r"<error>.*?</error>", parse_error_format):
        content.errors.append(err)
    for err in extract_all(r"<er>.*?</er>", parse_error_format):
        content.errors.append(err)
    # <e> is handled by parse_error_format which detects the tag type
    for err in extract_all(r"<e>.*?</e>", parse_error_format):
        content.errors.append(err)

    # training data (<train> and shorthand <tn>)
    for tr in extract_all(r"<train>.*?</train>", parse_training_data_format):
        content.training_data.append(tr)
    for tr in extract_all(r"<tn>.*?</tn>", parse_training_data_format):
        content.training_data.append(tr)

    # feelings
    for feel in extract_all(r"<feel>.*?</feel>", parse_feeling_format):
        content.feelings.append(feel)

    # summaries
    for s in extract_all(r"<summary>.*?</summary>", parse_summary_format):
        content.summaries.append(s)
    for s in extract_all(r"<sm>.*?</sm>", parse_summary_format):
        content.summaries.append(s)

    # reminders
    for r in extract_all(r"<reminder>.*?</reminder>", parse_reminder_format):
        content.reminders.append(r)
    for r in extract_all(r"<rd>.*?</rd>", parse_reminder_format):
        content.reminders.append(r)

    return content


# ========== Task Execution and Workflow ==========

async def execute_ai_task(task: Task) -> str:
    queue_item = QueueItem(
        title=f"AI: {task.action}",
        description=f"AI processing required for task: {task.action}",
        priority=task.priority,
        project_id=task.parent_project,
    )
    try:
        storage = await Storage.get_instance()
        await storage.add_queue_item(queue_item)
        return f"Task queued for AI processing: {task.action} (Queue ID: {queue_item.id})"
    except Exception as e:
        raise TodoziError(f"Failed to queue AI task: {e}")


async def execute_human_task(task: Task) -> str:
    queue_item = QueueItem(
        title=f"Human: {task.action}",
        description=task.context_notes or f"Human task: {task.action}",
        priority=task.priority,
        project_id=task.parent_project,
    )
    try:
        storage = await Storage.get_instance()
        await storage.add_queue_item(queue_item)
        return f"Task available in TUI queue: {task.action} (Queue ID: {queue_item.id})"
    except Exception as e:
        raise TodoziError(f"Failed to queue human task: {e}")


async def execute_collaborative_task(task: Task) -> str:
    ai_queue_item = QueueItem(
        title=f"AI Collab: {task.action}",
        description=f"AI portion of collaborative task: {task.action}",
        priority=task.priority,
        project_id=task.parent_project,
    )
    human_queue_item = QueueItem(
        title=f"Human Collab: {task.action}",
        description=f"Human portion of collaborative task: {task.action}",
        priority=task.priority,
        project_id=task.parent_project,
    )
    storage = await Storage.get_instance()
    try:
        await storage.add_queue_item(ai_queue_item)
    except Exception as e:
        raise TodoziError(f"Failed to queue AI portion: {e}")
    try:
        await storage.add_queue_item(human_queue_item)
    except Exception as e:
        raise TodoziError(f"Failed to queue human portion: {e}")
    return (
        f"Collaborative task queued: {task.action} "
        f"(AI Queue: {ai_queue_item.id}, Human Queue: {human_queue_item.id})"
    )


async def execute_agent_task(task: Task, agent_name: str) -> str:
    assignment = AgentAssignment(
        agent_id=agent_name,
        task_id=task.id,
        project_id=task.parent_project,
        assigned_at=datetime.now(timezone.utc),
        status=AssignmentStatus.Assigned,
    )
    storage = await Storage.get_instance()
    try:
        await storage.save_agent_assignment(assignment)
    except Exception as e:
        raise TodoziError(f"Failed to assign task to agent: {e}")

    queue_item = QueueItem(
        title=f"{agent_name} Agent: {task.action}",
        description=f"Agent {agent_name} assigned to task: {task.action}",
        priority=task.priority,
        project_id=task.parent_project,
    )
    try:
        await storage.add_queue_item(queue_item)
    except Exception:
        pass
    return (
        f"Task assigned to {agent_name} agent: {task.action} "
        f"(Assignment saved, Queue ID: {queue_item.id})"
    )


async def execute_task(storage: Storage, task: Task) -> str:
    if task.assignee is not None:
        if task.assignee.kind == AssigneeType.Ai:
            return await execute_ai_task(task)
        if task.assignee.kind == AssigneeType.Human:
            return await execute_human_task(task)
        if task.assignee.kind == AssigneeType.Collaborative:
            return await execute_collaborative_task(task)
        if task.assignee.kind == AssigneeType.Agent:
            return await execute_agent_task(task, task.assignee.name or "")

    # No assignee: try semantic hint
    try:
        similar_tasks = await storage.search_tasks_semantic(task.action, 5)
    except Exception:
        similar_tasks = []

    ai_count = sum(1 for r in similar_tasks if r.task.assignee and r.task.assignee.kind == AssigneeType.Ai)
    human_count = sum(1 for r in similar_tasks if r.task.assignee and r.task.assignee.kind == AssigneeType.Human)
    if ai_count > human_count:
        return await execute_ai_task(task)

    action_lc = task.action.lower()
    if any(k in action_lc for k in ("ai", "analyze", "generate", "review")):
        return await execute_ai_task(task)
    else:
        return await execute_human_task(task)


async def process_workflow(tasks: List[Task]) -> List[str]:
    results: List[str] = []
    storage = await Storage.get_instance()
    for task in tasks:
        try:
            res = await execute_task(storage, task)
            results.append(res)
        except Exception as e:
            results.append(f"Task execution failed: {e}")

        # Update status to Done (avoid reference aliasing)
        updated_task = copy.deepcopy(task)
        updated_task.status = Status.Done
        updated_task.updated_at = datetime.now(timezone.utc)

        try:
            await storage.update_task_in_project(
                updated_task.id,
                TaskUpdate(action=updated_task.action, status=updated_task.status),
            )
            print(f"✅ Task completed and saved: {updated_task.action}")
        except Exception as e:
            print(f"⚠️  Task completed but failed to save: {updated_task.action} ({e})")
    return results


# ========== JSON examples processing ==========

def process_json_examples(json_data: str) -> List[Task]:
    tasks: List[Task] = []
    try:
        data = json.loads(json_data)
    except Exception as e:
        raise validation_error(f"Invalid JSON: {e}")

    examples = data.get("tool_definition", {}).get("examples")
    if not isinstance(examples, list):
        return tasks

    for example in examples:
        todozi_format = example.get("todozi_format")
        if isinstance(todozi_format, str):
            try:
                task = parse_todozi_format(todozi_format)
                tasks.append(task)
            except Exception as e:
                print(f"Warning: Failed to parse example task: {e}")
                continue
    return tasks


# ========== Tests ==========

def _run_tests():
    test_functions = [
        test_parse_todozi_format_basic,
        test_parse_todozi_format_extended,
        test_process_chat_message,
        test_parse_error_format,
        test_parse_training_data_format,
        test_process_chat_message_extended_with_all_tags,
        test_transform_shorthand_tags,
        test_process_chat_message_with_shorthand_tags,
    ]

    for test_func in test_functions:
        try:
            test_func()
            print(f"✅ {test_func.__name__} passed")
        except AssertionError as ae:
            print(f"❌ {test_func.__name__} failed: {ae}")
        except Exception as e:
            print(f"❌ {test_func.__name__} error: {e}")


def test_parse_todozi_format_basic():
    todozi_text = "<todozi>Fix critical bug; ASAP; critical; rust-performance-optimizer; blocked</todozi>"
    task = parse_todozi_format(todozi_text)
    assert task.action == "Fix critical bug"
    assert task.time == "ASAP"
    assert task.priority == Priority.Critical
    assert task.parent_project == "rust-performance-optimizer"
    assert task.status == Status.Blocked


def test_parse_todozi_format_extended():
    todozi_text = "<todozi>Implement OAuth2 login flow; 6 hours; high; python-web-framework; todo; assignee=human; tags=auth,backend; dependencies=Design API; context_notes=Ensure security; progress=0%</todozi>"
    task = parse_todozi_format(todozi_text)
    assert task.action == "Implement OAuth2 login flow"
    assert task.time == "6 hours"
    assert task.priority == Priority.High
    assert task.parent_project == "python-web-framework"
    assert task.status == Status.Todo
    assert task.assignee == Assignee.human()
    assert task.tags == ["auth", "backend"]
    assert task.dependencies == ["Design API"]
    assert task.context_notes == "Ensure security"
    assert task.progress == 0


def test_process_chat_message():
    message = "I need to <todozi>Review pull request; 2 hours; high; testing-framework; deferred</todozi> and also <todozi>Fix critical bug; ASAP; critical; rust-performance-optimizer; blocked</todozi>"
    tasks = process_chat_message(message)
    assert len(tasks) == 2
    assert tasks[0].action == "Review pull request"
    assert tasks[1].action == "Fix critical bug"


def test_parse_error_format():
    error_text = "<error>Database connection failed; Unable to connect to PostgreSQL database; critical; network; database-service; Connection timeout after 30 seconds; database,postgres,connection</error>"
    error = parse_error_format(error_text)
    assert error.title == "Database connection failed"
    assert error.description == "Unable to connect to PostgreSQL database"
    assert error.severity == ErrorSeverity.Critical
    assert error.category == ErrorCategory.Network
    assert error.source == "database-service"
    assert error.context == "Connection timeout after 30 seconds"
    assert error.tags == ["database", "postgres", "connection"]
    assert error.resolved is False


def test_parse_training_data_format():
    train_text = "<train>instruction; Write a function to calculate fibonacci numbers; def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2); Python programming example; python,algorithm,recursion; 0.9; code-examples</train>"
    training_data = parse_training_data_format(train_text)
    assert training_data.data_type == TrainingDataType.Instruction
    assert training_data.prompt == "Write a function to calculate fibonacci numbers"
    assert "def fibonacci" in training_data.completion
    assert training_data.context == "Python programming example"
    assert training_data.tags == ["python", "algorithm", "recursion"]
    assert training_data.quality_score == 0.9
    assert training_data.source == "code-examples"


def test_process_chat_message_extended_with_all_tags():
    message = """
    I need to <todozi>Review pull request; 2 hours; high; testing-framework; deferred</todozi>
    <memory>standard; First insight; This is an important insight; High value information; high; long; insight,valuable</memory>
    <idea>Revolutionary approach; private; high; This could change everything</idea>
    <todozi_agent>task123; agent456; review_code; important</todozi_agent>
    <chunk>println!("Hello world");</chunk>
    <e>Connection error; Failed to connect to database; high; network; db_module</e>
    <train>instruction; Write a sort function; def bubble_sort(arr): pass; Sorting algorithms; python,algorithm; 0.8; examples</train>
    <feel>excited; 9; Making great progress on this project!; coding session; productive,happy</feel>
    """
    content = process_chat_message_extended(message, "test_user")
    assert len(content.tasks) == 1
    assert content.tasks[0].action == "Review pull request"
    assert len(content.memories) == 1
    assert content.memories[0].moment == "First insight"
    assert content.memories[0].meaning == "This is an important insight"
    assert content.memories[0].reason == "High value information"
    assert content.memories[0].importance == MemoryImportance.High
    assert content.memories[0].term == MemoryTerm.Long
    assert content.memories[0].memory_type == MemoryType.Standard
    assert content.memories[0].tags == ["insight", "valuable"]
    assert len(content.ideas) == 1
    assert content.ideas[0].idea == "Revolutionary approach"
    assert len(content.agent_assignments) == 1
    assert content.agent_assignments[0].task_id == "task123"
    assert len(content.code_chunks) == 1
    assert "println!" in content.code_chunks[0].code
    assert len(content.errors) == 1
    assert content.errors[0].title == "Connection error"
    assert len(content.training_data) == 1
    assert content.training_data[0].prompt == "Write a sort function"
    assert len(content.feelings) == 1
    assert content.feelings[0].emotion == "excited"
    assert content.feelings[0].intensity == 9
    assert content.feelings[0].description == "Making great progress on this project!"
    assert content.feelings[0].context == "coding session"
    assert content.feelings[0].tags == ["productive", "happy"]


def test_transform_shorthand_tags():
    message = """
    <tz>Quick task; 1 hour; medium; quick; todo</tz>
    <mm>standard; Quick insight; Important note; For reference; medium; short; insight</mm>
    <id>Quick idea; private; medium</id>
    <ch>quick_chunk; method; Simple function; utility; Basic helper</ch>
    <fe>happy; 7; Quick win; success; positive</fe>
    <tn>quick_training; Simple example; Basic response; example; simple; 0.8; quick</tn>
    <er>Quick error; Simple issue; low; general; system; Basic problem; simple</er>
    <sm>Quick summary; medium; Brief overview; quick,overview</sm>
    <rd>Quick reminder; 2025-01-17T12:00:00Z; low; pending; quick</rd>
    """
    transformed = transform_shorthand_tags(message)
    assert "<todozi>" in transformed and "</todozi>" in transformed
    assert "<memory>" in transformed and "</memory>" in transformed
    assert "<idea>" in transformed and "</idea>" in transformed
    assert "<chunk>" in transformed and "</chunk>" in transformed
    assert "<feel>" in transformed and "</feel>" in transformed
    assert "<train>" in transformed and "</train>" in transformed
    assert "<error>" in transformed and "</error>" in transformed
    assert "<summary>" in transformed and "</summary>" in transformed
    assert "<reminder>" in transformed and "</reminder>" in transformed
    assert "<tz>" not in transformed and "</tz>" not in transformed
    assert "<mm>" not in transformed and "</mm>" not in transformed
    assert "<id>" not in transformed and "</id>" not in transformed
    assert "<ch>" not in transformed and "</ch>" not in transformed
    assert "<fe>" not in transformed and "</fe>" not in transformed
    assert "<tn>" not in transformed and "</tn>" not in transformed
    assert "<er>" not in transformed and "</er>" not in transformed
    assert "<sm>" not in transformed and "</sm>" not in transformed
    assert "<rd>" not in transformed and "</rd>" not in transformed


def test_process_chat_message_with_shorthand_tags():
    message = """
    <tz>Quick task; 1 hour; medium; quick; todo</tz>
    <mm>standard; Quick insight; Important note; For reference; medium; short; insight</mm>
    <id>Quick idea; private; medium</id>
    <sm>Quick summary; medium; Brief overview; quick,overview</sm>
    <rd>Quick reminder; 2025-01-17T12:00:00Z; low; pending; quick</rd>
    """
    content = process_chat_message_extended(message, "test_user")
    assert len(content.tasks) == 1
    assert content.tasks[0].action == "Quick task"
    assert len(content.memories) == 1
    assert content.memories[0].moment == "Quick insight"
    assert len(content.ideas) == 1
    assert content.ideas[0].idea == "Quick idea"
    assert len(content.summaries) == 1
    assert content.summaries[0].content == "Quick summary"
    assert len(content.reminders) == 1
    assert content.reminders[0].content == "Quick reminder"


if __name__ == "__main__":
    _run_tests()
