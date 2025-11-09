from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from threading import Lock
from typing import Any, Dict, List, Optional, Pattern, Tuple, TypedDict, Union

# --------------------
# Enums and Typed Dicts
# --------------------

class ErrorSeverity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    URGENT = "urgent"

    @classmethod
    def _missing_(cls, value: object) -> Optional["ErrorSeverity"]:
        # Case-insensitive lookup by name
        if isinstance(value, str):
            for member in cls:
                if member.name.lower() == value.lower():
                    return member
        return None


class ErrorCategory(Enum):
    NETWORK = "network"
    VALIDATION = "validation"
    STORAGE = "storage"
    CONFIGURATION = "configuration"
    API = "api"
    EMBEDDING = "embedding"
    SYSTEM = "system"
    BUSINESS_LOGIC = "business_logic"

    @classmethod
    def _missing_(cls, value: object) -> Optional["ErrorCategory"]:
        if isinstance(value, str):
            for member in cls:
                if member.name.lower() == value.lower():
                    return member
        return None


API = "api"
BUSINESS_LOGIC = "business_logic"
CONFIGURATION = "configuration"
CRITICAL = "critical"
EMBEDDING = "embedding"
HIGH = "high"
LOW = "low"
MEDIUM = "medium"
NETWORK = "network"
STORAGE = "storage"
SYSTEM = "system"
URGENT = "urgent"
VALIDATION = "validation"


# Typed context dictionaries
class ValidationContext(TypedDict, total=False):
    field: str
    value: Any
    constraint: str


class StorageContext(TypedDict, total=False):
    storage_type: str
    path: str


class ConfigContext(TypedDict, total=False):
    config_key: str
    config_value: Any


class ApiContext(TypedDict, total=False):
    status_code: int
    response_data: Any
    endpoint: str


class NotFoundContext(TypedDict, total=False):
    id: str
    name: str


class InvalidAssigneeContext(TypedDict, total=False):
    assignee: str


class InvalidProgressContext(TypedDict, total=False):
    progress: int


class EmbeddingContext(TypedDict, total=False):
    model: str


class NotImplementedContext(TypedDict, total=False):
    feature: str


class DirContext(TypedDict, total=False):
    path: str


# --------------------
# Base Exception + Specific Errors
# --------------------

