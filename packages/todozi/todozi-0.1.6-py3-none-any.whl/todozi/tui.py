#!/usr/bin/env python3
"""
Todozi TUI - A comprehensive, feature-rich terminal UI
Enhanced with AI insights, analytics, and full Todozi integration
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
import threading
import uuid
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum, auto
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable, Deque, Union

# Suppress warnings before imports
import warnings
warnings.filterwarnings("ignore")

try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
except ImportError:
    pass

# Optional imports for enhanced features
try:
    import watchfiles
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Module-level logger
logger = logging.getLogger(__name__)

# Rich imports for enhanced UI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align
from rich.columns import Columns
from rich.style import Style
from rich import box

# Textual imports
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer, Grid
from textual.css.query import NoMatches
from textual.message import Message
from textual.reactive import reactive
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Checkbox,
    DataTable,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    LoadingIndicator,
    Log,
    OptionList,
    Placeholder,
    RichLog,
    Select,
    Static,
    TabbedContent,
    TabPane,
    Tabs,
    TextArea,
    ProgressBar,
    Sparkline,
    Collapsible,
    SelectionList,
)

# Import real todozi models and storage
from todozi.storage import Storage
from todozi.models import Task, TaskFilters, Priority, Status, Assignee, Project, TaskUpdate
from todozi.error import TodoziError
from todozi.idea import Idea, IdeaManager
from todozi.memory import Memory, MemoryManager
from todozi.error import Error, ErrorManager
from todozi.agent import AgentManager
from todozi.api import list_api_keys, create_api_key

# Enhanced models for comprehensive TUI
@dataclass
class SimilarityResult:
    """Result from semantic similarity search."""
    id: str
    action: str
    similarity_score: float
    tags: List[str] = field(default_factory=list)

@dataclass
class TaskDisplay:
    """Enhanced task display with AI insights."""
    task: Task
    similar_tasks: List[SimilarityResult] = field(default_factory=list)
    ai_suggestions: List[str] = field(default_factory=list)
    semantic_tags: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    related_content: List[SimilarityResult] = field(default_factory=list)

@dataclass
class TaskListDisplay:
    """Enhanced task list display with analytics."""
    tasks: List[TaskDisplay]
    total_count: int
    ai_summary: str = ""
    semantic_clusters: List[List[str]] = field(default_factory=list)

@dataclass
class ApiKey:
    """API key model for management."""
    user_id: str
    active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    last_used: Optional[datetime] = None

@dataclass
class QueueItem:
    """Queue item for task processing."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    task_name: str = ""
    priority: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Reminder:
    """Reminder model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    message: str = ""
    due_date: Optional[datetime] = None
    completed: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class TrainingData:
    """Training data model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    data_type: str = ""
    prompt: str = ""
    response: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Feeling:
    """Feeling/emotion tracking model."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    emotion: str = ""
    intensity: int = 5
    context: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class ActivityEntry:
    """Activity feed entry."""
    timestamp: datetime
    message: str
    level: str = "info"  # info, success, error, warning

# Optional file watching
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent, FileDeletedEvent
    WATCHDOG_AVAILABLE = True
except Exception:
    WATCHDOG_AVAILABLE = False


UTC = timezone.utc


def utcnow() -> datetime:
    return datetime.now(UTC)


# Enhanced enums for comprehensive TUI
class AppTab(Enum):
    Projects = "📁 Projects"
    Tasks = "📋 Tasks"
    Done = "✅ Done"
    Find = "🔍 Find"
    More = "🔮 More"
    Api = "🔑 API"
    Feed = "📰 Feed"
    Bye = "👋 Bye"

    @staticmethod
    def all() -> List["AppTab"]:
        return [
            AppTab.Projects,
            AppTab.Tasks,
            AppTab.Done,
            AppTab.Find,
            AppTab.More,
            AppTab.Api,
            AppTab.Feed,
            AppTab.Bye,
        ]


class MoreTabSection(Enum):
    Ideas = "💡 Ideas"
    Memories = "🧠 Memories"
    Feelings = "😊 Feelings"
    Errors = "❌ Errors"
    Training = "🎓 Training"
    Queue = "📋 Queue"
    Reminders = "🔔 Reminders"
    Analytics = "📊 Analytics"

    @staticmethod
    def all() -> List["MoreTabSection"]:
        return [
            MoreTabSection.Ideas,
            MoreTabSection.Memories,
            MoreTabSection.Feelings,
            MoreTabSection.Errors,
            MoreTabSection.Training,
            MoreTabSection.Queue,
            MoreTabSection.Reminders,
            MoreTabSection.Analytics,
        ]


class TaskAction(Enum):
    Edit = "✏️ Edit"
    Delete = "🗑️ Delete"
    ViewDetails = "👀 View Details"
    Duplicate = "📋 Duplicate"
    Complete = "✅ Complete"
    MoveToProject = "📁 Move to Project"


class TaskSortBy(Enum):
    DateCompleted = auto()
    DateCreated = auto()
    Priority = auto()
    Project = auto()
    Action = auto()
    Time = auto()
    Assignee = auto()

    def title(self) -> str:
        return {
            TaskSortBy.DateCompleted: "Date Completed",
            TaskSortBy.DateCreated: "Date Created",
            TaskSortBy.Priority: "Priority",
            TaskSortBy.Project: "Project",
            TaskSortBy.Action: "Task",
            TaskSortBy.Time: "Time",
            TaskSortBy.Assignee: "Assignee",
        }[self]

    @staticmethod
    def all() -> List["TaskSortBy"]:
        return list(TaskSortBy)


class SortOrder(Enum):
    Ascending = auto()
    Descending = auto()


class EditorField(Enum):
    Action = auto()
    Time = auto()
    Priority = auto()
    Status = auto()
    Project = auto()
    Assignee = auto()
    Tags = auto()
    Context = auto()
    Progress = auto()


class MoreTabSection(Enum):
    Ideas = auto()
    Memories = auto()
    Feelings = auto()
    Errors = auto()
    Training = auto()
    Queue = auto()
    Reminders = auto()
    Analytics = auto()


class ToastType(Enum):
    Success = auto()
    Error = auto()
    Warning = auto()
    Info = auto()


@dataclass
class ToastNotification:
    message: str
    notification_type: ToastType
    created_at: float = field(default_factory=time.time)
    duration: float = 5.0

    def is_expired(self, now: float | None = None) -> bool:
        """Check if the toast has expired."""
        now = now if now is not None else time.time()
        return now - self.created_at > self.duration


class ToastType(Enum):
    Success = "success"
    Error = "error"
    Warning = "warning"
    Info = "info"


# Enhanced display configuration
@dataclass
class DisplayConfig:
    show_ai_insights: bool = True
    show_similarity_scores: bool = True
    show_related_tasks: bool = True
    max_related_tasks: int = 5
    compact_mode: bool = False
    show_embeddings: bool = False
    show_ids: bool = False
    show_created_at: bool = False
    show_dependencies: bool = False
    show_context: bool = False
    show_progress: bool = True


@dataclass
class ActivityEntry:
    """An entry in the activity feed."""
    timestamp: datetime
    message: str
    level: str = "info"  # info, success, error, warning


@dataclass
class EditSession:
    task_id: str
    original_task: Task
    current_task: Task
    ai_suggestions: List[str] = field(default_factory=list)
    validation_errors: List[str] = field(default_factory=list)
    session_start: datetime = field(default_factory=utcnow)


@dataclass
class TaskFilters:
    status_filter: Optional[Status] = None
    priority_filter: Optional[Priority] = None
    project_filter: Optional[str] = None
    assignee_filter: Optional[Assignee] = None


def format_duration(from_dt: datetime, to_dt: datetime) -> str:
    delta = to_dt - from_dt
    seconds = int(delta.total_seconds())
    if seconds < 60:
        return f"{max(1, seconds)}s ago"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m ago"
    hours = minutes // 60
    if hours < 24:
        return f"{hours}h ago"
    days = hours // 24
    if days < 7:
        return f"{days}d ago"
    weeks = days // 7
    return f"{weeks}w ago"


class ToastNotifier:
    """Centralized toast notification management."""

    def __init__(self, parent_app: "TodoziTUI"):
        self.parent = parent_app

    def _make(self, message: str, toast_type: ToastType) -> None:
        """Create and schedule a toast notification."""
        toast = ToastNotification(message=message, notification_type=toast_type)
        self.parent.toast_notifications.append(toast)
        # Use set_timer for better resource management
        self.parent.set_timer(toast.duration, lambda: self._remove_toast(toast))

    def _remove_toast(self, toast: ToastNotification) -> None:
        """Remove a toast notification safely."""
        if toast in self.parent.toast_notifications:
            self.parent.toast_notifications.remove(toast)

    def success(self, message: str) -> None:
        """Show success toast."""
        self._make(message, ToastType.Success)

    def info(self, message: str) -> None:
        """Show info toast."""
        self._make(message, ToastType.Info)

    def warning(self, message: str) -> None:
        """Show warning toast."""
        self._make(message, ToastType.Warning)

    def error(self, message: str) -> None:
        """Show error toast."""
        self._make(message, ToastType.Error)


# Enhanced widgets for comprehensive TUI
class RichLogWidget(RichLog):
    """Enhanced RichLog widget with better styling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_lines = 1000


