from __future__ import annotations

import json
import re
import sys
import tempfile
import uuid
from dataclasses import dataclass, field, asdict
from enum import Enum, auto
from pathlib import Path
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    Union,
)


# =============================
# Exceptions
# =============================

class TodoziError(Exception):
    def __init__(self, kind: str, message: str, **context: Any):
        super().__init__(message)
        self.kind = kind
        self.context = context

    def __str__(self) -> str:
        return f"{self.kind}: {super().__str__()}"

    @staticmethod
    def task_not_found(task_id: str) -> "TodoziError":
        return TodoziError("TaskNotFound", f"Task not found: {task_id}", task_id=task_id)

    @staticmethod
    def project_not_found(name: str) -> "TodoziError":
        return TodoziError("ProjectNotFound", f"Project not found: {name}", project=name)

    @staticmethod
    def invalid_progress(progress: int) -> "TodoziError":
        return TodoziError("InvalidProgress", f"Progress must be between 0 and 100, got {progress}", progress=progress)

    @staticmethod
    def invalid_priority(priority: str) -> "TodoziError":
        return TodoziError("InvalidPriority", f"Invalid priority: {priority}", priority=priority)

    @staticmethod
    def invalid_status(status: str) -> "TodoziError":
        return TodoziError("InvalidStatus", f"Invalid status: {status}", status=status)

    @staticmethod
    def invalid_assignee(assignee: str) -> "TodoziError":
        return TodoziError("InvalidAssignee", f"Invalid assignee: {assignee}", assignee=assignee)

    @staticmethod
    def validation(message: str) -> "TodoziError":
        return TodoziError("ValidationError", message)


# =============================
# Enums and value objects
# =============================

class Priority(Enum):
    Low = auto()
    Medium = auto()
    High = auto()
    Critical = auto()
    Urgent = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def _normalize(s: str) -> str:
        return re.sub(r"[\s_\-]+", "", s.strip().lower())

    @classmethod
    def parse(cls, s: str) -> "Priority":
        key = cls._normalize(s)
        mapping = {
            "low": cls.Low,
            "medium": cls.Medium,
            "high": cls.High,
            "critical": cls.Critical,
            "urgent": cls.Urgent,
        }
        if key not in mapping:
            raise TodoziError.invalid_priority(s)
        return mapping[key]

    def to_json(self) -> str:
        return self.name.lower()

    @classmethod
    def from_json(cls, s: str) -> "Priority":
        return cls.parse(s)


class Status(Enum):
    Todo = auto()
    InProgress = auto()
    Blocked = auto()
    Review = auto()
    Done = auto()
    Cancelled = auto()
    Deferred = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def _normalize(s: str) -> str:
        return re.sub(r"[\s_\-]+", "", s.strip().lower())

    @classmethod
    def parse(cls, s: str) -> "Status":
        key = cls._normalize(s)
        mapping = {
            "todo": cls.Todo,
            "inprogress": cls.InProgress,
            "blocked": cls.Blocked,
            "review": cls.Review,
            "done": cls.Done,
            "cancelled": cls.Cancelled,
            "canceled": cls.Cancelled,  # accept US spelling
            "deferred": cls.Deferred,
        }
        if key not in mapping:
            raise TodoziError.invalid_status(s)
        return mapping[key]

    def to_json(self) -> str:
        # serialize as snake_case to match Rust
        return {
            self.Todo: "todo",
            self.InProgress: "in_progress",
            self.Blocked: "blocked",
            self.Review: "review",
            self.Done: "done",
            self.Cancelled: "cancelled",
            self.Deferred: "deferred",
        }[self]

    @classmethod
    def from_json(cls, s: str) -> "Status":
        return cls.parse(s)


class Assignee(Enum):
    Ai = auto()
    Human = auto()
    Collaborative = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def _normalize(s: str) -> str:
        return re.sub(r"[\s_\-]+", "", s.strip().lower())

    @classmethod
    def parse(cls, s: str) -> "Assignee":
        key = cls._normalize(s)
        mapping = {
            "ai": cls.Ai,
            "human": cls.Human,
            "collaborative": cls.Collaborative,
        }
        if key not in mapping:
            raise TodoziError.invalid_assignee(s)
        return mapping[key]

    def to_json(self) -> str:
        return self.name.lower()

    @classmethod
    def from_json(cls, s: str) -> "Assignee":
        return cls.parse(s)


