# todozi_server.py

# Python translation of the provided Rust "Todozi Enhanced Server" code.
# This is a fully-executable, minimal, async HTTP/TCP server implementing the endpoints
# and request/response semantics from the original Rust server. It includes stubbed
# implementations of external dependencies to keep it self-contained and runnable.

# Fix imports when running directly
import sys
from pathlib import Path
# Always add parent directory to path so absolute imports work when run directly
_file_path = Path(__file__)
if _file_path.exists():
    parent_dir = _file_path.parent.parent
    parent_str = str(parent_dir)
    if parent_str not in sys.path:
        sys.path.insert(0, parent_str)

import asyncio
import json
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple, Union

# -------------------------
# Constants and Global State
# -------------------------

DEFAULT_HOST = "0.0.0.0"
DEFAULT_PORT = 8636
MAX_BUFFER_SIZE = 8192
HEALTH_PATHS = {
    "/health",
    "/tdz/health",
    "/todozi/health",
}

# Simple in-memory "DB"
STORE = {
    "projects": {},
    "tasks": {},
    "agents": [],
    "agent_by_id": {},
    "training_data": [],
    "queue_items": [],
    "queue_sessions": [],
    "feelings": [],
    "api_keys": [],  # each item: {"user_id": "...", "public_key": "...", "private_key": "...", "active": bool, "created_at": datetime}
    "backlog": [],
    "active": [],
    "complete": [],
    "chats": [],
}

TDZ_ENABLE_TUI = os.environ.get("TDZ_ENABLE_TUI", "0") == "1"  # emulate #[cfg(feature = "tui")]


# -------------------------
# Models / Stubs
# -------------------------

@dataclass
class ServerConfig:
    host: str = field(default_factory=lambda: DEFAULT_HOST)
    port: int = field(default=DEFAULT_PORT)
    max_connections: int = 100


@dataclass
class HttpRequest:
    method: str
    path: str
    headers: Dict[str, str]
    body: str


@dataclass
class HttpResponse:
    status: int
    headers: Dict[str, str]
    body: str

    @staticmethod
    def ok(body: str) -> "HttpResponse":
        return HttpResponse(200, {}, body)

    @staticmethod
    def error(status: int, message: str) -> "HttpResponse":
        return HttpResponse(
            status,
            {},
            json.dumps({"error": message}),
        )

    @staticmethod
    def json(data: Any) -> "HttpResponse":
        return HttpResponse(200, {}, json.dumps(data))