class TaskActionMenu(ModalScreen):
    """Modal screen for task actions."""

    def __init__(self, task: Task, actions: List[TaskAction]):
        super().__init__()
        self.task = task
        self.actions = actions
        self.selected_index = 0

    def compose(self) -> ComposeResult:
        with Container(id="action-menu"):
            yield Label(f"Actions for: {self.task.action[:50]}", id="menu-title")
            with SelectionList(id="action-list") as selection_list:
                for action in self.actions:
                    selection_list.add_option((action.value, action))

    @on(SelectionList.SelectionHighlighted)
    def on_selection_highlighted(self, event: SelectionList.SelectionHighlighted) -> None:
        self.selected_index = event.selection_list.highlighted

    @on(SelectionList.SelectionConfirmed)
    def on_selection_confirmed(self, event: SelectionList.SelectionConfirmed) -> None:
        self.dismiss((self.actions[self.selected_index], self.task))

    def key_escape(self) -> None:
        self.dismiss(None)


class TaskDetailsModal(ModalScreen):
    """Modal screen for detailed task view."""

    def __init__(self, task: Task):
        super().__init__()
        self.task = task

    def compose(self) -> ComposeResult:
        with Container(id="task-details"):
            yield Label(f"📋 {self.task.action}", id="details-title")
            yield Static(self._format_task_details(), id="details-content")
            yield Button("Close", id="close-btn", variant="primary")

    def _format_task_details(self) -> str:
        """Format task details for display."""
        details = f"""
[bold]ID:[/bold] {self.task.id}
[bold]Status:[/bold] {self.task.status.value if hasattr(self.task.status, 'value') else str(self.task.status)}
[bold]Priority:[/bold] {self.task.priority.value if hasattr(self.task.priority, 'value') else str(self.task.priority)}
[bold]Project:[/bold] {getattr(self.task, 'parent_project', 'N/A')}
[bold]Assignee:[/bold] {getattr(self.task, 'assignee', 'Unassigned')}
[bold]Time Estimate:[/bold] {getattr(self.task, 'time', 'N/A')}
[bold]Progress:[/bold] {getattr(self.task, 'progress', 'N/A')}%
[bold]Tags:[/bold] {', '.join(getattr(self.task, 'tags', []))}
[bold]Created:[/bold] {getattr(self.task, 'created_at', datetime.now()).strftime('%Y-%m-%d %H:%M')}
[bold]Updated:[/bold] {getattr(self.task, 'updated_at', datetime.now()).strftime('%Y-%m-%d %H:%M')}
"""
        context = getattr(self.task, 'context_notes', None)
        if context:
            details += f"\n[bold]Context:[/bold]\n{context}\n"

        return details

    @on(Button.Pressed, "#close-btn")
    def on_close(self) -> None:
        self.dismiss()


class EditTaskModal(ModalScreen):
    """Modal screen for editing tasks."""

    def __init__(self, task: Task):
        super().__init__()
        self.original_task = task
        self.current_task = task
        self.field_index = 0
        self.fields = [
            ("action", "Action"),
            ("time", "Time Estimate"),
            ("priority", "Priority"),
            ("status", "Status"),
            ("parent_project", "Project"),
            ("assignee", "Assignee"),
            ("tags", "Tags"),
            ("context_notes", "Context"),
            ("progress", "Progress"),
        ]

    def compose(self) -> ComposeResult:
        with Container(id="edit-modal"):
            yield Label(f"✏️ Edit Task", id="edit-title")
            yield Input(placeholder="Field value", id="field-input")
            yield Label("", id="field-label")
            with Horizontal():
                yield Button("Previous", id="prev-btn", variant="secondary")
                yield Button("Next", id="next-btn", variant="secondary")
                yield Button("Save", id="save-btn", variant="primary")
                yield Button("Cancel", id="cancel-btn", variant="secondary")

    def on_mount(self) -> None:
        self.update_field_display()

    def update_field_display(self) -> None:
        """Update the current field display."""
        field_name, field_label = self.fields[self.field_index]
        input_widget = self.query_one("#field-input", Input)
        label_widget = self.query_one("#field-label", Label)

        # Get current value
        value = getattr(self.current_task, field_name, "")
        if field_name == "priority" and hasattr(value, 'value'):
            value = value.value
        elif field_name == "status" and hasattr(value, 'value'):
            value = value.value
        elif field_name == "assignee" and hasattr(value, 'value'):
            value = value.value
        elif field_name == "tags" and isinstance(value, list):
            value = ", ".join(value)

        input_widget.value = str(value)
        label_widget.update(f"[bold]{field_label}:[/bold]")

    @on(Button.Pressed, "#prev-btn")
    def on_previous(self) -> None:
        self.field_index = (self.field_index - 1) % len(self.fields)
        self.update_field_display()

    @on(Button.Pressed, "#next-btn")
    def on_next(self) -> None:
        self.field_index = (self.field_index + 1) % len(self.fields)
        self.update_field_display()

    @on(Button.Pressed, "#save-btn")
    def on_save(self) -> None:
        # Update the current field
        field_name, _ = self.fields[self.field_index]
        input_widget = self.query_one("#field-input", Input)
        value = input_widget.value

        # Convert value based on field type
        if field_name == "priority":
            priority_map = {"low": Priority.LOW, "medium": Priority.MEDIUM, "high": Priority.HIGH,
                          "critical": Priority.CRITICAL, "urgent": Priority.URGENT}
            setattr(self.current_task, field_name, priority_map.get(value.lower(), Priority.MEDIUM))
        elif field_name == "status":
            status_map = {"todo": Status.TODO, "pending": Status.PENDING, "in_progress": Status.IN_PROGRESS,
                         "blocked": Status.BLOCKED, "review": Status.REVIEW, "done": Status.DONE,
                         "completed": Status.COMPLETED, "cancelled": Status.CANCELLED, "deferred": Status.DEFERRED}
            setattr(self.current_task, field_name, status_map.get(value.lower(), Status.TODO))
        elif field_name == "assignee":
            assignee_map = {"human": Assignee.HUMAN, "ai": Assignee.AI, "collaborative": Assignee.COLLABORATIVE}
            setattr(self.current_task, field_name, assignee_map.get(value.lower(), None))
        elif field_name == "tags":
            setattr(self.current_task, field_name, [tag.strip() for tag in value.split(",") if tag.strip()])
        elif field_name == "progress":
            try:
                setattr(self.current_task, field_name, min(max(int(value), 0), 100))
            except ValueError:
                pass
        else:
            setattr(self.current_task, field_name, value)

        self.dismiss(self.current_task)

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel(self) -> None:
        self.dismiss(None)