class ProjectStatus(Enum):
    Active = auto()
    Archived = auto()
    Completed = auto()

    def __str__(self) -> str:
        return self.name

    @staticmethod
    def _normalize(s: str) -> str:
        return re.sub(r"[\s_\-]+", "", s.strip().lower())

    @classmethod
    def parse(cls, s: str) -> "ProjectStatus":
        key = cls._normalize(s)
        mapping = {
            "active": cls.Active,
            "archived": cls.Archived,
            "completed": cls.Completed,
        }
        if key not in mapping:
            raise TodoziError.validation(f"Invalid project status: {s}")
        return mapping[key]

    def to_json(self) -> str:
        return self.name.lower()

    @classmethod
    def from_json(cls, s: str) -> "ProjectStatus":
        return cls.parse(s)


# =============================
# Data models
# =============================

def _make_task_id() -> str:
    return f"task_{uuid.uuid4().hex[:8]}"


@dataclass
class Task:
    # To match Rust's Optional[Assignee], allow None, Assignee, or str (from JSON).
    assignee: Optional[Union[Assignee, str]]
    action: str
    time: str
    priority: Priority
    parent_project: str
    status: Status
    id: str = field(default_factory=_make_task_id)
    tags: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    context_notes: Optional[str] = None
    progress: Optional[int] = None

    def is_completed(self) -> bool:
        return self.status == Status.Done

    def is_active(self) -> bool:
        # active: not completed and not cancelled
        return not self.is_completed() and self.status != Status.Cancelled

    # API consistency with Rust: Task.update()
    def update(self, updates: "TaskUpdate") -> None:
        updates.apply_to(self)

    def complete(self) -> None:
        self.status = Status.Done
        self.progress = 100

    @staticmethod
    def new(
        assignee: str,
        action: str,
        time: str,
        priority: Priority,
        parent_project: str,
        status: Status,
    ) -> "Task":
        return Task(
            assignee=assignee,
            action=action,
            time=time,
            priority=priority,
            parent_project=parent_project,
            status=status,
        )

    @staticmethod
    def new_full(
        action: str,
        time: str,
        priority: Priority,
        parent_project: str,
        status: Status,
        assignee: Optional[Union[Assignee, str]],
        tags: List[str],
        dependencies: List[str],
        context_notes: Optional[str],
        progress: Optional[int],
    ) -> "Task":
        if progress is not None and not (0 <= progress <= 100):
            raise TodoziError.invalid_progress(progress)
        t = Task(
            assignee=assignee,
            action=action,
            time=time,
            priority=priority,
            parent_project=parent_project,
            status=status,
            tags=list(tags),
            dependencies=list(dependencies),
            context_notes=context_notes,
            progress=progress,
        )
        return t

    def to_json(self) -> Dict[str, Any]:
        assignee_val: Optional[str] = None
        if self.assignee is not None:
            if isinstance(self.assignee, Assignee):
                assignee_val = self.assignee.to_json()
            else:
                # treat as raw string
                assignee_val = str(self.assignee).lower()
        return {
            "id": self.id,
            "assignee": assignee_val,
            "action": self.action,
            "time": self.time,
            "priority": self.priority.to_json(),
            "parent_project": self.parent_project,
            "status": self.status.to_json(),
            "tags": list(self.tags),
            "dependencies": list(self.dependencies),
            "context_notes": self.context_notes,
            "progress": self.progress,
        }

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "Task":
        def _parse_assignee(value: Any) -> Optional[Union[Assignee, str]]:
            if value is None:
                return None
            if isinstance(value, Assignee):
                return value
            if isinstance(value, str):
                # Try parse as enum, otherwise pass through raw string
                try:
                    return Assignee.parse(value)
                except TodoziError:
                    return value
            raise TypeError(f"assignee must be None, str, or Assignee, got {type(value)}")

        return Task(
            id=data.get("id") or _make_task_id(),
            assignee=_parse_assignee(data.get("assignee")),
            action=data["action"],
            time=data["time"],
            priority=Priority.from_json(data["priority"]),
            parent_project=data["parent_project"],
            status=Status.from_json(data["status"]),
            tags=list(data.get("tags", [])),
            dependencies=list(data.get("dependencies", [])),
            context_notes=data.get("context_notes"),
            progress=data.get("progress"),
        )


