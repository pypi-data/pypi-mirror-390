from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
from pathlib import Path
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set,
    Tuple,
    ValuesView,
    Union,
    cast,
)
from uuid import uuid4

import json

# -----------------------------
# Errors and Validation
# -----------------------------


class TodoziError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


def _ensure_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        raise TodoziError("Naive datetime encountered; timezone-aware (UTC) datetime required")
    return dt.astimezone(timezone.utc)


def _require_non_empty_content(content: str) -> None:
    if not content or not content.strip():
        raise TodoziError("Reminder content cannot be empty")


# -----------------------------
# Enums and Data Models
# -----------------------------


class ReminderPriority(Enum):
    Low = "low"
    Medium = "medium"
    High = "high"


class ReminderStatus(Enum):
    Pending = "pending"
    Active = "active"
    Completed = "completed"
    Cancelled = "cancelled"


@dataclass
class Reminder:
    id: str
    content: str
    remind_at: datetime
    priority: ReminderPriority
    status: ReminderStatus
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    def mark_completed(self) -> None:
        if self.status != ReminderStatus.Completed:
            self.status = ReminderStatus.Completed
            self.updated_at = datetime.now(timezone.utc)

    def mark_cancelled(self) -> None:
        if self.status != ReminderStatus.Cancelled:
            self.status = ReminderStatus.Cancelled
            self.updated_at = datetime.now(timezone.utc)

    def activate(self) -> None:
        if self.status == ReminderStatus.Pending:
            self.status = ReminderStatus.Active
            self.updated_at = datetime.now(timezone.utc)

    def __str__(self) -> str:
        return f"Reminder({self.id[:8]}): {self.content} ({self.status.value})"


@dataclass
class ReminderStatistics:
    total_reminders: int
    pending_reminders: int
    active_reminders: int
    overdue_reminders: int
    unique_tags: int

    def pending_percentage(self) -> float:
        if self.total_reminders == 0:
            return 0.0
        return (self.pending_reminders / self.total_reminders) * 100.0

    def active_percentage(self) -> float:
        if self.total_reminders == 0:
            return 0.0
        return (self.active_reminders / self.total_reminders) * 100.0

    def overdue_percentage(self) -> float:
        if self.total_reminders == 0:
            return 0.0
        return (self.overdue_reminders / self.total_reminders) * 100.0


# Builder-style (non-frozen) for ergonomic updates
@dataclass
class ReminderUpdate:
    content: Optional[str] = None
    remind_at: Optional[datetime] = None
    priority: Optional[ReminderPriority] = None
    status: Optional[ReminderStatus] = None
    tags: Optional[List[str]] = None

    @classmethod
    def new(cls) -> ReminderUpdate:
        return cls()

    def with_content(self, content: str) -> ReminderUpdate:
        self.content = content
        return self

    def with_remind_at(self, remind_at: datetime) -> ReminderUpdate:
        self.remind_at = _ensure_utc(remind_at)
        return self

    def with_priority(self, priority: ReminderPriority) -> ReminderUpdate:
        self.priority = priority
        return self

    def with_status(self, status: ReminderStatus) -> ReminderUpdate:
        self.status = status
        return self

    def with_tags(self, tags: List[str]) -> ReminderUpdate:
        self.tags = [t.strip() for t in tags if t and t.strip()] or None
        return self


# -----------------------------
# Core Manager
# -----------------------------


