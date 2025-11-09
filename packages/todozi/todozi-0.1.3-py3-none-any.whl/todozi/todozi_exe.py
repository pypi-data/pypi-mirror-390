"""
Python translation of the Rust Todozi executor with improvements based on feedback:
- Granular exception hierarchy (mirrors Rust ExecutorError variants)
- Proper singleton pattern (TodoziSystem)
- Configuration management via TodoziConfig
- Logging instead of print
- Resource management with aiohttp context manager
- API response validation
- Search result formatting
- Testability via dependency injection
- Efficient data structures (deque, set)
- Type hints and docstrings
"""

import asyncio
import json
import logging
import os
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Union

import aiohttp

# --------------------------------------------------------------------------------------
# Exceptions
# --------------------------------------------------------------------------------------

class ExecutorError(Exception):
    """Base exception for executor operations."""
    pass


class ExecutionError(ExecutorError):
    """General execution error."""
    pass


class BashToolError(ExecutorError):
    """Errors from external tool/Bash/API calls."""
    pass


class MissingParameterError(ExecutorError):
    """A required parameter is missing."""
    pass


class UnknownActionError(ExecutorError):
    """Action is not supported."""
    pass


# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------

@dataclass
class TodoziConfig:
    api_key: str = field(default_factory=lambda: os.getenv("TDZ_API_KEY", ""))
    base_url: str = field(default_factory=lambda: os.getenv("TDZ_BASE_URL", "https://todozi.com"))

    def validate(self) -> None:
        if not self.api_key:
            raise ExecutorError("TDZ_API_KEY required")


# --------------------------------------------------------------------------------------
# Data classes
# --------------------------------------------------------------------------------------

@dataclass
class SearchResult:
    content_id: str
    text_content: str


@dataclass
class ChatContent:
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    memories: List[Dict[str, Any]] = field(default_factory=list)
    ideas: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: Optional[str]
    metadata: Dict[str, Any] = field(default_factory=dict)
    tool_used: str = "todozi_simple"
    execution_type: str = "simple_interface"


# --------------------------------------------------------------------------------------
# Todozi API client
# --------------------------------------------------------------------------------------