class TodoziError(Exception):
    """
    Base exception for the project. Provides:
    - error_code
    - context
    - timestamp
    - factory classmethods: validation, storage, config, api, io, serialization
    """

    def __init__(
        self,
        message: str,
        error_code: str = "UNKNOWN_ERROR",
        context: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.context = context or {}
        self.timestamp = datetime.now(timezone.utc)
        if cause:
            self.__cause__ = cause  # Support exception chaining

    def to_dict(self) -> Dict[str, Any]:
        return {
            "error_code": self.error_code,
            "message": self.message,
            "context": self.context,
            "timestamp": self.timestamp.isoformat(),
            "type": self.__class__.__name__,
        }

    def __str__(self) -> str:
        return f"[{self.error_code}] {self.message}"

    # Factory methods
    @classmethod
    def validation(cls, message: Union[str, ValidationContext]) -> "TodoziError":
        if isinstance(message, dict):
            ctx = message
            msg = ctx.get("message") or "Validation error"
        else:
            msg, ctx = message, {"message": message}
        return cls(msg, "VALIDATION_ERROR", ctx)

    @classmethod
    def storage(cls, message: Union[str, StorageContext]) -> "TodoziError":
        if isinstance(message, dict):
            ctx = message
            msg = ctx.get("message") or "Storage error"
        else:
            msg, ctx = message, {"message": message}
        return cls(msg, "STORAGE_ERROR", ctx)

    @classmethod
    def config(cls, message: Union[str, ConfigContext]) -> "TodoziError":
        if isinstance(message, dict):
            ctx = message
            msg = ctx.get("message") or "Configuration error"
        else:
            msg, ctx = message, {"message": message}
        return cls(msg, "CONFIGURATION_ERROR", ctx)

    @classmethod
    def api(cls, message: Union[str, ApiContext]) -> "TodoziError":
        if isinstance(message, dict):
            ctx = message
            msg = ctx.get("message") or "API error"
        else:
            msg, ctx = message, {"message": message}
        return cls(msg, "API_ERROR", ctx)

    @classmethod
    def io(cls, message: Union[str, Dict[str, Any]], cause: Optional[Exception] = None) -> "TodoziError":
        if isinstance(message, dict):
            ctx = message
            msg = ctx.get("message") or "IO error"
        else:
            msg, ctx = message, {"message": message}
        return cls(msg, "IO_ERROR", ctx, cause=cause)

    @classmethod
    def serialization(cls, message: Union[str, Dict[str, Any]], cause: Optional[Exception] = None) -> "TodoziError":
        if isinstance(message, dict):
            ctx = message
            msg = ctx.get("message") or "Serialization error"
        else:
            msg, ctx = message, {"message": message}
        return cls(msg, "SERIALIZATION_ERROR", ctx, cause=cause)


# Specific errors (with missing variants filled in)
class TaskNotFoundError(TodoziError):
    def __init__(self, task_id: str):
        super().__init__(
            f"Task not found: {task_id}",
            "TASK_NOT_FOUND",
            cast_context({"id": task_id}, NotFoundContext),
        )


class ProjectNotFoundError(TodoziError):
    def __init__(self, project_name: str):
        super().__init__(
            f"Project not found: {project_name}",
            "PROJECT_NOT_FOUND",
            cast_context({"name": project_name}, NotFoundContext),
        )


class FeelingNotFoundError(TodoziError):
    def __init__(self, feeling_id: str):
        super().__init__(
            f"Feeling not found: {feeling_id}",
            "FEELING_NOT_FOUND",
            cast_context({"id": feeling_id}, NotFoundContext),
        )


class InvalidPriorityError(TodoziError):
    def __init__(self, priority: str):
        super().__init__(
            f"Invalid priority: {priority}. Must be one of: low, medium, high, critical, urgent",
            "INVALID_PRIORITY",
            {"priority": priority, "valid_values": ["low", "medium", "high", "critical", "urgent"]},
        )


class InvalidStatusError(TodoziError):
    def __init__(self, status: str):
        super().__init__(
            f"Invalid status: {status}. Must be one of: todo, pending, in_progress, blocked, review, done, completed, cancelled, deferred",
            "INVALID_STATUS",
            {
                "status": status,
                "valid_values": ["todo", "pending", "in_progress", "blocked", "review", "done", "completed", "cancelled", "deferred"],
            },
        )


class InvalidAssigneeError(TodoziError):
    def __init__(self, assignee: str):
        super().__init__(
            f"Invalid assignee: {assignee}. Must be one of: ai, human, collaborative",
            "INVALID_ASSIGNEE",
            cast_context({"assignee": assignee}, InvalidAssigneeContext),
        )


class InvalidProgressError(TodoziError):
    def __init__(self, progress: int):
        super().__init__(
            f"Invalid progress: {progress}. Must be between 0 and 100",
            "INVALID_PROGRESS",
            cast_context({"progress": progress}, InvalidProgressContext),
        )


class EmbeddingError(TodoziError):
    def __init__(self, message: str, model: Optional[str] = None):
        ctx = cast_context({"message": message, "model": model}, EmbeddingContext)
        super().__init__(message, "EMBEDDING_ERROR", ctx)


class NotImplementedError_(TodoziError):
    def __init__(self, feature: str):
        super().__init__(
            f"Feature not implemented: {feature}",
            "NOT_IMPLEMENTED",
            cast_context({"feature": feature}, NotImplementedContext),
        )


class DirError(TodoziError):
    def __init__(self, message: str, path: Optional[str] = None):
        super().__init__(
            f"Directory error: {message}",
            "DIR_ERROR",
            cast_context({"message": message, "path": path}, DirContext),
        )


# Wrapper errors (From X for TodoziError)
class IoError(TodoziError):
    def __init__(self, cause: Exception):
        super().__init__(
            f"IO error: {cause}",
            "IO_ERROR",
            {"wrapped": str(cause)},
            cause=cause,
        )


class JsonError(TodoziError):
    def __init__(self, cause: Exception):
        super().__init__(
            f"JSON error: {cause}",
            "JSON_ERROR",
            {"wrapped": str(cause)},
            cause=cause,
        )


class UuidError(TodoziError):
    def __init__(self, cause: Exception):
        super().__init__(
            f"UUID error: {cause}",
            "UUID_ERROR",
            {"wrapped": str(cause)},
            cause=cause,
        )


class ChronoError(TodoziError):
    def __init__(self, cause: Exception):
        super().__init__(
            f"Chrono error: {cause}",
            "CHRONO_ERROR",
            {"wrapped": str(cause)},
            cause=cause,
        )


class DialoguerError(TodoziError):
    def __init__(self, cause: Exception):
        super().__init__(
            f"Dialoguer error: {cause}",
            "DIALOGUER_ERROR",
            {"wrapped": str(cause)},
            cause=cause,
        )


class HlxError(TodoziError):
    def __init__(self, cause: Exception):
        super().__init__(
            f"HLX error: {cause}",
            "HLX_ERROR",
            {"wrapped": str(cause)},
            cause=cause,
        )


class ReqwestError(TodoziError):
    def __init__(self, cause: Exception):
        super().__init__(
            f"Reqwest error: {cause}",
            "REQWEST_ERROR",
            {"wrapped": str(cause)},
            cause=cause,
        )


class CandleError(TodoziError):
    def __init__(self, message: Union[str, Exception]):
        msg = str(message) if isinstance(message, Exception) else message
        super().__init__(msg, "CANDLE_ERROR", {"message": msg})


# --------------------
# Error entity (dataclass)
# --------------------

@dataclass
class Error:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    severity: ErrorSeverity = ErrorSeverity.MEDIUM
    category: ErrorCategory = ErrorCategory.SYSTEM
    source: str = ""
    context: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    resolved: bool = False
    resolution: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        def iso(dt: Optional[datetime]) -> Optional[str]:
            return dt.isoformat() if dt else None

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "severity": self.severity.value,
            "category": self.category.value,
            "source": self.source,
            "context": self.context,
            "tags": self.tags,
            "resolved": self.resolved,
            "resolution": self.resolution,
            "created_at": iso(self.created_at),
            "updated_at": iso(self.updated_at),
            "resolved_at": iso(self.resolved_at),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Error":
        # Robust enum parsing
        severity_raw = (data.get("severity") or ErrorSeverity.MEDIUM.value)
        severity = _parse_enum(ErrorSeverity, severity_raw, ErrorSeverity.MEDIUM)

        category_raw = (data.get("category") or ErrorCategory.SYSTEM.value)
        category = _parse_enum(ErrorCategory, category_raw, ErrorCategory.SYSTEM)

        def parse_dt(key: str) -> Optional[datetime]:
            raw = data.get(key)
            if not raw:
                return None
            # Ensure timezone-aware ISO format
            try:
                return datetime.fromisoformat(raw)
            except Exception:
                # Fallback: attempt to parse naive as UTC
                try:
                    naive = datetime.fromisoformat(raw.replace("Z", "+00:00"))
                    if naive.tzinfo is None:
                        return naive.replace(tzinfo=timezone.utc)
                    return naive
                except Exception:
                    return None

        return cls(
            id=data.get("id"),
            title=data.get("title", ""),
            description=data.get("description", ""),
            severity=severity,
            category=category,
            source=data.get("source", ""),
            context=data.get("context"),
            tags=data.get("tags", []),
            resolved=data.get("resolved", False),
            resolution=data.get("resolution"),
            created_at=parse_dt("created_at") or datetime.now(timezone.utc),
            updated_at=parse_dt("updated_at") or datetime.now(timezone.utc),
            resolved_at=parse_dt("resolved_at"),
        )


# --------------------
# ErrorManager + Config
# --------------------

@dataclass
class ErrorManagerConfig:
    max_errors: int = 10000
    auto_cleanup_resolved: bool = True
    cleanup_interval_hours: int = 24


class ErrorManager:
    def __init__(self, config: Optional[ErrorManagerConfig] = None, logger: Optional[logging.Logger] = None):
        self.config = config or ErrorManagerConfig()
        self._lock = Lock()
        self.errors: Dict[str, Error] = {}
        self.logger = logger or logging.getLogger(__name__)
        self._last_cleanup: Optional[datetime] = None

    def _cleanup_if_needed(self) -> None:
        now = datetime.now(timezone.utc)
        if not self._last_cleanup:
            self._last_cleanup = now
            return

        if not self.config.auto_cleanup_resolved:
            return

        delta = now - self._last_cleanup
        if delta.total_seconds() >= self.config.cleanup_interval_hours * 3600:
            with self._lock:
                # Remove resolved errors if exceeding capacity
                if len(self.errors) > self.config.max_errors:
                    before = len(self.errors)
                    self.errors = {eid: e for eid, e in self.errors.items() if not e.resolved}
                    removed = before - len(self.errors)
                    if removed > 0:
                        self.logger.info(f"Auto-cleanup removed {removed} resolved errors.")
                self._last_cleanup = now

    def create_error(self, error: Error) -> str:
        with self._lock:
            self._cleanup_if_needed()
            if len(self.errors) >= self.config.max_errors and error.id not in self.errors:
                # Evict oldest unresolved first; if all resolved, delete oldest overall
                keys_sorted = sorted(self.errors.keys(), key=lambda k: self.errors[k].created_at)
                for k in keys_sorted:
                    if not self.errors[k].resolved:
                        del self.errors[k]
                        break
                else:
                    del self.errors[keys_sorted[0]]

            # Ensure IDs and timestamps
            if not error.id:
                error.id = str(uuid.uuid4())
            if not error.created_at:
                error.created_at = datetime.now(timezone.utc)
            error.updated_at = datetime.now(timezone.utc)

            self.errors[error.id] = error
            self.logger.error(
                f"Error {error.id}: {error.title}",
                extra=error.to_dict(),
            )
            return error.id

    def resolve_error(self, error_id: str, resolution: str) -> None:
        with self._lock:
            error = self.errors.get(error_id)
            if not error:
                raise TodoziError.validation({"message": f"Error {error_id} not found"})
            error.resolved = True
            error.resolution = resolution
            error.resolved_at = datetime.now(timezone.utc)
            error.updated_at = datetime.now(timezone.utc)
            self.logger.info(f"Resolved error {error_id} with: {resolution}")

    def get_unresolved_errors(self) -> List[Error]:
        with self._lock:
            return [e for e in self.errors.values() if not e.resolved]

    def get_errors_needing_attention(self) -> List[Error]:
        with self._lock:
            return [
                e
                for e in self.errors.values()
                if not e.resolved and e.severity in (ErrorSeverity.CRITICAL, ErrorSeverity.URGENT)
            ]

    def stats(self) -> Dict[str, int]:
        with self._lock:
            stats: Dict[str, int] = {}
            for e in self.errors.values():
                cat = e.category.value
                stats[cat] = stats.get(cat, 0) + 1
            return stats

    def export_errors_json(self, include_resolved: bool = True) -> str:
        with self._lock:
            items = [e.to_dict() for e in self.errors.values() if include_resolved or not e.resolved]
            return json.dumps(items, indent=2)


# --------------------
# Parser
# --------------------

ERROR_PATTERN: Pattern[str] = re.compile(r"<error>(.*?)</error>", re.DOTALL)

def parse_error_format(error_text: str) -> Error:
    match = ERROR_PATTERN.search(error_text)
    if not match:
        raise TodoziError.validation("Missing <error> or </error> tags")

    content = match.group(1)
    parts = [p.strip() for p in content.split(";")]
    if len(parts) < 5:
        raise TodoziError.validation(
            "Invalid error format: need at least 5 parts (title; description; severity; category; source)"
        )

    title = parts[0]
    description = parts[1]

    severity_str = parts[2]
    severity = _parse_enum(ErrorSeverity, severity_str)
    if severity is None:
        raise TodoziError.validation(f"Invalid error severity: '{severity_str}'")

    category_str = parts[3]
    category = _parse_enum(ErrorCategory, category_str)
    if category is None:
        raise TodoziError.validation(f"Invalid error category: '{category_str}'")

    source = parts[4]
    context = parts[5] if len(parts) > 5 and parts[5] else None

    tags: List[str] = []
    if len(parts) > 6 and parts[6]:
        tags = [t.strip() for t in parts[6].split(",") if t.strip()]

    return Error(
        title=title,
        description=description,
        severity=severity,
        category=category,
        source=source,
        context=context,
        tags=tags,
    )


def _parse_enum(enum_cls: type[Enum], raw: str, default: Optional[Enum] = None) -> Optional[Enum]:
    # Try exact match on .name or .value
    for member in enum_cls:  # type: ignore[assignment]
        if member.name.lower() == raw.lower() or member.value.lower() == raw.lower():
            return member
    return default


def cast_context(ctx: Dict[str, Any], typed: type[TypedDict]) -> Dict[str, Any]:
    # Ensures the context dict contains only the TypedDict keys (best effort).
    # We intentionally do not validate types to keep the function simple and compatible.
    return {k: ctx[k] for k in ctx if k in typed.__annotations__}


# --------------------
# Tests
# --------------------

def test_parse_error_format():
    text = (
        "<error>"
        "Database connection failed; "
        "Unable to connect to PostgreSQL database; "
        "critical; "
        "network; "
        "database-service; "
        "Connection timeout after 30 seconds; "
        "database,postgres,connection"
        "</error>"
    )
    err = parse_error_format(text)
    assert err.title == "Database connection failed"
    assert err.description == "Unable to connect to PostgreSQL database"
    assert err.severity == ErrorSeverity.CRITICAL
    assert err.category == ErrorCategory.NETWORK
    assert err.source == "database-service"
    assert err.context == "Connection timeout after 30 seconds"
    assert err.tags == ["database", "postgres", "connection"]
    assert err.resolved is False
    print("✅ test_parse_error_format passed")


def test_error_serde():
    e1 = Error(
        title="Serialization Test",
        description="Test serialization",
        severity=ErrorSeverity.HIGH,
        category=ErrorCategory.VALIDATION,
        source="pytest",
        context="Ctx",
        tags=["a", "b"],
    )
    d = e1.to_dict()
    e2 = Error.from_dict(d)
    assert e1.title == e2.title
    assert e1.description == e2.description
    assert e1.severity == e2.severity
    assert e1.category == e2.category
    assert e1.source == e2.source
    assert e1.context == e2.context
    assert e1.tags == e2.tags
    assert e1.resolved == e2.resolved
    # Timestamps might differ by milliseconds, but should be iso-parsable
    assert e1.created_at is not None
    assert e2.created_at is not None
    print("✅ test_error_serde passed")


def test_manager_stats_and_resolve():
    # Use a null logger to suppress test output
    null_logger = logging.getLogger("test")
    null_logger.setLevel(logging.CRITICAL)
    null_logger.addHandler(logging.NullHandler())
    
    mgr = ErrorManager(logger=null_logger)
    e1 = Error(title="e1", severity=ErrorSeverity.CRITICAL, category=ErrorCategory.STORAGE)
    e2 = Error(title="e2", severity=ErrorSeverity.URGENT, category=ErrorCategory.API)
    e3 = Error(title="e3", severity=ErrorSeverity.LOW, category=ErrorCategory.STORAGE)

    id1 = mgr.create_error(e1)
    id2 = mgr.create_error(e2)
    id3 = mgr.create_error(e3)

    stats = mgr.stats()
    assert stats["storage"] == 2
    assert stats["api"] == 1
    assert mgr.get_errors_needing_attention() == [e1, e2]

    mgr.resolve_error(id3, "Won't fix")
    assert mgr.get_unresolved_errors() == [e1, e2]
    print("✅ test_manager_stats_and_resolve passed")


def test_edge_parsing():
    # Missing severity
    try:
        parse_error_format("<error>A;B;bad;C;D;E;F</error>")
        assert False, "Should raise"
    except TodoziError as te:
        assert te.error_code == "VALIDATION_ERROR"
        assert "Invalid error severity" in te.message

    # Missing tags and context
    text = "<error>T;D;medium;storage;svc</error>"
    e = parse_error_format(text)
    assert e.tags == []
    assert e.context is None
    print("✅ test_edge_parsing passed")


def test_thread_safety():
    import threading
    # Use a null logger to suppress test output
    null_logger = logging.getLogger("test_thread")
    null_logger.setLevel(logging.CRITICAL)
    null_logger.addHandler(logging.NullHandler())
    
    mgr = ErrorManager(logger=null_logger)
    errors_created = []
    errors_resolved = []

    def create_batch():
        for _ in range(50):
            e = Error(title="thr", severity=ErrorSeverity.LOW, category=ErrorCategory.SYSTEM)
            eid = mgr.create_error(e)
            errors_created.append(eid)

    def resolve_batch():
        for _ in range(25):
            if errors_resolved:
                continue
            try:
                # Resolve the first half randomly
                for eid in list(mgr.errors.keys())[:25]:
                    mgr.resolve_error(eid, "ok")
                    errors_resolved.append(eid)
                    break
            except Exception:
                pass

    t1 = threading.Thread(target=create_batch)
    t2 = threading.Thread(target=resolve_batch)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    assert len(mgr.errors) <= mgr.config.max_errors
    print("✅ test_thread_safety passed")


# --------------------
# Demo / Example
# --------------------

def demo():
    # Basic usage
    mgr = ErrorManager(logger=logging.getLogger("todozi.demo"))
    logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s - %(message)s")

    e = Error(
        title="Disk full",
        description="No space left on device",
        severity=ErrorSeverity.CRITICAL,
        category=ErrorCategory.STORAGE,
        source="fsWatcher",
        context="Mount: /var/data",
        tags=["disk", "storage"],
    )
    eid = mgr.create_error(e)
    print(f"Created error: {eid}")

    mgr.resolve_error(eid, "Freed up 20GB")
    print(f"Unresolved count: {len(mgr.get_unresolved_errors())}")
    print(f"Stats: {mgr.stats()}")

    # Demonstrate error factories (caught for demo purposes)
    try:
        raise TodoziError.validation({"field": "email", "value": "not-an-email"})
    except TodoziError as err:
        print(f"Caught validation error: {err}")
        print(f"Error details: {err.to_dict()}")
    
    # Other examples (commented out, but available):
    # try:
    #     raise TodoziError.io("Failed to write file", cause=IOError("Permission denied"))
    # except TodoziError as err:
    #     print(f"Caught IO error: {err}")
    # 
    # try:
    #     raise CandleError("CUDA out of memory")
    # except TodoziError as err:
    #     print(f"Caught Candle error: {err}")


if __name__ == "__main__":
    test_parse_error_format()
    test_error_serde()
    test_manager_stats_and_resolve()
    test_edge_parsing()
    test_thread_safety()
    demo()