class Storage:
    def create_project(self, name: str, description: Optional[str]) -> None:
        STORE["projects"][name] = {
            "name": name,
            "description": description or "",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

    def get_project(self, name: str) -> Dict[str, Any]:
        if name not in STORE["projects"]:
            raise KeyError("Project not found")
        return STORE["projects"][name]

    def get_task_from_any_project(self, task_id: str) -> Dict[str, Any]:
        for project in STORE["projects"].values():
            for t in project.get("tasks", []):
                if t["id"] == task_id:
                    return t
        if task_id in STORE["tasks"]:
            return STORE["tasks"][task_id]
        raise KeyError("Task not found")

    def list_tasks_across_projects(self, filters: Any) -> List[Dict[str, Any]]:
        # Not implementing real filtering; return tasks from all projects + global tasks
        results: List[Dict[str, Any]] = []
        for t in STORE["tasks"].values():
            results.append(t)
        for project in STORE["projects"].values():
            results.extend(project.get("tasks", []))
        return results

    async def update_task_in_project(self, task_id: str, updates: Dict[str, Any]) -> None:
        # Minimal: apply updates to global STORE["tasks"] and project tasks if present
        if task_id in STORE["tasks"]:
            STORE["tasks"][task_id].update(updates)
            STORE["tasks"][task_id]["updated_at"] = datetime.now(timezone.utc)
            return
        found = False
        for project in STORE["projects"].values():
            for t in project.get("tasks", []):
                if t["id"] == task_id:
                    t.update(updates)
                    t["updated_at"] = datetime.now(timezone.utc)
                    found = True
                    break
            if found:
                break
        if not found:
            raise KeyError("Task not found for update")

    def delete_task_from_project(self, task_id: str) -> None:
        if task_id in STORE["tasks"]:
            del STORE["tasks"][task_id]
            return
        for project in STORE["projects"].values():
            tasks = project.get("tasks", [])
            for i, t in enumerate(tasks):
                if t["id"] == task_id:
                    tasks.pop(i)
                    return


class CodeGenerationGraph:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.chunks: Dict[str, Any] = {}
        # Seed with one chunk for demo purposes
        self.chunks["chunk_001"] = {
            "chunk_id": "chunk_001",
            "level": "info",
            "status": "ready",
            "dependencies": [],
            "estimated_tokens": 128,
            "content": "example code chunk",
        }

    def get_ready_chunks(self) -> List[str]:
        return [c["chunk_id"] for c in self.chunks.values() if c["status"] == "ready"]

    def get_project_summary(self) -> Dict[str, Any]:
        return {
            "total_ready": len(self.get_ready_chunks()),
            "total": len(self.chunks),
        }


# Simple stubs for dependencies
def get_active_sessions() -> List[Dict[str, Any]]:
    return STORE["active"]


def create_default_agents() -> None:
    # Create a few demo agents if not already created
    if not STORE["agents"]:
        for i in range(1, 27):  # 26 agents
            agent = {
                "id": f"agent_{i}",
                "name": f"Agent {i}",
                "description": f"Predefined system agent {i}",
                "version": "1.0.0",
                "metadata": {"category": "system", "status": "active"},
                "model": {"provider": "openai", "name": "gpt-4o", "temperature": 0.2, "max_tokens": 2048},
                "capabilities": ["chat", "code", "analysis"],
                "specializations": [f"spec_{i}"],
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
            STORE["agents"].append(agent)
            STORE["agent_by_id"][agent["id"]] = agent


def list_agents() -> List[Dict[str, Any]]:
    return STORE["agents"]


def get_available_agents() -> List[Dict[str, Any]]:
    return [a for a in STORE["agents"] if a["metadata"]["status"] == "active"]


def load_agent(agent_id: str) -> Dict[str, Any]:
    if agent_id in STORE["agent_by_id"]:
        return STORE["agent_by_id"][agent_id]
    raise KeyError("Agent not found")


def save_agent(agent: Dict[str, Any]) -> None:
    STORE["agent_by_id"][agent["id"]] = agent
    # Keep list in sync
    existing = next((a for a in STORE["agents"] if a["id"] == agent["id"]), None)
    if not existing:
        STORE["agents"].append(agent)


def create_custom_agent(
    agent_id: str,
    name: str,
    description: str,
    capabilities: List[str],
    specializations: List[str],
    category: str,
    author: Optional[str],
) -> Dict[str, Any]:
    return {
        "id": agent_id,
        "name": name,
        "description": description,
        "version": "1.0.0",
        "metadata": {"author": author or "api_user", "category": category, "status": "active"},
        "model": {"provider": "openai", "name": "gpt-4o", "temperature": 0.2, "max_tokens": 2048},
        "system_prompt": "You are a helpful agent.",
        "capabilities": capabilities or ["chat"],
        "specializations": specializations or [],
        "behaviors": {
            "auto_format_code": True,
            "include_examples": True,
            "explain_complexity": True,
            "suggest_tests": True,
        },
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


def list_training_data() -> List[Dict[str, Any]]:
    return STORE["training_data"]


def load_training_data(training_id: str) -> Dict[str, Any]:
    for td in STORE["training_data"]:
        if td["id"] == training_id:
            return td
    raise KeyError("Training data not found")


def save_training_data(td: Dict[str, Any]) -> None:
    existing = next((t for t in STORE["training_data"] if t["id"] == td["id"]), None)
    if existing:
        existing.update(td)
    else:
        STORE["training_data"].append(td)


def delete_training_data(training_id: str) -> None:
    STORE["training_data"] = [t for t in STORE["training_data"] if t["id"] != training_id]


def list_feelings() -> List[Dict[str, Any]]:
    return STORE["feelings"]


def load_feeling(feeling_id: str) -> Dict[str, Any]:
    for f in STORE["feelings"]:
        if f["id"] == feeling_id:
            return f
    raise KeyError("Feeling not found")


def save_feeling(f: Dict[str, Any]) -> None:
    existing = next((x for x in STORE["feelings"] if x["id"] == f["id"]), None)
    if existing:
        existing.update(f)
    else:
        STORE["feelings"].append(f)


def update_feeling(f: Dict[str, Any]) -> None:
    save_feeling(f)


def delete_feeling(feeling_id: str) -> None:
    STORE["feelings"] = [f for f in STORE["feelings"] if f["id"] != feeling_id]


# Queue management
def add_queue_item(item: Dict[str, Any]) -> None:
    STORE["queue_items"].append(item)
    if item["status"].name == "Backlog":
        STORE["backlog"].append(item)
    elif item["status"].name == "Active":
        STORE["active"].append(item)
    elif item["status"].name == "Complete":
        STORE["complete"].append(item)


def list_queue_items() -> List[Dict[str, Any]]:
    return STORE["queue_items"]


def list_backlog_items() -> List[Dict[str, Any]]:
    return STORE["backlog"]


def list_active_items() -> List[Dict[str, Any]]:
    return STORE["active"]


def list_complete_items() -> List[Dict[str, Any]]:
    return STORE["complete"]


def start_queue_session(task_id: str) -> str:
    session_id = f"session_{uuid.uuid4().hex[:8]}"
    sess = {
        "id": session_id,
        "queue_item_id": task_id,
        "start_time": datetime.now(timezone.utc),
        "end_time": None,
        "duration_seconds": 0,
    }
    STORE["queue_sessions"].append(sess)
    return session_id


def end_queue_session(session_id: str) -> None:
    sess = next((s for s in STORE["queue_sessions"] if s["id"] == session_id), None)
    if not sess:
        raise KeyError("Session not found")
    if not sess["end_time"]:
        now = datetime.now(timezone.utc)
        sess["end_time"] = now
        delta = (now - sess["start_time"]).total_seconds()
        sess["duration_seconds"] = int(delta)


def get_queue_session(session_id: str) -> Dict[str, Any]:
    sess = next((s for s in STORE["queue_sessions"] if s["id"] == session_id), None)
    if not sess:
        raise KeyError("Session not found")
    return sess


# API Key management
def create_api_key() -> Dict[str, Any]:
    user_id = f"user_{uuid.uuid4().hex[:6]}"
    public_key = f"pk_{uuid.uuid4().hex}"
    private_key = f"sk_{uuid.uuid4().hex}"
    key = {
        "user_id": user_id,
        "public_key": public_key,
        "private_key": private_key,
        "active": True,
        "created_at": datetime.now(timezone.utc),
    }
    STORE["api_keys"].append(key)
    return key


def check_api_key_auth(public_key: str, private_key: Optional[str]) -> Tuple[str, bool]:
    key = next((k for k in STORE["api_keys"] if k["public_key"] == public_key and k["active"]), None)
    if not key:
        raise PermissionError("Invalid API key")
    # Minimal private key check (demo)
    if private_key and key["private_key"] != private_key:
        raise PermissionError("Private key mismatch")
    is_admin = private_key is not None  # demo rule: having private key => admin
    return key["user_id"], is_admin


# -------------------------
# Enums
# -------------------------

class Priority:
    Low = "low"
    Medium = "medium"
    High = "high"
    Critical = "critical"


class Status:
    Todo = "todo"
    InProgress = "in_progress"
    Done = "done"


class Assignee:
    Human = "human"
    Agent = "agent"
    System = "system"


class TaskFilters:
    pass


class TrainingDataType:
    Instruction = "instruction"
    Conversation = "conversation"
    Completion = "completion"
    Code = "code"
    Analysis = "analysis"
    Planning = "planning"
    Review = "review"
    Documentation = "documentation"
    Example = "example"
    Test = "test"
    Validation = "validation"


class QueueStatus:
    Backlog = "backlog"
    Active = "active"
    Complete = "complete"


# -------------------------
# Embedded Services - using from emb.py
# -------------------------
from todozi.emb import TodoziEmbeddingService as RealEmbeddingService, TodoziEmbeddingConfig
from todozi.models import Ok

class TodoziEmbeddingService:
    def __init__(self, config: Dict[str, Any]):
        model_name = config.get("model_name", "sentence-transformers/all-MiniLM-L6-v2")
        self._real_service = RealEmbeddingService(TodoziEmbeddingConfig(model_name=model_name))
        self.config = config
        self.initialized = False

    async def initialize(self) -> None:
        await self._real_service.initialize()
        self.initialized = True

    async def add_task(self, task: Dict[str, Any]) -> str:
        from todozi.models import Task, Priority, Status
        from todozi.emb import Task as EmbTask
        
        task_id = f"task_{uuid.uuid4().hex[:8]}"
        task["id"] = task_id
        task["created_at"] = datetime.now(timezone.utc)
        task["updated_at"] = datetime.now(timezone.utc)
        
        priority_result = Priority.from_str(task.get("priority", "medium"))
        priority = priority_result.value if isinstance(priority_result, Ok) else Priority.MEDIUM
        
        status_result = Status.from_str(task.get("status", "todo"))
        status = status_result.value if isinstance(status_result, Ok) else Status.TODO
        
        emb_task = EmbTask(
            id=task_id,
            action=task.get("action", ""),
            parent_project=task.get("parent_project", "general"),
            priority=priority.value if hasattr(priority, 'value') else str(priority),
            status=status.value if hasattr(status, 'value') else str(status),
            tags=task.get("tags", []),
            time=task.get("time", "1 hour"),
            assignee=task.get("assignee"),
            context_notes=task.get("context_notes"),
            progress=task.get("progress"),
            embedding_vector=None,
        )
        
        await self._real_service.add_task(emb_task)
        task["embedding_vector"] = emb_task.embedding_vector
        STORE["tasks"][task_id] = task
        return task_id

    async def semantic_search(
        self,
        query: str,
        content_types: Optional[List[str]] = None,
        limit: Optional[int] = 20,
    ) -> List[Dict[str, Any]]:
        results = await self._real_service.semantic_search(query, content_types, limit)
        return [{
            "content_id": r.content_id,
            "text_content": r.text_content,
            "similarity_score": r.similarity_score,
            "tags": r.tags,
        } for r in results]

    async def find_similar_tasks(self, text: str, limit: Optional[int] = 10) -> List[str]:
        results = await self._real_service.find_similar_tasks(text, limit)
        return [r.content_id for r in results]

    async def get_stats(self) -> Dict[str, Any]:
        diag = await self._real_service.export_diagnostics()
        return {
            "total_embeddings": sum(diag.content_type_breakdown.values()),
            "model_name": self._real_service.config.model_name,
            "avg_similarity": diag.avg_similarity_score,
        }

    async def cluster_content(self) -> List[Dict[str, Any]]:
        clusters = await self._real_service.cluster_content()
        return [{
            "cluster_id": c.cluster_id,
            "size": c.cluster_size,
            "sample": [item.content_id for item in c.content_items[:5]],
            "avg_similarity": c.average_similarity,
        } for c in clusters]


# TUI Service implementation
class TuiService:
    def __init__(self, embedding_service: TodoziEmbeddingService, display_config: Dict[str, Any]):
        self.embedding_service = embedding_service
        self.display_config = display_config

    async def display_task(self, task_id: str) -> Dict[str, Any]:
        task = STORE["tasks"].get(task_id)
        if not task:
            raise KeyError("Task not found")
        return {
            "task": task,
            "confidence_score": 0.88,
            "similar_tasks": [],
            "ai_suggestions": ["Consider breaking this into smaller tasks"],
            "semantic_tags": task.get("tags", []),
            "related_content": [],
        }


# -------------------------
# Chat Processing
# -------------------------

def process_chat_message_extended(message: str, user: str) -> Dict[str, Any]:
    from todozi.tdz_tls import parse_chat_message_extended
    
    parsed = parse_chat_message_extended(message, "server")
    
    tasks = [{
        "action": t.action,
        "priority": t.priority,
        "parent_project": t.parent_project,
        "time": t.time,
        "context_notes": t.context_notes,
    } for t in parsed.tasks]
    
    memories = [{
        "moment": m.moment,
        "meaning": m.meaning,
        "reason": m.reason,
    } for m in parsed.memories]
    
    ideas = [{
        "idea": i.idea,
    } for i in parsed.ideas]
    
    errors = [{
        "title": e.title,
        "detail": e.detail,
    } for e in parsed.errors]
    
    code_chunks = [{
        "code": c.code,
        "lang": c.lang,
    } for c in parsed.code_chunks]
    
    return {
        "tasks": tasks,
        "memories": memories,
        "ideas": ideas,
        "agent_assignments": parsed.agent_assignments,
        "code_chunks": code_chunks,
        "errors": errors,
        "training_data": parsed.training_data,
        "feelings": parsed.feelings,
        "summaries": parsed.summaries,
        "reminders": parsed.reminders,
    }


# -------------------------
# Initialization
# -------------------------

async def init_storage() -> None:
    # Initialize a default project if not exists
    if "general" not in STORE["projects"]:
        STORE["projects"]["general"] = {
            "name": "general",
            "description": "General tasks",
            "status": "active",
            "tasks": [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }


async def initialize_system() -> Dict[str, Any]:
    create_default_agents()
    await init_storage()
    return {
        "message": "System initialized successfully",
        "directories_created": True,
        "storage_initialized": True,
        "agents_created": 26,
    }


# -------------------------
# HTTP Parsing and Utils
# -------------------------

def parse_request_from_bytes(data: bytes) -> HttpRequest:
    text = data.decode("utf-8", errors="ignore")
    return parse_request(text)


def parse_request(text: str) -> HttpRequest:
    lines = text.split("\r\n")
    if not lines:
        raise ValueError("Empty request")

    first = lines[0]
    parts = first.split()
    if len(parts) < 3:
        raise ValueError("Invalid request line")

    method = parts[0]
    path = parts[1]

    headers: Dict[str, str] = {}
    body_start_index = 0
    for i, line in enumerate(lines):
        if line.strip() == "":
            body_start_index = i + 1
            break
        if i == 0:
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            headers[k.strip()] = v.strip()

    body = "\r\n".join(lines[body_start_index:]) if body_start_index < len(lines) else ""
    return HttpRequest(method=method, path=path, headers=headers, body=body)


def parse_json_body(body: str) -> Any:
    if not body or body.strip() == "":
        raise ValueError("Empty request body")
    try:
        return json.loads(body)
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing error: {e} at position {e.pos}")
        raise ValueError(f"Invalid JSON: {e}")


def ensure_cors(headers: Dict[str, str]) -> None:
    headers.setdefault("Access-Control-Allow-Origin", "*")
    headers.setdefault("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    headers.setdefault("Access-Control-Allow-Headers", "Content-Type, Authorization, X-API-Key, X-API-Private-Key")


def path_parts(path: str) -> List[str]:
    # Normalize leading/trailing slashes, split
    if path.startswith("/"):
        path = path[1:]
    if path.endswith("/"):
        path = path[:-1]
    return path.split("/") if path else []


def parse_query_param(path: str, key: str) -> Optional[str]:
    # Very simple query extraction from raw path (handles /tasks/search?q=query)
    m = re.search(rf"[?&]{key}=([^&]+)", path)
    if m:
        return m.group(1)
    return None


# -------------------------
# Core Server
# -------------------------

class TodoziServer:
    def __init__(self, config: ServerConfig):
        self.config = config
        self.storage = Storage()
        self.code_graph = CodeGenerationGraph(10000)

    async def start(self) -> None:
        addr = (self.config.host, self.config.port)
        print(f"🚀 Todozi Enhanced Server starting on {addr[0]}:{addr[1]} (26 Agents Ready!)")
        self._print_endpoints()

        server = await asyncio.start_server(self.handle_connection, addr[0], addr[1])
        async with server:
            await server.serve_forever()

    def _print_endpoints(self) -> None:
        print("📡 Available endpoints:")
        print()
        print("🎯 CORE FUNCTIONALITY:")
        print("  GET  /health                    - Health check")
        print("  GET  /stats                     - System statistics")
        print("  GET  /init                      - Initialize system")
        print()
        print("📋 TASK MANAGEMENT:")
        print("  GET  /tasks                     - List all tasks")
        print("  POST /tasks                     - Create new task")
        print("  GET  /tasks/{id}                - Get task by ID")
        print("  PUT  /tasks/{id}                - Update task")
        print("  DELETE /tasks/{id}              - Delete task")
        print("  GET  /tasks/search?q={query}    - Search tasks")
        print()
        print("🤖 ENHANCED AGENT SYSTEM (26 AGENTS):")
        print("  GET  /agents                    - List all agents")
        print("  POST /agents                    - Create new agent")
        print("  GET  /agents/{id}               - Get agent by ID")
        print("  PUT  /agents/{id}               - Update agent")
        print("  DELETE /agents/{id}             - Delete agent")
        print("  GET  /agents/available          - Get available agents")
        print("  GET  /agents/{id}/status        - Get agent status")
        print()
        print("🧠 MEMORY & IDEA MANAGEMENT:")
        print("  GET  /memories                  - List all memories")
        print("  POST /memories                  - Create new memory")
        print("  GET  /ideas                     - List all ideas")
        print("  POST /ideas                     - Create new idea")
        print("  GET  /feelings                  - List all feelings")
        print("  POST /feelings                  - Create new feeling")
        print("  GET  /feelings/{id}             - Get feeling by ID")
        print("  PUT  /feelings/{id}             - Update feeling")
        print("  DELETE /feelings/{id}           - Delete feeling")
        print("  GET  /feelings/search?q={query} - Search feelings")
        print()
        print("🎓 TRAINING DATA SYSTEM:")
        print("  GET  /training                  - List all training data")
        print("  POST /training                  - Create training data")
        print("  GET  /training/{id}             - Get training data by ID")
        print("  PUT  /training/{id}             - Update training data")
        print("  DELETE /training/{id}           - Delete training data")
        print("  GET  /training/export           - Export training data")
        print("  GET  /training/stats            - Training data statistics")
        print()
        print("🧩 CODE CHUNKING SYSTEM:")
        print("  GET  /chunks                    - List all code chunks")
        print("  POST /chunks                    - Create new code chunk")
        print("  GET  /chunks/ready              - Get ready chunks")
        print("  GET  /chunks/graph              - Get dependency graph")
        print()
        print("💬 ENHANCED CHAT PROCESSING:")
        print("  POST /chat/process              - Process chat message")
        print("  POST /chat/agent/{id}           - Chat with specific agent")
        print("  GET  /chat/history              - Get chat history")
        print()
        print("📊 ANALYTICS & TRACKING:")
        print("  GET  /analytics/tasks           - Task analytics")
        print("  GET  /analytics/agents          - Agent analytics")
        print("  GET  /analytics/performance     - System performance")
        print("  POST /time/start/{task_id}      - Start time tracking")
        print("  POST /time/stop/{task_id}       - Stop time tracking")
        print("  GET  /time/report               - Time tracking report")
        print()
        print("📁 PROJECT MANAGEMENT:")
        print("  GET  /projects                  - List all projects")
        print("  POST /projects                  - Create new project")
        print("  GET  /projects/{name}           - Get project by name")
        print("  PUT  /projects/{name}           - Update project")
        print("  DELETE /projects/{name}         - Delete project")
        print()
        print("🔧 UTILITIES:")
        print("  POST /backup                    - Create backup")
        print("  GET  /backups                   - List backups")
        print("  POST /restore/{name}            - Restore from backup")
        print()
        print("📋 QUEUE MANAGEMENT:")
        print("  POST /queue/plan                - Plan new queue item")
        print("  GET  /queue/list                - List all queue items")
        print("  GET  /queue/list/backlog        - List backlog items")
        print("  GET  /queue/list/active         - List active items")
        print("  GET  /queue/list/complete       - List complete items")
        print("  POST /queue/start/{item_id}     - Start queue session")
        print("  POST /queue/end/{session_id}    - End queue session")
        print()
        print("🔑 API KEY MANAGEMENT:")
        print("  POST /api/register              - Register new API key")
        print("  POST /api/check                 - Check API key authentication")
        print()
        print("🤖 AI-ENHANCED ENDPOINTS:")
        print("  GET  /tasks/{id}/insights       - Get task with AI insights")
        print("  GET  /tasks/{id}/similar        - Find similar tasks")
        print("  POST /tasks/validate            - Validate task with AI")
        print("  GET  /tasks/suggest             - AI task suggestions")
        print("  GET  /semantic/search?q={query} - Semantic search")
        print("  GET  /insights                  - AI insights overview")
        print()

    async def handle_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter) -> None:
        try:
            # Read until end of headers "\r\n\r\n"
            buffer = bytearray()
            while True:
                chunk = await reader.read(8192)
                if not chunk:
                    break
                buffer.extend(chunk)
                if b"\r\n\r\n" in buffer:
                    break
                if len(buffer) > MAX_BUFFER_SIZE:
                    print(f"⚠️  Request too large, truncating at {MAX_BUFFER_SIZE} bytes")
                    break

            if not buffer:
                return

            request = parse_request_from_bytes(bytes(buffer))
            is_health = request.path in HEALTH_PATHS
            if not is_health:
                print(f"🔍 Debug: Request path: '{request.path}', method: {request.method}")

            response = await self.handle_request(request)
            ensure_cors(response.headers)
            if "Content-Type" not in response.headers:
                response.headers["Content-Type"] = "application/json"

            # Build HTTP response
            status_text = {200: "OK", 404: "Not Found", 500: "Internal Server Error", 401: "Unauthorized"}.get(
                response.status, "Unknown"
            )
            http_resp = f"HTTP/1.1 {response.status} {status_text}\r\n"
            for k, v in response.headers.items():
                http_resp += f"{k}: {v}\r\n"
            http_resp += f"Content-Length: {len(response.body)}\r\n"
            http_resp += "\r\n"
            http_resp += response.body

            writer.write(http_resp.encode("utf-8"))
            await writer.drain()
        except Exception as e:
            print(f"❌ Connection error: {e}")
        finally:
            try:
                writer.close()
            except Exception:
                pass
            await writer.wait_closed()

    async def handle_request(self, request: HttpRequest) -> HttpResponse:
        try:
            # Authentication and CORS preflight
            if request.method == "OPTIONS":
                return HttpResponse.ok("")

            # Route matching
            parts = path_parts(request.path)

            # Health checks
            if request.method == "GET" and parts == ["health"]:
                return HttpResponse.ok(
                    json.dumps(
                        {
                            "status": "healthy",
                            "service": "todozi-enhanced-server",
                            "version": "0.1.0",
                            "port": self.config.port,
                            "agents_available": 26,
                            "features": ["enhanced_agents", "training_data", "analytics", "time_tracking"],
                        }
                    )
                )

            # Paths that do not require authentication
            skip_auth_paths = {
                ("GET", ["health"]),
                ("GET", ["tdz", "health"]),
                ("GET", ["todozi", "health"]),
                ("POST", ["api", "register"]),
                ("POST", ["tdz", "api", "register"]),
                ("GET", ["init"]),
                ("GET", ["tdz", "init"]),
                ("GET", ["todozi", "init"]),
            }

            if (request.method, parts) not in skip_auth_paths and request.path not in HEALTH_PATHS:
                # Very simple header extraction for API key
                pub = None
                for key in [
                    "X-API-Key",
                    "x-api-key",
                    "X-APIKey",
                    "x-apikey",
                    "API-Key",
                    "api-key",
                    "x-api-token",
                    "X-APIToken",
                    "x-apitoken",
                    "API-Token",
                    "api-token",
                    "Authorization",
                    "authorization",
                ]:
                    val = request.headers.get(key)
                    if val:
                        if val.strip().startswith("Bearer "):
                            pub = val.strip()[7:]
                        elif val.strip().startswith("ApiKey "):
                            pub = val.strip()[7:]
                        elif val.strip().startswith("Token "):
                            pub = val.strip()[6:]
                        else:
                            pub = val.strip()
                        break

                priv = request.headers.get("X-API-Private-Key") or request.headers.get("x-api-private-key")

                if not pub:
                    return HttpResponse.error(401, "Unauthorized: API key required")

                try:
                    user_id, is_admin = check_api_key_auth(pub, priv)
                    print(f"🔑 API Key authenticated: user_id={user_id}, admin={is_admin}")
                except PermissionError as e:
                    print(f"❌ API Key authentication failed: {e}")
                    return HttpResponse.error(401, f"Unauthorized: {e}")

            # System endpoints
            if (request.method, parts) in [
                ("GET", ["stats"]),
                ("GET", ["tdz", "stats"]),
                ("GET", ["todozi", "stats"]),
            ]:
                stats = await self.get_system_stats()
                return HttpResponse.json(stats)

            if (request.method, parts) in [
                ("GET", ["init"]),
                ("GET", ["tdz", "init"]),
                ("GET", ["todozi", "init"]),
            ]:
                result = await initialize_system()
                return HttpResponse.json({"message": "System initialized successfully", "result": result})

            # Tasks
            if (request.method, parts) in [
                ("GET", ["tasks"]),
                ("GET", ["tdz", "tasks"]),
                ("GET", ["todozi", "tasks"]),
            ]:
                tasks = await self.get_all_tasks()
                return HttpResponse.json(tasks)

            if (request.method, parts) in [
                ("POST", ["tasks"]),
                ("POST", ["tdz", "tasks"]),
                ("POST", ["todozi", "tasks"]),
            ]:
                # Auth required path (would have failed earlier if not provided)
                task_data = parse_json_body(request.body)
                result = await self.create_task(task_data)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["tasks", "search"]),
                ("GET", ["tdz", "tasks", "search"]),
            ]:
                query = parse_query_param(request.path, "q") or ""
                results = await self.search_tasks(query)
                return HttpResponse.json(results)

            if TDZ_ENABLE_TUI and (request.method, parts) in [
                ("GET", ["tasks", "_", "insights"]),
                ("GET", ["tdz", "tasks", "_", "insights"]),
            ]:
                tid = parts[2]
                result = await self.get_task_insights(tid)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["tasks", "_", "similar"]),
                ("GET", ["tdz", "tasks", "_", "similar"]),
            ]:
                tid = parts[2]
                result = await self.get_similar_tasks(tid)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["tasks", "suggest"]),
                ("GET", ["tdz", "tasks", "suggest"]),
            ]:
                result = await self.get_ai_task_suggestions()
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["tasks", "_"]),
                ("GET", ["tdz", "tasks", "_"]),
            ]:
                tid = parts[2]
                task = await self.get_task(tid)
                return HttpResponse.json(task)

            if (request.method, parts) in [
                ("PUT", ["tasks", "_"]),
                ("PUT", ["tdz", "tasks", "_"]),
            ]:
                tid = parts[2]
                task_data = parse_json_body(request.body)
                result = await self.update_task(tid, task_data)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("DELETE", ["tasks", "_"]),
                ("DELETE", ["tdz", "tasks", "_"]),
            ]:
                tid = parts[2]
                result = await self.delete_task(tid)
                return HttpResponse.json(result)

            # Memories endpoints
            if (request.method, parts) in [
                ("GET", ["memories"]),
                ("GET", ["tdz", "memories"]),
            ]:
                from todozi.memory import MemoryManager
                import asyncio
                memory_manager = MemoryManager()
                asyncio.run(memory_manager.load_memories())
                memories = memory_manager.get_all_memories()
                return HttpResponse.json([{
                    "id": m.id,
                    "moment": m.moment,
                    "meaning": m.meaning,
                    "reason": m.reason,
                    "importance": m.importance.value if hasattr(m.importance, 'value') else str(m.importance),
                    "term": m.term.value if hasattr(m.term, 'value') else str(m.term),
                    "memory_type": m.memory_type.value if hasattr(m.memory_type, 'value') else str(m.memory_type),
                    "tags": m.tags,
                } for m in memories])

            if (request.method, parts) in [
                ("POST", ["memories"]),
                ("POST", ["tdz", "memories"]),
            ]:
                from todozi.memory import MemoryManager
                from todozi.models import MemoryImportance, MemoryTerm, MemoryType, ItemStatus
                import asyncio
                
                memory_data = parse_json_body(request.body)
                memory_manager = MemoryManager()
                asyncio.run(memory_manager.load_memories())
                
                importance_result = MemoryImportance.from_str(memory_data.get("importance", "medium"))
                importance = importance_result.value if isinstance(importance_result, Ok) else MemoryImportance.MEDIUM
                
                term_result = MemoryTerm.from_str(memory_data.get("term", "short"))
                term = term_result.value if isinstance(term_result, Ok) else MemoryTerm.SHORT
                
                memory_type_result = MemoryType.from_str(memory_data.get("memory_type", "standard"))
                memory_type = memory_type_result.value if isinstance(memory_type_result, Ok) else MemoryType.STANDARD
                
                from todozi.models import Memory
                memory = Memory(
                    user_id=memory_data.get("user_id", "server_user"),
                    project_id=memory_data.get("project_id"),
                    status=ItemStatus.ACTIVE,
                    moment=memory_data.get("moment", ""),
                    meaning=memory_data.get("meaning", ""),
                    reason=memory_data.get("reason", ""),
                    importance=importance,
                    term=term,
                    memory_type=memory_type,
                    tags=memory_data.get("tags", []),
                )
                asyncio.run(memory_manager.create_memory(memory))
                return HttpResponse.json({"message": "Memory created successfully", "id": memory.id, "memory": {
                    "id": memory.id,
                    "moment": memory.moment,
                    "meaning": memory.meaning,
                }})

            # Ideas endpoints
            if (request.method, parts) in [
                ("GET", ["ideas"]),
                ("GET", ["tdz", "ideas"]),
            ]:
                from todozi.idea import IdeaManager
                import asyncio
                idea_manager = IdeaManager()
                asyncio.run(idea_manager.load_ideas())
                ideas = idea_manager.get_all_ideas()
                return HttpResponse.json([{
                    "id": i.id,
                    "idea": i.idea,
                    "share": i.share.value if hasattr(i.share, 'value') else str(i.share),
                    "importance": i.importance.value if hasattr(i.importance, 'value') else str(i.importance),
                    "tags": i.tags,
                    "context": i.context,
                } for i in ideas])

            if (request.method, parts) in [
                ("POST", ["ideas"]),
                ("POST", ["tdz", "ideas"]),
            ]:
                from todozi.idea import IdeaManager
                from todozi.models import IdeaImportance, ShareLevel, ItemStatus
                import asyncio
                
                idea_data = parse_json_body(request.body)
                idea_manager = IdeaManager()
                asyncio.run(idea_manager.load_ideas())
                
                share_result = ShareLevel.from_str(idea_data.get("share", "team"))
                share = share_result.value if isinstance(share_result, Ok) else ShareLevel.TEAM
                
                importance_result = IdeaImportance.from_str(idea_data.get("importance", "medium"))
                importance = importance_result.value if isinstance(importance_result, Ok) else IdeaImportance.MEDIUM
                
                from todozi.models import Idea
                idea = Idea(
                    idea=idea_data.get("idea", ""),
                    project_id=idea_data.get("project_id"),
                    status=ItemStatus.ACTIVE,
                    share=share,
                    importance=importance,
                    tags=idea_data.get("tags", []),
                    context=idea_data.get("context"),
                )
                asyncio.run(idea_manager.create_idea(idea))
                return HttpResponse.json({"message": "Idea created successfully", "id": idea.id, "idea": {
                    "id": idea.id,
                    "idea": idea.idea,
                }})

            # Agents
            if (request.method, parts) in [
                ("GET", ["agents"]),
                ("GET", ["tdz", "agents"]),
            ]:
                agents = await self.get_all_agents()
                return HttpResponse.json(agents)

            if (request.method, parts) in [
                ("POST", ["agents"]),
                ("POST", ["tdz", "agents"]),
            ]:
                agent_data = parse_json_body(request.body)
                result = await self.create_agent(agent_data)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["agents", "available"]),
                ("GET", ["tdz", "agents", "available"]),
            ]:
                agents = await self.get_available_agents()
                return HttpResponse.json(agents)

            if (request.method, parts) in [
                ("GET", ["agents", "_", "status"]),
                ("GET", ["tdz", "agents", "_", "status"]),
            ]:
                aid = parts[2]
                status = await self.get_agent_status(aid)
                return HttpResponse.json(status)

            if (request.method, parts) in [
                ("GET", ["agents", "_"]),
                ("GET", ["tdz", "agents", "_"]),
            ]:
                aid = parts[2]
                agent = await self.get_agent(aid)
                return HttpResponse.json(agent)

            if (request.method, parts) in [
                ("PUT", ["agents", "_"]),
                ("PUT", ["tdz", "agents", "_"]),
            ]:
                aid = parts[2]
                agent_data = parse_json_body(request.body)
                result = await self.update_agent(aid, agent_data)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("DELETE", ["agents", "_"]),
                ("DELETE", ["tdz", "agents", "_"]),
            ]:
                aid = parts[2]
                result = await self.delete_agent(aid)
                return HttpResponse.json(result)

            # Training
            if (request.method, parts) in [
                ("GET", ["training"]),
                ("GET", ["tdz", "training"]),
            ]:
                data = await self.get_all_training_data()
                return HttpResponse.json(data)

            if (request.method, parts) in [
                ("POST", ["training"]),
                ("POST", ["tdz", "training"]),
            ]:
                td = parse_json_body(request.body)
                result = await self.create_training_data(td)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["training", "export"]),
                ("GET", ["tdz", "training", "export"]),
            ]:
                export_data = await self.export_training_data()
                return HttpResponse.json(export_data)

            if (request.method, parts) in [
                ("GET", ["training", "stats"]),
                ("GET", ["tdz", "training", "stats"]),
            ]:
                stats = await self.get_training_stats()
                return HttpResponse.json(stats)

            if (request.method, parts) in [
                ("GET", ["training", "_"]),
                ("GET", ["tdz", "training", "_"]),
            ]:
                tid = parts[2]
                td = await self.get_training_data(tid)
                return HttpResponse.json(td)

            if (request.method, parts) in [
                ("PUT", ["training", "_"]),
                ("PUT", ["tdz", "training", "_"]),
            ]:
                tid = parts[2]
                td = parse_json_body(request.body)
                result = await self.update_training_data(tid, td)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("DELETE", ["training", "_"]),
                ("DELETE", ["tdz", "training", "_"]),
            ]:
                tid = parts[2]
                result = await self.delete_training_data(tid)
                return HttpResponse.json(result)

            # Chat
            if (request.method, parts) in [
                ("POST", ["chat", "process"]),
                ("POST", ["tdz", "chat", "process"]),
            ]:
                chat_data = parse_json_body(request.body)
                result = await self.process_chat_message(chat_data)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("POST", ["chat", "agent", "_"]),
                ("POST", ["tdz", "chat", "agent", "_"]),
            ]:
                agent_id = parts[3]
                chat_data = parse_json_body(request.body)
                result = await self.chat_with_agent(agent_id, chat_data)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["chat", "history"]),
                ("GET", ["tdz", "chat", "history"]),
            ]:
                history = await self.get_chat_history()
                return HttpResponse.json(history)

            # Analytics
            if (request.method, parts) in [
                ("GET", ["analytics", "tasks"]),
                ("GET", ["tdz", "analytics", "tasks"]),
            ]:
                analytics = await self.get_task_analytics()
                return HttpResponse.json(analytics)

            if (request.method, parts) in [
                ("GET", ["analytics", "agents"]),
                ("GET", ["tdz", "analytics", "agents"]),
            ]:
                analytics = await self.get_agent_analytics()
                return HttpResponse.json(analytics)

            if (request.method, parts) in [
                ("GET", ["analytics", "performance"]),
                ("GET", ["tdz", "analytics", "performance"]),
            ]:
                analytics = await self.get_performance_analytics()
                return HttpResponse.json(analytics)

            # Time tracking
            if (request.method, parts) in [
                ("POST", ["time", "start", "_"]),
                ("POST", ["tdz", "time", "start", "_"]),
            ]:
                task_id = parts[3]
                result = await self.start_time_tracking(task_id)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("POST", ["time", "stop", "_"]),
                ("POST", ["tdz", "time", "stop", "_"]),
            ]:
                task_id = parts[3]
                result = await self.stop_time_tracking(task_id)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["time", "report"]),
                ("GET", ["tdz", "time", "report"]),
            ]:
                report = await self.get_time_tracking_report()
                return HttpResponse.json(report)

            # Chunks
            if (request.method, parts) in [
                ("GET", ["chunks"]),
                ("GET", ["tdz", "chunks"]),
            ]:
                chunks = [
                    {
                        "id": c["chunk_id"],
                        "level": c["level"],
                        "status": c["status"],
                        "dependencies": c["dependencies"],
                        "estimated_tokens": c["estimated_tokens"],
                    }
                    for c in self.code_graph.chunks.values()
                ]
                return HttpResponse.json(chunks)

            if (request.method, parts) in [
                ("POST", ["chunks"]),
                ("POST", ["tdz", "chunks"]),
            ]:
                chunk_data = parse_json_body(request.body)
                return HttpResponse.json({"message": "Code chunk created successfully", "chunk": chunk_data})

            if (request.method, parts) in [
                ("GET", ["chunks", "ready"]),
                ("GET", ["tdz", "chunks", "ready"]),
            ]:
                ready = self.code_graph.get_ready_chunks()
                return HttpResponse.json({"ready_chunks": ready, "count": len(ready)})

            if (request.method, parts) in [
                ("GET", ["chunks", "graph"]),
                ("GET", ["tdz", "chunks", "graph"]),
            ]:
                graph_data = {
                    "total_chunks": len(self.code_graph.chunks),
                    "project_summary": self.code_graph.get_project_summary(),
                }
                return HttpResponse.json(graph_data)

            # Projects
            if (request.method, parts) in [
                ("GET", ["projects"]),
                ("GET", ["tdz", "projects"]),
            ]:
                projects = [{"name": p["name"], "description": p["description"], "status": "active"} for p in STORE["projects"].values()]
                return HttpResponse.json(projects)

            if (request.method, parts) in [
                ("POST", ["projects"]),
                ("POST", ["tdz", "projects"]),
            ]:
                project_data = parse_json_body(request.body)
                name = (project_data.get("name") or "").strip()
                if not name:
                    return HttpResponse.error(400, "Missing or invalid 'name' field")
                desc = project_data.get("description")
                self.storage.create_project(name, desc)
                return HttpResponse.json({"message": "Project created successfully", "project": {"name": name, "description": desc, "status": "active"}})

            if (request.method, parts) in [
                ("GET", ["projects", "_"]),
                ("GET", ["tdz", "projects", "_"]),
            ]:
                name = parts[2]
                try:
                    project = self.storage.get_project(name)
                except KeyError:
                    return HttpResponse.error(404, "Project not found")
                return HttpResponse.json(
                    {
                        "name": project["name"],
                        "description": project["description"],
                        "created_at": project["created_at"],
                        "updated_at": project["updated_at"],
                    }
                )

            if (request.method, parts) in [
                ("PUT", ["projects", "_"]),
                ("PUT", ["tdz", "projects", "_"]),
            ]:
                name = parts[2]
                project_data = parse_json_body(request.body)
                desc = project_data.get("description")
                return HttpResponse.json(
                    {"message": "Project update not yet fully implemented", "name": name, "description": desc}
                )

            if (request.method, parts) in [
                ("DELETE", ["projects", "_"]),
                ("DELETE", ["tdz", "projects", "_"]),
            ]:
                name = parts[2]
                return HttpResponse.json({"message": "Project deletion not yet fully implemented", "name": name})

            # Feelings
            if (request.method, parts) in [
                ("GET", ["feelings"]),
                ("GET", ["tdz", "feelings"]),
            ]:
                feelings = await self.get_all_feelings()
                return HttpResponse.json(feelings)

            if (request.method, parts) in [
                ("POST", ["feelings"]),
                ("POST", ["tdz", "feelings"]),
            ]:
                feeling_data = parse_json_body(request.body)
                result = await self.create_feeling(feeling_data)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["feelings", "_"]),
                ("GET", ["tdz", "feelings", "_"]),
            ]:
                fid = parts[2]
                feeling = await self.get_feeling(fid)
                return HttpResponse.json(feeling)

            if (request.method, parts) in [
                ("PUT", ["feelings", "_"]),
                ("PUT", ["tdz", "feelings", "_"]),
            ]:
                fid = parts[2]
                feeling_data = parse_json_body(request.body)
                result = await self.update_feeling(fid, feeling_data)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("DELETE", ["feelings", "_"]),
                ("DELETE", ["tdz", "feelings", "_"]),
            ]:
                fid = parts[2]
                result = await self.delete_feeling(fid)
                return HttpResponse.json(result)

            # Queue
            if (request.method, parts) in [
                ("POST", ["queue", "plan"]),
                ("POST", ["tdz", "queue", "plan"]),
            ]:
                queue_data = parse_json_body(request.body)
                result = await self.create_queue_item(queue_data)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["queue", "list"]),
                ("GET", ["tdz", "queue", "list"]),
            ]:
                items = await self.get_all_queue_items()
                return HttpResponse.json(items)

            if (request.method, parts) in [
                ("GET", ["queue", "list", "backlog"]),
                ("GET", ["tdz", "queue", "list", "backlog"]),
            ]:
                items = await self.get_backlog_items()
                return HttpResponse.json(items)

            if (request.method, parts) in [
                ("GET", ["queue", "list", "active"]),
                ("GET", ["tdz", "queue", "list", "active"]),
            ]:
                items = await self.get_active_items()
                return HttpResponse.json(items)

            if (request.method, parts) in [
                ("GET", ["queue", "list", "complete"]),
                ("GET", ["tdz", "queue", "list", "complete"]),
            ]:
                items = await self.get_complete_items()
                return HttpResponse.json(items)

            if (request.method, parts) in [
                ("POST", ["queue", "start", "_"]),
                ("POST", ["tdz", "queue", "start", "_"]),
            ]:
                item_id = parts[3]
                result = await self.start_queue_session(item_id)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("POST", ["queue", "end", "_"]),
                ("POST", ["tdz", "queue", "end", "_"]),
            ]:
                session_id = parts[3]
                result = await self.end_queue_session(session_id)
                return HttpResponse.json(result)

            # API
            if (request.method, parts) in [
                ("POST", ["api", "register"]),
                ("POST", ["tdz", "api", "register"]),
            ]:
                result = await self.register_api_key()
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("POST", ["api", "check"]),
                ("POST", ["tdz", "api", "check"]),
            ]:
                auth_data = parse_json_body(request.body)
                result = await self.check_api_key(auth_data)
                return HttpResponse.json(result)

            # AI endpoints
            if (request.method, parts) in [
                ("POST", ["tasks", "validate"]),
                ("POST", ["tdz", "tasks", "validate"]),
            ]:
                task_data = parse_json_body(request.body)
                result = await self.validate_task_with_ai(task_data)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["semantic", "search"]),
                ("GET", ["tdz", "semantic", "search"]),
            ]:
                query = parse_query_param(request.path, "q") or ""
                result = await self.semantic_search(query)
                return HttpResponse.json(result)

            if (request.method, parts) in [
                ("GET", ["insights"]),
                ("GET", ["tdz", "insights"]),
            ]:
                result = await self.get_ai_insights()
                return HttpResponse.json(result)

            # Fallback
            return HttpResponse.error(404, "Route not found")

        except ValueError as ve:
            return HttpResponse.error(400, f"Bad request: {ve}")
        except KeyError as ke:
            return HttpResponse.error(404, f"Not found: {ke}")
        except PermissionError as pe:
            return HttpResponse.error(401, f"Unauthorized: {pe}")
        except Exception as e:
            print(f"❌ Internal error: {e}")
            return HttpResponse.error(500, "Internal Server Error")

    # ------------- Implementation Methods -------------

    async def get_system_stats(self) -> Dict[str, Any]:
        try:
            agents = list_agents()
        except Exception:
            agents = []
        try:
            tasks = self.storage.list_tasks_across_projects(TaskFilters())
        except Exception:
            tasks = []
        memory_count = 0
        training_count = 0
        try:
            training_count = len(list_training_data())
        except Exception:
            training_count = 0
        uptime_seconds = int(time.time())
        active_sessions = get_active_sessions()
        return {
            "system": {
                "version": "0.1.0",
                "uptime_seconds": uptime_seconds,
                "uptime_hours": uptime_seconds / 3600.0,
                "port": self.config.port,
            },
            "data": {
                "agents": len(agents),
                "tasks": len(tasks),
                "memories": memory_count,
                "training_data": training_count,
            },
            "performance": {
                "active_connections": len(active_sessions),
                "requests_per_second": 0.0,
                "memory_usage_mb": 50,
            },
        }

    async def get_all_tasks(self) -> List[Dict[str, Any]]:
        tasks = self.storage.list_tasks_across_projects(TaskFilters())
        return [
            {
                "id": t["id"],
                "user_id": t.get("user_id"),
                "action": t.get("action"),
                "time": t.get("time"),
                "priority": t.get("priority"),
                "parent_project": t.get("parent_project"),
                "status": t.get("status"),
                "assignee": t.get("assignee"),
                "tags": t.get("tags", []),
                "dependencies": t.get("dependencies", []),
                "context_notes": t.get("context_notes"),
                "progress": t.get("progress", 0),
                "created_at": t.get("created_at"),
                "updated_at": t.get("updated_at"),
            }
            for t in tasks
        ]

    async def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        action = task_data.get("action")
        time_str = task_data.get("time")
        if not action or not time_str:
            raise ValueError("Missing or invalid 'action' or 'time' field")
        priority_str = task_data.get("priority", "medium")
        parent_project = task_data.get("parent_project", "default")
        status = "todo"

        task = {
            "id": "",
            "user_id": "api_user",
            "action": str(action),
            "time": str(time_str),
            "priority": str(priority_str),
            "parent_project": str(parent_project),
            "status": status,
            "assignee": None,
            "tags": [],
            "dependencies": [],
            "context_notes": None,
            "progress": 0,
            "embedding_vector": None,
        }

        embedding_config = {"model_name": "sentence-transformers/all-MiniLM-L6-v2"}
        embedding_service = TodoziEmbeddingService(embedding_config)
        task_id = await embedding_service.add_task(task)
        created = self.storage.get_task_from_any_project(task_id)
        return {
            "message": "Task created successfully",
            "task": {
                "id": created["id"],
                "user_id": created.get("user_id"),
                "action": created.get("action"),
                "time": created.get("time"),
                "priority": created.get("priority"),
                "parent_project": created.get("parent_project"),
                "status": created.get("status"),
                "created_at": created.get("created_at"),
                "updated_at": created.get("updated_at"),
                "embedding_vector": created.get("embedding_vector"),
            },
        }

    async def get_task(self, task_id: str) -> Dict[str, Any]:
        t = self.storage.get_task_from_any_project(task_id)
        return {
            "id": t["id"],
            "user_id": t.get("user_id"),
            "action": t.get("action"),
            "time": t.get("time"),
            "priority": t.get("priority"),
            "parent_project": t.get("parent_project"),
            "status": t.get("status"),
            "assignee": t.get("assignee"),
            "tags": t.get("tags", []),
            "dependencies": t.get("dependencies", []),
            "context_notes": t.get("context_notes"),
            "progress": t.get("progress", 0),
            "embedding_vector": t.get("embedding_vector"),
            "created_at": t.get("created_at"),
            "updated_at": t.get("updated_at"),
        }

    async def update_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        updates: Dict[str, Any] = {}
        for field in ["action", "time", "parent_project", "context_notes"]:
            if field in task_data and task_data[field] is not None:
                updates[field] = str(task_data[field])
        if "priority" in task_data and task_data["priority"]:
            updates["priority"] = str(task_data["priority"])
        if "status" in task_data and task_data["status"]:
            updates["status"] = str(task_data["status"])
        if "assignee" in task_data and task_data["assignee"]:
            updates["assignee"] = str(task_data["assignee"])
        if "tags" in task_data and isinstance(task_data["tags"], list):
            updates["tags"] = [str(x) for x in task_data["tags"]]
        if "dependencies" in task_data and isinstance(task_data["dependencies"], list):
            updates["dependencies"] = [str(x) for x in task_data["dependencies"]]
        if "progress" in task_data and isinstance(task_data["progress"], int):
            p = task_data["progress"]
            if 0 <= p <= 100:
                updates["progress"] = p

        await self.storage.update_task_in_project(task_id, updates)
        task = self.storage.get_task_from_any_project(task_id)
        return {
            "message": "Task updated successfully",
            "task": {
                "id": task["id"],
                "user_id": task.get("user_id"),
                "action": task.get("action"),
                "time": task.get("time"),
                "priority": task.get("priority"),
                "parent_project": task.get("parent_project"),
                "status": task.get("status"),
                "assignee": task.get("assignee"),
                "tags": task.get("tags", []),
                "dependencies": task.get("dependencies", []),
                "context_notes": task.get("context_notes"),
                "progress": task.get("progress", 0),
                "embedding_vector": task.get("embedding_vector"),
                "created_at": task.get("created_at"),
                "updated_at": task.get("updated_at"),
            },
        }

    async def delete_task(self, task_id: str) -> Dict[str, Any]:
        self.storage.delete_task_from_project(task_id)
        return {"id": task_id, "message": "Task deleted successfully"}

    async def search_tasks(self, query: str) -> List[Dict[str, Any]]:
        if not query:
            return await self.get_all_tasks()
        embedding_config = {"model_name": "sentence-transformers/all-MiniLM-L6-v2"}
        embedding_service = TodoziEmbeddingService(embedding_config)
        await embedding_service.initialize()
        results = await embedding_service.semantic_search(query, None, 20)
        return [
            {
                "id": r["content_id"],
                "action": r["text_content"],
                "similarity_score": r["similarity_score"],
                "tags": r.get("tags", []),
            }
            for r in results
        ]

    async def get_all_agents(self) -> List[Dict[str, Any]]:
        agents = list_agents()
        return [
            {
                "id": a["id"],
                "name": a["name"],
                "description": a["description"],
                "version": a["version"],
                "category": a["metadata"]["category"],
                "status": a["metadata"]["status"],
                "model_provider": a["model"]["provider"],
                "model_name": a["model"]["name"],
                "capabilities": a.get("capabilities", []),
                "specializations": a.get("specializations", []),
                "created_at": a["created_at"],
                "updated_at": a["updated_at"],
            }
            for a in agents
        ]

    async def create_agent(self, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        name = agent_data.get("name")
        description = agent_data.get("description")
        category = agent_data.get("category", "custom")
        if not name or not description:
            raise ValueError("Missing or invalid 'name' or 'description' field")
        agent_id = f"agent_{int(time.time() * 1000)}"
        agent = create_custom_agent(agent_id, str(name), str(description), [], [], str(category), "api_user")
        save_agent(agent)
        return {
            "message": "Agent created successfully",
            "agent": {
                "id": agent["id"],
                "name": agent["name"],
                "description": agent["description"],
                "version": agent["version"],
                "category": agent["metadata"]["category"],
                "status": agent["metadata"]["status"],
                "model_provider": agent["model"]["provider"],
                "model_name": agent["model"]["name"],
                "capabilities": agent["capabilities"],
                "specializations": agent["specializations"],
                "created_at": agent["created_at"],
                "updated_at": agent["updated_at"],
            },
        }

    async def get_agent(self, agent_id: str) -> Dict[str, Any]:
        agent = load_agent(agent_id)
        return {
            "id": agent["id"],
            "name": agent["name"],
            "description": agent["description"],
            "version": agent["version"],
            "model": {
                "provider": agent["model"]["provider"],
                "name": agent["model"]["name"],
                "temperature": agent["model"]["temperature"],
                "max_tokens": agent["model"]["max_tokens"],
            },
            "system_prompt": agent.get("system_prompt", ""),
            "capabilities": agent.get("capabilities", []),
            "specializations": agent.get("specializations", []),
            "behaviors": agent.get("behaviors", {}),
            "metadata": {
                "author": agent["metadata"].get("author"),
                "tags": agent["metadata"].get("tags", []),
                "category": agent["metadata"]["category"],
                "status": agent["metadata"]["status"],
            },
            "created_at": agent["created_at"],
            "updated_at": agent["updated_at"],
        }

    async def update_agent(self, agent_id: str, agent_data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "id": agent_id,
            "message": "Agent update partially implemented - metadata updates only",
            "note": "Full agent updates would require Agent struct modification",
            "data": agent_data,
        }

    async def delete_agent(self, agent_id: str) -> Dict[str, Any]:
        return {
            "id": agent_id,
            "message": "Agent deletion not supported - agents are predefined system components",
            "note": "To disable an agent, use the update endpoint to change its status",
        }

    async def get_available_agents(self) -> List[Dict[str, Any]]:
        agents = get_available_agents()
        return [{"id": a["id"], "name": a["name"], "description": a["description"], "status": a["metadata"]["status"]} for a in agents]

    async def get_agent_status(self, agent_id: str) -> Dict[str, Any]:
        agent = load_agent(agent_id)
        return {"id": agent["id"], "status": agent["metadata"]["status"], "last_updated": agent["updated_at"]}

    # Training data
    async def get_all_training_data(self) -> List[Dict[str, Any]]:
        training_data = list_training_data()
        return [
            {
                "id": t["id"],
                "data_type": t["data_type"].lower(),
                "prompt": t["prompt"],
                "completion": t["completion"],
                "context": t.get("context"),
                "tags": t.get("tags", []),
                "quality_score": t.get("quality_score"),
                "source": t.get("source", "api"),
                "created_at": t["created_at"],
                "updated_at": t["updated_at"],
            }
            for t in training_data
        ]

    async def create_training_data(self, training_data: Dict[str, Any]) -> Dict[str, Any]:
        dtype_str = training_data.get("data_type")
        prompt = training_data.get("prompt")
        completion = training_data.get("completion")
        if not dtype_str or not prompt or not completion:
            raise ValueError("Missing or invalid 'data_type', 'prompt', or 'completion' field")

        type_map = {
            "instruction": TrainingDataType.Instruction,
            "conversation": TrainingDataType.Conversation,
            "completion": TrainingDataType.Completion,
            "code": TrainingDataType.Code,
            "analysis": TrainingDataType.Analysis,
            "planning": TrainingDataType.Planning,
            "review": TrainingDataType.Review,
            "documentation": TrainingDataType.Documentation,
            "example": TrainingDataType.Example,
            "test": TrainingDataType.Test,
            "validation": TrainingDataType.Validation,
        }
        dtype = type_map.get(str(dtype_str).lower())
        if not dtype:
            raise ValueError(f"Invalid data_type: {dtype_str}")

        td = {
            "id": f"training_{int(time.time() * 1000)}",
            "data_type": dtype,
            "prompt": str(prompt),
            "completion": str(completion),
            "context": training_data.get("context"),
            "tags": training_data.get("tags", []),
            "quality_score": training_data.get("quality_score"),
            "source": training_data.get("source", "api"),
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        save_training_data(td)
        return {
            "message": "Training data created successfully",
            "training_data": {
                "id": td["id"],
                "data_type": td["data_type"].lower(),
                "prompt": td["prompt"],
                "completion": td["completion"],
                "context": td.get("context"),
                "tags": td.get("tags", []),
                "quality_score": td.get("quality_score"),
                "source": td.get("source"),
                "created_at": td["created_at"],
                "updated_at": td["updated_at"],
            },
        }

    async def get_training_data(self, training_id: str) -> Dict[str, Any]:
        td = load_training_data(training_id)
        return {
            "id": td["id"],
            "data_type": td["data_type"].lower(),
            "prompt": td["prompt"],
            "completion": td["completion"],
            "context": td.get("context"),
            "tags": td.get("tags", []),
            "quality_score": td.get("quality_score"),
            "source": td.get("source"),
            "created_at": td["created_at"],
            "updated_at": td["updated_at"],
        }

    async def update_training_data(self, training_id: str, training_data: Dict[str, Any]) -> Dict[str, Any]:
        td = load_training_data(training_id)
        if "data_type" in training_data:
            dtype_str = str(training_data["data_type"]).lower()
            type_map = {
                "instruction": TrainingDataType.Instruction,
                "conversation": TrainingDataType.Conversation,
                "completion": TrainingDataType.Completion,
                "code": TrainingDataType.Code,
                "analysis": TrainingDataType.Analysis,
                "planning": TrainingDataType.Planning,
                "review": TrainingDataType.Review,
                "documentation": TrainingDataType.Documentation,
                "example": TrainingDataType.Example,
                "test": TrainingDataType.Test,
                "validation": TrainingDataType.Validation,
            }
            if dtype_str not in type_map:
                raise ValueError(f"Invalid data_type: {dtype_str}")
            td["data_type"] = type_map[dtype_str]
        for f in ["prompt", "completion", "source"]:
            if f in training_data and training_data[f] is not None:
                td[f] = str(training_data[f])
        if "context" in training_data:
            td["context"] = training_data["context"]
        if "tags" in training_data and isinstance(training_data["tags"], list):
            td["tags"] = [str(x) for x in training_data["tags"]]
        if "quality_score" in training_data:
            td["quality_score"] = training_data["quality_score"]
        td["updated_at"] = datetime.now(timezone.utc)
        save_training_data(td)
        return {
            "message": "Training data updated successfully",
            "training_data": {
                "id": td["id"],
                "data_type": td["data_type"].lower(),
                "prompt": td["prompt"],
                "completion": td["completion"],
                "context": td.get("context"),
                "tags": td.get("tags", []),
                "quality_score": td.get("quality_score"),
                "source": td.get("source"),
                "created_at": td["created_at"],
                "updated_at": td["updated_at"],
            },
        }

    async def delete_training_data(self, training_id: str) -> Dict[str, Any]:
        delete_training_data(training_id)
        return {"id": training_id, "message": "Training data deleted successfully"}

    async def export_training_data(self) -> Dict[str, Any]:
        data = list_training_data()
        json_export = []
        jsonl_export = []
        for td in data:
            json_export.append(
                {
                    "id": td["id"],
                    "data_type": td["data_type"].lower(),
                    "prompt": td["prompt"],
                    "completion": td["completion"],
                    "context": td.get("context"),
                    "tags": td.get("tags", []),
                    "quality_score": td.get("quality_score"),
                    "source": td.get("source"),
                    "created_at": td["created_at"],
                    "updated_at": td["updated_at"],
                }
            )
            jsonl_export.append(
                {
                    "messages": [{"role": "user", "content": td["prompt"]}, {"role": "assistant", "content": td["completion"]}],
                    "context": td.get("context"),
                    "tags": td.get("tags", []),
                    "quality_score": td.get("quality_score"),
                    "source": td.get("source"),
                }
            )
        return {
            "message": "Training data exported successfully",
            "total_entries": len(data),
            "exports": {"json": json_export, "jsonl": jsonl_export},
            "formats": ["json", "jsonl", "csv"],
            "note": "CSV format requires additional implementation",
        }

    async def get_training_stats(self) -> Dict[str, Any]:
        data = list_training_data()
        by_dtype: Dict[str, int] = {}
        by_source: Dict[str, int] = {}
        quality_scores: List[float] = []
        for td in data:
            by_dtype.setdefault(td["data_type"].lower(), 0)
            by_dtype[td["data_type"].lower()] += 1
            src = td.get("source", "api")
            by_source.setdefault(src, 0)
            by_source[src] += 1
            if "quality_score" in td and td["quality_score"] is not None:
                quality_scores.append(float(td["quality_score"]))

        quality_distribution: Dict[str, int] = {"excellent": 0, "good": 0, "fair": 0, "poor": 0}
        for score in quality_scores:
            if score >= 0.9:
                quality_distribution["excellent"] += 1
            elif score >= 0.7:
                quality_distribution["good"] += 1
            elif score >= 0.5:
                quality_distribution["fair"] += 1
            else:
                quality_distribution["poor"] += 1
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        tags_used_count = len({tag for td in data for tag in td.get("tags", [])})

        return {
            "total_entries": len(data),
            "by_data_type": by_dtype,
            "by_source": by_source,
            "quality_distribution": quality_distribution,
            "average_quality_score": avg_quality,
            "quality_score_count": len(quality_scores),
            "tags_used": tags_used_count,
        }

    # Chat processing
    async def process_chat_message(self, chat_data: Dict[str, Any]) -> Dict[str, Any]:
        message = chat_data.get("message")
        if not message:
            raise ValueError("Missing 'message' field in chat data")
        content = process_chat_message_extended(str(message), "api_user")
        return {
            "message": "Chat processed successfully",
            "processed_message": message,
            "content": {
                "tasks": len(content["tasks"]),
                "memories": len(content["memories"]),
                "ideas": len(content["ideas"]),
                "agent_assignments": len(content["agent_assignments"]),
                "code_chunks": len(content["code_chunks"]),
            },
            "details": content,
        }

    async def chat_with_agent(self, agent_id: str, chat_data: Dict[str, Any]) -> Dict[str, Any]:
        message = chat_data.get("message")
        if not message:
            raise ValueError("Missing 'message' field in chat data")
        agent = load_agent(agent_id)
        content = process_chat_message_extended(str(message), agent_id)
        return {
            "agent_id": agent_id,
            "agent_name": agent["name"],
            "message": message,
            "response": {
                "tasks": len(content["tasks"]),
                "memories": len(content["memories"]),
                "ideas": len(content["ideas"]),
                "agent_assignments": len(content["agent_assignments"]),
                "code_chunks": len(content["code_chunks"]),
            },
            "content": content,
            "processed_at": datetime.now(timezone.utc),
        }

    async def get_chat_history(self) -> List[Dict[str, Any]]:
        tasks = self.storage.list_tasks_across_projects(TaskFilters())
        recent = sorted(tasks, key=lambda t: t.get("created_at") or datetime.min, reverse=True)[:10]
        return [
            {
                "id": f"chat_{t['id']}",
                "type": "task_created",
                "message": f"Task created: {t.get('action')}",
                "timestamp": t.get("created_at"),
                "data": {"task_id": t["id"], "action": t.get("action"), "status": t.get("status")},
            }
            for t in recent
        ]

    # Analytics
    async def get_task_analytics(self) -> Dict[str, Any]:
        tasks = self.storage.list_tasks_across_projects(TaskFilters())
        by_status: Dict[str, int] = {}
        by_priority: Dict[str, int] = {}
        by_assignee: Dict[str, int] = {}
        for t in tasks:
            by_status.setdefault(str(t.get("status", "unknown")).lower(), 0)
            by_status[str(t.get("status", "unknown")).lower()] += 1
            by_priority.setdefault(str(t.get("priority", "unknown")).lower(), 0)
            by_priority[str(t.get("priority", "unknown")).lower()] += 1
            assignee = t.get("assignee")
            by_assignee.setdefault(str(assignee).lower() if assignee else "unassigned", 0)
            by_assignee[str(assignee).lower() if assignee else "unassigned"] += 1
        completed = sum(1 for t in tasks if t.get("status") == "done")
        total = len(tasks)
        completion_rate = (completed / total) if total else 0.0
        now = datetime.now(timezone.utc)
        last_24h = sum(1 for t in tasks if self._hours_since(t.get("created_at")) <= 24)
        last_7d = sum(1 for t in tasks if self._days_since(t.get("created_at")) <= 7)
        return {
            "total_tasks": total,
            "by_status": by_status,
            "by_priority": by_priority,
            "by_assignee": by_assignee,
            "completion_rate": completion_rate,
            "completed_tasks": completed,
            "average_completion_time": "unknown",
            "recent_activity": {"last_24h": last_24h, "last_7d": last_7d},
        }

    def _hours_since(self, dt: Any) -> float:
        if not dt:
            return float("inf")
        try:
            return (datetime.now(timezone.utc) - dt).total_seconds() / 3600.0
        except Exception:
            return float("inf")

    def _days_since(self, dt: Any) -> float:
        if not dt:
            return float("inf")
        try:
            return (datetime.now(timezone.utc) - dt).days
        except Exception:
            return float("inf")

    async def get_agent_analytics(self) -> Dict[str, Any]:
        agents = list_agents()
        available = get_available_agents()
        by_category: Dict[str, int] = {}
        for a in agents:
            by_category.setdefault(a["metadata"]["category"], 0)
            by_category[a["metadata"]["category"]] += 1
        return {
            "total_agents": len(agents),
            "available_agents": len(available),
            "busy_agents": 0,
            "inactive_agents": 0,
            "by_category": by_category,
            "agent_statistics": {
                "total_assignments": 0,
                "completed_assignments": 0,
                "completion_rate": 0.0,
                "note": "Advanced agent statistics require assignment tracking implementation",
            },
        }

    async def get_performance_analytics(self) -> Dict[str, Any]:
        uptime = int(time.time())
        tasks = self.storage.list_tasks_across_projects(TaskFilters())
        agents = list_agents()
        active_sessions = get_active_sessions()
        backlog_items = list_backlog_items()
        return {
            "response_times": {"average_ms": 150, "p95_ms": 300, "p99_ms": 500},
            "throughput": {"requests_per_second": 10.0, "bytes_per_second": 10240},
            "error_rate": 0.01,
            "uptime_percentage": 99.9,
            "system_metrics": {
                "total_uptime_seconds": uptime,
                "active_connections": len(active_sessions),
                "total_tasks": len(tasks),
                "total_agents": len(agents),
                "backlog_items": len(backlog_items),
                "memory_usage_mb": 50,
                "cpu_usage_percent": 15.0,
            },
            "performance_score": {"overall": 85, "task_processing": 90, "agent_response": 80, "memory_efficiency": 95},
        }

    # Time tracking
    async def start_time_tracking(self, task_id: str) -> Dict[str, Any]:
        session_id = start_queue_session(task_id)
        return {
            "task_id": task_id,
            "session_id": session_id,
            "message": "Time tracking started successfully",
            "started_at": datetime.now(timezone.utc),
            "note": "Time tracking is implemented via queue sessions",
        }

    async def stop_time_tracking(self, task_id: str) -> Dict[str, Any]:
        active_sessions = get_active_sessions()
        sess = next((s for s in active_sessions if s.get("queue_item_id") == task_id), None)
        if not sess:
            return {"task_id": task_id, "message": "No active time tracking session found for this task", "error": "not_tracking"}
        session_id = sess["id"]
        end_queue_session(session_id)
        ended = get_queue_session(session_id)
        return {
            "task_id": task_id,
            "session_id": session_id,
            "message": "Time tracking stopped successfully",
            "stopped_at": ended["end_time"],
            "duration_seconds": ended["duration_seconds"],
        }

    async def get_time_tracking_report(self) -> Dict[str, Any]:
        items = list_queue_items()
        total_sessions = 0
        total_time = 0
        by_task: Dict[str, int] = {}
        by_date: Dict[str, int] = {}
        for it in items:
            if it.get("status") == "Complete":
                total_sessions += 1
                total_time += 3600
                by_task.setdefault(it.get("task_name", "unknown"), 0)
                by_task[it.get("task_name", "unknown")] += 1
                day = it.get("created_at").date().isoformat() if isinstance(it.get("created_at"), datetime) else str(it.get("created_at"))
                by_date.setdefault(day, 0)
                by_date[day] += 1
        total_items = len(items)
        completed = sum(1 for i in items if i.get("status") == "Complete")
        productivity = (completed / total_items * 100.0) if total_items else 0.0
        return {
            "total_sessions": total_sessions,
            "total_time_seconds": total_time,
            "total_time_hours": total_time / 3600.0,
            "by_task": by_task,
            "by_date": by_date,
            "productivity_score": productivity,
            "completion_stats": {
                "total_items": total_items,
                "completed_items": completed,
                "completion_rate": (completed / total_items) if total_items else 0.0,
            },
        }

    # Feelings
    async def get_all_feelings(self) -> List[Dict[str, Any]]:
        feelings = list_feelings()
        return [
            {
                "id": f["id"],
                "emotion": f["emotion"],
                "intensity": f["intensity"],
                "description": f["description"],
                "context": f.get("context", ""),
                "tags": f.get("tags", []),
                "created_at": f["created_at"],
                "updated_at": f["updated_at"],
            }
            for f in feelings
        ]

    async def create_feeling(self, feeling_data: Dict[str, Any]) -> Dict[str, Any]:
        emotion = feeling_data.get("emotion")
        intensity = feeling_data.get("intensity")
        description = feeling_data.get("description")
        if not emotion or not description:
            raise ValueError("Missing or invalid 'emotion' or 'description' field")
        if not isinstance(intensity, int) or not (1 <= intensity <= 10):
            raise ValueError("Missing or invalid 'intensity' field (must be 1-10)")
        context = feeling_data.get("context", "general")
        tags = feeling_data.get("tags", [])
        f = {
            "id": f"feeling_{int(time.time() * 1000)}",
            "emotion": str(emotion),
            "intensity": int(intensity),
            "description": str(description),
            "context": str(context),
            "tags": [str(t) for t in tags] if isinstance(tags, list) else [],
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        save_feeling(f)
        return {
            "message": "Feeling created successfully",
            "feeling": {
                "id": f["id"],
                "emotion": f["emotion"],
                "intensity": f["intensity"],
                "description": f["description"],
                "context": f["context"],
                "tags": f["tags"],
                "created_at": f["created_at"],
                "updated_at": f["updated_at"],
            },
        }

    async def get_feeling(self, feeling_id: str) -> Dict[str, Any]:
        f = load_feeling(feeling_id)
        return {
            "id": f["id"],
            "emotion": f["emotion"],
            "intensity": f["intensity"],
            "description": f["description"],
            "context": f.get("context", ""),
            "tags": f.get("tags", []),
            "created_at": f["created_at"],
            "updated_at": f["updated_at"],
        }

    async def update_feeling(self, feeling_id: str, feeling_data: Dict[str, Any]) -> Dict[str, Any]:
        f = load_feeling(feeling_id)
        if "emotion" in feeling_data:
            f["emotion"] = str(feeling_data["emotion"])
        if "intensity" in feeling_data and isinstance(feeling_data["intensity"], int) and 1 <= feeling_data["intensity"] <= 10:
            f["intensity"] = int(feeling_data["intensity"])
        if "description" in feeling_data:
            f["description"] = str(feeling_data["description"])
        if "context" in feeling_data:
            f["context"] = str(feeling_data["context"])
        if "tags" in feeling_data and isinstance(feeling_data["tags"], list):
            f["tags"] = [str(x) for x in feeling_data["tags"]]
        f["updated_at"] = datetime.now(timezone.utc)
        update_feeling(f)
        return {
            "message": "Feeling updated successfully",
            "feeling": {
                "id": f["id"],
                "emotion": f["emotion"],
                "intensity": f["intensity"],
                "description": f["description"],
                "context": f["context"],
                "tags": f["tags"],
                "created_at": f["created_at"],
                "updated_at": f["updated_at"],
            },
        }

    async def delete_feeling(self, feeling_id: str) -> Dict[str, Any]:
        delete_feeling(feeling_id)
        return {"id": feeling_id, "message": "Feeling deleted successfully"}

    # Queue
    async def create_queue_item(self, queue_data: Dict[str, Any]) -> Dict[str, Any]:
        task_name = queue_data.get("task_name")
        task_description = queue_data.get("task_description")
        priority_str = queue_data.get("priority")
        if not task_name or not task_description or not priority_str:
            raise ValueError("Missing 'task_name', 'task_description', or 'priority' field")
        # Minimal queue item
        item = {
            "id": f"q_{int(time.time() * 1000)}",
            "task_name": str(task_name),
            "task_description": str(task_description),
            "priority": str(priority_str),
            "project_id": queue_data.get("project_id"),
            "status": "Backlog",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
        add_queue_item(item)
        return {
            "message": "Queue item created successfully",
            "item": {
                "id": item["id"],
                "task_name": item["task_name"],
                "task_description": item["task_description"],
                "priority": item["priority"],
                "project_id": item["project_id"],
                "status": item["status"],
                "created_at": item["created_at"],
            },
        }

    async def get_all_queue_items(self) -> List[Dict[str, Any]]:
        items = list_queue_items()
        return [
            {
                "id": i["id"],
                "task_name": i["task_name"],
                "task_description": i["task_description"],
                "priority": i["priority"],
                "project_id": i.get("project_id"),
                "status": i["status"],
                "created_at": i["created_at"],
                "updated_at": i.get("updated_at"),
            }
            for i in items
        ]

    async def get_backlog_items(self) -> List[Dict[str, Any]]:
        items = list_backlog_items()
        return [
            {
                "id": i["id"],
                "task_name": i["task_name"],
                "task_description": i["task_description"],
                "priority": i["priority"],
                "project_id": i.get("project_id"),
                "status": i["status"],
                "created_at": i["created_at"],
                "updated_at": i.get("updated_at"),
            }
            for i in items
        ]

    async def get_active_items(self) -> List[Dict[str, Any]]:
        items = list_active_items()
        return [
            {
                "id": i["id"],
                "task_name": i["task_name"],
                "task_description": i["task_description"],
                "priority": i["priority"],
                "project_id": i.get("project_id"),
                "status": i["status"],
                "created_at": i["created_at"],
                "updated_at": i.get("updated_at"),
            }
            for i in items
        ]

    async def get_complete_items(self) -> List[Dict[str, Any]]:
        items = list_complete_items()
        return [
            {
                "id": i["id"],
                "task_name": i["task_name"],
                "task_description": i["task_description"],
                "priority": i["priority"],
                "project_id": i.get("project_id"),
                "status": i["status"],
                "created_at": i["created_at"],
                "updated_at": i.get("updated_at"),
            }
            for i in items
        ]

    async def start_queue_session(self, queue_item_id: str) -> Dict[str, Any]:
        session_id = start_queue_session(queue_item_id)
        return {"message": "Queue session started successfully", "session_id": session_id, "queue_item_id": queue_item_id, "started_at": datetime.now(timezone.utc)}

    async def end_queue_session(self, session_id: str) -> Dict[str, Any]:
        end_queue_session(session_id)
        sess = get_queue_session(session_id)
        return {
            "message": "Queue session ended successfully",
            "session_id": session_id,
            "queue_item_id": sess["queue_item_id"],
            "start_time": sess["start_time"],
            "end_time": sess["end_time"],
            "duration_seconds": sess["duration_seconds"],
        }

    # API Keys
    async def register_api_key(self) -> Dict[str, Any]:
        key = create_api_key()
        return {
            "message": "API key created successfully",
            "user_id": key["user_id"],
            "public_key": key["public_key"],
            "private_key": key["private_key"],
            "active": key["active"],
            "created_at": key["created_at"],
        }

    async def check_api_key(self, auth_data: Dict[str, Any]) -> Dict[str, Any]:
        public_key = auth_data.get("public_key")
        private_key = auth_data.get("private_key")
        if not public_key:
            raise ValueError("Missing 'public_key' field")
        user_id, is_admin = check_api_key_auth(public_key, private_key)
        return {
            "message": "API key authentication successful",
            "user_id": user_id,
            "public_key": public_key,
            "is_admin": is_admin,
            "access_level": "admin" if is_admin else "read_only",
        }

    # AI Endpoints
    async def get_task_insights(self, task_id: str) -> Dict[str, Any]:
        if not TDZ_ENABLE_TUI:
            return {
                "error": "Task insights require TUI feature enabled (TDZ_ENABLE_TUI=1)",
                "task_id": task_id,
                "available": False
            }
        embedding_config = {"model_name": "sentence-transformers/all-MiniLM-L6-v2"}
        embedding_service = TodoziEmbeddingService(embedding_config)
        await embedding_service.initialize()
        display_config = {"format": "json"}
        tui = TuiService(embedding_service, display_config)
        task_display = await tui.display_task(task_id)
        return {
            "task_id": task_display["task"]["id"],
            "action": task_display["task"]["action"],
            "ai_insights": {
                "confidence_score": task_display["confidence_score"],
                "similar_tasks": task_display["similar_tasks"],
                "ai_suggestions": task_display["ai_suggestions"],
                "semantic_tags": task_display["semantic_tags"],
                "related_content": task_display["related_content"],
            },
            "task_details": {
                "priority": task_display["task"]["priority"],
                "status": task_display["task"]["status"],
                "assignee": task_display["task"]["assignee"],
                "progress": task_display["task"]["progress"],
                "tags": task_display["task"]["tags"],
                "context_notes": task_display["task"]["context_notes"],
            },
        }

    async def get_similar_tasks(self, task_id: str) -> Dict[str, Any]:
        task = await self.get_task(task_id)
        action = task.get("action", "")
        embedding_config = {"model_name": "sentence-transformers/all-MiniLM-L6-v2"}
        embedding_service = TodoziEmbeddingService(embedding_config)
        await embedding_service.initialize()
        similar = await embedding_service.find_similar_tasks(action, 10)
        return {"task_id": task_id, "query": action, "similar_tasks": similar, "count": len(similar)}

    async def validate_task_with_ai(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        action = task_data.get("action", "")
        embedding_config = {"model_name": "sentence-transformers/all-MiniLM-L6-v2"}
        embedding_service = TodoziEmbeddingService(embedding_config)
        await embedding_service.initialize()
        similar = await embedding_service.find_similar_tasks(action, 5)
        validation_results: List[Dict[str, str]] = []
        if len(action) < 3:
            validation_results.append({"type": "error", "message": "Task action too short (minimum 3 characters)", "field": "action"})
        if len(action) > 200:
            validation_results.append({"type": "warning", "message": "Task action very long (consider breaking into smaller tasks)", "field": "action"})
        ai_suggestions: List[Dict[str, Any]] = []
        if similar:
            ai_suggestions.append(
                {
                    "type": "suggestion",
                    "message": f"Found {len(similar)} similar tasks - consider reviewing for duplicates",
                    "similar_tasks": similar,
                }
            )
        return {"valid": len(validation_results) == 0, "validation_results": validation_results, "ai_suggestions": ai_suggestions, "similar_tasks_found": len(similar)}

    async def get_ai_task_suggestions(self) -> Dict[str, Any]:
        embedding_config = {"model_name": "sentence-transformers/all-MiniLM-L6-v2"}
        embedding_service = TodoziEmbeddingService(embedding_config)
        await embedding_service.initialize()
        stats = await embedding_service.get_stats()
        clusters = await embedding_service.cluster_content()
        return {
            "suggestions": {
                "total_embeddings": stats.get("total_embeddings", 0),
                "semantic_clusters": len(clusters),
                "recommendations": [
                    "Consider grouping similar tasks together",
                    "Review task priorities based on semantic similarity",
                    "Look for potential task dependencies in similar content",
                ],
            },
            "clusters": clusters,
            "stats": stats,
        }

    async def semantic_search(self, query: str) -> Dict[str, Any]:
        if not query:
            return {"error": "Query parameter is required", "usage": "GET /semantic/search?q=your_search_query"}
        embedding_config = {"model_name": "sentence-transformers/all-MiniLM-L6-v2"}
        embedding_service = TodoziEmbeddingService(embedding_config)
        await embedding_service.initialize()
        results = await embedding_service.semantic_search(query, None, 20)
        return {"query": query, "results": results, "count": len(results), "search_type": "semantic"}

    async def get_ai_insights(self) -> Dict[str, Any]:
        embedding_config = {"model_name": "sentence-transformers/all-MiniLM-L6-v2"}
        embedding_service = TodoziEmbeddingService(embedding_config)
        await embedding_service.initialize()
        stats = await embedding_service.get_stats()
        clusters = await embedding_service.cluster_content()
        return {
            "ai_insights": {
                "embedding_statistics": stats,
                "semantic_clusters": clusters,
                "recommendations": {
                    "task_organization": "Consider grouping semantically similar tasks",
                    "priority_optimization": "Review task priorities based on AI confidence scores",
                    "dependency_detection": "Look for potential task dependencies in similar content",
                },
            },
            "system_status": {
                "embedding_model": embedding_config["model_name"],
                "similarity_threshold": 0.8,
                "max_results": 20,
            },
        }


# -------------------------
# Entry points
# -------------------------

async def start_server(host: Optional[str] = None, port: Optional[int] = None) -> None:
    config = ServerConfig(
        host=host or DEFAULT_HOST,
        port=port or DEFAULT_PORT,
        max_connections=100,
    )
    server = TodoziServer(config)
    await server.start()


async def example_usage() -> None:
    print("🚀 Starting Todozi Server on port 8636")
    await start_server(None, None)


# -------------------------
# Main
# -------------------------

if __name__ == "__main__":
    asyncio.run(example_usage())