class ReminderManager:
    """
    Core reminder manager. Methods that were async in Rust are async here.
    All methods raise TodoziError on validation issues; no method returns None on error.
    """

    def __init__(self) -> None:
        self.reminders: Dict[str, Reminder] = {}
        self.reminder_tags: Dict[str, List[str]] = {}

    async def create_reminder(self, reminder: Reminder) -> str:
        _require_non_empty_content(reminder.content)
        reminder.remind_at = _ensure_utc(reminder.remind_at)
        if reminder.remind_at <= datetime.now(timezone.utc):
            raise TodoziError("Reminder time must be in the future")

        reminder.id = str(uuid4())
        now = datetime.now(timezone.utc)
        reminder.created_at = now
        reminder.updated_at = now

        self.reminder_tags[reminder.id] = list(reminder.tags)
        self.reminders[reminder.id] = reminder
        return reminder.id

    def get_reminder(self, reminder_id: str) -> Reminder:
        reminder = self.reminders.get(reminder_id)
        if reminder is None:
            raise TodoziError(f"Reminder {reminder_id} not found")
        return reminder

    def get_all_reminders(self) -> List[Reminder]:
        # Returns copies for API stability (avoid external mutation of internal state)
        return [r for r in self.reminders.values()]

    async def update_reminder(self, reminder_id: str, updates: ReminderUpdate) -> None:
        reminder = self.reminders.get(reminder_id)
        if reminder is None:
            raise TodoziError(f"Reminder {reminder_id} not found")

        if updates.content is not None:
            _require_non_empty_content(updates.content)
            reminder.content = updates.content

        if updates.remind_at is not None:
            remind_at = _ensure_utc(updates.remind_at)
            if remind_at <= datetime.now(timezone.utc):
                raise TodoziError("Reminder time must be in the future")
            reminder.remind_at = remind_at

        if updates.priority is not None:
            reminder.priority = updates.priority

        if updates.status is not None:
            reminder.status = updates.status

        if updates.tags is not None:
            reminder.tags = list(updates.tags)
            self.reminder_tags[reminder_id] = list(updates.tags)

        reminder.updated_at = datetime.now(timezone.utc)

    async def delete_reminder(self, reminder_id: str) -> None:
        if reminder_id not in self.reminders:
            raise TodoziError(f"Reminder {reminder_id} not found")
        del self.reminders[reminder_id]
        self.reminder_tags.pop(reminder_id, None)

    def search_reminders(self, query: str) -> List[Reminder]:
        q = query.lower()
        return [
            r
            for r in self.reminders.values()
            if q in r.content.lower() or any(q in t.lower() for t in r.tags)
        ]

    def get_reminders_by_priority(self, priority: ReminderPriority) -> List[Reminder]:
        return [r for r in self.reminders.values() if r.priority == priority]

    def get_reminders_by_status(self, status: ReminderStatus) -> List[Reminder]:
        return [r for r in self.reminders.values() if r.status == status]

    def get_reminders_by_tag(self, tag: str) -> List[Reminder]:
        tag_lc = tag.lower()
        return [
            r
            for r in self.reminders.values()
            if any(tag_lc == t.lower() for t in r.tags)
        ]

    def get_pending_reminders(self) -> List[Reminder]:
        return self.get_reminders_by_status(ReminderStatus.Pending)

    def get_active_reminders(self) -> List[Reminder]:
        return self.get_reminders_by_status(ReminderStatus.Active)

    def get_overdue_reminders(self) -> List[Reminder]:
        now = datetime.now(timezone.utc)
        return [
            r
            for r in self.reminders.values()
            if r.remind_at < now and r.status in (ReminderStatus.Pending, ReminderStatus.Active)
        ]

    def get_reminders_due_soon(self, duration: timedelta) -> List[Reminder]:
        now = datetime.now(timezone.utc)
        due_time = now + duration
        return [
            r
            for r in self.reminders.values()
            if now < r.remind_at <= due_time and r.status in (ReminderStatus.Pending, ReminderStatus.Active)
        ]

    def get_recent_reminders(self, limit: int) -> List[Reminder]:
        reminders = [r for r in self.reminders.values()]
        reminders.sort(key=lambda r: r.created_at, reverse=True)
        return reminders[:limit]

    def get_all_tags(self) -> List[str]:
        tags: Set[str] = set()
        for lst in self.reminder_tags.values():
            tags.update(lst)
        return sorted(tags)

    def get_tag_statistics(self) -> Dict[str, int]:
        stats: Dict[str, int] = defaultdict(int)
        for lst in self.reminder_tags.values():
            for tag in lst:
                stats[tag] += 1
        return dict(stats)

    def get_reminder_statistics(self) -> ReminderStatistics:
        total = len(self.reminders)
        pending = len(self.get_pending_reminders())
        active = len(self.get_active_reminders())
        overdue = len(self.get_overdue_reminders())
        unique_tags = len(self.get_all_tags())
        return ReminderStatistics(
            total_reminders=total,
            pending_reminders=pending,
            active_reminders=active,
            overdue_reminders=overdue,
            unique_tags=unique_tags,
        )

    async def mark_reminder_completed(self, reminder_id: str) -> None:
        r = self.reminders.get(reminder_id)
        if r is None:
            raise TodoziError(f"Reminder {reminder_id} not found")
        r.mark_completed()

    async def mark_reminder_cancelled(self, reminder_id: str) -> None:
        r = self.reminders.get(reminder_id)
        if r is None:
            raise TodoziError(f"Reminder {reminder_id} not found")
        r.mark_cancelled()

    async def activate_reminder(self, reminder_id: str) -> None:
        r = self.reminders.get(reminder_id)
        if r is None:
            raise TodoziError(f"Reminder {reminder_id} not found")
        r.activate()

    # --------- Observability: Listener interface ---------
    def add_listener(self, callback: Callable[[str, str], None]) -> None:
        # event: create|update|delete|status_change|activate|complete|cancel
        if not hasattr(self, "_listeners"):
            self._listeners: List[Callable[[str, str], None]] = []
        self._listeners.append(callback)

    def _notify_listeners(self, event: str, reminder_id: str) -> None:
        listeners = getattr(self, "_listeners", [])
        for cb in listeners:
            try:
                cb(event, reminder_id)
            except Exception:
                # Avoid breaking manager on listener failure
                pass

    # Override mutating methods to notify
    async def _notify_create(self, reminder_id: str) -> None:
        self._notify_listeners("create", reminder_id)

    async def _notify_update(self, reminder_id: str) -> None:
        self._notify_listeners("update", reminder_id)

    async def _notify_delete(self, reminder_id: str) -> None:
        self._notify_listeners("delete", reminder_id)

    async def _notify_status(self, reminder_id: str, status: ReminderStatus) -> None:
        self._notify_listeners(f"status_change:{status.value}", reminder_id)

    async def _notify_activate(self, reminder_id: str) -> None:
        self._notify_listeners("activate", reminder_id)

    async def _notify_complete(self, reminder_id: str) -> None:
        self._notify_listeners("complete", reminder_id)

    async def _notify_cancel(self, reminder_id: str) -> None:
        self._notify_listeners("cancel", reminder_id)