@dataclass
class TaskUpdate:
    action: Optional[str] = None
    priority: Optional[Priority] = None
    status: Optional[Status] = None
    progress: Optional[int] = None

    @staticmethod
    def new() -> "TaskUpdate":
        return TaskUpdate()

    def with_action(self, action: str) -> "TaskUpdate":
        self.action = action
        return self

    def with_priority(self, priority: Priority) -> "TaskUpdate":
        self.priority = priority
        return self

    def with_status(self, status: Status) -> "TaskUpdate":
        self.status = status
        return self

    def with_progress(self, progress: int) -> "TaskUpdate":
        self.progress = progress
        return self

    def apply_to(self, task: "Task") -> None:
        if self.action is not None:
            task.action = self.action
        if self.priority is not None:
            task.priority = self.priority
        if self.status is not None:
            task.status = self.status
        if self.progress is not None:
            if not (0 <= self.progress <= 100):
                raise TodoziError.invalid_progress(self.progress)
            task.progress = self.progress

    def to_json(self) -> Dict[str, Any]:
        d: Dict[str, Any] = {}
        if self.action is not None:
            d["action"] = self.action
        if self.priority is not None:
            d["priority"] = self.priority.to_json()
        if self.status is not None:
            d["status"] = self.status.to_json()
        if self.progress is not None:
            d["progress"] = self.progress
        return d

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "TaskUpdate":
        upd = TaskUpdate()
        if "action" in data:
            upd.action = data["action"]
        if "priority" in data:
            upd.priority = Priority.from_json(data["priority"])
        if "status" in data:
            upd.status = Status.from_json(data["status"])
        if "progress" in data:
            upd.progress = data["progress"]
        return upd


@dataclass
class TaskFilters:
    priority: Optional[Priority] = None
    project: Optional[str] = None
    status: Optional[Status] = None

    @staticmethod
    def default() -> "TaskFilters":
        return TaskFilters()


@dataclass
class Project:
    name: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.Active
    tasks: Set[str] = field(default_factory=set)

    def add_task(self, task_id: str) -> None:
        self.tasks.add(task_id)

    def remove_task(self, task_id: str) -> None:
        if task_id in self.tasks:
            self.tasks.remove(task_id)

    def archive(self) -> None:
        self.status = ProjectStatus.Archived

    def complete(self) -> None:
        self.status = ProjectStatus.Completed

    def to_json(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "status": self.status.to_json(),
            "tasks": sorted(self.tasks),
        }

    @staticmethod
    def from_json(data: Dict[str, Any]) -> "Project":
        return Project(
            name=data["name"],
            description=data.get("description"),
            status=ProjectStatus.from_json(data.get("status", "active")),
            tasks=set(data.get("tasks", [])),
        )


@dataclass
class TaskCollection:
    tasks: Dict[str, Task] = field(default_factory=dict)

    @staticmethod
    def new() -> "TaskCollection":
        return TaskCollection()

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def remove_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.pop(task_id, None)

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def get_filtered_tasks(self, f: TaskFilters) -> List[Task]:
        result: List[Task] = []
        for t in self.tasks.values():
            if f.priority is not None and t.priority != f.priority:
                continue
            if f.project is not None and t.parent_project != f.project:
                continue
            if f.status is not None and t.status != f.status:
                continue
            result.append(t)
        return result

    def to_json(self) -> List[Dict[str, Any]]:
        return [t.to_json() for t in self.tasks.values()]

    @staticmethod
    def from_json(data: List[Dict[str, Any]]) -> "TaskCollection":
        col = TaskCollection()
        for item in data:
            t = Task.from_json(item)
            col.tasks[t.id] = t
        return col


