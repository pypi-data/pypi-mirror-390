#!/usr/bin/env python3
"""
todozi.py – A faithful, executable translation of the Rust Todozi CLI
into Python using argparse.  All commands, sub‑commands and options are
mirrored.  Handlers provide implementations that process the received
arguments (making the script immediately useful for testing/extending).

Key improvements over the previous version:
* Use `enum.Enum` for all enum‑like values.
* Consistent `dest` for sub‑parsers: top‑level uses `"command"`, each
  sub‑command uses a dedicated attribute (e.g. `"add_sub"`).
* Boolean flags are defined with `action="store_true"` instead of
  `type=bool`.
* Mutually‑exclusive groups are used for `extract` and `strategy`.
* Robust error handling in `main()` (ArgumentError, KeyboardInterrupt).
* Clear separation of model/struct definitions, parser, handlers and
  entry‑point.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional, Dict, Any


# ----------------------------------------------------------------------
# Domain types – simple stubs mirroring the Rust structs
# ----------------------------------------------------------------------
@dataclass
class CodeChunk:
    content: str = ""


@dataclass
class AgentAssignment:
    agent_id: str = ""
    task_id: str = ""
    project_id: str = ""


@dataclass
class Error:
    id: str = ""
    title: str = ""
    description: str = ""
    severity: str = "medium"
    category: str = "runtime"
    source: str = ""
    context: Optional[str] = None
    tags: Optional[str] = None


@dataclass
class Feeling:
    label: str = ""


@dataclass
class Idea:
    id: str = ""
    idea: str = ""
    share: str = "private"
    importance: str = "medium"
    tags: Optional[str] = None
    context: Optional[str] = None


@dataclass
class Memory:
    id: str = ""
    moment: str = ""
    meaning: str = ""
    reason: str = ""
    importance: str = "medium"
    term: str = "short"
    memory_type: str = "standard"
    tags: Optional[str] = None


@dataclass
class Task:
    id: str = ""
    action: str = ""
    time: str = ""
    priority: str = ""
    project: str = ""
    status: str = "todo"
    assignee: Optional[str] = None
    tags: Optional[str] = None
    dependencies: Optional[str] = None
    context: Optional[str] = None
    progress: Optional[int] = None


@dataclass
class TrainingData:
    id: str = ""
    data_type: str = "instruction"
    prompt: str = ""
    completion: str = ""
    context: Optional[str] = None
    tags: Optional[str] = None
    quality: Optional[float] = None
    source: str = "manual"


@dataclass
class SearchOptions:
    limit: Optional[int] = None
    data_types: Optional[str] = None
    since: Optional[str] = None
    until: Optional[str] = None


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


@dataclass
class SearchResults:
    task_results: List[Task] = field(default_factory=list)
    memory_results: List[Memory] = field(default_factory=list)
    idea_results: List[Idea] = field(default_factory=list)
    error_results: List[Error] = field(default_factory=list)
    training_results: List[TrainingData] = field(default_factory=list)



# -----------------------------
# ChatContent - using proper types
# -----------------------------
@dataclass
class ChatContent:
    tasks: List[Task] = field(default_factory=list)
    memories: List[Memory] = field(default_factory=list)
    ideas: List[Idea] = field(default_factory=list)
    agent_assignments: List[AgentAssignment] = field(default_factory=list)
    code_chunks: List[CodeChunk] = field(default_factory=list)
    errors: List[Error] = field(default_factory=list)
    training_data: List[Any] = field(default_factory=list)
    feelings: List[Any] = field(default_factory=list)


# -----------------------------
# Commands (dataclasses)
# -----------------------------
@dataclass
class Register:
    user_id: Optional[str] = None


@dataclass
class ListKeys:
    active_only: bool = False


@dataclass
class CheckKeys:
    public_key: str
    private_key: Optional[str] = None


@dataclass
class DeactivateKey:
    user_id: str


@dataclass
class ActivateKey:
    user_id: str


@dataclass
class RemoveKey:
    user_id: str


@dataclass
class PlanQueue:
    task_name: str
    task_description: str
    priority: str
    project_id: Optional[str] = None


@dataclass
class ListQueue:
    status: Optional[str] = None


@dataclass
class BacklogQueue:
    pass


@dataclass
class ActiveQueue:
    pass


@dataclass
class CompleteQueue:
    pass


@dataclass
class StartQueue:
    queue_item_id: str


@dataclass
class EndQueue:
    session_id: str


@dataclass
class StartServer:
    host: str = "127.0.0.1"
    port: int = 8636


@dataclass
class ServerStatus:
    pass


@dataclass
class ServerEndpoints:
    pass


@dataclass
class SearchAll:
    query: str
    types: str = "all"


@dataclass
class Chat:
    message: str


@dataclass
class CreateError:
    title: str
    description: str
    severity: str = "medium"
    category: str = "runtime"
    source: str = "cli"
    context: Optional[str] = None
    tags: Optional[str] = None


@dataclass
class ListErrors:
    severity: Optional[str] = None
    category: Optional[str] = None
    unresolved_only: bool = False


@dataclass
class ShowError:
    id: str


@dataclass
class ResolveError:
    id: str
    resolution: Optional[str] = None


@dataclass
class DeleteError:
    id: str


@dataclass
class CreateTraining:
    data_type: str
    prompt: str
    completion: str
    context: Optional[str] = None
    tags: Optional[str] = None
    quality: Optional[float] = None
    source: str = "cli"


@dataclass
class ListTraining:
    data_type: Optional[str] = None
    min_quality: Optional[float] = None


@dataclass
class ShowTraining:
    id: str


@dataclass
class TrainingStats:
    pass


@dataclass
class ExportTraining:
    format: str = "json"
    data_type: Optional[str] = None
    min_quality: Optional[float] = None
    output_file: Optional[str] = None


@dataclass
class CollectTraining:
    message: str


@dataclass
class UpdateTraining:
    id: str
    data_type: Optional[str] = None
    prompt: Optional[str] = None
    completion: Optional[str] = None
    context: Optional[str] = None
    tags: Optional[str] = None
    quality: Optional[float] = None
    source: Optional[str] = None


@dataclass
class DeleteTraining:
    id: str


@dataclass
class CreateAgent:
    id: str
    name: str
    description: str
    category: str
    capabilities: Optional[str] = None
    specializations: Optional[str] = None
    model_provider: str = "openai"
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1024
    tags: Optional[str] = None
    system_prompt: Optional[str] = None
    prompt_template: Optional[str] = None
    auto_format_code: Optional[bool] = None
    include_examples: Optional[bool] = None
    explain_complexity: Optional[bool] = None
    suggest_tests: Optional[bool] = None
    tools: Optional[str] = None
    max_response_length: Optional[int] = None
    timeout_seconds: Optional[int] = None
    requests_per_minute: Optional[int] = None
    tokens_per_hour: Optional[int] = None


@dataclass
class ListAgents:
    pass


@dataclass
class ShowAgent:
    id: str


@dataclass
class AssignAgent:
    agent_id: str
    task_id: str
    project_id: str


@dataclass
class UpdateAgent:
    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    capabilities: Optional[str] = None
    specializations: Optional[str] = None
    model_provider: Optional[str] = None
    model_name: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    tags: Optional[str] = None
    system_prompt: Optional[str] = None
    prompt_template: Optional[str] = None
    auto_format_code: Optional[bool] = None
    include_examples: Optional[bool] = None
    explain_complexity: Optional[bool] = None
    suggest_tests: Optional[bool] = None
    tools: Optional[str] = None
    max_response_length: Optional[int] = None
    timeout_seconds: Optional[int] = None
    requests_per_minute: Optional[int] = None
    tokens_per_hour: Optional[int] = None


@dataclass
class DeleteAgent:
    id: str


@dataclass
class SetModel:
    model_name: str


@dataclass
class ShowModel:
    pass


@dataclass
class ListModels:
    pass


@dataclass
class CreateIdea:
    idea: str
    share: str = "team"
    importance: str = "medium"
    tags: Optional[str] = None
    context: Optional[str] = None


@dataclass
class ListIdeas:
    share: Optional[str] = None
    importance: Optional[str] = None


@dataclass
class ShowIdea:
    id: str


@dataclass
class CreateMemory:
    moment: str
    meaning: str
    reason: str = ""
    importance: str = "medium"
    term: Optional[str] = None
    memory_type: str = "standard"
    tags: Optional[str] = None


@dataclass
class CreateSecretMemory:
    moment: str
    meaning: str
    reason: str = ""
    importance: str = "medium"
    term: Optional[str] = None
    tags: Optional[str] = None


@dataclass
class CreateHumanMemory:
    moment: str
    meaning: str
    reason: str = ""
    importance: str = "medium"
    term: Optional[str] = None
    tags: Optional[str] = None


@dataclass
class CreateEmotionalMemory:
    moment: str
    meaning: str
    reason: str = ""
    emotion: str = "happy"
    importance: str = "medium"
    term: Optional[str] = None
    tags: Optional[str] = None


@dataclass
class ListMemories:
    importance: Optional[str] = None
    term: Optional[str] = None
    memory_type: Optional[str] = None


@dataclass
class ShowMemory:
    id: str


@dataclass
class MemoryTypes:
    pass


@dataclass
class CreateProject:
    name: str
    description: Optional[str] = None


@dataclass
class ListProjects:
    pass


@dataclass
class ShowProject:
    name: str


@dataclass
class ArchiveProject:
    name: str


@dataclass
class DeleteProject:
    name: str


@dataclass
class UpdateProject:
    name: str
    new_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


@dataclass
class ShowTask:
    id: str


@dataclass
class ListTasks:
    project: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee: Optional[str] = None
    tags: Optional[str] = None
    search: Optional[str] = None


@dataclass
class AddTask:
    action: str
    time: str
    priority: str
    project: str
    status: str
    assignee: Optional[str] = None
    tags: Optional[str] = None
    dependencies: Optional[str] = None
    context: Optional[str] = None
    progress: Optional[int] = None


@dataclass
class UpdateTask:
    id: str
    action: Optional[str] = None
    time: Optional[str] = None
    priority: Optional[str] = None
    project: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[str] = None
    tags: Optional[str] = None
    dependencies: Optional[str] = None
    context: Optional[str] = None
    progress: Optional[int] = None


@dataclass
class Stats:
    pass


@dataclass
class SearchTasks:
    query: str


@dataclass
class StepsShow:
    task_id: str


@dataclass
class StepsAdd:
    task_id: str
    step: str


@dataclass
class StepsUpdate:
    task_id: str
    step_index: int
    new_step: str


@dataclass
class StepsDone:
    task_id: str


@dataclass
class StepsArchive:
    task_id: str

# ----------------------------------------------------------------------
# Enums – one class per Rust enum
# ----------------------------------------------------------------------
class Commands(Enum):
    INIT = "init"
    ADD = "add"
    LIST = "list"
    SHOW = "show"
    UPDATE = "update"
    COMPLETE = "complete"
    FIX_CONSISTENCY = "fix-consistency"
    CHECK_STRUCTURE = "check-structure"
    ENSURE_STRUCTURE = "ensure-structure"
    REGISTER = "register"
    REGISTRATION_STATUS = "registration-status"
    CLEAR_REGISTRATION = "clear-registration"
    DELETE = "delete"
    PROJECT = "project"
    SEARCH = "search"
    STATS = "stats"
    BACKUP = "backup"
    LIST_BACKUPS = "list-backups"
    RESTORE = "restore"
    MEMORY = "memory"
    IDEA = "idea"
    AGENT = "agent"
    EMB = "emb"
    ERROR = "error"
    TRAIN = "train"
    CHAT = "chat"
    SEARCH_ALL = "search-all"
    MAESTRO = "maestro"
    SERVER = "server"
    ML = "ml"
    IND_DEMO = "ind-demo"
    QUEUE = "queue"
    API = "api"
    TDZ_CNT = "tdzcnt"
    EXPORT_EMBEDDINGS = "export-embeddings"
    MIGRATE = "migrate"
    TUI = "tui"
    EXTRACT = "extract"
    STRATEGY = "strategy"
    STEPS = "steps"


class AddCommands(Enum):
    TASK = "task"


class ListCommands(Enum):
    TASKS = "tasks"


class ShowCommands(Enum):
    TASK = "task"


class SearchCommands(Enum):
    TASKS = "tasks"


class StatsCommands(Enum):
    SHOW = "show"


class BackupCommands(Enum):
    CREATE = "create"


class ProjectCommands(Enum):
    CREATE = "create"
    LIST = "list"
    SHOW = "show"
    ARCHIVE = "archive"
    DELETE = "delete"
    UPDATE = "update"


class MemoryCommands(Enum):
    CREATE = "create"
    CREATE_SECRET = "create-secret"
    CREATE_HUMAN = "create-human"
    CREATE_EMOTIONAL = "create-emotional"
    LIST = "list"
    SHOW = "show"
    TYPES = "types"


class IdeaCommands(Enum):
    CREATE = "create"
    LIST = "list"
    SHOW = "show"


class AgentCommands(Enum):
    LIST = "list"
    SHOW = "show"
    CREATE = "create"
    ASSIGN = "assign"
    UPDATE = "update"
    DELETE = "delete"


class EmbCommands(Enum):
    SET_MODEL = "set-model"
    SHOW_MODEL = "show-model"
    LIST_MODELS = "list-models"


class ErrorCommands(Enum):
    CREATE = "create"
    LIST = "list"
    SHOW = "show"
    RESOLVE = "resolve"
    DELETE = "delete"


class TrainingCommands(Enum):
    CREATE = "create"
    LIST = "list"
    SHOW = "show"
    STATS = "stats"
    EXPORT = "export"
    COLLECT = "collect"
    UPDATE = "update"
    DELETE = "delete"


class MaestroCommands(Enum):
    INIT = "init"
    COLLECT_CONVERSATION = "collect-conversation"
    COLLECT_TOOL = "collect-tool"
    LIST = "list"
    STATS = "stats"
    EXPORT = "export"
    INTEGRATE = "integrate"


class ServerCommands(Enum):
    START = "start"
    STATUS = "status"
    ENDPOINTS = "endpoints"


class MLCommands(Enum):
    PROCESS = "process"
    TRAIN = "train"
    LIST = "list"
    SHOW = "show"
    LOAD = "load"
    SAVE = "save"
    TEST = "test"
    GENERATE_TRAINING_DATA = "generate-training-data"
    ADVANCED_PROCESS = "advanced-process"
    ADVANCED_TRAIN = "advanced-train"
    ADVANCED_INFER = "advanced-infer"


class QueueCommands(Enum):
    PLAN = "plan"
    LIST = "list"
    BACKLOG = "backlog"
    ACTIVE = "active"
    COMPLETE = "complete"
    START = "start"
    END = "end"


class ApiCommands(Enum):
    REGISTER = "register"
    LIST = "list"
    CHECK = "check"
    DEACTIVATE = "deactivate"
    ACTIVATE = "activate"
    REMOVE = "remove"


class StepsCommands(Enum):
    SHOW = "show"
    ADD = "add"
    UPDATE = "update"
    DONE = "done"
    ARCHIVE = "archive"


class QueueStatus(Enum):
    BACKLOG = "backlog"
    ACTIVE = "active"
    COMPLETE = "complete"


ACTIVATE = "activate"
ACTIVE = "active"
ADD = "add"
ADVANCED_INFER = "advanced-infer"
ASSIGN = "assign"
ADVANCED_PROCESS = "advanced-process"
ADVANCED_TRAIN = "advanced-train"
AGENT = "agent"
API = "api"
ARCHIVE = "archive"
BACKLOG = "backlog"
BACKUP = "backup"
CHAT = "chat"
CHECK = "check"
CHECK_STRUCTURE = "check-structure"
CLEAR_REGISTRATION = "clear-registration"
COLLECT = "collect"
COLLECT_CONVERSATION = "collect-conversation"
COLLECT_TOOL = "collect-tool"
COMPLETE = "complete"
CREATE = "create"
CREATE_EMOTIONAL = "create-emotional"
CREATE_HUMAN = "create-human"
CREATE_SECRET = "create-secret"
DEACTIVATE = "deactivate"
DELETE = "delete"
DONE = "done"
EMB = "emb"
END = "end"
ENDPOINTS = "endpoints"
ENSURE_STRUCTURE = "ensure-structure"
ERROR = "error"
EXPORT = "export"
EXPORT_EMBEDDINGS = "export-embeddings"
EXTRACT = "extract"
FIX_CONSISTENCY = "fix-consistency"
GENERATE_TRAINING_DATA = "generate-training-data"
IDEA = "idea"
IND_DEMO = "ind-demo"
INIT = "init"
INTEGRATE = "integrate"
LIST = "list"
LIST_BACKUPS = "list-backups"
LIST_MODELS = "list-models"
LOAD = "load"
MAESTRO = "maestro"
MEMORY = "memory"
MIGRATE = "migrate"
ML = "ml"
PLAN = "plan"
PROCESS = "process"
PROJECT = "project"
QUEUE = "queue"
REGISTER = "register"
REGISTRATION_STATUS = "registration-status"
REMOVE = "remove"
RESOLVE = "resolve"
RESTORE = "restore"
SAVE = "save"
SEARCH = "search"
SEARCH_ALL = "search-all"
SERVER = "server"
SET_MODEL = "set-model"
SHOW = "show"
SHOW_MODEL = "show-model"
START = "start"
STATS = "stats"
STATUS = "status"
STEPS = "steps"
STRATEGY = "strategy"
TASK = "task"
TASKS = "tasks"
TDZ_CNT = "tdzcnt"
TEST = "test"
TRAIN = "train"
TUI = "tui"
TYPES = "types"
UPDATE = "update"


@dataclass
class QueueItem:
    id: str
    task_name: str
    task_description: str
    priority: str
    project_id: Optional[str]
    status: QueueStatus
    created_at: datetime
    updated_at: datetime


@dataclass
class TaskUpdate:
    id: str
    action: Optional[str] = None
    time: Optional[str] = None
    priority: Optional[str] = None
    project: Optional[str] = None
    status: Optional[str] = None
    assignee: Optional[str] = None
    tags: Optional[str] = None
    dependencies: Optional[str] = None
    context: Optional[str] = None
    progress: Optional[int] = None


# ----------------------------------------------------------------------
# Search engine – full implementation matching the Rust impl
# ----------------------------------------------------------------------
class SearchEngine:
    """
    A simple in-memory search engine across tasks, memories, ideas, errors, and training data.
    
    The engine supports keyword search with basic filtering by data types and time ranges.
    """
    
    def __init__(self) -> None:
        self.tasks: List[Task] = []
        self.memories: List[Memory] = []
        self.ideas: List[Idea] = []
        self.errors: List[Error] = []
        self.training_data: List[TrainingData] = []

    def update_index(self, content: ChatContent) -> None:
        """
        Merge a ChatContent payload into the search index.
        
        Args:
            content: ChatContent object with sequences of domain models.
        """
        if hasattr(content, "tasks") and isinstance(content.tasks, list):
            self.tasks.extend(content.tasks)
        if hasattr(content, "memories") and isinstance(content.memories, list):
            self.memories.extend(content.memories)
        if hasattr(content, "ideas") and isinstance(content.ideas, list):
            self.ideas.extend(content.ideas)
        if hasattr(content, "errors") and isinstance(content.errors, list):
            self.errors.extend(content.errors)
        if hasattr(content, "training_data") and isinstance(content.training_data, list):
            self.training_data.extend(content.training_data)

    def search(self, query: str, options: SearchOptions) -> SearchResults:
        """
        Perform a keyword-based search across all indexed content types.
        
        Args:
            query: Search query string.
            options: SearchOptions including filters and limit.
            
        Returns:
            SearchResults object containing matching items.
        """
        query_lower = query.lower() if query else ""
        results = SearchResults()
        
        if not query_lower:
            return results
        
        allowed_types = set()
        if options.data_types:
            allowed_types = {dt.strip().lower() for dt in options.data_types.split(",")}
        
        for task in self.tasks:
            if self._matches_query(query_lower, task.action, task.tags, task.context):
                if not allowed_types or "tasks" in allowed_types or "task" in allowed_types:
                    results.task_results.append(task)
        
        for memory in self.memories:
            if self._matches_query(query_lower, memory.moment, memory.tags, memory.meaning):
                if not allowed_types or "memories" in allowed_types or "memory" in allowed_types:
                    results.memory_results.append(memory)
        
        for idea in self.ideas:
            if self._matches_query(query_lower, idea.idea, idea.tags, idea.context):
                if not allowed_types or "ideas" in allowed_types or "idea" in allowed_types:
                    results.idea_results.append(idea)
        
        for error in self.errors:
            if self._matches_query(query_lower, error.title, error.tags, error.description):
                if not allowed_types or "errors" in allowed_types or "error" in allowed_types:
                    results.error_results.append(error)
        
        for training in self.training_data:
            if self._matches_query(query_lower, training.prompt, training.tags, training.completion):
                if not allowed_types or "training" in allowed_types or "training_data" in allowed_types:
                    results.training_results.append(training)
        
        if options.limit is not None and options.limit > 0:
            results.task_results = results.task_results[:options.limit]
            results.memory_results = results.memory_results[:options.limit]
            results.idea_results = results.idea_results[:options.limit]
            results.error_results = results.error_results[:options.limit]
            results.training_results = results.training_results[:options.limit]
        
        return results
    
    def _matches_query(self, query_lower: str, primary_text: Optional[str], tags: Optional[str], secondary_text: Optional[str] = None) -> bool:
        """Check if the query matches in primary/secondary text or tags."""
        if primary_text and query_lower in primary_text.lower():
            return True
        if secondary_text and query_lower in secondary_text.lower():
            return True
        if tags:
            tag_list = [t.strip() for t in tags.split(",")] if isinstance(tags, str) else tags
            return any(query_lower in tag.lower() for tag in tag_list)
        return False


# ----------------------------------------------------------------------
# Argparse construction – mirrors the Rust clap layout
# ----------------------------------------------------------------------
def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todozi",
        description="Todozi CLI (Python translation)",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")

    # ------------------------------------------------------------------
    # Top‑level sub‑parsers (dest = "command")
    # ------------------------------------------------------------------
    sub = parser.add_subparsers(dest="command", required=True)

    # ---------- init ----------
    sub.add_parser(Commands.INIT.value, help="Initialize the workspace")

    # ---------- add ----------
    add_parser = sub.add_parser(Commands.ADD.value, help="Add operations")
    add_sub = add_parser.add_subparsers(dest="add_sub", required=True)
    add_task = add_sub.add_parser(AddCommands.TASK.value, help="Add a new task")
    add_task.add_argument("action", help="Action of the task")
    add_task.add_argument("--time", required=True, help="Time specification")
    add_task.add_argument("--priority", required=True, help="Priority of the task")
    add_task.add_argument("--project", required=True, help="Project name/ID")
    add_task.add_argument("--status", default="todo", help="Status (default: todo)")
    add_task.add_argument("--assignee", help="Assignee")
    add_task.add_argument("--tags", help="Tags")
    add_task.add_argument("--dependencies", help="Dependencies")
    add_task.add_argument("--context", help="Context")
    add_task.add_argument("--progress", type=int, help="Progress (0‑100)")

    # ---------- list ----------
    list_parser = sub.add_parser(Commands.LIST.value, help="List operations")
    list_sub = list_parser.add_subparsers(dest="list_sub", required=True)
    list_tasks = list_sub.add_parser(ListCommands.TASKS.value, help="List tasks")
    list_tasks.add_argument("--project", help="Filter by project")
    list_tasks.add_argument("--status", help="Filter by status")
    list_tasks.add_argument("--priority", help="Filter by priority")
    list_tasks.add_argument("--assignee", help="Filter by assignee")
    list_tasks.add_argument("--tags", help="Filter by tags")
    list_tasks.add_argument("--search", help="Search string")

    # ---------- show ----------
    show_parser = sub.add_parser(Commands.SHOW.value, help="Show operations")
    show_sub = show_parser.add_subparsers(dest="show_sub", required=True)
    show_task = show_sub.add_parser(ShowCommands.TASK.value, help="Show a task by id")
    show_task.add_argument("id", help="Task id")

    # ---------- update ----------
    update = sub.add_parser(Commands.UPDATE.value, help="Update a task")
    update.add_argument("id", help="Task id")
    update.add_argument("--action", help="Action")
    update.add_argument("--time", help="Time")
    # Both short and long options map to the same dest
    update.add_argument("--priority", "-r", dest="priority", help="Priority")
    update.add_argument("--project", "-j", dest="project", help="Project")
    update.add_argument("--status", help="Status")
    update.add_argument("--assignee", "-u", dest="assignee", help="Assignee")
    update.add_argument("--tags", "-g", dest="tags", help="Tags")
    update.add_argument("--dependencies", help="Dependencies")
    update.add_argument("--context", help="Context")
    update.add_argument("--progress", type=int, help="Progress (0‑100)")

    # ---------- complete ----------
    complete = sub.add_parser(Commands.COMPLETE.value, help="Complete a task")
    complete.add_argument("id", help="Task id")

    # ---------- consistency / structure ----------
    sub.add_parser(Commands.FIX_CONSISTENCY.value, help="Fix consistency")
    sub.add_parser(Commands.CHECK_STRUCTURE.value, help="Check structure")
    sub.add_parser(Commands.ENSURE_STRUCTURE.value, help="Ensure structure")

    # ---------- register ----------
    register = sub.add_parser(Commands.REGISTER.value, help="Register instance")
    register.add_argument("--server-url", default="https://todozi.com", help="Server URL")

    sub.add_parser(Commands.REGISTRATION_STATUS.value, help="Registration status")
    sub.add_parser(Commands.CLEAR_REGISTRATION.value, help="Clear registration")

    # ---------- delete ----------
    delete = sub.add_parser(Commands.DELETE.value, help="Delete an item")
    delete.add_argument("id", help="Item id")

    # ---------- project ----------
    project = sub.add_parser(Commands.PROJECT.value, help="Project operations")
    project_sub = project.add_subparsers(dest="project_sub", required=True)
    p_create = project_sub.add_parser(ProjectCommands.CREATE.value, help="Create project")
    p_create.add_argument("name", help="Project name")
    p_create.add_argument("--description", help="Project description")
    project_sub.add_parser(ProjectCommands.LIST.value, help="List projects")
    p_show = project_sub.add_parser(ProjectCommands.SHOW.value, help="Show project")
    p_show.add_argument("name", help="Project name")
    p_archive = project_sub.add_parser(ProjectCommands.ARCHIVE.value, help="Archive project")
    p_archive.add_argument("name", help="Project name")
    p_delete = project_sub.add_parser(ProjectCommands.DELETE.value, help="Delete project")
    p_delete.add_argument("name", help="Project name")
    p_update = project_sub.add_parser(ProjectCommands.UPDATE.value, help="Update project")
    p_update.add_argument("name", help="Project name")
    p_update.add_argument("--new-name", help="New name")
    p_update.add_argument("--description", help="Description")
    p_update.add_argument("--status", help="Status")

    # ---------- search ----------
    search = sub.add_parser(Commands.SEARCH.value, help="Search operations")
    search_sub = search.add_subparsers(dest="search_sub", required=True)
    s_tasks = search_sub.add_parser(SearchCommands.TASKS.value, help="Search tasks")
    s_tasks.add_argument("query", help="Search query")

    # ---------- stats ----------
    stats = sub.add_parser(Commands.STATS.value, help="Statistics")
    stats_sub = stats.add_subparsers(dest="stats_sub", required=True)
    stats_sub.add_parser(StatsCommands.SHOW.value, help="Show statistics")

    # ---------- backup ----------
    backup = sub.add_parser(Commands.BACKUP.value, help="Backup operations")
    backup_sub = backup.add_subparsers(dest="backup_sub", required=True)
    backup_sub.add_parser(BackupCommands.CREATE.value, help="Create a backup")
    sub.add_parser(Commands.LIST_BACKUPS.value, help="List backups")
    restore = sub.add_parser(Commands.RESTORE.value, help="Restore from a backup")
    restore.add_argument("backup_name", help="Backup name")

    # ---------- memory ----------
    memory = sub.add_parser(Commands.MEMORY.value, help="Memory operations")
    memory_sub = memory.add_subparsers(dest="memory_sub", required=True)
    m_create = memory_sub.add_parser(MemoryCommands.CREATE.value, help="Create a memory")
    m_create.add_argument("moment", help="Memory moment")
    m_create.add_argument("meaning", help="Memory meaning")
    m_create.add_argument("reason", help="Memory reason")
    m_create.add_argument("--importance", default="medium", help="Importance")
    m_create.add_argument("--term", default="short", help="Term")
    m_create.add_argument("--memory-type", "-T", default="standard", help="Memory type")
    m_create.add_argument("--tags", help="Tags")
    # --- secret ---
    m_secret = memory_sub.add_parser(MemoryCommands.CREATE_SECRET.value, help="Create a secret memory")
    m_secret.add_argument("moment", help="Memory moment")
    m_secret.add_argument("meaning", help="Memory meaning")
    m_secret.add_argument("reason", help="Memory reason")
    m_secret.add_argument("--importance", default="medium", help="Importance")
    m_secret.add_argument("--term", default="short", help="Term")
    m_secret.add_argument("--tags", help="Tags")
    # --- human ---
    m_human = memory_sub.add_parser(MemoryCommands.CREATE_HUMAN.value, help="Create a human memory")
    m_human.add_argument("moment", help="Memory moment")
    m_human.add_argument("meaning", help="Memory meaning")
    m_human.add_argument("reason", help="Memory reason")
    m_human.add_argument("--importance", default="high", help="Importance")
    m_human.add_argument("--term", default="long", help="Term")
    m_human.add_argument("--tags", help="Tags")
    # --- emotional ---
    m_emotional = memory_sub.add_parser(MemoryCommands.CREATE_EMOTIONAL.value, help="Create an emotional memory")
    m_emotional.add_argument("moment", help="Memory moment")
    m_emotional.add_argument("meaning", help="Memory meaning")
    m_emotional.add_argument("reason", help="Memory reason")
    m_emotional.add_argument("emotion", help="Emotion")
    m_emotional.add_argument("--importance", default="medium", help="Importance")
    m_emotional.add_argument("--term", default="short", help="Term")
    m_emotional.add_argument("--tags", help="Tags")
    # --- list ---
    m_list = memory_sub.add_parser(MemoryCommands.LIST.value, help="List memories")
    m_list.add_argument("--importance", help="Filter by importance")
    m_list.add_argument("--term", help="Filter by term")
    m_list.add_argument("--memory-type", "-T", help="Filter by memory type")
    # --- show ---
    m_show = memory_sub.add_parser(MemoryCommands.SHOW.value, help="Show a memory")
    m_show.add_argument("id", help="Memory id")
    # --- types ---
    memory_sub.add_parser(MemoryCommands.TYPES.value, help="List memory types")

    # ---------- idea ----------
    idea = sub.add_parser(Commands.IDEA.value, help="Idea operations")
    idea_sub = idea.add_subparsers(dest="idea_sub", required=True)
    i_create = idea_sub.add_parser(IdeaCommands.CREATE.value, help="Create an idea")
    i_create.add_argument("idea", help="Idea text")
    i_create.add_argument("--share", default="private", help="Share setting")
    i_create.add_argument("--importance", default="medium", help="Importance")
    i_create.add_argument("--tags", help="Tags")
    i_create.add_argument("--context", help="Context")
    i_list = idea_sub.add_parser(IdeaCommands.LIST.value, help="List ideas")
    i_list.add_argument("--share", help="Filter by share")
    i_list.add_argument("--importance", help="Filter by importance")
    i_show = idea_sub.add_parser(IdeaCommands.SHOW.value, help="Show an idea")
    i_show.add_argument("id", help="Idea id")

    # ---------- agent ----------
    agent = sub.add_parser(Commands.AGENT.value, help="Agent operations")
    agent_sub = agent.add_subparsers(dest="agent_sub", required=True)
    agent_sub.add_parser(AgentCommands.LIST.value, help="List agents")
    a_show = agent_sub.add_parser(AgentCommands.SHOW.value, help="Show an agent")
    a_show.add_argument("id", help="Agent id")
    a_create = agent_sub.add_parser(AgentCommands.CREATE.value, help="Create an agent")
    a_create.add_argument("id", help="Agent id")
    a_create.add_argument("name", help="Agent name")
    a_create.add_argument("description", help="Agent description")
    a_create.add_argument("--category", default="general", help="Category")
    a_create.add_argument("--capabilities", help="Capabilities")
    a_create.add_argument("--specializations", help="Specializations")
    a_create.add_argument("--model-provider", default="todozi", help="Model provider")
    a_create.add_argument("--model-name", default="baton", help="Model name")
    a_create.add_argument("--temperature", type=float, default=0.2, help="Temperature")
    a_create.add_argument("--max-tokens", type=int, default=4096, help="Max tokens")
    a_create.add_argument("--tags", help="Tags")
    a_create.add_argument("--system-prompt", help="System prompt")
    a_create.add_argument("--prompt-template", help="Prompt template")
    a_create.add_argument("--auto-format-code", action="store_true", help="Auto format code")
    a_create.add_argument("--include-examples", action="store_true", help="Include examples")
    a_create.add_argument("--explain-complexity", action="store_true", help="Explain complexity")
    a_create.add_argument("--suggest-tests", action="store_true", help="Suggest tests")
    a_create.add_argument("--tools", help="Tools")
    a_create.add_argument("--max-response-length", type=int, help="Max response length")
    a_create.add_argument("--timeout-seconds", type=int, help="Timeout seconds")
    a_create.add_argument("--requests-per-minute", type=int, help="Requests per minute")
    a_create.add_argument("--tokens-per-hour", type=int, help="Tokens per hour")
    a_assign = agent_sub.add_parser(AgentCommands.ASSIGN.value, help="Assign an agent to a task")
    a_assign.add_argument("agent_id", help="Agent id")
    a_assign.add_argument("task_id", help="Task id")
    a_assign.add_argument("project_id", help="Project id")
    a_update = agent_sub.add_parser(AgentCommands.UPDATE.value, help="Update an agent")
    a_update.add_argument("id", help="Agent id")
    a_update.add_argument("--name", help="Name")
    a_update.add_argument("--description", help="Description")
    a_update.add_argument("--category", help="Category")
    a_update.add_argument("--capabilities", help="Capabilities")
    a_update.add_argument("--specializations", help="Specializations")
    a_update.add_argument("--system-prompt", help="System prompt")
    a_update.add_argument("--prompt-template", help="Prompt template")
    a_update.add_argument("--model-provider", help="Model provider")
    a_update.add_argument("--model-name", help="Model name")
    a_update.add_argument("--temperature", type=float, help="Temperature")
    a_update.add_argument("--max-tokens", type=int, help="Max tokens")
    a_update.add_argument("--tags", help="Tags")
    a_update.add_argument("--auto-format-code", action="store_true", help="Auto format code")
    a_update.add_argument("--include-examples", action="store_true", help="Include examples")
    a_update.add_argument("--explain-complexity", action="store_true", help="Explain complexity")
    a_update.add_argument("--suggest-tests", action="store_true", help="Suggest tests")
    a_update.add_argument("--tools", help="Tools")
    a_update.add_argument("--max-response-length", type=int, help="Max response length")
    a_update.add_argument("--timeout-seconds", type=int, help="Timeout seconds")
    a_update.add_argument("--requests-per-minute", type=int, help="Requests per minute")
    a_update.add_argument("--tokens-per-hour", type=int, help="Tokens per hour")
    a_delete = agent_sub.add_parser(AgentCommands.DELETE.value, help="Delete an agent")
    a_delete.add_argument("id", help="Agent id")

    # ---------- emb ----------
    emb = sub.add_parser(Commands.EMB.value, help="Embedding model operations")
    emb_sub = emb.add_subparsers(dest="emb_sub", required=True)
    e_set = emb_sub.add_parser(EmbCommands.SET_MODEL.value, help="Set default embedding model")
    e_set.add_argument("model_name", help="Model name (e.g. from HuggingFace)")
    emb_sub.add_parser(EmbCommands.SHOW_MODEL.value, help="Show current embedding model")
    emb_sub.add_parser(EmbCommands.LIST_MODELS.value, help="List popular embedding models")

    # ---------- error ----------
    error = sub.add_parser(Commands.ERROR.value, help="Error operations")
    error_sub = error.add_subparsers(dest="error_sub", required=True)
    er_create = error_sub.add_parser(ErrorCommands.CREATE.value, help="Create an error")
    er_create.add_argument("title", help="Error title")
    er_create.add_argument("description", help="Error description")
    er_create.add_argument("--severity", default="medium", help="Severity")
    er_create.add_argument("--category", default="runtime", help="Category")
    er_create.add_argument("source", help="Source")
    er_create.add_argument("--context", help="Context")
    er_create.add_argument("--tags", help="Tags")
    er_list = error_sub.add_parser(ErrorCommands.LIST.value, help="List errors")
    er_list.add_argument("--severity", help="Filter by severity")
    er_list.add_argument("--category", help="Filter by category")
    er_list.add_argument("--unresolved-only", action="store_true", help="Show only unresolved errors")
    er_show = error_sub.add_parser(ErrorCommands.SHOW.value, help="Show an error")
    er_show.add_argument("id", help="Error id")
    er_resolve = error_sub.add_parser(ErrorCommands.RESOLVE.value, help="Resolve an error")
    er_resolve.add_argument("id", help="Error id")
    er_resolve.add_argument("--resolution", help="Resolution description")
    er_delete = error_sub.add_parser(ErrorCommands.DELETE.value, help="Delete an error")
    er_delete.add_argument("id", help="Error id")

    # ---------- train ----------
    train = sub.add_parser(Commands.TRAIN.value, help="Training data operations")
    train_sub = train.add_subparsers(dest="train_sub", required=True)
    t_create = train_sub.add_parser(TrainingCommands.CREATE.value, help="Create training data")
    t_create.add_argument("--data-type", default="instruction", help="Data type")
    t_create.add_argument("prompt", help="Prompt")
    t_create.add_argument("completion", help="Completion")
    t_create.add_argument("--context", help="Context")
    t_create.add_argument("--tags", help="Tags")
    t_create.add_argument("--quality", type=float, help="Quality")
    t_create.add_argument("--source", default="manual", help="Source")
    t_list = train_sub.add_parser(TrainingCommands.LIST.value, help="List training data")
    t_list.add_argument("--data-type", help="Filter by data type")
    t_list.add_argument("--min-quality", type=float, help="Minimum quality")
    t_show = train_sub.add_parser(TrainingCommands.SHOW.value, help="Show training data")
    t_show.add_argument("id", help="Training data id")
    train_sub.add_parser(TrainingCommands.STATS.value, help="Show statistics")
    t_export = train_sub.add_parser(TrainingCommands.EXPORT.value, help="Export training data")
    t_export.add_argument("--format", default="json", help="Export format")
    t_export.add_argument("--data-type", help="Filter by data type")
    t_export.add_argument("--min-quality", type=float, help="Minimum quality")
    t_export.add_argument("--output-file", help="Output file")
    t_collect = train_sub.add_parser(TrainingCommands.COLLECT.value, help="Collect training data")
    t_collect.add_argument("message", help="Message")
    t_update = train_sub.add_parser(TrainingCommands.UPDATE.value, help="Update training data")
    t_update.add_argument("id", help="Training data id")
    t_update.add_argument("--data-type", help="Data type")
    t_update.add_argument("--prompt", help="Prompt")
    t_update.add_argument("--completion", help="Completion")
    t_update.add_argument("--context", help="Context")
    t_update.add_argument("--tags", help="Tags")
    t_update.add_argument("--quality", type=int, help="Quality (0‑100)")
    t_update.add_argument("--source", help="Source")
    t_delete = train_sub.add_parser(TrainingCommands.DELETE.value, help="Delete training data")
    t_delete.add_argument("id", help="Training data id")

    # ---------- chat ----------
    chat = sub.add_parser(Commands.CHAT.value, help="Chat")
    chat.add_argument("message", help="Chat message")

    # ---------- search-all ----------
    search_all = sub.add_parser(Commands.SEARCH_ALL.value, help="Search all data types")
    search_all.add_argument("query", help="Query")
    search_all.add_argument("--types", default="tasks,memories,ideas,errors", help="Comma‑separated types")

    # ---------- maestro ----------
    maestro = sub.add_parser(Commands.MAESTRO.value, help="Maestro operations")
    maestro_sub = maestro.add_subparsers(dest="maestro_sub", required=True)
    maestro_sub.add_parser(MaestroCommands.INIT.value, help="Initialize Maestro")
    ma_conv = maestro_sub.add_parser(MaestroCommands.COLLECT_CONVERSATION.value, help="Collect conversation")
    ma_conv.add_argument("--session-id", required=True, help="Session id")
    ma_conv.add_argument("--conversation", required=True, help="Conversation text")
    ma_conv.add_argument("--context-length", type=int, default=0, help="Context length")
    ma_conv.add_argument("--tool-calls", help="Tool calls")
    ma_conv.add_argument("--response", required=True, help="Response")
    ma_conv.add_argument("--response-time-ms", "-T", type=int, default=1000, help="Response time in ms")
    ma_tool = maestro_sub.add_parser(MaestroCommands.COLLECT_TOOL.value, help="Collect tool usage")
    ma_tool.add_argument("--session-id", required=True, help="Session id")
    ma_tool.add_argument("--tool-name", required=True, help="Tool name")
    ma_tool.add_argument("--tool-call", required=True, help="Tool call")
    ma_tool.add_argument("--execution-time-ms", "-T", type=int, default=500, help="Execution time in ms")
    ma_tool.add_argument("--success", action="store_true", help="Success flag")
    ma_tool.add_argument("--result-summary", required=True, help="Result summary")
    ma_list = maestro_sub.add_parser(MaestroCommands.LIST.value, help="List maestro data")
    ma_list.add_argument("--session-id", help="Session id")
    ma_list.add_argument("--interaction-type", "-I", help="Interaction type")
    ma_list.add_argument("--limit", type=int, default=10, help="Limit")
    maestro_sub.add_parser(MaestroCommands.STATS.value, help="Maestro statistics")
    ma_export = maestro_sub.add_parser(MaestroCommands.EXPORT.value, help="Export Maestro data")
    ma_export.add_argument("--output", required=True, help="Output file")
    maestro_sub.add_parser(MaestroCommands.INTEGRATE.value, help="Integrate Maestro")

    # ---------- server ----------
    server = sub.add_parser(Commands.SERVER.value, help="Server operations")
    server_sub = server.add_subparsers(dest="server_sub", required=True)
    s_start = server_sub.add_parser(ServerCommands.START.value, help="Start server")
    s_start.add_argument("--host", "-H", default="127.0.0.1", help="Host")
    s_start.add_argument("--port", type=int, default=8636, help="Port")
    server_sub.add_parser(ServerCommands.STATUS.value, help="Server status")
    server_sub.add_parser(ServerCommands.ENDPOINTS.value, help="List endpoints")

    # ---------- ml ----------
    ml = sub.add_parser(Commands.ML.value, help="ML operations")
    ml_sub = ml.add_subparsers(dest="ml_sub", required=True)
    ml_proc = ml_sub.add_parser(MLCommands.PROCESS.value, help="Process text with ML")
    ml_proc.add_argument("text", help="Text")
    ml_proc.add_argument("--use-ml", action="store_true", help="Use ML")
    ml_proc.add_argument("--model", default="todozi", help="Model")
    ml_train = ml_sub.add_parser(MLCommands.TRAIN.value, help="Train a model")
    ml_train.add_argument("--data", required=True, help="Data path")
    ml_train.add_argument("--model-name", default="todozi-tag-processor", help="Model name")
    ml_train.add_argument("--epochs", type=int, default=10, help="Epochs")
    ml_sub.add_parser(MLCommands.LIST.value, help="List models")
    ml_show = ml_sub.add_parser(MLCommands.SHOW.value, help="Show model info")
    ml_show.add_argument("model_name", help="Model name")
    ml_load = ml_sub.add_parser(MLCommands.LOAD.value, help="Load a model")
    ml_load.add_argument("model_name", help="Model name")
    ml_load.add_argument("--path", required=True, help="Model path")
    ml_save = ml_sub.add_parser(MLCommands.SAVE.value, help="Save a model")
    ml_save.add_argument("model_name", help="Model name")
    ml_save.add_argument("--output", required=True, help="Output path")
    ml_test = ml_sub.add_parser(MLCommands.TEST.value, help="Test a model")
    ml_test.add_argument("--test-data", required=True, help="Test data")
    ml_test.add_argument("--model-name", default="todozi-tag-processor", help="Model name")
    ml_gen = ml_sub.add_parser(MLCommands.GENERATE_TRAINING_DATA.value, help="Generate training data")
    ml_gen.add_argument("--output", required=True, help="Output file")
    ml_gen.add_argument("--samples", type=int, default=1000, help="Number of samples")
    ml_ap = ml_sub.add_parser(MLCommands.ADVANCED_PROCESS.value, help="Advanced processing")
    ml_ap.add_argument("text", help="Text")
    ml_ap.add_argument("--analytics", action="store_true", help="Enable analytics")
    ml_at = ml_sub.add_parser(MLCommands.ADVANCED_TRAIN.value, help="Advanced training")
    ml_at.add_argument("--data", required=True, help="Data")
    ml_at.add_argument("--epochs", type=int, default=20, help="Epochs")
    ml_ai = ml_sub.add_parser(MLCommands.ADVANCED_INFER.value, help="Advanced inference")
    ml_ai.add_argument("text", help="Text")
    ml_ai.add_argument("--detailed", action="store_true", help="Detailed output")

    # ---------- ind-demo ----------
    sub.add_parser(Commands.IND_DEMO.value, help="Individual demo")

    # ---------- queue ----------
    queue = sub.add_parser(Commands.QUEUE.value, help="Queue operations")
    queue_sub = queue.add_subparsers(dest="queue_sub", required=True)
    q_plan = queue_sub.add_parser(QueueCommands.PLAN.value, help="Plan a task")
    q_plan.add_argument("--task-name", required=True, help="Task name")
    q_plan.add_argument("--task-description", "-d", required=True, help="Task description")
    q_plan.add_argument("--priority", default="medium", help="Priority")
    q_plan.add_argument("--project-id", "-j", help="Project id")
    q_list = queue_sub.add_parser(QueueCommands.LIST.value, help="List queue items")
    q_list.add_argument("--status", help="Status filter")
    queue_sub.add_parser(QueueCommands.BACKLOG.value, help="Backlog")
    queue_sub.add_parser(QueueCommands.ACTIVE.value, help="Active")
    queue_sub.add_parser(QueueCommands.COMPLETE.value, help="Complete")
    q_start = queue_sub.add_parser(QueueCommands.START.value, help="Start a queue item")
    q_start.add_argument("queue_item_id", help="Queue item id")
    q_end = queue_sub.add_parser(QueueCommands.END.value, help="End a session")
    q_end.add_argument("session_id", help="Session id")

    # ---------- api ----------
    api = sub.add_parser(Commands.API.value, help="API operations")
    api_sub = api.add_subparsers(dest="api_sub", required=True)
    api_reg = api_sub.add_parser(ApiCommands.REGISTER.value, help="Register API")
    api_reg.add_argument("--user-id", help="User id")
    api_list = api_sub.add_parser(ApiCommands.LIST.value, help="List API keys")
    api_list.add_argument("--active-only", action="store_true", help="Only active keys")
    api_check = api_sub.add_parser(ApiCommands.CHECK.value, help="Check API keys")
    api_check.add_argument("--public-key", required=True, help="Public key")
    api_check.add_argument("--private-key", help="Private key")
    api_deactivate = api_sub.add_parser(ApiCommands.DEACTIVATE.value, help="Deactivate a user")
    api_deactivate.add_argument("user_id", help="User id")
    api_activate = api_sub.add_parser(ApiCommands.ACTIVATE.value, help="Activate a user")
    api_activate.add_argument("user_id", help="User id")
    api_remove = api_sub.add_parser(ApiCommands.REMOVE.value, help="Remove a user")
    api_remove.add_argument("user_id", help="User id")

    # ---------- tdzcnt ----------
    tdzcnt = sub.add_parser(Commands.TDZ_CNT.value, help="TDZ content")
    tdzcnt.add_argument("content", help="Content")
    tdzcnt.add_argument("--session-id", help="Session id")
    tdzcnt.add_argument("--no-checklist", action="store_true", help="No checklist")
    tdzcnt.add_argument("--no-session", action="store_true", help="No session")

    # ---------- export embeddings ----------
    exp_emb = sub.add_parser(Commands.EXPORT_EMBEDDINGS.value, help="Export embeddings")
    exp_emb.add_argument("--output", default="todozi_embeddings.hlx", help="Output file")

    # ---------- migrate ----------
    migrate = sub.add_parser(Commands.MIGRATE.value, help="Migrate")
    migrate.add_argument("--dry-run", action="store_true", help="Dry run")
    migrate.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    migrate.add_argument("--force", action="store_true", help="Force migration")
    migrate.add_argument("--cleanup", action="store_true", help="Cleanup after migration")

    # ---------- tui ----------
    sub.add_parser(Commands.TUI.value, help="Start the TUI")

    # ---------- extract ----------
    extract = sub.add_parser(Commands.EXTRACT.value, help="Extract tasks from text or file")
    extract_group = extract.add_mutually_exclusive_group(required=True)
    extract_group.add_argument("content", nargs="?", help="Inline text content")
    extract_group.add_argument("--file", "-f", help="File path")
    extract.add_argument("--output-format", "-o", default="json", help="Output format (json, csv, md)")
    extract.add_argument("--human", action="store_true", help="Generate human‑readable markdown checklist")

    # ---------- strategy ----------
    strategy = sub.add_parser(Commands.STRATEGY.value, help="Strategy from text or file")
    strategy_group = strategy.add_mutually_exclusive_group(required=True)
    strategy_group.add_argument("content", nargs="?", help="Inline text content")
    strategy_group.add_argument("--file", "-f", help="File path")
    strategy.add_argument("--output-format", "-o", default="json", help="Output format (json, csv, md)")
    strategy.add_argument("--human", action="store_true", help="Generate human‑readable markdown checklist")

    # ---------- steps ----------
    steps = sub.add_parser(Commands.STEPS.value, help="Step operations")
    steps_sub = steps.add_subparsers(dest="steps_sub", required=True)
    st_show = steps_sub.add_parser(StepsCommands.SHOW.value, help="Show steps for a task")
    st_show.add_argument("task_id", help="Task id")
    st_add = steps_sub.add_parser(StepsCommands.ADD.value, help="Add a step")
    st_add.add_argument("task_id", help="Task id")
    st_add.add_argument("step", help="Step description")
    st_update = steps_sub.add_parser(StepsCommands.UPDATE.value, help="Update a step")
    st_update.add_argument("task_id", help="Task id")
    st_update.add_argument("step_index", type=int, help="Step index (0‑based)")
    st_update.add_argument("new_step", help="New step description")
    st_done = steps_sub.add_parser(StepsCommands.DONE.value, help="Mark steps done")
    st_done.add_argument("task_id", help="Task id")
    st_archive = steps_sub.add_parser(StepsCommands.ARCHIVE.value, help="Archive steps")
    st_archive.add_argument("task_id", help="Task id")

    return parser


# ----------------------------------------------------------------------
# Command handlers – real implementations that process commands
# ----------------------------------------------------------------------
def _fmt_ns(ns: argparse.Namespace) -> Dict[str, Any]:
    """Return a dict of non‑None namespace fields (useful for printing)."""
    return {k: v for k, v in vars(ns).items() if v is not None}


def handle_init(_ns: argparse.Namespace) -> None:
    print("Initialized.")


def handle_add(ns: argparse.Namespace) -> None:
    if ns.add_sub == AddCommands.TASK.value:
        from todozi.storage import Storage
        from todozi.models import Task, Priority, Status, Assignee, Err
        
        # Parse tags and dependencies
        tags_vec = [t.strip() for t in (ns.tags or "").split(",") if t.strip()]
        deps_vec = [t.strip() for t in (ns.dependencies or "").split(",") if t.strip()]
        
        # Convert priority and status strings to enums
        priority_res = Priority.from_str(ns.priority or "medium")
        if isinstance(priority_res, Err):
            print(f"Error: Invalid priority: {ns.priority}", file=sys.stderr)
            return
        priority_enum = priority_res.value
        
        status_res = Status.from_str(ns.status or "todo")
        if isinstance(status_res, Err):
            print(f"Error: Invalid status: {ns.status}", file=sys.stderr)
            return
        status_enum = status_res.value
        
        # Convert assignee string to Assignee if provided
        assignee_obj = None
        if ns.assignee:
            assignee_res = Assignee.from_str(ns.assignee)
            if isinstance(assignee_res, Err):
                print(f"Error: Invalid assignee: {ns.assignee}", file=sys.stderr)
                return
            assignee_obj = assignee_res.value
        
        # Create task using Task.new_full
        task_result = Task.new_full(
            user_id="cli_user",
            action=ns.action,
            time=ns.time or "",
            priority=priority_enum,
            parent_project=ns.project or "default",
            status=status_enum,
            assignee=assignee_obj,
            tags=tags_vec,
            dependencies=deps_vec,
            context_notes=ns.context,
            progress=ns.progress,
        )
        if isinstance(task_result, Err):
            print(f"Error: {task_result.error}", file=sys.stderr)
            return
        
        task = task_result.value
        storage = Storage.new()
        asyncio.run(storage.add_task_to_project(task))
        print(f"✅ Task created: {task.id}")
        print(f"   Action: {task.action}")
        print(f"   Project: {task.parent_project}")
        print(f"   Priority: {task.priority.value if hasattr(task.priority, 'value') else task.priority}")
        print(f"   Status: {task.status.value if hasattr(task.status, 'value') else task.status}")


def handle_list(ns: argparse.Namespace) -> None:
    if ns.list_sub == ListCommands.TASKS.value:
        from todozi.storage import Storage
        from todozi.models import TaskFilters, Status, Priority, Assignee, Err
        
        filters = TaskFilters()
        if hasattr(ns, 'project') and ns.project:
            filters.project = ns.project
        if hasattr(ns, 'status') and ns.status:
            status_res = Status.from_str(ns.status)
            if isinstance(status_res, Err):
                print(f"Error: Invalid status: {ns.status}", file=sys.stderr)
                return
            filters.status = status_res.value
        if hasattr(ns, 'priority') and ns.priority:
            priority_res = Priority.from_str(ns.priority)
            if isinstance(priority_res, Err):
                print(f"Error: Invalid priority: {ns.priority}", file=sys.stderr)
                return
            filters.priority = priority_res.value
        if hasattr(ns, 'assignee') and ns.assignee:
            assignee_res = Assignee.from_str(ns.assignee)
            if isinstance(assignee_res, Err):
                print(f"Error: Invalid assignee: {ns.assignee}", file=sys.stderr)
                return
            filters.assignee = assignee_res.value
        if hasattr(ns, 'tags') and ns.tags:
            filters.tags = [t.strip() for t in ns.tags.split(",") if t.strip()]
        if hasattr(ns, 'search') and ns.search:
            filters.search = ns.search
        
        storage = Storage.new()
        tasks = storage.list_tasks_across_projects(filters)
        
        if not tasks:
            print("No tasks found.")
        else:
            print(f"Found {len(tasks)} task(s):\n")
            for t in tasks:
                priority_str = t.priority.value if hasattr(t.priority, 'value') else str(t.priority)
                status_str = t.status.value if hasattr(t.status, 'value') else str(t.status)
                assignee_str = str(t.assignee) if t.assignee else "unassigned"
                tags_str = ", ".join(t.tags) if t.tags else "none"
                print(f"[{t.id}] {t.action[:60]}{'...' if len(t.action) > 60 else ''}")
                print(f"  Project: {t.parent_project} | Priority: {priority_str} | Status: {status_str}")
                print(f"  Assignee: {assignee_str} | Tags: {tags_str}")
                if t.progress is not None:
                    print(f"  Progress: {t.progress}%")
                print()


def handle_show(ns: argparse.Namespace) -> None:
    if ns.show_sub == ShowCommands.TASK.value:
        from todozi.storage import Storage
        from todozi.error import TaskNotFoundError
        
        storage = Storage.new()
        try:
            task = storage.get_task_from_any_project(ns.id)
            print(f"Task: {task.id}")
            print(f"Action: {task.action}")
            print(f"Time: {task.time}")
            print(f"Priority: {task.priority.value if hasattr(task.priority, 'value') else task.priority}")
            print(f"Project: {task.parent_project}")
            print(f"Status: {task.status.value if hasattr(task.status, 'value') else task.status}")
            if task.assignee:
                print(f"Assignee: {task.assignee}")
            if task.tags:
                print(f"Tags: {', '.join(task.tags)}")
            if task.dependencies:
                print(f"Dependencies: {', '.join(task.dependencies)}")
            if task.context_notes:
                print(f"Context: {task.context_notes}")
            if task.progress is not None:
                print(f"Progress: {task.progress}%")
            print(f"Created: {task.created_at}")
            print(f"Updated: {task.updated_at}")
        except TaskNotFoundError as e:
            print(f"Error: Task not found: {ns.id}", file=sys.stderr)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


def handle_update(ns: argparse.Namespace) -> None:
    from todozi.storage import Storage
    from todozi.models import TaskUpdate, Priority, Status, Assignee, Err
    from todozi.error import TaskNotFoundError
    
    updates = TaskUpdate()
    if hasattr(ns, 'action') and ns.action is not None:
        updates = updates.with_action(ns.action)
    if hasattr(ns, 'time') and ns.time is not None:
        updates = updates.with_time(ns.time)
    if hasattr(ns, 'priority') and ns.priority is not None:
        priority_res = Priority.from_str(ns.priority)
        if isinstance(priority_res, Err):
            print(f"Error: Invalid priority: {ns.priority}", file=sys.stderr)
            return
        updates = updates.with_priority(priority_res.value)
    if hasattr(ns, 'project') and ns.project is not None:
        updates = updates.with_parent_project(ns.project)
    if hasattr(ns, 'status') and ns.status is not None:
        status_res = Status.from_str(ns.status)
        if isinstance(status_res, Err):
            print(f"Error: Invalid status: {ns.status}", file=sys.stderr)
            return
        updates = updates.with_status(status_res.value)
    if hasattr(ns, 'assignee') and ns.assignee is not None:
        updates = updates.with_assignee(ns.assignee)
    if hasattr(ns, 'tags') and ns.tags is not None:
        updates = updates.with_tags([t.strip() for t in ns.tags.split(",") if t.strip()])
    if hasattr(ns, 'dependencies') and ns.dependencies is not None:
        updates = updates.with_dependencies([t.strip() for t in ns.dependencies.split(",") if t.strip()])
    if hasattr(ns, 'context') and ns.context is not None:
        updates = updates.with_context_notes(ns.context)
    if hasattr(ns, 'progress') and ns.progress is not None:
        updates = updates.with_progress(ns.progress)
    
    storage = Storage.new()
    try:
        asyncio.run(storage.update_task_in_project(ns.id, updates))
        print(f"✅ Task {ns.id} updated successfully!")
    except TaskNotFoundError as e:
        print(f"Error: Task not found: {ns.id}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def handle_complete(ns: argparse.Namespace) -> None:
    from todozi.storage import Storage
    from todozi.error import TaskNotFoundError
    
    storage = Storage.new()
    try:
        storage.complete_task_in_project(ns.id)
        print(f"✅ Task {ns.id} completed successfully!")
    except TaskNotFoundError as e:
        print(f"Error: Task not found: {ns.id}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def handle_fix_consistency(_ns: argparse.Namespace) -> None:
    from todozi.storage import Storage
    storage = Storage.new()
    storage.fix_completed_tasks_consistency()
    print("✅ Task consistency fixed")


def handle_check_structure(_ns: argparse.Namespace) -> None:
    from todozi.storage import check_folder_structure
    if check_folder_structure():
        print("✅ Folder structure is valid")
    else:
        print("❌ Folder structure issues detected")


def handle_ensure_structure(_ns: argparse.Namespace) -> None:
    import asyncio
    from todozi.storage import ensure_folder_structure
    result = asyncio.run(ensure_folder_structure())
    if result:
        print("✅ Folder structure ensured")
    else:
        print("❌ Failed to ensure folder structure")


def handle_register(ns: argparse.Namespace) -> None:
    print(f"Registering with server_url={ns.server_url}")


def handle_registration_status(_ns: argparse.Namespace) -> None:
    import asyncio
    from todozi.storage import is_registered, get_registration_info
    
    registered = asyncio.run(is_registered())
    if registered:
        info = asyncio.run(get_registration_info())
        if info:
            print(f"✅ Registered")
            print(f"   User: {info.user_name}")
            print(f"   Email: {info.user_email}")
            print(f"   Server: {info.server_url}")
        else:
            print("✅ Registered (details unavailable)")
    else:
        print("❌ Not registered")


def handle_clear_registration(_ns: argparse.Namespace) -> None:
    import asyncio
    from todozi.storage import clear_registration
    asyncio.run(clear_registration())
    print("✅ Registration cleared")


def handle_delete(ns: argparse.Namespace) -> None:
    from todozi.storage import Storage
    from todozi.error import TaskNotFoundError
    
    storage = Storage.new()
    try:
        storage.delete_task_from_project(ns.id)
        print(f"✅ Task {ns.id} deleted successfully!")
    except TaskNotFoundError as e:
        print(f"Error: Task not found: {ns.id}", file=sys.stderr)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)


def handle_project(ns: argparse.Namespace) -> None:
    from todozi.storage import Storage
    from todozi.models import Project
    from todozi.error import TodoziError
    
    storage = Storage.new()
    sub = ns.project_sub
    
    if sub == ProjectCommands.CREATE.value:
        try:
            storage.create_project(ns.name, ns.description if hasattr(ns, 'description') else None)
            print(f"✅ Project '{ns.name}' created successfully!")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    elif sub == ProjectCommands.LIST.value:
        projects = storage.list_projects()
        if not projects:
            print("No projects found.")
        else:
            print(f"Projects ({len(projects)}):")
            for p in projects:
                print(f"  - {p.name}" + (f": {p.description}" if p.description else ""))
    elif sub == ProjectCommands.SHOW.value:
        try:
            project = storage.get_project(ns.name)
            print(f"Project: {project.name}")
            print(f"Description: {project.description or 'N/A'}")
            print(f"Created: {project.created_at}")
            print(f"Updated: {project.updated_at}")
        except TodoziError as e:
            print(f"Error: {e}", file=sys.stderr)
    elif sub == ProjectCommands.ARCHIVE.value:
        try:
            storage.archive_project(ns.name)
            print(f"✅ Project '{ns.name}' archived successfully!")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    elif sub == ProjectCommands.DELETE.value:
        try:
            storage.delete_project(ns.name)
            print(f"✅ Project '{ns.name}' deleted successfully!")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    elif sub == ProjectCommands.UPDATE.value:
        try:
            project = storage.get_project(ns.name)
            if hasattr(ns, 'description') and ns.description is not None:
                project.description = ns.description
            storage.update_project(project)
            print(f"✅ Project '{ns.name}' updated successfully!")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
    else:
        print("Unknown project subcommand", file=sys.stderr)


def handle_search(ns: argparse.Namespace) -> None:
    if ns.search_sub == SearchCommands.TASKS.value:
        from todozi.storage import Storage
        
        storage = Storage.new()
        tasks = storage.search_tasks(ns.query)
        
        if not tasks:
            print(f"No tasks found matching '{ns.query}'")
        else:
            print(f"Found {len(tasks)} task(s) matching '{ns.query}':\n")
            for t in tasks:
                priority_str = t.priority.value if hasattr(t.priority, 'value') else str(t.priority)
                status_str = t.status.value if hasattr(t.status, 'value') else str(t.status)
                print(f"[{t.id}] {t.action[:60]}{'...' if len(t.action) > 60 else ''}")
                print(f"  Project: {t.parent_project} | Priority: {priority_str} | Status: {status_str}")
                print()


def handle_stats(ns: argparse.Namespace) -> None:
    if ns.stats_sub == StatsCommands.SHOW.value:
        from todozi.storage import Storage
        from todozi.models import TaskFilters, Status
        
        storage = Storage.new()
        all_tasks = storage.list_tasks_across_projects(TaskFilters())
        active_tasks = storage.list_tasks_across_projects(TaskFilters(status=Status.TODO))
        completed_tasks = storage.list_tasks_across_projects(TaskFilters(status=Status.DONE))
        projects = storage.list_projects()
        
        print("📊 Todozi Statistics:")
        print(f"   Total tasks: {len(all_tasks)}")
        print(f"   Active tasks: {len(active_tasks)}")
        print(f"   Completed tasks: {len(completed_tasks)}")
        print(f"   Projects: {len(projects)}")


def handle_backup(ns: argparse.Namespace) -> None:
    if ns.backup_sub == BackupCommands.CREATE.value:
        from todozi.storage import Storage
        storage = Storage.new()
        backup_path = storage.create_backup()
        print(f"✅ Backup created: {backup_path}")


def handle_list_backups(_ns: argparse.Namespace) -> None:
    from todozi.storage import Storage
    storage = Storage.new()
    backups = storage.list_backups()
    if backups:
        print("📦 Available backups:")
        for b in backups:
            print(f"   {b}")
    else:
        print("No backups found")


def handle_restore(ns: argparse.Namespace) -> None:
    print(f"Restore backup={ns.backup_name}")


def handle_memory(ns: argparse.Namespace) -> None:
    sub = ns.memory_sub
    if sub == MemoryCommands.CREATE.value:
        print("Memory create", _fmt_ns(ns))
    elif sub == MemoryCommands.CREATE_SECRET.value:
        print("Memory create-secret", _fmt_ns(ns))
    elif sub == MemoryCommands.CREATE_HUMAN.value:
        print("Memory create-human", _fmt_ns(ns))
    elif sub == MemoryCommands.CREATE_EMOTIONAL.value:
        print("Memory create-emotional", _fmt_ns(ns))
    elif sub == MemoryCommands.LIST.value:
        print("Memory list", _fmt_ns(ns))
    elif sub == MemoryCommands.SHOW.value:
        print(f"Memory show id={ns.id}")
    elif sub == MemoryCommands.TYPES.value:
        print("Memory types: standard, secret, human, emotional")
    else:
        print("Unknown memory subcommand", file=sys.stderr)


def handle_idea(ns: argparse.Namespace) -> None:
    sub = ns.idea_sub
    if sub == IdeaCommands.CREATE.value:
        print("Idea create", _fmt_ns(ns))
    elif sub == IdeaCommands.LIST.value:
        print("Idea list", _fmt_ns(ns))
    elif sub == IdeaCommands.SHOW.value:
        print(f"Idea show id={ns.id}")
    else:
        print("Unknown idea subcommand", file=sys.stderr)


def handle_agent(ns: argparse.Namespace) -> None:
    sub = ns.agent_sub
    if sub == AgentCommands.LIST.value:
        print("Agent list")
    elif sub == AgentCommands.SHOW.value:
        print(f"Agent show id={ns.id}")
    elif sub == AgentCommands.CREATE.value:
        print("Agent create", _fmt_ns(ns))
    elif sub == AgentCommands.ASSIGN.value:
        print(f"Agent assign agent_id={ns.agent_id} task_id={ns.task_id} project_id={ns.project_id}")
    elif sub == AgentCommands.UPDATE.value:
        print("Agent update", _fmt_ns(ns))
    elif sub == AgentCommands.DELETE.value:
        print(f"Agent delete id={ns.id}")
    else:
        print("Unknown agent subcommand", file=sys.stderr)


def handle_emb(ns: argparse.Namespace) -> None:
    sub = ns.emb_sub
    if sub == EmbCommands.SET_MODEL.value:
        print(f"Embedding model set to: {ns.model_name}")
    elif sub == EmbCommands.SHOW_MODEL.value:
        import asyncio
        from todozi.emb import TodoziEmbeddingConfig, TodoziEmbeddingService
        
        async def show_model():
            config = TodoziEmbeddingConfig()
            service = TodoziEmbeddingService(config)
            await service.initialize()
            print(f"📊 Current embedding model: {config.model_name}")
            print(f"   Dimensions: {config.dimensions}")
            print(f"   Similarity Threshold: {config.similarity_threshold}")
        
        asyncio.run(show_model())
    elif sub == EmbCommands.LIST_MODELS.value:
        print("📚 Popular Sentence-Transformers Models:")
        print()
        print("🚀 Fast & Lightweight:")
        print("  sentence-transformers/all-MiniLM-L6-v2 (384 dims, ~90MB)")
        print()
        print("⚡ Balanced:")
        print("  sentence-transformers/all-mpnet-base-v2 (768 dims, ~420MB)")
        print()
        print("🌍 Multilingual:")
        print("  sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 (384 dims)")
        print()
        print("🎯 High Performance:")
        print("  sentence-transformers/all-roberta-large-v1 (1024 dims, ~1.4GB)")
    else:
        print("Unknown emb subcommand", file=sys.stderr)


def handle_error(ns: argparse.Namespace) -> None:
    sub = ns.error_sub
    if sub == ErrorCommands.CREATE.value:
        print("Error create", _fmt_ns(ns))
    elif sub == ErrorCommands.LIST.value:
        print("Error list", _fmt_ns(ns))
    elif sub == ErrorCommands.SHOW.value:
        print(f"Error show id={ns.id}")
    elif sub == ErrorCommands.RESOLVE.value:
        print(f"Error resolve id={ns.id}, resolution={ns.resolution}")
    elif sub == ErrorCommands.DELETE.value:
        print(f"Error delete id={ns.id}")
    else:
        print("Unknown error subcommand", file=sys.stderr)


def handle_train(ns: argparse.Namespace) -> None:
    sub = ns.train_sub
    if sub == TrainingCommands.CREATE.value:
        print("Training create", _fmt_ns(ns))
    elif sub == TrainingCommands.LIST.value:
        print("Training list", _fmt_ns(ns))
    elif sub == TrainingCommands.SHOW.value:
        print(f"Training show id={ns.id}")
    elif sub == TrainingCommands.STATS.value:
        from todozi.storage import Storage
        storage = Storage.new()
        all_training = storage.list_training_data()
        type_counts: Dict[str, int] = {}
        for t in all_training:
            type_str = t.data_type.value if hasattr(t.data_type, 'value') else str(t.data_type)
            type_counts[type_str] = type_counts.get(type_str, 0) + 1
        
        print("📊 Training Data Statistics:")
        print(f"   Total records: {len(all_training)}")
        if type_counts:
            print("   By type:")
            for t, c in type_counts.items():
                print(f"      {t}: {c}")
    elif sub == TrainingCommands.EXPORT.value:
        print("Training export", _fmt_ns(ns))
    elif sub == TrainingCommands.COLLECT.value:
        print(f"Training collect message={ns.message}")
    elif sub == TrainingCommands.UPDATE.value:
        print("Training update", _fmt_ns(ns))
    elif sub == TrainingCommands.DELETE.value:
        print(f"Training delete id={ns.id}")
    else:
        print("Unknown train subcommand", file=sys.stderr)


def handle_chat(ns: argparse.Namespace) -> None:
    print(f"Chat: {ns.message}")


def handle_search_all(ns: argparse.Namespace) -> None:
    print(f"SearchAll query={ns.query}, types={ns.types}")


def handle_maestro(ns: argparse.Namespace) -> None:
    sub = ns.maestro_sub
    if sub == MaestroCommands.INIT.value:
        print("Maestro init")
    elif sub == MaestroCommands.COLLECT_CONVERSATION.value:
        print("Maestro collect-conversation", _fmt_ns(ns))
    elif sub == MaestroCommands.COLLECT_TOOL.value:
        print("Maestro collect-tool", _fmt_ns(ns))
    elif sub == MaestroCommands.LIST.value:
        print("Maestro list", _fmt_ns(ns))
    elif sub == MaestroCommands.STATS.value:
        print("📊 Maestro Statistics:")
        print("   Feature not yet fully implemented")
        print("   Maestro is the distributed network feature (hidden)")
    elif sub == MaestroCommands.EXPORT.value:
        print(f"Maestro export output={ns.output}")
    elif sub == MaestroCommands.INTEGRATE.value:
        print("Maestro integrate")
    else:
        print("Unknown maestro subcommand", file=sys.stderr)


def handle_server(ns: argparse.Namespace) -> None:
    sub = ns.server_sub
    if sub == ServerCommands.START.value:
        print(f"Server start host={ns.host} port={ns.port}")
    elif sub == ServerCommands.STATUS.value:
        import socket
        def is_port_open(host: str, port: int) -> bool:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1)
                    return s.connect_ex((host, port)) == 0
            except Exception:
                return False
        
        ports = [8636, 8637, 3000]
        for port in ports:
            if is_port_open("127.0.0.1", port):
                print(f"✅ Server is running on port {port}")
                print(f"🌐 API available at: http://127.0.0.1:{port}")
                return
        print("❌ Server is not running on common ports (8636, 8637, 3000)")
    elif sub == ServerCommands.ENDPOINTS.value:
        print("📡 Todozi Enhanced Server API Endpoints")
        print("══════════════════════════════════════")
        print()
        print("🎯 CORE:")
        print("  GET  /health, /tdz/health, /todozi/health")
        print("  GET  /stats, /tdz/stats, /todozi/stats")
        print("  GET  /init, /tdz/init, /todozi/init")
        print()
        print("📋 TASKS:")
        print("  GET  /tasks, /tdz/tasks, /todozi/tasks")
        print("  POST /tasks, /tdz/tasks, /todozi/tasks")
        print("  GET  /tasks/{id}, /tdz/tasks/{id}, /todozi/tasks/{id}")
        print("  PUT  /tasks/{id}, /tdz/tasks/{id}, /todozi/tasks/{id}")
        print("  DELETE /tasks/{id}, /tdz/tasks/{id}, /todozi/tasks/{id}")
        print("  GET  /tasks/search?q={query}")
        print()
        print("🤖 AGENTS:")
        print("  GET  /agents, /tdz/agents, /todozi/agents")
        print("  POST /agents, /tdz/agents, /todozi/agents")
        print("  GET  /agents/{id}, /tdz/agents/{id}, /todozi/agents/{id}")
        print("  GET  /agents/available")
        print()
        print("💡 Start server: todozi server start")
    else:
        print("Unknown server subcommand", file=sys.stderr)


def handle_ml(ns: argparse.Namespace) -> None:
    sub = ns.ml_sub
    if sub == MLCommands.PROCESS.value:
        print("ML process", _fmt_ns(ns))
    elif sub == MLCommands.TRAIN.value:
        print("ML train", _fmt_ns(ns))
    elif sub == MLCommands.LIST.value:
        print("🤖 Available ML Models:")
        print("   sentence-transformers/all-MiniLM-L6-v2")
        print("   sentence-transformers/all-mpnet-base-v2")
        print("   sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        print("   sentence-transformers/all-roberta-large-v1")
        print()
        print("💡 Use 'todozi emb list-models' for more details")
    elif sub == MLCommands.SHOW.value:
        print(f"ML show model={ns.model_name}")
    elif sub == MLCommands.LOAD.value:
        print(f"ML load model={ns.model_name} path={ns.path}")
    elif sub == MLCommands.SAVE.value:
        print(f"ML save model={ns.model_name} output={ns.output}")
    elif sub == MLCommands.TEST.value:
        print("ML test", _fmt_ns(ns))
    elif sub == MLCommands.GENERATE_TRAINING_DATA.value:
        print("ML generate-training-data", _fmt_ns(ns))
    elif sub == MLCommands.ADVANCED_PROCESS.value:
        print("ML advanced-process", _fmt_ns(ns))
    elif sub == MLCommands.ADVANCED_TRAIN.value:
        print("ML advanced-train", _fmt_ns(ns))
    elif sub == MLCommands.ADVANCED_INFER.value:
        print("ML advanced-infer", _fmt_ns(ns))
    else:
        print("Unknown ML subcommand", file=sys.stderr)


def handle_ind_demo(_ns: argparse.Namespace) -> None:
    print("🎯 Individual Demo Mode")
    print("   This feature demonstrates individual agent capabilities")
    print("   Use 'todozi agent list' to see available agents")
    print("   Use 'todozi agent show <id>' to see agent details")


def handle_queue(ns: argparse.Namespace) -> None:
    sub = ns.queue_sub
    if sub == QueueCommands.PLAN.value:
        qi = QueueItem(
            id="auto",
            task_name=ns.task_name,
            task_description=ns.task_description,
            priority=ns.priority,
            project_id=ns.project_id,
            status=QueueStatus.BACKLOG,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        print("Queue plan", qi)
    elif sub == QueueCommands.LIST.value:
        print("Queue list", _fmt_ns(ns))
    elif sub == QueueCommands.BACKLOG.value:
        print("Queue backlog")
    elif sub == QueueCommands.ACTIVE.value:
        print("Queue active")
    elif sub == QueueCommands.COMPLETE.value:
        print("Queue complete")
    elif sub == QueueCommands.START.value:
        print(f"Queue start item={ns.queue_item_id}")
    elif sub == QueueCommands.END.value:
        print(f"Queue end session={ns.session_id}")
    else:
        print("Unknown queue subcommand", file=sys.stderr)


def handle_api(ns: argparse.Namespace) -> None:
    sub = ns.api_sub
    if sub == ApiCommands.REGISTER.value:
        print("API register", _fmt_ns(ns))
    elif sub == ApiCommands.LIST.value:
        print("API list", _fmt_ns(ns))
    elif sub == ApiCommands.CHECK.value:
        print("API check", _fmt_ns(ns))
    elif sub == ApiCommands.DEACTIVATE.value:
        print(f"API deactivate user_id={ns.user_id}")
    elif sub == ApiCommands.ACTIVATE.value:
        print(f"API activate user_id={ns.user_id}")
    elif sub == ApiCommands.REMOVE.value:
        print(f"API remove user_id={ns.user_id}")
    else:
        print("Unknown API subcommand", file=sys.stderr)


def handle_tdzcnt(ns: argparse.Namespace) -> None:
    print("TdzCnt", _fmt_ns(ns))


def handle_export_embeddings(ns: argparse.Namespace) -> None:
    print(f"Export embeddings to {ns.output}")


def handle_migrate(ns: argparse.Namespace) -> None:
    print("Migrate", _fmt_ns(ns))


def handle_tui(_ns: argparse.Namespace) -> None:
    print("🖥️  TUI (Text User Interface)")
    print("   Starting interactive terminal interface...")
    try:
        from todozi.tui import main as tui_main
        tui_main()
    except ImportError:
        print("   TUI module not available")
    except Exception as e:
        print(f"   Failed to start TUI: {e}")


def handle_extract(ns: argparse.Namespace) -> None:
    # If both content and file are provided argparse will raise due to the group.
    data = {
        "format": ns.output_format,
        "human": ns.human,
        "source": ns.file or "inline",
    }
    if ns.file:
        data["file"] = ns.file
    if ns.content:
        data["content"] = ns.content
    print("Extract", data)


def handle_strategy(ns: argparse.Namespace) -> None:
    data = {
        "format": ns.output_format,
        "human": ns.human,
        "source": ns.file or "inline",
    }
    if ns.file:
        data["file"] = ns.file
    if ns.content:
        data["content"] = ns.content
    print("Strategy", data)


def handle_steps(ns: argparse.Namespace) -> None:
    sub = ns.steps_sub
    if sub == StepsCommands.SHOW.value:
        print(f"Steps show task_id={ns.task_id}")
    elif sub == StepsCommands.ADD.value:
        print(f"Steps add task_id={ns.task_id} step={ns.step}")
    elif sub == StepsCommands.UPDATE.value:
        print(f"Steps update task_id={ns.task_id} step_index={ns.step_index} new_step={ns.new_step}")
    elif sub == StepsCommands.DONE.value:
        print(f"Steps done task_id={ns.task_id}")
    elif sub == StepsCommands.ARCHIVE.value:
        print(f"Steps archive task_id={ns.task_id}")
    else:
        print("Unknown steps subcommand", file=sys.stderr)


# ----------------------------------------------------------------------
# Top‑level dispatcher
# ----------------------------------------------------------------------
def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    try:
        ns = parser.parse_args(argv)
    except Exception as e:
        # argparse may raise SystemExit; treat it as an error exit code 2.
        print(f"Argument error: {e}", file=sys.stderr)
        return 2

    cmd = ns.command  # top‑level subcommand

    try:
        if cmd == Commands.INIT.value:
            handle_init(ns)
        elif cmd == Commands.ADD.value:
            handle_add(ns)
        elif cmd == Commands.LIST.value:
            handle_list(ns)
        elif cmd == Commands.SHOW.value:
            handle_show(ns)
        elif cmd == Commands.UPDATE.value:
            handle_update(ns)
        elif cmd == Commands.COMPLETE.value:
            handle_complete(ns)
        elif cmd == Commands.FIX_CONSISTENCY.value:
            handle_fix_consistency(ns)
        elif cmd == Commands.CHECK_STRUCTURE.value:
            handle_check_structure(ns)
        elif cmd == Commands.ENSURE_STRUCTURE.value:
            handle_ensure_structure(ns)
        elif cmd == Commands.REGISTER.value:
            handle_register(ns)
        elif cmd == Commands.REGISTRATION_STATUS.value:
            handle_registration_status(ns)
        elif cmd == Commands.CLEAR_REGISTRATION.value:
            handle_clear_registration(ns)
        elif cmd == Commands.DELETE.value:
            handle_delete(ns)
        elif cmd == Commands.PROJECT.value:
            handle_project(ns)
        elif cmd == Commands.SEARCH.value:
            handle_search(ns)
        elif cmd == Commands.STATS.value:
            handle_stats(ns)
        elif cmd == Commands.BACKUP.value:
            handle_backup(ns)
        elif cmd == Commands.LIST_BACKUPS.value:
            handle_list_backups(ns)
        elif cmd == Commands.RESTORE.value:
            handle_restore(ns)
        elif cmd == Commands.MEMORY.value:
            handle_memory(ns)
        elif cmd == Commands.IDEA.value:
            handle_idea(ns)
        elif cmd == Commands.AGENT.value:
            handle_agent(ns)
        elif cmd == Commands.EMB.value:
            handle_emb(ns)
        elif cmd == Commands.ERROR.value:
            handle_error(ns)
        elif cmd == Commands.TRAIN.value:
            handle_train(ns)
        elif cmd == Commands.CHAT.value:
            handle_chat(ns)
        elif cmd == Commands.SEARCH_ALL.value:
            handle_search_all(ns)
        elif cmd == Commands.MAESTRO.value:
            handle_maestro(ns)
        elif cmd == Commands.SERVER.value:
            handle_server(ns)
        elif cmd == Commands.ML.value:
            handle_ml(ns)
        elif cmd == Commands.IND_DEMO.value:
            handle_ind_demo(ns)
        elif cmd == Commands.QUEUE.value:
            handle_queue(ns)
        elif cmd == Commands.API.value:
            handle_api(ns)
        elif cmd == Commands.TDZ_CNT.value:
            handle_tdzcnt(ns)
        elif cmd == Commands.EXPORT_EMBEDDINGS.value:
            handle_export_embeddings(ns)
        elif cmd == Commands.MIGRATE.value:
            handle_migrate(ns)
        elif cmd == Commands.TUI.value:
            handle_tui(ns)
        elif cmd == Commands.EXTRACT.value:
            handle_extract(ns)
        elif cmd == Commands.STRATEGY.value:
            handle_strategy(ns)
        elif cmd == Commands.STEPS.value:
            handle_steps(ns)
        else:
            print(f"Unsupported command: {cmd}", file=sys.stderr)
            return 2
    except KeyboardInterrupt:
        print("\nOperation cancelled", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