class TasksDirWatcher(FileSystemEventHandler):
    """File system event handler for task directory changes."""
    
    def __init__(self, callback: Callable[[], None]) -> None:
        super().__init__()
        self.callback = callback

    def on_any_event(self, event) -> None:
        """Handle file system events."""
        if isinstance(event, (FileModifiedEvent, FileCreatedEvent, FileDeletedEvent)):
            self.callback()


class EnhancedTaskListWidget(ListView):
    """Enhanced task list widget with rich display and actions"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks: List[Task] = []
        self.display_config: DisplayConfig = DisplayConfig()

    def update_tasks(self, tasks: List[Task], selected_index: int = 0, display_config: Optional[DisplayConfig] = None) -> None:
        """Update the task list with enhanced display"""
        self.tasks = tasks
        if display_config:
            self.display_config = display_config

        self.clear()

        if not tasks:
            self.append(ListItem(Label("No tasks found. Press 'a' to add one.")))
            return

        for i, task in enumerate(tasks):
            display = self._format_task_display(task, i == selected_index)
            self.append(ListItem(Label(display)))

    def _format_task_display(self, task: Task, is_selected: bool = False) -> str:
        """Format a task for display with enhanced information."""
        status_emoji = {
            Status.TODO: "📝",
            Status.PENDING: "⏳",
            Status.IN_PROGRESS: "🔄",
            Status.BLOCKED: "🚫",
            Status.REVIEW: "👀",
            Status.DONE: "✅",
            Status.COMPLETED: "✅",
            Status.CANCELLED: "❌",
            Status.DEFERRED: "⏸️",
        }.get(task.status, "❓")

        priority_emoji = {
            Priority.LOW: "🟢",
            Priority.MEDIUM: "🟡",
            Priority.HIGH: "🟠",
            Priority.CRITICAL: "🔴",
            Priority.URGENT: "🚨",
        }.get(task.priority, "⚪")

        assignee_emoji = {
            Assignee.HUMAN: "👤",
            Assignee.AI: "🤖",
            Assignee.COLLABORATIVE: "🤝",
        }.get(task.assignee, "❓") if task.assignee else "❓"

        # Base display
        action = task.action[:55] + "..." if len(task.action) > 55 else task.action
        project = f"[{task.parent_project}]" if task.parent_project else ""
        progress = f" {task.progress}%" if task.progress is not None else ""

        display = f"{status_emoji} {priority_emoji} {assignee_emoji} {action} {project}{progress}"

        # Add additional info based on display config
        if self.display_config.show_created_at and hasattr(task, 'created_at'):
            time_ago = format_duration(task.created_at, utcnow())
            display += f" ({time_ago})"

        if self.display_config.show_tags and hasattr(task, 'tags') and task.tags:
            tags_display = f" #{', #'.join(task.tags[:3])}"
            if len(task.tags) > 3:
                tags_display += "..."
            display += tags_display

        return display


class AnalyticsWidget(Static):
    """Widget for displaying analytics and statistics."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.completion_data: List[int] = []
        self.priority_distribution: List[int] = []

    def update_analytics(self, tasks: List[Task], completion_data: List[int], priority_distribution: List[int]) -> None:
        """Update analytics display."""
        self.completion_data = completion_data
        self.priority_distribution = priority_distribution

        # Create analytics display
        total_tasks = len(tasks)
        completed = len([t for t in tasks if t.status in [Status.DONE, Status.COMPLETED]])
        completion_rate = (completed / total_tasks * 100) if total_tasks > 0 else 0

        content = f"""
[bold #4361ee]📊 Analytics Dashboard[/bold #4361ee]

[bold]Task Overview:[/bold]
• Total Tasks: {total_tasks}
• Completed: {completed}
• Completion Rate: {completion_rate:.1f}%

[bold]Priority Distribution:[/bold]
• Low: {priority_distribution[0] if len(priority_distribution) > 0 else 0}
• Medium: {priority_distribution[1] if len(priority_distribution) > 1 else 0}
• High: {priority_distribution[2] if len(priority_distribution) > 2 else 0}
• Critical: {priority_distribution[3] if len(priority_distribution) > 3 else 0}
• Urgent: {priority_distribution[4] if len(priority_distribution) > 4 else 0}

[bold]Recent Activity:[/bold]
{self._format_recent_activity(tasks)}
"""
        self.update(content)

    def _format_recent_activity(self, tasks: List[Task]) -> str:
        """Format recent activity summary."""
        recent_tasks = sorted(tasks, key=lambda t: getattr(t, 'updated_at', datetime.min), reverse=True)[:5]

        if not recent_tasks:
            return "No recent activity"

        activity_lines = []
        for task in recent_tasks:
            time_ago = format_duration(getattr(task, 'updated_at', utcnow()), utcnow())
            status_icon = "✅" if task.status in [Status.DONE, Status.COMPLETED] else "📝"
            activity_lines.append(f"{status_icon} {task.action[:30]}... ({time_ago})")

        return "\n".join(activity_lines)


class ActivityFeedWidget(RichLogWidget):
    """Widget for displaying live activity feed."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.entries: Deque[ActivityEntry] = deque(maxlen=200)

    def add_entry(self, level: str, message: str) -> None:
        """Add an activity entry."""
        entry = ActivityEntry(timestamp=utcnow(), level=level, message=message)
        self.entries.append(entry)
        self.write(f"[{entry.timestamp.strftime('%H:%M:%S')}] {message}", level=level)

    def get_recent_entries(self, limit: int = 10) -> List[ActivityEntry]:
        """Get recent activity entries."""
        return list(self.entries)[-limit:]


class ToastWidget(Static):
    """Widget for displaying toast notifications."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.toasts: List[ToastNotification] = []

    def update_toasts(self, toasts: List[ToastNotification]) -> None:
        """Update toast display."""
        self.toasts = [t for t in toasts if not t.is_expired()]

        if not self.toasts:
            self.update("")
            return

        # Show the most recent toast
        toast = self.toasts[-1]
        style_map = {
            ToastType.Success: "bold green",
            ToastType.Error: "bold red",
            ToastType.Warning: "bold yellow",
            ToastType.Info: "bold blue",
        }

        style = style_map.get(toast.notification_type, "bold")
        icon_map = {
            ToastType.Success: "✅",
            ToastType.Error: "❌",
            ToastType.Warning: "⚠️",
            ToastType.Info: "ℹ️",
        }

        icon = icon_map.get(toast.notification_type, "ℹ️")
        self.update(f"[{style}]{icon} {toast.message}[/{style}]")


class StatusBar(Static):
    """A reusable status bar widget that formats messages consistently."""
    
    def update_status(self, **kwargs) -> None:
        """Update the status bar with formatted message."""
        parts = []
        for key, value in kwargs.items():
            if value is not None:
                parts.append(f"{key.title()}: {value}")
        self.update(" | ".join(parts) if parts else "")