class TodoziAPI:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def post(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                text = await resp.text()
                if resp.status != 200:
                    raise BashToolError(f"API request failed with status {resp.status}: {text}")
                # Validate response format
                try:
                    data = await resp.json()
                except Exception as e:
                    raise BashToolError(f"Failed to parse JSON response: {e}")

                if not isinstance(data, dict):
                    raise BashToolError(f"Invalid API response format: expected dict, got {type(data)}")
                return data


# --------------------------------------------------------------------------------------
# Global system (singleton)
# --------------------------------------------------------------------------------------

class TodoziSystem:
    _instance: Optional["TodoziSystem"] = None
    _lock = asyncio.Lock()

    def __init__(self) -> None:
        self.storage: Optional["Storage"] = None
        self.embedding_service: Optional[Any] = None
        self._initialized = False

    @classmethod
    async def get_instance(cls) -> "TodoziSystem":
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
                    await cls._instance.initialize()
        return cls._instance

    async def initialize(self) -> None:
        if self._initialized:
            return
        self.storage = Storage()
        try:
            from todozi.emb import TodoziEmbeddingService, TodoziEmbeddingConfig
            config = TodoziEmbeddingConfig()
            self.embedding_service = TodoziEmbeddingService(config)
            await self.embedding_service.initialize()
        except Exception:
            self.embedding_service = None
        self._initialized = True

    @property
    def storage_or_error(self) -> "Storage":
        if self.storage is None:
            raise ExecutionError("Todozi system storage not initialized")
        return self.storage


TDZ_SYSTEM: Optional[TodoziSystem] = None


async def ensure_todozi_system() -> None:
    global TDZ_SYSTEM
    if TDZ_SYSTEM is None:
        TDZ_SYSTEM = await TodoziSystem.get_instance()
    else:
        # Ensure single initialization even if created elsewhere
        await TDZ_SYSTEM.initialize()


def get_storage() -> "Storage":
    if TDZ_SYSTEM is None:
        raise ExecutionError("Todozi system not initialized")
    return TDZ_SYSTEM.storage_or_error


def get_embedding_service() -> Optional[Any]:
    if TDZ_SYSTEM is None:
        return None
    return TDZ_SYSTEM.embedding_service


# --------------------------------------------------------------------------------------
# Storage (in-memory) with efficient structures
# --------------------------------------------------------------------------------------

class Storage:
    def __init__(self) -> None:
        self._tasks: Dict[str, Dict[str, Any]] = {}
        self._ideas: Dict[str, Dict[str, Any]] = {}
        self._memories: Dict[str, Dict[str, Any]] = {}
        self._priority_queue: deque = deque()  # Faster append/pop for queue-like ops
        self._active_tasks: Set[str] = set()   # O(1) lookups
        self._next_ids: Dict[str, int] = {"task": 1, "idea": 1, "memory": 1}

    # Task operations
    def create_task(self, content: str, priority: str, assignee: str) -> str:
        tid = str(self._next_ids["task"])
        self._next_ids["task"] += 1
        task = {
            "id": tid,
            "content": content,
            "priority": priority,
            "assignee": assignee,
            "status": "backlog",
            "created_at": self._now_ts(),
        }
        self._tasks[tid] = task
        if priority in ("urgent", "high", "low"):
            self._priority_queue.append(tid)
        return tid

    def complete_task(self, task_id: str) -> bool:
        t = self._tasks.get(task_id)
        if not t:
            return False
        t["status"] = "completed"
        t["completed_at"] = self._now_ts()
        self._active_tasks.discard(task_id)
        return True

    def start_task(self, task_id: str) -> bool:
        t = self._tasks.get(task_id)
        if not t:
            return False
        t["status"] = "in_progress"
        t["started_at"] = self._now_ts()
        self._active_tasks.add(task_id)
        return True

    def get_backlog(self) -> List[Dict[str, Any]]:
        return [t for t in self._tasks.values() if t["status"] in ("backlog", "in_progress")]

    def get_active(self) -> List[Dict[str, Any]]:
        return [t for t in self._tasks.values() if t["status"] == "in_progress"]

    def list_queue_items(self) -> List[Dict[str, Any]]:
        return [self._tasks[tid] for tid in self._priority_queue if tid in self._tasks]

    # Memory operations
    def create_memory(self, content: str, extra: str, note: str, importance: str) -> str:
        mid = str(self._next_ids["memory"])
        self._next_ids["memory"] += 1
        mem = {
            "id": mid,
            "content": content,
            "extra": extra,
            "note": note,
            "importance": importance,
            "created_at": self._now_ts(),
        }
        self._memories[mid] = mem
        return mid

    def important_memory(self, content: str, extra: str, note: str) -> str:
        return self.create_memory(content, extra, note, importance="high")

    # Idea operations
    def create_idea(self, content: str, extra: Optional[str], note: Optional[str]) -> str:
        iid = str(self._next_ids["idea"])
        self._next_ids["idea"] += 1
        idea = {
            "id": iid,
            "content": content,
            "extra": extra or "",
            "note": note or "",
            "importance": "medium",
            "created_at": self._now_ts(),
        }
        self._ideas[iid] = idea
        return iid

    def breakthrough_idea(self, content: str) -> str:
        iid = str(self._next_ids["idea"])
        self._next_ids["idea"] += 1
        idea = {
            "id": iid,
            "content": content,
            "extra": "",
            "note": "",
            "importance": "breakthrough",
            "created_at": self._now_ts(),
        }
        self._ideas[iid] = idea
        return iid

    # Search operations (very simple, in-memory)
    def search_fast(self, query: str) -> List[SearchResult]:
        q = query.lower()
        res: List[SearchResult] = []
        for t in self._tasks.values():
            if q in t["content"].lower():
                res.append(SearchResult(content_id=t["id"], text_content=t["content"]))
        for m in self._memories.values():
            if q in m["content"].lower() or q in (m.get("extra") or "").lower():
                res.append(SearchResult(content_id=m["id"], text_content=m["content"]))
        for i in self._ideas.values():
            if q in i["content"].lower():
                res.append(SearchResult(content_id=i["id"], text_content=i["content"]))
        return res

    def search_ai(self, query: str) -> List[SearchResult]:
        # Simulate AI semantic search by returning everything
        res: List[SearchResult] = []
        for t in self._tasks.values():
            res.append(SearchResult(content_id=t["id"], text_content=t["content"]))
        for m in self._memories.values():
            res.append(SearchResult(content_id=m["id"], text_content=m["content"]))
        for i in self._ideas.values():
            res.append(SearchResult(content_id=i["id"], text_content=i["content"]))
        return res

    def search_smart(self, query: str) -> List[SearchResult]:
        # Hybrid: fast + results scored by length proximity
        candidates = self.search_fast(query)
        if not candidates:
            return []
        scored = [(len(c.text_content) - abs(len(c.text_content) - len(query)), c) for c in candidates]
        scored.sort(key=lambda x: x[0], reverse=True)
        return [c for _, c in scored]

    def search_find(self, query: str) -> List[SearchResult]:
        fast_results = self.search_fast(query)
        if not fast_results:
            return []
        query_lower = query.lower()
        query_words = set(query_lower.split())
        scored_results: List[tuple[float, SearchResult]] = []
        for result in fast_results:
            content_lower = result.text_content.lower()
            content_words = set(content_lower.split())
            word_match_score = len(query_words.intersection(content_words)) / max(len(query_words), 1)
            length_proximity = 1.0 / (1.0 + abs(len(result.text_content) - len(query)))
            position_bonus = 1.0 if content_lower.startswith(query_lower) else 0.5
            total_score = word_match_score * 0.5 + length_proximity * 0.3 + position_bonus * 0.2
            scored_results.append((total_score, result))
        scored_results.sort(key=lambda x: x[0], reverse=True)
        return [result for _, result in scored_results]

    # Chat processing (very naive extraction simulation)
    def process_chat(self, content: str) -> ChatContent:
        lines = [ln.strip() for ln in content.splitlines() if ln.strip()]
        tasks: List[Dict[str, Any]] = []
        memories: List[Dict[str, Any]] = []
        ideas: List[Dict[str, Any]] = []
        for ln in lines:
            if ln.lower().startswith("todo "):
                tasks.append({"action": ln[5:].strip()})
            elif ln.lower().startswith("remember "):
                memories.append({"content": ln[9:].strip()})
            elif ln.lower().startswith("idea "):
                ideas.append({"content": ln[5:].strip()})
        return ChatContent(tasks=tasks, memories=memories, ideas=ideas)

    # Stats
    def quick_stats(self) -> str:
        total = len(self._tasks)
        completed = sum(1 for t in self._tasks.values() if t["status"] == "completed")
        active = sum(1 for t in self._tasks.values() if t["status"] == "in_progress")
        backlog = total - completed - active
        return (
            f"Total tasks: {total}\n"
            f"Completed: {completed}\n"
            f"Active: {active}\n"
            f"Backlog: {backlog}\n"
            f"Ideas: {len(self._ideas)}\n"
            f"Memories: {len(self._memories)}"
        )

    @staticmethod
    def _now_ts() -> int:
        # Compatibility with event loop time; fallback to time.time if no loop
        try:
            return int(asyncio.get_event_loop().time())
        except RuntimeError:
            return int(time.time())


# --------------------------------------------------------------------------------------
# Helpers
# --------------------------------------------------------------------------------------

def _require_config() -> TodoziConfig:
    cfg = TodoziConfig()
    cfg.validate()
    return cfg


async def get_tdz_api_key() -> str:
    cfg = _require_config()
    return cfg.api_key


async def make_todozi_request(
    endpoint: str, payload: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> Dict[str, Any]:
    cfg = _require_config()
    client = api_client or TodoziAPI(base_url=cfg.base_url, api_key=cfg.api_key)
    return await client.post(endpoint, payload)


# --------------------------------------------------------------------------------------
# Search result formatting
# --------------------------------------------------------------------------------------

def format_search_results(results: List[SearchResult], limit: int = 10) -> str:
    """Format search results for user-friendly display."""
    if not results:
        return "No results found"
    trimmed = results[:limit]
    return "\n".join(
        f"• {r.text_content[:100]}... (ID: {r.content_id})" for r in trimmed
    )


# --------------------------------------------------------------------------------------
# Public async helpers (to mirror Rust Done/SearchResult usage)
# --------------------------------------------------------------------------------------

class Done:
    @staticmethod
    async def task(content: str) -> str:
        return get_storage().create_task(content, priority="normal", assignee="human")

    @staticmethod
    async def urgent(content: str) -> str:
        return get_storage().create_task(content, priority="urgent", assignee="human")

    @staticmethod
    async def high(content: str) -> str:
        return get_storage().create_task(content, priority="high", assignee="human")

    @staticmethod
    async def low(content: str) -> str:
        return get_storage().create_task(content, priority="low", assignee="human")

    @staticmethod
    async def ai(content: str) -> str:
        return get_storage().create_task(content, priority="normal", assignee="ai")

    @staticmethod
    async def human(content: str) -> str:
        return get_storage().create_task(content, priority="normal", assignee="human")

    @staticmethod
    async def collab(content: str) -> str:
        return get_storage().create_task(content, priority="normal", assignee="collaborative")

    @staticmethod
    async def tdz_find(query: str) -> List[SearchResult]:
        return get_storage().search_find(query)

    @staticmethod
    async def deep(query: str) -> List[SearchResult]:
        return get_storage().search_ai(query)

    @staticmethod
    async def fast(query: str) -> List[SearchResult]:
        return get_storage().search_fast(query)

    @staticmethod
    async def smart(query: str) -> List[SearchResult]:
        return get_storage().search_smart(query)

    @staticmethod
    async def create_memory(content: str, extra: str, note: str) -> Dict[str, Any]:
        mid = get_storage().create_memory(content, extra, note, importance="medium")
        return {"id": mid}

    @staticmethod
    async def important(content: str, extra: str, note: str) -> str:
        return get_storage().important_memory(content, extra, note)

    @staticmethod
    async def create_idea(content: str, extra: Optional[str]) -> Dict[str, Any]:
        iid = get_storage().create_idea(content, extra, None)
        return {"id": iid}

    @staticmethod
    async def breakthrough(content: str) -> str:
        return get_storage().breakthrough_idea(content)

    @staticmethod
    async def complete(task_id: str) -> bool:
        return get_storage().complete_task(task_id)

    @staticmethod
    async def begin(task_id: str) -> bool:
        return get_storage().start_task(task_id)

    @staticmethod
    async def quick() -> str:
        return get_storage().quick_stats()

    @staticmethod
    async def list_queue_items() -> List[Dict[str, Any]]:
        return get_storage().list_queue_items()

    @staticmethod
    async def backlog() -> List[Dict[str, Any]]:
        return get_storage().get_backlog()

    @staticmethod
    async def active() -> List[Dict[str, Any]]:
        return get_storage().get_active()

    @staticmethod
    async def chat(content: str) -> ChatContent:
        return get_storage().process_chat(content)


# --------------------------------------------------------------------------------------
# Content extraction and strategy wrappers
# --------------------------------------------------------------------------------------

async def extract_content(
    message: Optional[str],
    context: Optional[str],
    output_format: str,
    _: bool,
    api_client: Optional[TodoziAPI] = None,
) -> str:
    from todozi.extract import TodoziConfig, get_api_client, parse_extract_response, format_as_markdown, format_as_csv
    
    if not message:
        return "No content provided for planning."
    
    try:
        config = await TodoziConfig.load()
        async with get_api_client(config) as client:
            response_data = await client.extract_content(
                endpoint="extract",
                content=message,
                user_id=config.user_id,
                fingerprint=config.fingerprint,
            )
            response = parse_extract_response(response_data)
            
            if output_format == "json":
                return response.to_json()
            elif output_format == "csv":
                return format_as_csv(response)
            else:
                return format_as_markdown(response)
    except Exception as e:
        return f"Extraction failed: {e}"


async def strategy_content(
    message: Optional[str],
    context: Optional[str],
    output_format: str,
    _: bool,
    api_client: Optional[TodoziAPI] = None,
) -> str:
    from todozi.extract import TodoziConfig, get_api_client, parse_extract_response, format_as_markdown, format_as_csv
    
    if not message:
        return "No content provided for strategy."
    
    try:
        config = await TodoziConfig.load()
        async with get_api_client(config) as client:
            response_data = await client.extract_content(
                endpoint="strategy",
                content=message,
                user_id=config.user_id,
                fingerprint=config.fingerprint,
            )
            response = parse_extract_response(response_data)
            
            if output_format == "json":
                return response.to_json()
            elif output_format == "csv":
                return format_as_csv(response)
            else:
                return format_as_markdown(response)
    except Exception as e:
        return f"Strategy generation failed: {e}"


# --------------------------------------------------------------------------------------
# Entry point: enhanced Todozi tool integration (delegated)
# --------------------------------------------------------------------------------------

logger = logging.getLogger(__name__)


async def execute_todozi_tool_delegated(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    """
    Execute Todozi operations using enhanced simple interfaces.

    Args:
        params: Dictionary containing 'action' and action-specific parameters
        api_client: Optional API client for dependency injection/testing

    Returns:
        ExecutionResult with operation outcome

    Raises:
        ExecutorError: If operation fails
    """
    logger.info("🎯 Executing Todozi operation using enhanced simple interfaces")
    try:
        await ensure_todozi_system()
    except Exception as e:
        logger.warning("⚠️ Failed to initialize Todozi system: %s", e)

    action = params.get("action")
    if not isinstance(action, str):
        raise MissingParameterError("Missing parameter: action")
    logger.info("🎯 Todozi action: %s", action)

    handlers: Dict[str, Any] = {
        "task": execute_simple_task,
        "urgent": execute_urgent_task,
        "high": execute_high_task,
        "low": execute_low_task,
        "ai": execute_ai_task,
        "human": execute_human_task,
        "collab": execute_collab_task,
        "find": execute_find,
        "ai_search": execute_ai_search,
        "fast_search": execute_fast_search,
        "smart_search": execute_smart_search,
        "remember": execute_remember,
        "important_memory": execute_important_memory,
        "idea": execute_idea,
        "breakthrough_idea": execute_breakthrough_idea,
        "complete": execute_complete,
        "start": execute_start,
        "stats": execute_stats,
        "queue": execute_queue,
        "chat": execute_chat,
        "extract": execute_extract_api,
        "expand": execute_expand_api,
        "plan": execute_plan_api,
        "strategy": execute_strategy_api,
    }

    if action not in handlers:
        raise UnknownActionError(f"Unsupported Todozi action: {action}")

    return await handlers[action](params, api_client=api_client)


# --------------------------------------------------------------------------------------
# Action implementations
# --------------------------------------------------------------------------------------

async def execute_simple_task(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        task_id = await Done.task(content)
        return ExecutionResult(
            success=True,
            output=f"✅ Task created: {task_id}",
            error=None,
            metadata={
                "action": "task",
                "task_id": task_id,
                "execution_type": "simple_interface",
            },
            tool_used="todozi_simple",
            execution_type="easy_interface",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to create task: {e}")


async def execute_urgent_task(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        task_id = await Done.urgent(content)
        return ExecutionResult(
            success=True,
            output=f"🚨 Urgent task created: {task_id}",
            error=None,
            metadata={
                "action": "urgent",
                "task_id": task_id,
                "priority": "urgent",
            },
            tool_used="todozi_simple",
            execution_type="priority_interface",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to create urgent task: {e}")


async def execute_high_task(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        task_id = await Done.high(content)
        return ExecutionResult(
            success=True,
            output=f"🟠 High priority task created: {task_id}",
            error=None,
            metadata={
                "action": "high",
                "task_id": task_id,
                "priority": "high",
            },
            tool_used="todozi_simple",
            execution_type="priority_interface",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to create high priority task: {e}")


async def execute_low_task(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        task_id = await Done.low(content)
        return ExecutionResult(
            success=True,
            output=f"🟢 Low priority task created: {task_id}",
            error=None,
            metadata={
                "action": "low",
                "task_id": task_id,
                "priority": "low",
            },
            tool_used="todozi_simple",
            execution_type="priority_interface",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to create low priority task: {e}")


async def execute_ai_task(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        task_id = await Done.ai(content)
        return ExecutionResult(
            success=True,
            output=f"🤖 AI task queued: {task_id} (available for Maestro/Claude/etc.)",
            error=None,
            metadata={
                "action": "ai",
                "task_id": task_id,
                "assignee": "ai",
                "queued_for": "external_ai_systems",
            },
            tool_used="todozi_simple",
            execution_type="ai_assignment",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to create AI task: {e}")


async def execute_human_task(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        task_id = await Done.human(content)
        return ExecutionResult(
            success=True,
            output=f"👤 Human task created: {task_id} (visible in TUI)",
            error=None,
            metadata={
                "action": "human",
                "task_id": task_id,
                "assignee": "human",
                "visible_in": "tui_interface",
            },
            tool_used="todozi_simple",
            execution_type="human_assignment",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to create human task: {e}")


async def execute_collab_task(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        task_id = await Done.collab(content)
        return ExecutionResult(
            success=True,
            output=f"🤝 Collaborative task created: {task_id} (AI+Human coordination)",
            error=None,
            metadata={
                "action": "collab",
                "task_id": task_id,
                "assignee": "collaborative",
                "coordination": "ai_human",
            },
            tool_used="todozi_simple",
            execution_type="collaborative_assignment",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to create collaborative task: {e}")


async def execute_find(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        results = await Done.tdz_find(content)
        return ExecutionResult(
            success=True,
            output="🔍 Smart search results:\n" + format_search_results(results),
            error=None,
            metadata={
                "action": "find",
                "query": content,
                "search_type": "ai_plus_keyword",
            },
            tool_used="todozi_simple",
            execution_type="smart_search",
        )
    except Exception as e:
        raise ExecutionError(f"Search failed: {e}")


async def execute_ai_search(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        results = await Done.deep(content)
        return ExecutionResult(
            success=True,
            output="🤖 AI semantic search results:\n" + format_search_results(results),
            error=None,
            metadata={
                "action": "ai_search",
                "query": content,
                "search_type": "semantic_only",
                "results_count": len(results),
            },
            tool_used="todozi_simple",
            execution_type="semantic_search",
        )
    except Exception as e:
        raise ExecutionError(f"AI search failed: {e}")


async def execute_fast_search(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        results = await Done.fast(content)
        return ExecutionResult(
            success=True,
            output="⚡ Fast search results:\n" + format_search_results(results),
            error=None,
            metadata={
                "action": "fast_search",
                "query": content,
                "search_type": "keyword_only",
            },
            tool_used="todozi_simple",
            execution_type="fast_search",
        )
    except Exception as e:
        raise ExecutionError(f"Fast search failed: {e}")


async def execute_smart_search(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        results = await Done.smart(content)
        return ExecutionResult(
            success=True,
            output="🧠 Smart intent search results:\n" + format_search_results(results),
            error=None,
            metadata={
                "action": "smart_search",
                "query": content,
                "search_type": "intent_aware",
            },
            tool_used="todozi_simple",
            execution_type="intent_search",
        )
    except Exception as e:
        raise ExecutionError(f"Smart search failed: {e}")


async def execute_remember(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    extra = _opt_str(params, "extra") or content
    try:
        mem = await Done.create_memory(content, extra, "Created via simple interface")
        memory_id = mem["id"]
        return ExecutionResult(
            success=True,
            output=f"🧠 Memory saved: {memory_id}",
            error=None,
            metadata={
                "action": "remember",
                "memory_id": memory_id,
                "importance": "medium",
            },
            tool_used="todozi_simple",
            execution_type="memory_creation",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to save memory: {e}")


async def execute_important_memory(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    extra = _opt_str(params, "extra") or content
    try:
        memory_id = await Done.important(content, extra, "Important via simple interface")
        return ExecutionResult(
            success=True,
            output=f"🧠⭐ Important memory saved: {memory_id}",
            error=None,
            metadata={
                "action": "important_memory",
                "memory_id": memory_id,
                "importance": "high",
            },
            tool_used="todozi_simple",
            execution_type="important_memory",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to save important memory: {e}")


async def execute_idea(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        idea = await Done.create_idea(content, None)
        idea_id = idea["id"]
        return ExecutionResult(
            success=True,
            output=f"💡 Idea saved: {idea_id}",
            error=None,
            metadata={
                "action": "idea",
                "idea_id": idea_id,
                "importance": "medium",
            },
            tool_used="todozi_simple",
            execution_type="idea_creation",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to save idea: {e}")


async def execute_breakthrough_idea(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        idea_id = await Done.breakthrough(content)
        return ExecutionResult(
            success=True,
            output=f"💡🚀 Breakthrough idea saved: {idea_id}",
            error=None,
            metadata={
                "action": "breakthrough_idea",
                "idea_id": idea_id,
                "importance": "breakthrough",
            },
            tool_used="todozi_simple",
            execution_type="breakthrough_idea",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to save breakthrough idea: {e}")


async def execute_complete(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    task_id = _req_str(params, "content")
    try:
        ok = await Done.complete(task_id)
        if ok:
            return ExecutionResult(
                success=True,
                output=f"✅ Task {task_id} marked as completed",
                error=None,
                metadata={
                    "action": "complete",
                    "task_id": task_id,
                    "status": "completed",
                },
                tool_used="todozi_simple",
                execution_type="task_completion",
            )
        else:
            raise ExecutionError("Task not found")
    except Exception as e:
        raise ExecutionError(f"Failed to complete task: {e}")


async def execute_start(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    task_id = _req_str(params, "content")
    try:
        ok = await Done.begin(task_id)
        if ok:
            return ExecutionResult(
                success=True,
                output=f"🔄 Task {task_id} started",
                error=None,
                metadata={
                    "action": "start",
                    "task_id": task_id,
                    "status": "in_progress",
                },
                tool_used="todozi_simple",
                execution_type="task_start",
            )
        else:
            raise ExecutionError("Task not found")
    except Exception as e:
        raise ExecutionError(f"Failed to start task: {e}")


async def execute_stats(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    try:
        stats = await Done.quick()
        return ExecutionResult(
            success=True,
            output=f"📊 Todozi Stats:\n{stats}",
            error=None,
            metadata={
                "action": "stats",
                "stats_type": "quick_overview",
            },
            tool_used="todozi_simple",
            execution_type="stats_retrieval",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to get stats: {e}")


async def execute_queue(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    try:
        items = await Done.list_queue_items()
        backlog = await Done.backlog()
        active = await Done.active()
        return ExecutionResult(
            success=True,
            output=(
                f"📋 Queue Status:\n"
                f"  Total: {len(items)} items\n"
                f"  Backlog: {len(backlog)} items\n"
                f"  Active: {len(active)} items"
            ),
            error=None,
            metadata={
                "action": "queue",
                "total_items": len(items),
                "backlog_items": len(backlog),
                "active_items": len(active),
            },
            tool_used="todozi_simple",
            execution_type="queue_status",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to get queue status: {e}")


async def execute_chat(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    try:
        chat = await Done.chat(content)
        results: List[str] = []
        metadata: Dict[str, Any] = {"action": "chat"}
        if chat.tasks:
            results.append(f"📋 Created {len(chat.tasks)} tasks")
            metadata["tasks_created"] = len(chat.tasks)
        if chat.memories:
            results.append(f"🧠 Created {len(chat.memories)} memories")
            metadata["memories_created"] = len(chat.memories)
        if chat.ideas:
            results.append(f"💡 Created {len(chat.ideas)} ideas")
            metadata["ideas_created"] = len(chat.ideas)
        summary = (
            "✅ Chat processed - no structured content extracted"
            if not results
            else f"✅ Chat processed: {', '.join(results)}"
        )
        metadata["total_items"] = len(results)
        return ExecutionResult(
            success=True,
            output=summary,
            error=None,
            metadata=metadata,
            tool_used="todozi_simple",
            execution_type="chat_processing",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to process chat: {e}")


async def execute_extract_api(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    extra = _opt_str(params, "extra") or ""
    payload = {"message": content, "context": extra}
    try:
        response = await make_todozi_request("/api/todozi/extract", payload, api_client=api_client)
        results: List[str] = []
        if "extracted_content" in response:
            extracted = response["extracted_content"]
            if "tasks" in extracted and isinstance(extracted["tasks"], list):
                tasks = extracted["tasks"]
                results.append(f"📋 Extracted {len(tasks)} tasks")
                for i, t in enumerate(tasks, start=1):
                    act = t.get("action") if isinstance(t, dict) else str(t)
                    results.append(f"{i}. {act}")
            if "memories" in extracted and isinstance(extracted["memories"], list):
                results.append(f"🧠 Created {len(extracted['memories'])} memories")
            if "ideas" in extracted and isinstance(extracted["ideas"], list):
                results.append(f"💡 Generated {len(extracted['ideas'])} ideas")
        out = "\n".join(results) if results else "✅ Message processed successfully - no structured content extracted"
        return ExecutionResult(
            success=True,
            output=out,
            error=None,
            metadata={
                "action": "extract",
                "execution_type": "todozi_com_api",
            },
            tool_used="todozi_api",
            execution_type="ai_extraction",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to extract tasks: {e}")


async def execute_expand_api(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    extra = _opt_str(params, "extra") or ""
    tasks_array = [content]
    payload = {"tasks": tasks_array, "context": extra}
    try:
        response = await make_todozi_request("/api/todozi/expand", payload, api_client=api_client)
        if "expanded_tasks" in response:
            expanded = response["expanded_tasks"]
            if isinstance(expanded, list):
                expanded_tasks = [str(x) for x in expanded]
                if not expanded_tasks:
                    output = "🤖 No task expansion generated"
                else:
                    task_list = "\n".join(f"{i + 1}. {t}" for i, t in enumerate(expanded_tasks))
                    output = f"🚀 Expanded into {len(expanded_tasks)} detailed tasks:\n{task_list}"
                return ExecutionResult(
                    success=True,
                    output=output,
                    error=None,
                    metadata={
                        "action": "expand",
                        "execution_type": "todozi_com_api",
                        "tasks_created": len(expanded_tasks),
                    },
                    tool_used="todozi_api",
                    execution_type="ai_expansion",
                )
            else:
                raise ExecutionError("Invalid response format from API")
        else:
            raise ExecutionError("No expanded tasks in API response")
    except Exception as e:
        raise ExecutionError(f"Failed to expand tasks: {e}")


async def execute_plan_api(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    output_format = _opt_str(params, "output_format") or "json"
    extra = _opt_str(params, "extra")
    try:
        result = await extract_content(content, extra, output_format, False, api_client=api_client)
        return ExecutionResult(
            success=True,
            output=f"🎯 AI Project Planning Complete:\n{result}",
            error=None,
            metadata={
                "action": "plan",
                "execution_type": "todozi_plan_api",
                "output_format": output_format,
                "endpoint": "/api/tdz/plan",
            },
            tool_used="todozi_plan",
            execution_type="ai_project_planning",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to execute AI planning: {e}")


async def execute_strategy_api(
    params: Dict[str, Any], api_client: Optional[TodoziAPI] = None
) -> ExecutionResult:
    content = _req_str(params, "content")
    output_format = _opt_str(params, "output_format") or "json"
    extra = _opt_str(params, "extra")
    try:
        result = await strategy_content(content, extra, output_format, False, api_client=api_client)
        return ExecutionResult(
            success=True,
            output=f"🎭 AI Strategic Planning Complete:\n{result}",
            error=None,
            metadata={
                "action": "strategy",
                "execution_type": "todozi_strategy_api",
                "output_format": output_format,
                "endpoint": "/api/tdz/strategy",
            },
            tool_used="todozi_strategy",
            execution_type="ai_strategic_planning",
        )
    except Exception as e:
        raise ExecutionError(f"Failed to execute AI strategy: {e}")


# --------------------------------------------------------------------------------------
# Utilities
# --------------------------------------------------------------------------------------

def _req_str(params: Dict[str, Any], key: str) -> str:
    v = params.get(key)
    if v is None:
        raise MissingParameterError(f"Missing parameter: {key}")
    if isinstance(v, str):
        return v
    raise ExecutorError(f"Invalid parameter type for {key}, expected string")


def _opt_str(params: Dict[str, Any], key: str) -> Optional[str]:
    v = params.get(key)
    if v is None:
        return None
    if isinstance(v, str):
        return v
    return str(v)


# --------------------------------------------------------------------------------------
# Example: CLI entry (optional)
# --------------------------------------------------------------------------------------

if __name__ == "__main__":
    import logging

    logging.basicConfig(level=logging.INFO)

    async def _demo():
        # Example usage
        res = await execute_todozi_tool_delegated(
            {"action": "task", "content": "Write documentation for the executor translation"}
        )
        print(res.output)
        print(res.metadata)

    asyncio.run(_demo())