# Monkey-patch notification-aware wrappers to avoid duplicating code
def _patch_notifications(manager: ReminderManager) -> None:
    original_create = manager.create_reminder
    original_update = manager.update_reminder
    original_delete = manager.delete_reminder
    original_mark_completed = manager.mark_reminder_completed
    original_mark_cancelled = manager.mark_reminder_cancelled
    original_activate = manager.activate_reminder

    async def create_reminder_and_notify(reminder: Reminder) -> str:
        rid = await original_create(reminder)
        await manager._notify_create(rid)
        return rid

    async def update_reminder_and_notify(reminder_id: str, updates: ReminderUpdate) -> None:
        await original_update(reminder_id, updates)
        await manager._notify_update(reminder_id)

    async def delete_reminder_and_notify(reminder_id: str) -> None:
        await original_delete(reminder_id)
        await manager._notify_delete(reminder_id)

    async def mark_completed_and_notify(reminder_id: str) -> None:
        await original_mark_completed(reminder_id)
        r = manager.reminders.get(reminder_id)
        if r:
            await manager._notify_status(reminder_id, r.status)
            await manager._notify_complete(reminder_id)

    async def mark_cancelled_and_notify(reminder_id: str) -> None:
        await original_mark_cancelled(reminder_id)
        r = manager.reminders.get(reminder_id)
        if r:
            await manager._notify_status(reminder_id, r.status)
            await manager._notify_cancel(reminder_id)

    async def activate_and_notify(reminder_id: str) -> None:
        await original_activate(reminder_id)
        r = manager.reminders.get(reminder_id)
        if r:
            await manager._notify_status(reminder_id, r.status)
            await manager._notify_activate(reminder_id)

    manager.create_reminder = create_reminder_and_notify  # type: ignore[assignment]
    manager.update_reminder = update_reminder_and_notify  # type: ignore[assignment]
    manager.delete_reminder = delete_reminder_and_notify  # type: ignore[assignment]
    manager.mark_reminder_completed = mark_completed_and_notify  # type: ignore[assignment]
    manager.mark_reminder_cancelled = mark_cancelled_and_notify  # type: ignore[assignment]
    manager.activate_reminder = activate_and_notify  # type: ignore[assignment]