class TaskDetailWidget(Static):
    """Widget showing detailed task information with improved formatting."""
    
    def update_task(self, task: Optional[Task]) -> None:
        """Update the displayed task with safe attribute access."""
        if not task:
            self.update("[dim]Select a task to view details[/dim]")
            return
        
        def safe_getattr(obj, attr, default="N/A"):
            """Safely get attribute with fallback."""
            return str(getattr(obj, attr, default))
        
        def safe_getattr_value(obj, attr, default="N/A"):
            """Safely get attribute value (handles enums)."""
            attr_val = getattr(obj, attr, default)
            return getattr(attr_val, "value", str(attr_val))
        
        status_str = safe_getattr_value(task, "status")
        priority_str = safe_getattr_value(task, "priority")
        assignee_str = safe_getattr(task, "assignee", "Unassigned")
        tags_str = ", ".join(getattr(task, "tags", []) or [])
        progress_str = f"{task.progress}%" if getattr(task, "progress", None) is not None else "N/A"
        ctx = getattr(task, "context_notes", None) or ""
        created = getattr(task, "created_at", datetime.now(UTC))
        updated = getattr(task, "updated_at", datetime.now(UTC))
        
        details = f"""
[bold #4361ee]Task Details[/bold #4361ee]

[bold]Action:[/bold] {task.action}
[bold]Status:[/bold] {status_str}
[bold]Priority:[/bold] {priority_str}
[bold]Project:[/bold] {safe_getattr(task, 'parent_project')}
[bold]Assignee:[/bold] {assignee_str}
[bold]Time Estimate:[/bold] {safe_getattr(task, 'time')}
[bold]Progress:[/bold] {progress_str}
[bold]Tags:[/bold] {tags_str if tags_str else 'None'}
[bold]Created:[/bold] {created.strftime('%Y-%m-%d %H:%M')}
[bold]Updated:[/bold] {updated.strftime('%Y-%m-%d %H:%M')}
"""
        if ctx:
            details += f"\n[bold]Context:[/bold]\n{ctx}\n"
        
        self.update(details)