@dataclass
class Config:
    version: str = "1.2.0"
    default_project: str = "general"
    auto_backup: bool = True
    backup_interval: str = "daily"
    ai_enabled: bool = True
    default_assignee: Optional[Assignee] = Assignee.Collaborative
    date_format: str = "%Y-%m-%d %H:%M:%S"
    timezone: str = "UTC"

    def to_json(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "Config":
        return cls(
            version=data.get("version", cls().version),
            default_project=data.get("default_project", cls().default_project),
            auto_backup=data.get("auto_backup", cls().auto_backup),
            backup_interval=data.get("backup_interval", cls().backup_interval),
            ai_enabled=data.get("ai_enabled", cls().ai_enabled),
            default_assignee=(
                Assignee.from_json(data["default_assignee"])
                if "default_assignee" in data
                else cls().default_assignee
            ),
            date_format=data.get("date_format", cls().date_format),
            timezone=data.get("timezone", cls().timezone),
        )

    @staticmethod
    def default() -> "Config":
        return Config()


# =============================
# Storage
# =============================

class Storage:
    def __init__(self, root: Path, config: Optional[Config] = None):
        self.root = Path(root)
        self.config = config or Config.default()
        self._ensure_structure()
        self._write_config_if_missing()

    def _dir(self, name: str) -> Path:
        return self.root / name

    def _ensure_structure(self) -> None:
        for d in ("tasks", "projects", "templates", "backups"):
            self._dir(d).mkdir(parents=True, exist_ok=True)

    def _write_config_if_missing(self) -> None:
        cfg_path = self.root / "config.json"
        if not cfg_path.exists():
            with cfg_path.open("w", encoding="utf-8") as f:
                json.dump(self.config.to_json(), f, indent=2)

    # Convenience helpers
    def _tasks_file(self, name: str) -> Path:
        return self._dir("tasks") / f"{name}.json"

    def _project_file(self, name: str) -> Path:
        return self._dir("projects") / f"{name}.json"

    # Public API used by tests
    def load_config(self) -> Config:
        cfg_path = self.root / "config.json"
        if not cfg_path.exists():
            return self.config
        with cfg_path.open("r", encoding="utf-8") as f:
            return Config.from_json(json.load(f))

    def save_config(self, config: Config) -> None:
        cfg_path = self.root / "config.json"
        with cfg_path.open("w", encoding="utf-8") as f:
            json.dump(config.to_json(), f, indent=2)

    def load_collection(self, name: str) -> TaskCollection:
        path = self._tasks_file(name)
        if not path.exists():
            return TaskCollection()
        with path.open("r", encoding="utf-8") as f:
            return TaskCollection.from_json(json.load(f))

    def save_collection(self, collection: TaskCollection, name: str) -> None:
        path = self._tasks_file(name)
        with path.open("w", encoding="utf-8") as f:
            json.dump(collection.to_json(), f, indent=2)

    def load_project(self, name: str) -> Project:
        path = self._project_file(name)
        if not path.exists():
            raise TodoziError.project_not_found(name)
        with path.open("r", encoding="utf-8") as f:
            return Project.from_json(json.load(f))

    def save_project(self, project: Project) -> None:
        path = self._project_file(project.name)
        with path.open("w", encoding="utf-8") as f:
            json.dump(project.to_json(), f, indent=2)

    def list_project_names(self) -> List[str]:
        return [p.stem for p in self._dir("projects").glob("*.json")]


# =============================
# Tests
# =============================

def _create_test_storage() -> Tuple[tempfile.TemporaryDirectory, Storage]:
    tmpdir = tempfile.TemporaryDirectory()
    root = Path(tmpdir.name) / ".todozi"
    root.mkdir(parents=True, exist_ok=True)
    for d in ("tasks", "projects", "templates", "backups"):
        (root / d).mkdir(parents=True, exist_ok=True)

    config = Config.default()
    cfg_json = json.dumps(config.to_json(), indent=2)
    (root / "config.json").write_text(cfg_json, encoding="utf-8")

    project = Project(
        name="general",
        description="General tasks",
    )
    (root / "projects" / "general.json").write_text(json.dumps(project.to_json(), indent=2), encoding="utf-8")

    collection = TaskCollection()
    col_json = json.dumps(collection.to_json(), indent=2)
    (root / "tasks" / "active.json").write_text(col_json, encoding="utf-8")
    (root / "tasks" / "completed.json").write_text(col_json, encoding="utf-8")
    (root / "tasks" / "archived.json").write_text(col_json, encoding="utf-8")

    storage = Storage(root, config=config)
    return tmpdir, storage


class TaskModelTests:
    def test_task_creation(self):
        task = Task.new(
            assignee="user_123",
            action="Test task",
            time="1 hour",
            priority=Priority.Medium,
            parent_project="test-project",
            status=Status.Todo,
        )
        assert task.action == "Test task"
        assert task.time == "1 hour"
        assert task.priority == Priority.Medium
        assert task.parent_project == "test-project"
        assert task.status == Status.Todo
        assert task.id.startswith("task_")
        assert task.assignee == "user_123"  # new() assigns the provided assignee value
        assert task.tags == []
        assert task.dependencies == []
        assert task.context_notes is None
        assert task.progress is None

    def test_task_creation_full(self):
        task = Task.new_full(
            action="Test task",
            time="2 hours",
            priority=Priority.High,
            parent_project="test-project",
            status=Status.InProgress,
            assignee=Assignee.Human,
            tags=["test", "example"],
            dependencies=["task_001"],
            context_notes="Test context",
            progress=50,
        )
        assert task.action == "Test task"
        assert task.time == "2 hours"
        assert task.priority == Priority.High
        assert task.parent_project == "test-project"
        assert task.status == Status.InProgress
        assert task.assignee == Assignee.Human
        assert task.tags == ["test", "example"]
        assert task.dependencies == ["task_001"]
        assert task.context_notes == "Test context"
        assert task.progress == 50

    def test_task_creation_invalid_progress(self):
        try:
            Task.new_full(
                action="Test task",
                time="1 hour",
                priority=Priority.Medium,
                parent_project="test-project",
                status=Status.Todo,
                assignee=None,
                tags=[],
                dependencies=[],
                context_notes=None,
                progress=150,
            )
            assert False, "Expected TodoziError"
        except TodoziError as e:
            assert e.kind == "InvalidProgress"
            assert e.context["progress"] == 150

    def test_task_update(self):
        task = Task.new(
            assignee="user_123",
            action="Original task",
            time="1 hour",
            priority=Priority.Low,
            parent_project="test-project",
            status=Status.Todo,
        )
        updates = TaskUpdate.new() \
            .with_action("Updated task") \
            .with_priority(Priority.High) \
            .with_status(Status.InProgress) \
            .with_progress(75)
        # Use OOP API like Rust
        task.update(updates)
        assert task.action == "Updated task"
        assert task.priority == Priority.High
        assert task.status == Status.InProgress
        assert task.progress == 75

    def test_task_complete(self):
        task = Task.new(
            assignee="user_123",
            action="Test task",
            time="1 hour",
            priority=Priority.Medium,
            parent_project="test-project",
            status=Status.Todo,
        )
        task.complete()
        assert task.status == Status.Done
        assert task.progress == 100
        assert task.is_completed()

    def test_task_is_active(self):
        active_task = Task.new(
            assignee="user_123",
            action="Active task",
            time="1 hour",
            priority=Priority.Medium,
            parent_project="test-project",
            status=Status.Todo,
        )
        completed_task = Task.new(
            assignee="user_123",
            action="Completed task",
            time="1 hour",
            priority=Priority.Medium,
            parent_project="test-project",
            status=Status.Todo,
        )
        completed_task.complete()
        cancelled_task = Task.new(
            assignee="user_123",
            action="Cancelled task",
            time="1 hour",
            priority=Priority.Medium,
            parent_project="test-project",
            status=Status.Cancelled,
        )
        assert active_task.is_active()
        assert not completed_task.is_active()
        assert not cancelled_task.is_active()

    def test_priority_parsing(self):
        assert Priority.parse("low") == Priority.Low
        assert Priority.parse("medium") == Priority.Medium
        assert Priority.parse("high") == Priority.High
        assert Priority.parse("critical") == Priority.Critical
        assert Priority.parse("urgent") == Priority.Urgent
        try:
            Priority.parse("invalid")
            assert False, "Expected TodoziError"
        except TodoziError:
            pass

    def test_status_parsing(self):
        assert Status.parse("todo") == Status.Todo
        assert Status.parse("in_progress") == Status.InProgress
        assert Status.parse("in-progress") == Status.InProgress
        assert Status.parse("blocked") == Status.Blocked
        assert Status.parse("review") == Status.Review
        assert Status.parse("done") == Status.Done
        assert Status.parse("cancelled") == Status.Cancelled
        assert Status.parse("canceled") == Status.Cancelled
        assert Status.parse("deferred") == Status.Deferred
        try:
            Status.parse("invalid")
            assert False, "Expected TodoziError"
        except TodoziError:
            pass

    def test_assignee_parsing(self):
        assert Assignee.parse("ai") == Assignee.Ai
        assert Assignee.parse("human") == Assignee.Human
        assert Assignee.parse("collaborative") == Assignee.Collaborative
        try:
            Assignee.parse("invalid")
            assert False, "Expected TodoziError"
        except TodoziError:
            pass

    def test_project_creation(self):
        project = Project(
            name="test-project",
            description="Test project description",
        )
        assert project.name == "test-project"
        assert project.description == "Test project description"
        assert project.status == ProjectStatus.Active
        assert len(project.tasks) == 0

    def test_project_add_task(self):
        project = Project(name="test-project")
        project.add_task("task_001")
        project.add_task("task_002")
        project.add_task("task_001")
        assert len(project.tasks) == 2
        assert "task_001" in project.tasks
        assert "task_002" in project.tasks

    def test_project_remove_task(self):
        project = Project(name="test-project")
        project.add_task("task_001")
        project.add_task("task_002")
        project.remove_task("task_001")
        assert len(project.tasks) == 1
        assert "task_001" not in project.tasks
        assert "task_002" in project.tasks

    def test_project_archive(self):
        project = Project(name="test-project")
        project.archive()
        assert project.status == ProjectStatus.Archived

    def test_project_complete(self):
        project = Project(name="test-project")
        project.complete()
        assert project.status == ProjectStatus.Completed

    def test_task_collection(self):
        collection = TaskCollection.new()
        task1 = Task.new(
            assignee="user_123",
            action="Task 1",
            time="1 hour",
            priority=Priority.Low,
            parent_project="project1",
            status=Status.Todo,
        )
        task2 = Task.new(
            assignee="user_123",
            action="Task 2",
            time="2 hours",
            priority=Priority.High,
            parent_project="project2",
            status=Status.InProgress,
        )
        collection.add_task(task1)
        collection.add_task(task2)
        assert len(collection.tasks) == 2
        assert collection.get_task(task1.id) is not None
        assert collection.get_task(task2.id) is not None
        assert collection.get_task("nonexistent") is None
        all_tasks = collection.get_all_tasks()
        assert len(all_tasks) == 2
        removed = collection.remove_task(task1.id)
        assert removed is not None
        assert len(collection.tasks) == 1

    def test_task_collection_filtering(self):
        collection = TaskCollection.new()
        task1 = Task.new(
            assignee="user_123",
            action="Low priority task",
            time="1 hour",
            priority=Priority.Low,
            parent_project="project1",
            status=Status.Todo,
        )
        task2 = Task.new(
            assignee="user_123",
            action="High priority task",
            time="2 hours",
            priority=Priority.High,
            parent_project="project2",
            status=Status.InProgress,
        )
        collection.add_task(task1)
        collection.add_task(task2)
        high_priority_filter = TaskFilters(priority=Priority.High)
        high_priority_tasks = collection.get_filtered_tasks(high_priority_filter)
        assert len(high_priority_tasks) == 1
        assert high_priority_tasks[0].priority == Priority.High

        project1_filter = TaskFilters(project="project1")
        project1_tasks = collection.get_filtered_tasks(project1_filter)
        assert len(project1_tasks) == 1
        assert project1_tasks[0].parent_project == "project1"

        todo_filter = TaskFilters(status=Status.Todo)
        todo_tasks = collection.get_filtered_tasks(todo_filter)
        assert len(todo_tasks) == 1
        assert todo_tasks[0].status == Status.Todo

    def test_config_default(self):
        config = Config.default()
        assert config.version == "1.2.0"
        assert config.default_project == "general"
        assert config.auto_backup is True
        assert config.backup_interval == "daily"
        assert config.ai_enabled is True
        assert config.default_assignee == Assignee.Collaborative
        assert config.date_format == "%Y-%m-%d %H:%M:%S"
        assert config.timezone == "UTC"

    def test_task_update_validation(self):
        task = Task.new(
            assignee="user_123",
            action="Test task",
            time="1 hour",
            priority=Priority.Medium,
            parent_project="test-project",
            status=Status.Todo,
        )
        invalid_update = TaskUpdate.new().with_progress(150)
        try:
            invalid_update.apply_to(task)
            assert False, "Expected TodoziError"
        except TodoziError as e:
            assert e.kind == "InvalidProgress"
        valid_update = TaskUpdate.new().with_progress(75)
        valid_update.apply_to(task)
        assert task.progress == 75

    def test_error_types(self):
        e1 = TodoziError.task_not_found("test")
        assert "Task not found" in str(e1)
        e2 = TodoziError.invalid_priority("invalid")
        assert "Invalid priority" in str(e2)
        e3 = TodoziError.validation("Test validation error")
        assert "ValidationError" in str(e3)  # Error string format is "ValidationError: message"


if __name__ == "__main__":
    # Run the test suite defined in TaskModelTests
    import traceback

    suite = []
    test_methods = [m for m in dir(TaskModelTests) if m.startswith("test_")]
    runner = TaskModelTests()
    for name in test_methods:
        try:
            getattr(runner, name)()
            print(f"PASS {name}")
        except Exception as ex:
            print(f"FAIL {name}: {ex}")
            traceback.print_exc()