# -----------------------------
# Persistent Manager (Optional)
# -----------------------------


class PersistentReminderManager(ReminderManager):
    def __init__(self, storage_path: Path) -> None:
        super().__init__()
        self.storage_path = storage_path
        self._load()

    def save(self) -> None:
        data = {
            "reminders": [
                {
                    "id": r.id,
                    "content": r.content,
                    "remind_at": r.remind_at.isoformat(),
                    "priority": r.priority.value,
                    "status": r.status.value,
                    "tags": r.tags,
                    "created_at": r.created_at.isoformat(),
                    "updated_at": r.updated_at.isoformat(),
                }
                for r in self.reminders.values()
            ]
        }
        tmp_path = self.storage_path.with_suffix(self.storage_path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        tmp_path.replace(self.storage_path)

    def _load(self) -> None:
        if not self.storage_path.exists():
            return
        with self.storage_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        reminders = data.get("reminders", [])
        for item in reminders:
            try:
                r = Reminder(
                    id=item["id"],
                    content=item["content"],
                    remind_at=datetime.fromisoformat(item["remind_at"]).astimezone(timezone.utc),
                    priority=ReminderPriority(item["priority"]),
                    status=ReminderStatus(item["status"]),
                    tags=item.get("tags", []),
                    created_at=datetime.fromisoformat(item["created_at"]).astimezone(timezone.utc),
                    updated_at=datetime.fromisoformat(item["updated_at"]).astimezone(timezone.utc),
                )
                self.reminders[r.id] = r
                self.reminder_tags[r.id] = list(r.tags)
            except Exception as e:
                # Continue loading despite malformed entries
                print(f"[WARN] Failed to load reminder {item.get('id', '?')}: {e}")


# -----------------------------
# Enhanced Manager
# -----------------------------


class EnhancedReminderManager(ReminderManager):
    """
    Adds useful features like JSON export/import and batch ops.
    """

    def get_reminders_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Reminder]:
        start = _ensure_utc(start_time)
        end = _ensure_utc(end_time)
        return [r for r in self.reminders.values() if start <= r.remind_at <= end]

    def get_reminders_by_multiple_tags(self, tags: List[str]) -> List[Reminder]:
        tags_lc = [t.lower() for t in tags]
        return [
            r
            for r in self.reminders.values()
            if any(t.lower() in tags_lc for t in r.tags)
        ]

    def get_reminder_categories(self) -> Dict[str, List[Reminder]]:
        categories: Dict[str, List[Reminder]] = defaultdict(list)
        for r in self.reminders.values():
            key = r.tags[0].capitalize() if r.tags else "Uncategorized"
            categories[key].append(r)
        return dict(categories)

    def bulk_update_status(
        self,
        reminder_ids: List[str],
        new_status: ReminderStatus,
    ) -> Dict[str, bool]:
        results: Dict[str, bool] = {}
        for rid in reminder_ids:
            r = self.reminders.get(rid)
            if r is None:
                results[rid] = False
                continue
            try:
                r.status = new_status
                r.updated_at = datetime.now(timezone.utc)
                results[rid] = True
            except Exception:
                results[rid] = False
        return results

    def export_reminders_to_json(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": r.id,
                "content": r.content,
                "remind_at": r.remind_at.isoformat(),
                "priority": r.priority.value,
                "status": r.status.value,
                "tags": r.tags,
                "created_at": r.created_at.isoformat(),
                "updated_at": r.updated_at.isoformat(),
            }
            for r in self.reminders.values()
        ]

    def import_reminders_from_json(self, reminders_data: List[Dict[str, Any]]) -> List[str]:
        imported_ids: List[str] = []
        for item in reminders_data:
            try:
                r = Reminder(
                    id=item.get("id", str(uuid4())),
                    content=item["content"],
                    remind_at=datetime.fromisoformat(item["remind_at"]).astimezone(timezone.utc),
                    priority=ReminderPriority(item["priority"]),
                    status=ReminderStatus(item["status"]),
                    tags=item.get("tags", []),
                    created_at=datetime.fromisoformat(item["created_at"]).astimezone(timezone.utc),
                    updated_at=datetime.fromisoformat(item["updated_at"]).astimezone(timezone.utc),
                )
                self.reminders[r.id] = r
                self.reminder_tags[r.id] = list(r.tags)
                imported_ids.append(r.id)
            except Exception as e:
                print(f"[WARN] Failed to import reminder: {e}")
        return imported_ids