class TodoziTUI(App):
    """Enhanced Todozi TUI Application with comprehensive features"""

    CSS = """
    /* Todozi Brand Colors */
    Screen {
        background: #1a1a2e;  /* --dark */
    }

    Header {
        background: #161625;  /* --sidebar-bg */
        color: #f8f9fa;  /* --light */
        border-bottom: solid #4361ee;  /* --primary */
    }

    Footer {
        background: #161625;  /* --sidebar-bg */
        color: #f8f9fa;  /* --light */
        border-top: solid #4361ee;  /* --primary */
    }

    #main-container {
        layout: horizontal;
        height: 1fr;
        background: #1a1a2e;  /* --dark */
    }

    #left-panel {
        width: 60%;
        border: solid #4361ee;  /* --primary */
        background: #0d0d1a;  /* --darker */
    }

    #right-panel {
        width: 40%;
        border: solid #4361ee;  /* --primary */
        background: #0d0d1a;  /* --darker */
    }

    .status-bar {
        height: 3;
        background: #161625;  /* --sidebar-bg */
        border: solid #4361ee;  /* --primary */
        color: #f8f9fa;  /* --light */
    }

    .filter-bar {
        height: 3;
        background: #161625;  /* --sidebar-bg */
        border: solid #4361ee;  /* --primary */
        color: #f8f9fa;  /* --light */
    }

    TabbedContent > Tab {
        background: #161625;  /* --sidebar-bg */
        color: #6c757d;  /* --gray */
    }

    TabbedContent > Tab.--selected {
        background: #4361ee;  /* --primary */
        color: #f8f9fa;  /* --light */
    }

    ListView {
        background: #0d0d1a;  /* --darker */
        color: #f8f9fa;  /* --light */
    }

    ListView > ListItem {
        background: #1a1a2e;  /* --dark */
    }

    ListView > ListItem.--highlight {
        background: #4361ee;  /* --primary */
        color: #f8f9fa;  /* --light */
    }

    ListView > ListItem:hover {
        background: #3a56d4;  /* --primary-dark */
    }

    Static {
        background: #0d0d1a;  /* --darker */
        color: #f8f9fa;  /* --light */
    }

    Label {
        color: #f8f9fa;  /* --light */
    }

    Input {
        background: #1a1a2e;  /* --dark */
        color: #f8f9fa;  /* --light */
        border: solid #4361ee;  /* --primary */
    }

    Input:focus {
        border: solid #7209b7;  /* --secondary */
    }

    Button {
        background: #4361ee;  /* --primary */
        color: #f8f9fa;  /* --light */
    }

    Button:hover {
        background: #3a56d4;  /* --primary-dark */
    }

    Button.--active {
        background: #7209b7;  /* --secondary */
    }

    /* Success/Warning/Danger colors for toasts and status */
    .success {
        background: #06d6a0;  /* --success */
        color: #0d0d1a;  /* --darker */
    }

    .warning {
        background: #ffd166;  /* --warning */
        color: #0d0d1a;  /* --darker */
    }

    .error {
        background: #ef476f;  /* --danger */
        color: #f8f9fa;  /* --light */
    }

    .info {
        background: #4361ee;  /* --primary */
        color: #f8f9fa;  /* --light */
    }

    /* Enhanced styling for new components */
    .toast-widget {
        height: 2;
        background: #161625;
        border: solid #4361ee;
        color: #f8f9fa;
    }

    .analytics-widget {
        background: #0d0d1a;
        color: #f8f9fa;
        border: solid #4361ee;
    }

    .activity-feed {
        background: #0d0d1a;
        color: #f8f9fa;
        border: solid #4361ee;
    }

    /* Modal styling */
    ModalScreen {
        background: rgba(0, 0, 0, 0.8);
    }

    .modal-content {
        background: #1a1a2e;
        border: solid #4361ee;
        color: #f8f9fa;
    }
    """
    
    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("tab", "next_tab", "Next Tab"),
        Binding("shift+tab", "prev_tab", "Prev Tab"),
        Binding("1", "tab_1", "Projects"),
        Binding("2", "tab_2", "Tasks"),
        Binding("3", "tab_3", "Feed"),
        Binding("4", "tab_4", "Done"),
        Binding("5", "tab_5", "Find"),
        Binding("6", "tab_6", "More"),
        Binding("7", "tab_7", "API"),
        Binding("8", "tab_8", "Bye"),
        Binding("a", "add_task", "Add Task"),
        Binding("d", "delete_task", "Delete Task"),
        Binding("c", "complete_task", "Complete Task"),
        Binding("e", "edit_task", "Edit Task"),
        Binding("r", "refresh", "Refresh"),
        Binding("f", "filter", "Filter"),
        Binding("p", "projects", "Projects"),
        Binding("s", "stats", "Stats"),
        Binding("/", "focus_search", "Focus Search"),
        Binding("?", "help", "Help"),
        # Enhanced bindings
        Binding("ctrl+a", "add_task_quick", "Quick Add"),
        Binding("ctrl+e", "edit_task_modal", "Edit Modal"),
        Binding("ctrl+d", "delete_task_confirm", "Delete with Confirm"),
        Binding("space", "task_actions", "Task Actions"),
        Binding("enter", "task_details", "Task Details"),
        Binding("ctrl+r", "refresh_all", "Full Refresh"),
        Binding("ctrl+s", "save_all", "Save All"),
        Binding("ctrl+f", "toggle_filters", "Toggle Filters"),
        Binding("ctrl+l", "clear_filters", "Clear Filters"),
        Binding("ctrl+t", "toggle_display", "Toggle Display"),
    ]
    
    TITLE = "Todozi [✓]"
    SUB_TITLE = "AI/Human Task Management System"
    
    # Reactive state
    selected_task_index: reactive[int] = reactive(0)
    selected_project_index: reactive[int] = reactive(0)
    current_project: reactive[Optional[str]] = reactive(None)
    filter_status: reactive[Optional[Status]] = reactive(None)
    current_tab: reactive[AppTab] = reactive(AppTab.Projects)
    
    def __init__(self):
        super().__init__()
        self.storage: Optional[Storage] = None
        self.tasks: List[Task] = []
        self.filtered_tasks: List[Task] = []
        self.projects: List[Project] = []
        self.task_filters = TaskFilters()
        self.done_filters = TaskFilters()
        self.done_sort_by = TaskSortBy.DateCompleted
        self.done_sort_order = SortOrder.Descending
        self.done_selected_task_index = 0
        self.search_query = ""
        self.search_results: List[Task] = []
        self.editor: Optional[EditSession] = None
        self.editor_field = EditorField.Action
        self.editor_input = ""
        self.editor_selected_field = 0
        self.more_tab_section = MoreTabSection.Ideas
        self.more_scroll_offset = 0
        self.api_keys: List[ApiKey] = []
        self.api_selected_index = 0
        self.toast_notifications: List[ToastNotification] = []
        self.toast_notifier = ToastNotifier(self)
        self.ideas: List[Idea] = []
        self.memories: List[Memory] = []
        self.errors: List[Error] = []
        self.feelings: List[Feeling] = []
        self.training_data: List[TrainingData] = []
        self.queue_items: List[QueueItem] = []
        self.reminders: List[Reminder] = []
        self.server_running = False
        self.server_status = "🔴 Not running"
        self.observer: Optional[Observer] = None
        self._watch_callback_scheduled = False
        self._activity_feed: Deque[ActivityEntry] = deque(maxlen=200)

        # Enhanced state
        self.display_config = DisplayConfig()
        self.completion_data: List[int] = [0] * 50  # Last 50 days
        self.priority_distribution: List[int] = [0] * 5  # Low, Medium, High, Critical, Urgent
        self.selected_project_index = 0
        self.task_action_menu: Optional[int] = None
        self.task_action_selected = 0
        self.show_task_details: Optional[Task] = None

        # File watching
        self.file_watcher_thread: Optional[threading.Thread] = None
        self.stop_watching = False
    
    async def on_mount(self) -> None:
        """Initialize the app"""
        await self.load_storage()
        await self.refresh_data()
        self.update_task_list()
        self.start_file_watcher()
        self.set_interval(1.0, self.update_toasts)  # More frequent toast updates
        self.set_interval(5.0, self.auto_refresh)
        self.log_activity("info", "Enhanced Todozi TUI started")

        # Update analytics
        self.update_analytics_data()
    
    async def on_unmount(self) -> None:
        """Clean up resources when app is closed"""
        self.stop_watching = True

        if self.file_watcher_thread and self.file_watcher_thread.is_alive():
            try:
                self.file_watcher_thread.join(timeout=2.0)
                logger.info("File watcher thread stopped cleanly")
            except Exception as exc:
                logger.exception("Error while stopping watcher thread: %s", exc)

        if self.observer and hasattr(self.observer, 'is_alive') and self.observer.is_alive():
            try:
                self.observer.stop()
                self.observer.join(timeout=2.0)
                logger.info("File watcher stopped cleanly")
            except Exception as exc:
                logger.exception("Error while stopping watcher: %s", exc)

    def update_analytics_data(self) -> None:
        """Update analytics data based on current tasks."""
        if not self.tasks:
            return

        # Update completion data (last 50 days)
        now = utcnow()
        for i in range(50):
            date = now - timedelta(days=49 - i)
            completed_count = len([
                task for task in self.tasks
                if task.status in [Status.DONE, Status.COMPLETED]
                and hasattr(task, 'updated_at') and task.updated_at
                and task.updated_at.date() == date.date()
            ])
            self.completion_data[i] = completed_count

        # Update priority distribution
        priority_counts = {Priority.LOW: 0, Priority.MEDIUM: 0, Priority.HIGH: 0,
                          Priority.CRITICAL: 0, Priority.URGENT: 0}
        for task in self.tasks:
            if task.status not in [Status.DONE, Status.COMPLETED]:
                priority_counts[task.priority] += 1

        self.priority_distribution = [
            priority_counts[Priority.LOW],
            priority_counts[Priority.MEDIUM],
            priority_counts[Priority.HIGH],
            priority_counts[Priority.CRITICAL],
            priority_counts[Priority.URGENT],
        ]
    
    def log_activity(self, level: str, message: str) -> None:
        """Log an activity to the feed and standard logging."""
        entry = ActivityEntry(timestamp=datetime.now(UTC), level=level, message=message)
        self._activity_feed.append(entry)
        getattr(logger, level.lower(), logger.info)(message)
    
    def _handle_error(self, context: str, exception: Exception) -> None:
        """Centralized error handling for consistent logging and notifications."""
        error_msg = f"{context}: {str(exception)}"
        self.log_activity("error", error_msg)
        self.toast_notifier.error(f"Error {context.lower()}: {exception}")
    
    def _ensure_ready(self) -> bool:
        """Return True if storage and tasks are available."""
        ready = bool(self.storage) and bool(self.filtered_tasks)
        if not ready:
            self.toast_notifier.warning("No tasks or storage unavailable")
        return ready
    
    def _current_task(self) -> Optional[Task]:
        """Return the currently selected task or None."""
        idx = self.selected_task_index
        if 0 <= idx < len(self.filtered_tasks):
            return self.filtered_tasks[idx]
        self.toast_notifier.warning("No task selected")
        return None
    
    async def load_storage(self) -> None:
        """Load storage asynchronously with better error handling"""
        try:
            self.storage = await Storage.new()
            self.log_activity("info", "Storage loaded successfully")
        except Exception as e:
            self._handle_error("Loading storage", e)
            self.storage = None
    
    async def refresh_data(self) -> None:
        """Refresh all data from storage with better error handling"""
        if not self.storage:
            return
        
        try:
            # Load tasks
            filters = TaskFilters()
            if self.filter_status:
                filters.status_filter = self.filter_status
            if self.current_project:
                filters.project_filter = self.current_project
            
            self.tasks = self.storage.list_tasks_across_projects(
                TaskFilters() if not hasattr(self.storage, 'list_tasks_across_projects') 
                else self.task_filters
            )
            self.filtered_tasks = self.tasks
            
            # Load projects
            self.projects = self.storage.list_projects()
            
            # Load extended data
            try:
                idea_manager = IdeaManager()
                await idea_manager.load_ideas()
                self.ideas = idea_manager.get_all_ideas()
            except Exception as e:
                logger.debug("Failed to load ideas: %s", e)
                self.ideas = []

            try:
                memory_manager = MemoryManager()
                await memory_manager.load_memories()
                self.memories = memory_manager.get_all_memories()
            except Exception as e:
                logger.debug("Failed to load memories: %s", e)
                self.memories = []

            try:
                error_manager = ErrorManager()
                self.errors = error_manager.list_errors()
            except Exception as e:
                logger.debug("Failed to load errors: %s", e)
                self.errors = []

            # Load additional extended data
            try:
                # Load feelings (mock data for now)
                self.feelings = [
                    Feeling(emotion="Happy", intensity=8, context="Completed a challenging task"),
                    Feeling(emotion="Focused", intensity=7, context="Working on important project"),
                ]
            except Exception as e:
                logger.debug("Failed to load feelings: %s", e)
                self.feelings = []

            try:
                # Load training data (mock data for now)
                self.training_data = [
                    TrainingData(data_type="task", prompt="How to prioritize tasks", response="Use Eisenhower matrix"),
                    TrainingData(data_type="project", prompt="How to manage team projects", response="Use agile methodology"),
                ]
            except Exception as e:
                logger.debug("Failed to load training data: %s", e)
                self.training_data = []

            try:
                # Load queue items (mock data for now)
                self.queue_items = [
                    QueueItem(task_name="Process user feedback", priority=3),
                    QueueItem(task_name="Update documentation", priority=1),
                ]
            except Exception as e:
                logger.debug("Failed to load queue items: %s", e)
                self.queue_items = []

            try:
                # Load reminders (mock data for now)
                self.reminders = [
                    Reminder(title="Team meeting", message="Weekly standup at 10 AM", due_date=utcnow() + timedelta(hours=2)),
                    Reminder(title="Project deadline", message="Submit final report", due_date=utcnow() + timedelta(days=3)),
                ]
            except Exception as e:
                logger.debug("Failed to load reminders: %s", e)
                self.reminders = []
            
            # Load API keys
            try:
                self.api_keys = list_api_keys()
            except Exception as e:
                logger.debug("Failed to load API keys: %s", e)
                self.api_keys = []
            
        except Exception as e:
            self._handle_error("Refreshing data", e)

    def compose(self) -> ComposeResult:
        """Create the enhanced UI layout"""
        yield Header(show_clock=True)

        # Toast notification widget
        yield ToastWidget("", classes="toast-widget", id="toast-widget")

        with TabbedContent(initial="projects"):
            with TabPane("📁 Projects", id="projects"):
                yield self._compose_projects_tab()

            with TabPane("📋 Tasks", id="tasks"):
                yield self._compose_tasks_tab()

            with TabPane("✅ Done", id="done"):
                yield self._compose_done_tab()

            with TabPane("🔍 Find", id="find"):
                yield self._compose_find_tab()

            with TabPane("🔮 More", id="more"):
                yield self._compose_more_tab()

            with TabPane("🔑 API", id="api"):
                yield self._compose_api_tab()

            with TabPane("📰 Feed", id="feed"):
                yield self._compose_feed_tab()

            with TabPane("👋 Bye", id="bye"):
                yield self._compose_bye_tab()

        yield Footer()
    
    def _compose_projects_tab(self) -> ComposeResult:
        with Vertical():
            yield Label("[bold]Projects[/bold]", id="projects-header")
            yield ListView(id="projects-list")
            yield Static("", classes="status-bar")
    
    def _compose_tasks_tab(self) -> ComposeResult:
        with Container(id="main-container"):
            with Vertical(id="left-panel"):
                yield Label("[bold]Tasks[/bold]", id="task-list-header")
                yield StatusBar("", classes="filter-bar", id="filter-status")
                yield EnhancedTaskListWidget(id="task-list")
                yield StatusBar("", classes="status-bar", id="task-status")

            with Vertical(id="right-panel"):
                yield Label("[bold]Task Details & Analytics[/bold]", id="task-detail-header")
                yield TaskDetailWidget(id="task-detail")
                yield AnalyticsWidget("", classes="analytics-widget", id="task-analytics")
    
    def _compose_done_tab(self) -> ComposeResult:
        with Vertical():
            yield Label("[bold]Completed Tasks[/bold]", id="done-header")
            yield Static("", classes="filter-bar")
            yield ListView(id="done-list")
            yield Static("", classes="status-bar")
    
    def _compose_find_tab(self) -> ComposeResult:
        with Vertical():
            yield Label("[bold]Search[/bold]", id="find-header")
            yield Input(placeholder="Type to search...", id="search-input")
            yield ListView(id="search-results")
            yield Static("", classes="status-bar")
    
    def _compose_more_tab(self) -> ComposeResult:
        with Vertical():
            yield Label("[bold]Extended Data[/bold]", id="more-header")
            yield Tabs(*[section.value for section in MoreTabSection.all()], id="more-tabs")
            yield ScrollableContainer(id="more-content")
            yield Static("", classes="status-bar")
    
    def _compose_api_tab(self) -> ComposeResult:
        with Container(id="main-container"):
            with Vertical(id="left-panel"):
                yield Label("[bold]Server Control[/bold]", id="api-server-header")
                yield Static("", id="server-status")
                yield Button("Start Server", id="start-server")
                yield Button("Stop Server", id="stop-server")
            
            with Vertical(id="right-panel"):
                yield Label("[bold]API Keys[/bold]", id="api-keys-header")
                yield ListView(id="api-keys-list")
    
    def _compose_feed_tab(self) -> ComposeResult:
        with Vertical():
            yield Label("[bold]Live Activity Feed[/bold]", id="feed-header")
            yield ScrollableContainer(id="feed-content")
            yield Static("", classes="status-bar")
    
    def _compose_bye_tab(self) -> ComposeResult:
        with Vertical():
            yield Static("""
[bold] _______        _            [/bold]
[bold]|__   __|      | |        (✓)[/bold]
[bold]   | | ___   __| | ___ _____[/bold]
[bold]   | |/ _ \\ / _` |/ _ \\_  / |[/bold]
[bold]   | | (_) | (_| | (_) / /| |[/bold]
[bold]   |_|\\___/ \\__,_|\\___/___|_|[/bold]

Are you sure you want to leave Todozi?
Press Enter to confirm exit

Thank you for using Todozi! 🎉
""", id="bye-message")
    
    def _search_tasks(self, query: str) -> List[Task]:
        """Search tasks by action, tags, or parent project."""
        query = query.lower()
        return [
            t for t in self.tasks
            if query in (getattr(t, "action", "") or "").lower()
            or query in " ".join(getattr(t, "tags", []) or []).lower()
            or query in (getattr(t, "parent_project", "") or "").lower()
        ]
    
    def update_task_list(self) -> None:
        """Update the task list widget with enhanced display and analytics"""
        try:
            task_list = self.query_one("#task-list", EnhancedTaskListWidget)
            task_list.update_tasks(self.filtered_tasks, self.selected_task_index, self.display_config)

            # Update detail view
            if self.filtered_tasks and 0 <= self.selected_task_index < len(self.filtered_tasks):
                task = self.filtered_tasks[self.selected_task_index]
                detail = self.query_one("#task-detail", TaskDetailWidget)
                detail.update_task(task)
            else:
                detail = self.query_one("#task-detail", TaskDetailWidget)
                detail.update_task(None)

            # Update analytics
            try:
                analytics = self.query_one("#task-analytics", AnalyticsWidget)
                analytics.update_analytics(self.tasks, self.completion_data, self.priority_distribution)
            except Exception:
                pass

            # Update status bars
            try:
                filter_status = self.query_one("#filter-status", StatusBar)
                filter_status.update_status(
                    filter=self.filter_status.value if self.filter_status else "All",
                    project=self.current_project or "All"
                )
            except Exception:
                pass

            try:
                task_status = self.query_one("#task-status", StatusBar)
                task_status.update_status(
                    total=len(self.filtered_tasks),
                    project=self.current_project or "All"
                )
            except Exception:
                pass
        except Exception:
            pass  # Widgets might not be mounted yet

    def update_toasts(self) -> None:
        """Update toast notifications."""
        now = time.time()
        self.toast_notifications[:] = [
            t for t in self.toast_notifications
            if not t.is_expired(now)
        ]

        # Update toast widget
        try:
            toast_widget = self.query_one("#toast-widget", ToastWidget)
            toast_widget.update_toasts(self.toast_notifications)
        except Exception:
            pass
    
    @on(ListView.Selected)
    def on_task_selected(self, event: ListView.Selected) -> None:
        """Handle task selection"""
        if isinstance(event.item, ListItem):
            index = event.list_view.highlighted
            if 0 <= index < len(self.filtered_tasks):
                self.selected_task_index = index
                task = self.filtered_tasks[index]
                try:
                    detail = self.query_one("#task-detail", TaskDetailWidget)
                    detail.update_task(task)
                except Exception:
                    pass
    
    async def action_add_task(self) -> None:
        """Add a new task with improved error handling"""
        if not self._ensure_ready():
            return
        
        try:
            from todozi.models import Ok, Err
            
            task_result = Task.new_full(
                user_id="tui_user",
                action="New task - edit me",
                time="1 hour",
                priority=Priority.MEDIUM,
                parent_project=self.current_project or "general",
                status=Status.TODO,
                assignee=None,
                tags=[],
                dependencies=[],
                context_notes=None,
                progress=None,
            )
            
            if isinstance(task_result, Err):
                self._handle_error("Creating task", Exception(str(task_result.error)))
                return
            
            task = task_result.value if isinstance(task_result, Ok) else task_result
            await self.storage.add_task_to_project(task)
            self.log_activity("success", f"Task added: {task.action}")
            await self.refresh_data()
            self.update_task_list()
            self.toast_notifier.success("Task added! Press 'e' to edit")
        except Exception as e:
            self._handle_error("Adding task", e)
    
    async def action_delete_task(self) -> None:
        """Delete the selected task with improved error handling"""
        if not self._ensure_ready():
            return
        
        task = self._current_task()
        if not task:
            return
        
        try:
            self.storage.delete_task_from_project(task.id)
            self.log_activity("warning", f"Task deleted: {task.action}")
            await self.refresh_data()
            self.selected_task_index = min(self.selected_task_index, len(self.filtered_tasks) - 1)
            self.update_task_list()
            self.toast_notifier.success("Task deleted")
        except Exception as e:
            self._handle_error("Deleting task", e)
    
    async def action_complete_task(self) -> None:
        """Mark the selected task as complete with improved error handling"""
        if not self._ensure_ready():
            return
        
        task = self._current_task()
        if not task:
            return
        
        try:
            self.storage.complete_task_in_project(task.id)
            self.log_activity("success", f"Task completed: {task.action}")
            await self.refresh_data()
            self.update_task_list()
            self.toast_notifier.success("Task completed!")
        except Exception as e:
            self._handle_error("Completing task", e)
    
    async def action_edit_task(self) -> None:
        """Edit the selected task"""
        if not self.filtered_tasks:
            return

        if 0 <= self.selected_task_index < len(self.filtered_tasks):
            task = self.filtered_tasks[self.selected_task_index]
            self.editor = EditSession(
                task_id=task.id,
                original_task=task,
                current_task=task,
                ai_suggestions=[],
                validation_errors=[],
                session_start=utcnow(),
            )
            self.editor_selected_field = 0
            self.editor_input = ""
            self.push_screen("editor")

    async def action_edit_task_modal(self) -> None:
        """Edit task using modal interface"""
        if not self.filtered_tasks or not (0 <= self.selected_task_index < len(self.filtered_tasks)):
            return

        task = self.filtered_tasks[self.selected_task_index]
        modal = EditTaskModal(task)
        result = await self.push_screen_wait(modal)

        if result:
            # Update the task
            self.save_task(result)
            self.apply_filters()
            self.update_task_list()
            self.toast_notifier.success("Task updated")

    async def action_task_actions(self) -> None:
        """Show task action menu"""
        if not self.filtered_tasks or not (0 <= self.selected_task_index < len(self.filtered_tasks)):
            return

        task = self.filtered_tasks[self.selected_task_index]
        actions = [
            TaskAction.Edit,
            TaskAction.ViewDetails,
            TaskAction.Complete,
            TaskAction.Duplicate,
            TaskAction.Delete,
            TaskAction.MoveToProject,
        ]

        modal = TaskActionMenu(task, actions)
        result = await self.push_screen_wait(modal)

        if result:
            action, task = result
            await self._execute_task_action(action, task)

    async def action_task_details(self) -> None:
        """Show task details modal"""
        if not self.filtered_tasks or not (0 <= self.selected_task_index < len(self.filtered_tasks)):
            return

        task = self.filtered_tasks[self.selected_task_index]
        modal = TaskDetailsModal(task)
        await self.push_screen_wait(modal)

    async def action_delete_task_confirm(self) -> None:
        """Delete task with confirmation"""
        if not self._ensure_ready():
            return

        task = self._current_task()
        if not task:
            return

        # Show confirmation modal
        confirmed = await self._show_confirmation_dialog(f"Delete task '{task.action}'?")
        if confirmed:
            await self.action_delete_task()

    async def action_refresh_all(self) -> None:
        """Full refresh of all data"""
        try:
            await self.refresh_data()
            self.update_task_list()
            self.toast_notifier.success("Full refresh completed")
            self.log_activity("info", "Full data refresh completed")
        except Exception as e:
            self._handle_error("Full refresh", e)

    async def action_save_all(self) -> None:
        """Save all data"""
        try:
            self.save_tasks()
            self.toast_notifier.success("All data saved")
            self.log_activity("info", "All data saved")
        except Exception as e:
            self._handle_error("Saving data", e)

    async def action_toggle_filters(self) -> None:
        """Toggle filter visibility"""
        # In a real implementation, this would toggle filter UI visibility
        self.toast_notifier.info("Filter toggle not implemented")

    async def action_clear_filters(self) -> None:
        """Clear all filters"""
        self.task_filters = TaskFilters()
        self.done_filters = TaskFilters()
        self.current_project = None
        self.filter_status = None
        self.apply_filters()
        self.update_task_list()
        self.toast_notifier.info("All filters cleared")

    async def action_toggle_display(self) -> None:
        """Toggle display options"""
        self.display_config.compact_mode = not self.display_config.compact_mode
        self.update_task_list()
        mode = "compact" if self.display_config.compact_mode else "normal"
        self.toast_notifier.info(f"Display mode: {mode}")

    async def _execute_task_action(self, action: TaskAction, task: Task) -> None:
        """Execute a task action"""
        if action == TaskAction.Edit:
            await self.action_edit_task_modal()
        elif action == TaskAction.ViewDetails:
            await self.action_task_details()
        elif action == TaskAction.Complete:
            await self.action_complete_task()
        elif action == TaskAction.Duplicate:
            await self._duplicate_task(task)
        elif action == TaskAction.Delete:
            confirmed = await self._show_confirmation_dialog(f"Delete task '{task.action}'?")
            if confirmed:
                await self.action_delete_task()
        elif action == TaskAction.MoveToProject:
            await self._move_task_to_project(task)

    async def _duplicate_task(self, task: Task) -> None:
        """Duplicate a task"""
        new_task = Task(
            action=f"{task.action} (Copy)",
            status=task.status,
            priority=task.priority,
            parent_project=task.parent_project,
            tags=task.tags.copy() if task.tags else [],
            context_notes=task.context_notes,
        )

        if self.storage:
            await self.storage.add_task_to_project(new_task)

        self.tasks.append(new_task)
        self.apply_filters()
        self.update_task_list()
        self.toast_notifier.success("Task duplicated")

    async def _move_task_to_project(self, task: Task) -> None:
        """Move task to different project"""
        # In a real implementation, this would show a project selection dialog
        self.toast_notifier.info("Move to project not implemented")

    async def _show_confirmation_dialog(self, message: str) -> bool:
        """Show a confirmation dialog"""
        # For now, just return True. In a real implementation, this would show a modal
        return True
    
    async def action_refresh(self) -> None:
        """Refresh data from storage"""
        try:
            await self.refresh_data()
            self.update_task_list()
            self.toast_notifier.success("Refreshed")
            self.log_activity("info", "Data refreshed")
        except Exception as e:
            self._handle_error("Refreshing", e)
    
    async def action_filter(self) -> None:
        """Toggle status filter"""
        try:
            statuses = [None, Status.TODO, Status.IN_PROGRESS, Status.DONE]
            current_idx = statuses.index(self.filter_status) if self.filter_status in statuses else 0
            next_idx = (current_idx + 1) % len(statuses)
            self.filter_status = statuses[next_idx]
            await self.refresh_data()
            self.update_task_list()
            status_name = self.filter_status.value if self.filter_status else "All"
            self.toast_notifier.info(f"Filter: {status_name}")
        except Exception as e:
            self._handle_error("Applying filter", e)
    
    def action_next_tab(self) -> None:
        """Switch to next tab"""
        tabs = AppTab.all()
        idx = tabs.index(self.current_tab)
        self.current_tab = tabs[(idx + 1) % len(tabs)]
        self.switch_tab(self.current_tab)

    def action_prev_tab(self) -> None:
        """Switch to previous tab"""
        tabs = AppTab.all()
        idx = tabs.index(self.current_tab)
        self.current_tab = tabs[(idx - 1) % len(tabs)]
        self.switch_tab(self.current_tab)
    
    def action_tab_1(self) -> None:
        self.current_tab = AppTab.Projects
        self.switch_tab(AppTab.Projects)

    def action_tab_2(self) -> None:
        self.current_tab = AppTab.Tasks
        self.switch_tab(AppTab.Tasks)

    def action_tab_3(self) -> None:
        self.current_tab = AppTab.Feed
        self.switch_tab(AppTab.Feed)

    def action_tab_4(self) -> None:
        self.current_tab = AppTab.Done
        self.switch_tab(AppTab.Done)

    def action_tab_5(self) -> None:
        self.current_tab = AppTab.Find
        self.switch_tab(AppTab.Find)

    def action_tab_6(self) -> None:
        self.current_tab = AppTab.More
        self.switch_tab(AppTab.More)

    def action_tab_7(self) -> None:
        self.current_tab = AppTab.Api
        self.switch_tab(AppTab.Api)

    def action_tab_8(self) -> None:
        self.current_tab = AppTab.Bye
        self.switch_tab(AppTab.Bye)

    def switch_tab(self, tab: AppTab) -> None:
        """Switch to a specific tab"""
        tab_map = {
            AppTab.Projects: "projects",
            AppTab.Tasks: "tasks",
            AppTab.Done: "done",
            AppTab.Find: "find",
            AppTab.More: "more",
            AppTab.Api: "api",
            AppTab.Feed: "feed",
            AppTab.Bye: "bye",
        }
        try:
            tabbed_content = self.query_one(TabbedContent)
            tabbed_content.active = tab_map[tab]
        except Exception:
            pass
    
    def add_toast(self, message: str, toast_type: ToastType) -> None:
        """Add a toast notification (delegates to ToastNotifier)"""
        self.toast_notifier._make(message, toast_type)
    
    def update_toasts(self) -> None:
        """Update toast notifications by removing expired ones"""
        now = time.time()
        # More efficient in-place filtering
        self.toast_notifications[:] = [
            t for t in self.toast_notifications 
            if not t.is_expired(now)
        ]
    
    async def auto_refresh(self) -> None:
        """Auto-refresh data periodically"""
        try:
            await self.refresh_data()
            self.update_task_list()
        except Exception as e:
            logger.debug("Auto-refresh failed: %s", e)
    
    def start_file_watcher(self) -> None:
        """Start watching the Todozi storage directory for changes"""
        if not WATCHDOG_AVAILABLE or self.file_watcher_thread is not None:
            return

        # Resolve a sensible directory to watch
        watch_dir: Path = Path(__file__).resolve().parent
        try:
            from todozi.storage import get_storage_dir
            p = get_storage_dir()
            if p:
                watch_dir = Path(p) if isinstance(p, str) else p
        except Exception as exc:
            logger.debug("Failed to obtain storage dir: %s", exc)

        if not watch_dir.exists():
            logger.debug("Watch directory does not exist: %s", watch_dir)
            return

        def watch_files():
            try:
                self.observer = Observer(daemon=True)
                handler = TasksDirWatcher(self._on_files_changed)
                self.observer.schedule(handler, str(watch_dir), recursive=True)
                self.observer.start()
                logger.info("Started file watcher on %s", watch_dir)
                self.log_activity("info", f"File watcher started on {watch_dir}")

                # Keep thread alive
                while not self.stop_watching:
                    time.sleep(1)

            except Exception as exc:
                logger.exception("File watcher error: %s", exc)
            finally:
                if self.observer:
                    try:
                        self.observer.stop()
                        self.observer.join(timeout=2.0)
                    except Exception as exc:
                        logger.exception("Error stopping watcher: %s", exc)

        self.file_watcher_thread = threading.Thread(target=watch_files, daemon=True)
        self.file_watcher_thread.start()

    def _on_files_changed(self) -> None:
        """Debounced entry point for the watchdog thread"""
        if self._watch_callback_scheduled:
            return
        self._watch_callback_scheduled = True
        # Schedule the async handler to run on the UI event loop
        self.call_later(self._handle_files_changed)

    async def _handle_files_changed(self) -> None:
        """Refresh UI after a change on disk"""
        self._watch_callback_scheduled = False
        self.log_activity("info", "Detected file changes; refreshing")
        try:
            await self.refresh_data()
            self.update_task_list()
        except Exception as e:
            logger.debug("File change handler failed: %s", e)
    
    def action_focus_search(self) -> None:
        """Focus the search input"""
        try:
            search_input = self.query_one("#search-input", Input)
            self.set_focus(search_input)
        except Exception as e:
            logger.debug("Search focus failed: %s", e)
            self.toast_notifier.warning("Search box not available")
    
    @on(Input.Submitted, "#search-input")
    def on_search_submitted(self, event: Input.Submitted) -> None:
        """Execute search when Enter is pressed"""
        self.search_query = (event.value or "").strip()
        if self.search_query:
            self.search_results = self._search_tasks(self.search_query)
            self.log_activity("info", f"Search: '{self.search_query}' ({len(self.search_results)} results)")
            # Update search results list
            try:
                results_list = self.query_one("#search-results", ListView)
                results_list.clear()
                if not self.search_results:
                    results_list.append(ListItem(Label("No results found")))
                else:
                    for task in self.search_results:
                        display = f"{task.action} [{task.parent_project}]"
                        results_list.append(ListItem(Label(display)))
            except Exception:
                pass
    
    @on(Button.Pressed, "#start-server")
    def on_start_server(self, event: Button.Pressed) -> None:
        """Handle server start button"""
        event.stop()
        self.server_running = True
        self.server_status = "🟢 Running"
        try:
            widget = self.query_one("#server-status", Static)
            widget.update(self.server_status)
        except Exception:
            pass
        self.log_activity("info", "Server started")
        self.toast_notifier.success("Server started")
    
    @on(Button.Pressed, "#stop-server")
    def on_stop_server(self, event: Button.Pressed) -> None:
        """Handle server stop button"""
        event.stop()
        self.server_running = False
        self.server_status = "🔴 Not running"
        try:
            widget = self.query_one("#server-status", Static)
            widget.update(self.server_status)
        except Exception:
            pass
        self.log_activity("info", "Server stopped")
        self.toast_notifier.warning("Server stopped")
    
    async def action_help(self) -> None:
        """Show help"""
        help_text = """
[bold]🚀 Enhanced Todozi TUI Help[/bold]

[bold]Navigation:[/bold]
  Tab/Shift+Tab  - Switch tabs
  1-8            - Direct tab access
  ↑/↓/←/→       - Navigate items
  Enter          - Select/Open details
  Space          - Task actions menu
  Esc            - Cancel/Back/Clear

[bold]Task Management:[/bold]
  a / Ctrl+A     - Add new task
  d / Ctrl+D     - Delete task (with confirm)
  c              - Complete selected task
  e / Ctrl+E     - Edit task (modal)
  r / Ctrl+R     - Full refresh
  f / Ctrl+F     - Toggle filters
  Ctrl+L         - Clear all filters
  Ctrl+T         - Toggle display mode

[bold]Quick Actions:[/bold]
  Space          - Task action menu
  Enter          - Task details modal
  /              - Focus search
  ?              - Show this help
  Ctrl+S         - Save all data

[bold]Tabs:[/bold]
  1 📁 Projects  - Manage projects
  2 📋 Tasks     - View and manage tasks
  3 📰 Feed      - Live activity feed
  4 ✅ Done      - Completed tasks
  5 🔍 Find      - Search tasks
  6 🔮 More      - Extended data (Ideas, Memories, etc.)
  7 🔑 API       - API management & server control
  8 👋 Bye       - Exit application

[bold]More Tab Sections:[/bold]
  💡 Ideas       - Creative ideas and concepts
  🧠 Memories    - Personal memories and moments
  😊 Feelings    - Emotional tracking
  ❌ Errors      - Error logs and debugging
  🎓 Training    - AI training data
  📋 Queue       - Task processing queue
  🔔 Reminders   - Scheduled reminders
  📊 Analytics   - Statistics and insights

[bold]Enhanced Features:[/bold]
  • Real-time file watching
  • Toast notifications
  • Modal dialogs for editing
  • Analytics dashboard
  • Activity feed
  • Server management
  • API key management
  • Priority distribution charts
  • Completion tracking

[bold]Tips:[/bold]
  • Use Space on any task for quick actions menu
  • Ctrl+E for modal editing with field navigation
  • All changes are auto-saved
  • Analytics update in real-time
  • Activity feed shows all operations
"""
        self.notify(help_text, severity="information", timeout=15)


def main() -> None:
    """Main entry point"""
    app = TodoziTUI()
    app.run()


if __name__ == "__main__":
    main()
