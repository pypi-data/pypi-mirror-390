"""
Python translation of the provided Rust code for the Todozi client.

Key improvements over the previous version:
- Consistent error handling using a tiny Result[T, E] type.
- Safer parameter access with safe_get_param.
- Refactored endpoint mapping with a simple, configurable scheme.
- Input validation for commands.
- Logging for observability.
- Request timeout configuration for HTTP calls.
- Enum for HTTP methods, constants for defaults.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import re
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import aiohttp

logger = logging.getLogger(__name__)


# ---------- Error and Result types ----------

class TodoziError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class Result:
    """
    A tiny, idiomatic Result[T, E] type for Python.
    Usage:
        ok, value = Result.ok(42)
        err, value = Result.err("failed")
    """
    def __init__(self, is_ok: bool, value: Any):
        self._ok = is_ok
        self._value = value

    @staticmethod
    def ok(value: Any) -> "Result":
        return Result(True, value)

    @staticmethod
    def err(error: Any) -> "Result":
        return Result(False, error)

    @property
    def is_ok(self) -> bool:
        return self._ok

    @property
    def is_err(self) -> bool:
        return not self._ok

    def unwrap(self) -> Any:
        if self._ok:
            return self._value
        raise self._value

    def unwrap_or(self, default: Any) -> Any:
        if self._ok:
            return self._value
        return default

    def map_or(self, default: Any, f: Callable[[Any], Any]) -> Any:
        if self._ok:
            return f(self._value)
        return default

    def map_err(self, f: Callable[[Any], Any]) -> "Result":
        if self._ok:
            return self
        return Result.err(f(self._value))


# ---------- Enums and constants ----------

class HttpMethod(Enum):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"


DELETE = "DELETE"
GET = "GET"
PARAM = "param"
PARAMS_2 = "params_2"
POST = "POST"
PUT = "PUT"
QUERY = "query"
STATIC = "static"


DEFAULT_INTENSITY = 5
DEFAULT_TIMEOUT_TOTAL_SECONDS = 30


# ---------- Data models ----------

@dataclass
class TdzCommand:
    command: str
    target: str
    parameters: List[str]
    options: Dict[str, str]


# ---------- Utilities ----------

def safe_get_param(params: List[str], index: int, default: str = "") -> str:
    return params[index] if index < len(params) else default


def validate_command(command: TdzCommand) -> bool:
    required_fields = {"command", "target"}
    return all(hasattr(command, field) for field in required_fields)


# ---------- Config: Endpoint mappings ----------

class EndpointStyle(Enum):
    STATIC = auto()          # Just a path, e.g., "/tasks"
    PARAM = auto()           # One param appended, e.g., "/tasks/{p0}"
    PARAMS_2 = auto()        # Two params appended, e.g., "/feelings/{p0}/{p1}"
    QUERY = auto()           # One query param q, e.g., "/tasks/search?q={p0}"


@dataclass
class EndpointConfig:
    style: EndpointStyle
    path: str


class TodoziConfig:
    """
    Defines endpoint mappings. You can add or modify entries here to change behavior.
    """
    def __init__(self) -> None:
        self._endpoints: Dict[Tuple[str, str], EndpointConfig] = {
            ("list", "health"): EndpointConfig(EndpointStyle.STATIC, "/health"),
            ("get", "health"): EndpointConfig(EndpointStyle.STATIC, "/health"),
            ("list", "stats"): EndpointConfig(EndpointStyle.STATIC, "/stats"),
            ("run", "init"): EndpointConfig(EndpointStyle.STATIC, "/init"),

            ("list", "tasks"): EndpointConfig(EndpointStyle.STATIC, "/tasks"),
            ("get", "task"): EndpointConfig(EndpointStyle.PARAM, "/tasks/{p0}"),
            ("create", "task"): EndpointConfig(EndpointStyle.STATIC, "/tasks"),
            ("update", "task"): EndpointConfig(EndpointStyle.PARAM, "/tasks/{p0}"),
            ("delete", "task"): EndpointConfig(EndpointStyle.PARAM, "/tasks/{p0}"),

            ("search", "tasks"): EndpointConfig(EndpointStyle.QUERY, "/tasks/search?q={p0}"),

            ("list", "memories"): EndpointConfig(EndpointStyle.STATIC, "/memories"),
            ("list", "memories_secret"): EndpointConfig(EndpointStyle.STATIC, "/memories/secret"),
            ("list", "memories_human"): EndpointConfig(EndpointStyle.STATIC, "/memories/human"),
            ("list", "memories_short"): EndpointConfig(EndpointStyle.STATIC, "/memories/short"),
            ("list", "memories_long"): EndpointConfig(EndpointStyle.STATIC, "/memories/long"),
            ("create", "memory"): EndpointConfig(EndpointStyle.STATIC, "/memories"),

            ("list", "ideas"): EndpointConfig(EndpointStyle.STATIC, "/ideas"),
            ("create", "idea"): EndpointConfig(EndpointStyle.STATIC, "/ideas"),

            ("list", "agents"): EndpointConfig(EndpointStyle.STATIC, "/agents"),
            ("list", "agents_available"): EndpointConfig(EndpointStyle.STATIC, "/agents/available"),
            ("get", "agent"): EndpointConfig(EndpointStyle.PARAM, "/agents/{p0}"),
            ("get", "agent_status"): EndpointConfig(EndpointStyle.PARAM, "/agents/{p0}/status"),
            ("create", "agent"): EndpointConfig(EndpointStyle.STATIC, "/agents"),
            ("update", "agent"): EndpointConfig(EndpointStyle.PARAM, "/agents/{p0}"),
            ("delete", "agent"): EndpointConfig(EndpointStyle.PARAM, "/agents/{p0}"),
            ("run", "agent"): EndpointConfig(EndpointStyle.PARAM, "/chat/agent/{p0}"),

            ("list", "training"): EndpointConfig(EndpointStyle.STATIC, "/training"),
            ("get", "training"): EndpointConfig(EndpointStyle.PARAM, "/training/{p0}"),
            ("create", "training"): EndpointConfig(EndpointStyle.STATIC, "/training"),
            ("update", "training"): EndpointConfig(EndpointStyle.PARAM, "/training/{p0}"),
            ("delete", "training"): EndpointConfig(EndpointStyle.PARAM, "/training/{p0}"),
            ("run", "training_export"): EndpointConfig(EndpointStyle.STATIC, "/training/export"),
            ("list", "training_stats"): EndpointConfig(EndpointStyle.STATIC, "/training/stats"),

            ("run", "chat"): EndpointConfig(EndpointStyle.STATIC, "/chat/process"),
            ("list", "chat_history"): EndpointConfig(EndpointStyle.STATIC, "/chat/history"),

            ("list", "analytics_tasks"): EndpointConfig(EndpointStyle.STATIC, "/analytics/tasks"),
            ("list", "analytics_agents"): EndpointConfig(EndpointStyle.STATIC, "/analytics/agents"),
            ("list", "analytics_performance"): EndpointConfig(EndpointStyle.STATIC, "/analytics/performance"),

            ("run", "time_start"): EndpointConfig(EndpointStyle.PARAM, "/time/start/{p0}"),
            ("run", "time_stop"): EndpointConfig(EndpointStyle.PARAM, "/time/stop/{p0}"),
            ("list", "time_report"): EndpointConfig(EndpointStyle.STATIC, "/time/report"),

            ("list", "chunks"): EndpointConfig(EndpointStyle.STATIC, "/chunks"),
            ("list", "chunks_ready"): EndpointConfig(EndpointStyle.STATIC, "/chunks/ready"),
            ("list", "chunks_graph"): EndpointConfig(EndpointStyle.STATIC, "/chunks/graph"),
            ("create", "chunk"): EndpointConfig(EndpointStyle.STATIC, "/chunks"),

            ("list", "projects"): EndpointConfig(EndpointStyle.STATIC, "/projects"),
            ("create", "project"): EndpointConfig(EndpointStyle.STATIC, "/projects"),

            ("list", "feelings"): EndpointConfig(EndpointStyle.STATIC, "/feelings"),
            ("get", "feeling"): EndpointConfig(EndpointStyle.PARAM, "/feelings/{p0}"),
            ("create", "feeling"): EndpointConfig(EndpointStyle.STATIC, "/feelings"),
            ("update", "feeling"): EndpointConfig(EndpointStyle.PARAMS_2, "/feelings/{p0}/{p1}"),
            ("delete", "feeling"): EndpointConfig(EndpointStyle.PARAM, "/feelings/{p0}"),

            ("list", "errors"): EndpointConfig(EndpointStyle.STATIC, "/errors"),
            ("get", "error"): EndpointConfig(EndpointStyle.PARAM, "/errors/{p0}"),
            ("create", "error"): EndpointConfig(EndpointStyle.STATIC, "/errors"),
            ("update", "error"): EndpointConfig(EndpointStyle.PARAM, "/errors/{p0}"),
            ("delete", "error"): EndpointConfig(EndpointStyle.PARAM, "/errors/{p0}"),
            ("search", "errors"): EndpointConfig(EndpointStyle.QUERY, "/errors/search?q={p0}"),

            ("create", "queue_item"): EndpointConfig(EndpointStyle.STATIC, "/queue/plan"),
            ("list", "queue"): EndpointConfig(EndpointStyle.STATIC, "/queue/list"),
            ("list", "queue_backlog"): EndpointConfig(EndpointStyle.STATIC, "/queue/list/backlog"),
            ("list", "queue_active"): EndpointConfig(EndpointStyle.STATIC, "/queue/list/active"),
            ("list", "queue_complete"): EndpointConfig(EndpointStyle.STATIC, "/queue/list/complete"),
            ("run", "queue_start"): EndpointConfig(EndpointStyle.PARAM, "/queue/start/{p0}"),
            ("run", "queue_end"): EndpointConfig(EndpointStyle.PARAM, "/queue/end/{p0}"),

            ("run", "api_register"): EndpointConfig(EndpointStyle.STATIC, "/api/register"),
            ("run", "api_check"): EndpointConfig(EndpointStyle.STATIC, "/api/check"),
        }

    def get_endpoint(self, command: TdzCommand) -> str:
        key = (command.command, command.target)
        cfg = self._endpoints.get(key)
        if cfg is None:
            # Default to "/{target}"
            return f"/{command.target}"

        p0 = safe_get_param(command.parameters, 0, "")
        p1 = safe_get_param(command.parameters, 1, "")

        if cfg.style == EndpointStyle.STATIC:
            return cfg.path
        elif cfg.style == EndpointStyle.PARAM:
            return cfg.path.replace("{p0}", p0)
        elif cfg.style == EndpointStyle.PARAMS_2:
            return cfg.path.replace("{p0}", p0).replace("{p1}", p1)
        elif cfg.style == EndpointStyle.QUERY:
            # keep as-is; if p0 empty, results in "...?q="
            return cfg.path.replace("{p0}", p0)
        else:
            return f"/{command.target}"


# Global config instance
ENDPOINT_CONFIG = TodoziConfig()


# ---------- Core functions ----------

def find_todozi(s: Optional[str] = None) -> Optional[str]:
    home = os.getenv("HOME")
    if home is None:
        return None
    base = f"{home}/.todozi"
    if s is not None:
        return f"{base}/{s}"
    return base


def parse_tdz_command(text: str) -> Result[List[TdzCommand], TodoziError]:
    try:
        commands: List[TdzCommand] = []
        pattern = re.compile(r"<tdz>(.*?)</tdz>", re.DOTALL)
        for match in pattern.finditer(text):
            content = match.group(1).strip()
            parts = [part.strip() for part in content.split(";") if part.strip()]
            if not parts:
                continue

            command = parts[0].lower()
            target = parts[1].lower() if len(parts) > 1 else ""
            parameters: List[str] = []
            options: Dict[str, str] = {}
            for part in parts[2:]:
                if "=" in part:
                    key, value = part.split("=", 1)
                    options[key.lower()] = value
                else:
                    parameters.append(part)
            commands.append(TdzCommand(command, target, parameters, options))

        return Result.ok(commands)
    except re.error as e:
        return Result.err(TodoziError(f"Regex error: {e}"))


def get_endpoint_path(command: TdzCommand) -> str:
    return ENDPOINT_CONFIG.get_endpoint(command)


def build_request_body(command: TdzCommand) -> Result[dict, TodoziError]:
    target = command.target
    options = command.options

    def parse_int(value: str, default: int) -> int:
        try:
            return int(value)
        except Exception:
            return default

    def parse_float(value: str) -> Optional[float]:
        try:
            return float(value)
        except Exception:
            return None

    def split_tags(value: str) -> Optional[List[str]]:
        if not value:
            return None
        return [t.strip() for t in value.split(",") if t.strip()]

    if target == "task":
        return Result.ok({
            "action": options.get("action", ""),
            "time": options.get("time", ""),
            "priority": options.get("priority", ""),
            "project": options.get("project", ""),
            "status": options.get("status", ""),
            "assignee": options.get("assignee"),
            "tags": split_tags(options.get("tags", "")),
        })
    elif target == "memory":
        return Result.ok({
            "moment": options.get("moment", ""),
            "meaning": options.get("meaning", ""),
            "reason": options.get("reason", ""),
            "importance": options.get("importance", ""),
            "term": options.get("term", ""),
            "memory_type": options.get("memory_type", ""),
            "emotion": options.get("emotion"),
        })
    elif target == "idea":
        return Result.ok({
            "idea": options.get("idea", ""),
            "share": options.get("share", ""),
            "importance": options.get("importance", ""),
        })
    elif target == "agent":
        return Result.ok({
            "name": options.get("name", ""),
            "description": options.get("description", ""),
            "capabilities": split_tags(options.get("capabilities", "")),
        })
    elif target == "chunk":
        return Result.ok({
            "id": options.get("id", ""),
            "level": options.get("level", ""),
            "description": options.get("description", ""),
            "dependencies": split_tags(options.get("dependencies", "")),
            "code": options.get("code", ""),
        })
    elif target == "project":
        return Result.ok({
            "name": options.get("name", ""),
            "description": options.get("description", ""),
            "status": options.get("status", ""),
        })
    elif target == "feeling":
        intensity = parse_int(options.get("intensity", str(DEFAULT_INTENSITY)), DEFAULT_INTENSITY)
        return Result.ok({
            "emotion": options.get("emotion", ""),
            "intensity": intensity,
            "description": options.get("description", ""),
            "context": options.get("context"),
            "tags": split_tags(options.get("tags", "")),
        })
    elif target == "training":
        quality_score = parse_float(options.get("quality_score", "")) if options.get("quality_score") else None
        return Result.ok({
            "data_type": options.get("data_type", ""),
            "prompt": options.get("prompt", ""),
            "completion": options.get("completion", ""),
            "source": options.get("source", ""),
            "context": options.get("context"),
            "tags": split_tags(options.get("tags", "")),
            "quality_score": quality_score,
        })
    else:
        return Result.ok({})  # Empty JSON object for unknown targets to keep consistency


def build_run_body(command: TdzCommand) -> Result[dict, TodoziError]:
    target = command.target
    options = command.options

    if target == "agent":
        return Result.ok({
            "message": options.get("message", ""),
            "context": options.get("context"),
        })
    elif target == "chat":
        return Result.ok({
            "message": options.get("message", ""),
            "context": options.get("context"),
        })
    elif target in ("queue_start", "queue_end"):
        return Result.ok({})
    elif target == "api_check":
        return Result.ok({
            "public_key": options.get("public_key", ""),
            "private_key": options.get("private_key"),
        })
    else:
        return Result.ok({})


def _command_to_http_method(command: TdzCommand) -> Result[HttpMethod, TodoziError]:
    cmd = command.command
    if cmd in ("list", "get", "search"):
        return Result.ok(HttpMethod.GET)
    elif cmd == "create":
        return Result.ok(HttpMethod.POST)
    elif cmd == "update":
        return Result.ok(HttpMethod.PUT)
    elif cmd == "delete":
        return Result.ok(HttpMethod.DELETE)
    elif cmd in ("run", "execute"):
        return Result.ok(HttpMethod.POST)
    else:
        return Result.err(TodoziError(f"Unknown command: {cmd}"))


async def execute_tdz_command(
    command: TdzCommand,
    base_url: str,
    api_key: Optional[str] = None,
    timeout_total: float = DEFAULT_TIMEOUT_TOTAL_SECONDS,
) -> Result[dict, TodoziError]:
    # Basic input validation
    if not validate_command(command):
        return Result.err(TodoziError("Invalid command: missing required fields"))

    method_res = _command_to_http_method(command)
    if method_res.is_err:
        return method_res

    method = method_res.unwrap()
    url = f"{base_url.rstrip('/')}{get_endpoint_path(command)}"

    logger.debug(f"Executing {command.command} on {command.target} -> {method.value} {url}")

    headers: Dict[str, str] = {}
    if api_key is not None:
        headers["X-API-Key"] = api_key

    json_payload: Optional[dict] = None
    if method in (HttpMethod.POST, HttpMethod.PUT):
        if command.command in ("create", "update"):
            body_res = build_request_body(command)
            if body_res.is_err:
                return body_res
            json_payload = body_res.unwrap()
        elif command.command in ("run", "execute"):
            body_res = build_run_body(command)
            if body_res.is_err:
                return body_res
            json_payload = body_res.unwrap()

    timeout = aiohttp.ClientTimeout(total=timeout_total)

    try:
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.request(method.value, url, headers=headers, json=json_payload) as response:
                status = response.status
                if not (200 <= status < 300):
                    text = await response.text()
                    return Result.err(TodoziError(f"HTTP error {status}: {text}"))
                try:
                    data = await response.json()
                except aiohttp.ContentTypeError as e:
                    return Result.err(TodoziError(f"JSON parse error: {e}"))
                logger.debug(f"Response status {status} for {method.value} {url}")
                return Result.ok(data)
    except asyncio.TimeoutError as e:
        return Result.err(TodoziError(f"Request timeout: {e}"))
    except aiohttp.ClientError as e:
        return Result.err(TodoziError(f"Network error: {e}"))
    except Exception as e:
        return Result.err(TodoziError(f"Unexpected error: {e}"))


async def process_tdz_commands(
    text: str,
    base_url: str,
    api_key: Optional[str] = None,
    timeout_total: float = DEFAULT_TIMEOUT_TOTAL_SECONDS,
) -> Result[List[dict], TodoziError]:
    parse_res = parse_tdz_command(text)
    if parse_res.is_err:
        return parse_res

    commands = parse_res.unwrap()
    results: List[dict] = []
    for cmd in commands:
        exec_res = await execute_tdz_command(cmd, base_url, api_key, timeout_total=timeout_total)
        if exec_res.is_err:
            return exec_res
        results.append(exec_res.unwrap())

    return Result.ok(results)


# ---------- Example usage (uncomment to run) ----------
# if __name__ == "__main__":
#     logging.basicConfig(level=logging.DEBUG)
#
#     async def main():
#         text = "<tdz>list; tasks</tdz>"
#         res = await process_tdz_commands(text, base_url="https://api.example.com", api_key="your_key")
#         if res.is_ok:
#             print(res.unwrap())
#         else:
#             print("Error:", res.unwrap())
#
#     asyncio.run(main())