# Optional: context manager for batch operations
from contextlib import contextmanager


@contextmanager
def batch_update(manager: ReminderManager):
    """
    Context manager for batch updates. Provides hooks for future optimization.
    For example, you could defer notifications or coalesce multiple updates.
    """
    try:
        yield manager
    finally:
        # Perform any batch cleanup here if needed in the future
        pass


# -----------------------------
# Parser (string -> Reminder)
# -----------------------------


def parse_reminder_format(reminder_text: str) -> Reminder:
    start_tag = "<reminder>"
    end_tag = "</reminder>"

    start_idx = reminder_text.find(start_tag)
    if start_idx == -1:
        raise TodoziError("Missing <reminder> start tag")
    end_idx = reminder_text.find(end_tag)
    if end_idx == -1:
        raise TodoziError("Missing </reminder> end tag")

    content_part = reminder_text[start_idx + len(start_tag) : end_idx]
    parts = [p.strip() for p in content_part.split(";")]
    if len(parts) < 3:
        raise TodoziError("Invalid reminder format: need at least 3 parts (content; remind_at; priority)")

    # Parse remind_at
    try:
        # Accepts ISO 8601. If it ends with 'Z', replace with '+00:00' for fromisoformat
        dt_raw = parts[1]
        if dt_raw.endswith("Z"):
            dt_raw = dt_raw[:-1] + "+00:00"
        remind_at = _ensure_utc(datetime.fromisoformat(dt_raw))
    except Exception:
        raise TodoziError("Invalid reminder date format")

    # Parse priority
    try:
        priority = ReminderPriority(parts[2].lower())
    except Exception:
        raise TodoziError("Invalid reminder priority")

    # Parse optional status
    status = ReminderStatus.Pending
    if len(parts) > 3 and parts[3]:
        try:
            status = ReminderStatus(parts[3].lower())
        except Exception:
            raise TodoziError("Invalid reminder status")

    # Parse optional tags
    tags: List[str] = []
    if len(parts) > 4 and parts[4]:
        tags = [t.strip() for t in parts[4].split(",") if t and t.strip()]

    now = datetime.now(timezone.utc)
    return Reminder(
        id=str(uuid4()),
        content=parts[0],
        remind_at=remind_at,
        priority=priority,
        status=status,
        tags=tags,
        created_at=now,
        updated_at=now,
    )


# -----------------------------
# Example usage / quick demo
# -----------------------------

async def _demo() -> None:
    # Initialize manager and patch for notifications
    manager = EnhancedReminderManager()
    _patch_notifications(manager)

    # Add a listener
    def on_event(event: str, rid: str) -> None:
        print(f"[Listener] event={event} reminder_id={rid}")

    manager.add_listener(on_event)

    # Create reminder
    r1 = Reminder(
        id="",
        content="Review project proposal",
        remind_at=datetime.now(timezone.utc) + timedelta(hours=2),
        priority=ReminderPriority.High,
        status=ReminderStatus.Pending,
        tags=["review", "project", "deadline"],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    rid1 = await manager.create_reminder(r1)
    print(f"Created reminder: {rid1}")

    # Update reminder
    await manager.update_reminder(
        rid1,
        ReminderUpdate.new().with_content("Review project proposal (updated)").with_priority(ReminderPriority.Medium),
    )

    # Activate
    await manager.activate_reminder(rid1)

    # Due soon
    due_soon = manager.get_reminders_due_soon(timedelta(hours=3))
    print(f"Due soon: {len(due_soon)}")

    # Search
    found = manager.search_reminders("project")
    print(f"Search results: {len(found)}")

    # Statistics
    stats = manager.get_reminder_statistics()
    print(f"Stats: {stats}")

    # Bulk update
    manager.bulk_update_status([rid1], ReminderStatus.Completed)
    print(f"Final status: {manager.get_reminder(rid1).status.value}")

    # Export / Import
    exported = manager.export_reminders_to_json()
    print(f"Exported: {len(exported)} reminders")


if __name__ == "__main__":
    asyncio.run(_demo())
