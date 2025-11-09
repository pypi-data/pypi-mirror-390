"""
tool_defs.py

A complete, production‑ready Python translation of the Rust “tool” library.
Implements all original functionality and incorporates the requested improvements:
- ResourceLock enum with proper as_str() and display helpers
- ToolRegistryTrait interface and ToolRegistry implementation
- Robust type validation via ErrorHandler._is_valid_type()
- Serialization helpers (ToolParameter.to_dict, ToolDefinition.to_ollama_format)
- Sophisticated error handling (ErrorHandler.handle_error)
- Context manager support for ToolRegistry
- ToolDefinition.validate() for parameter definition consistency
- ToolConfig to make the library flexible
- Factory helpers mirroring the Rust create_* API
- Internal tests that match the Rust #[cfg(test)] block

The library works with plain dicts for JSON‑like data. All public symbols are
exposed in __all__ for drop‑in replacement.
"""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Type, Union, cast

# ---------------------------------------------------------------------------
# Logging – mirrors the Rust ``log`` crate.
# ---------------------------------------------------------------------------
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class ResourceLock(Enum):
    """
    Mirrors the Rust ResourceLock enum.

    - as_str() returns the snake_case value used in Rust.
    - display_name returns a PascalCase representation for __str__.
    """
    FILESYSTEM_WRITE = "filesystem_write"
    FILESYSTEM_READ = "filesystem_read"
    GIT = "git"
    MEMORY = "memory"
    SHELL = "shell"
    NETWORK = "network"

    @property
    def display_name(self) -> str:
        """Convert the enum name (e.g., FILESYSTEM_WRITE) to PascalCase."""
        return "".join(part.capitalize() for part in self.name.split("_"))

    def __str__(self) -> str:
        """Display as PascalCase."""
        return self.display_name

    def as_str(self) -> str:
        """Return the snake_case value (mirrors Rust as_str)."""
        return self.value


class ErrorType(Enum):
    """
    Mirrors ErrorType from the Rust crate.

    The __str__ implementation returns the snake_case name.
    """
    VALIDATION_ERROR = "validation_error"
    PERMISSION_ERROR = "permission_error"
    FILE_NOT_FOUND = "file_not_found"
    TIMEOUT_ERROR = "timeout_error"
    RESOURCE_ERROR = "resource_error"
    NETWORK_ERROR = "network_error"
    SECURITY_ERROR = "security_error"
    INTERNAL_ERROR = "internal_error"

    def __str__(self) -> str:
        return self.value


FILESYSTEM_READ = "filesystem_read"
FILESYSTEM_WRITE = "filesystem_write"
FILE_NOT_FOUND = "file_not_found"
GIT = "git"
INTERNAL_ERROR = "internal_error"
MEMORY = "memory"
NETWORK = "network"
NETWORK_ERROR = "network_error"
PERMISSION_ERROR = "permission_error"
RESOURCE_ERROR = "resource_error"
SECURITY_ERROR = "security_error"
SHELL = "shell"
TIMEOUT_ERROR = "timeout_error"
VALIDATION_ERROR = "validation_error"


# ---------------------------------------------------------------------------
# Value-object structs (dataclasses)
# ---------------------------------------------------------------------------

@dataclass
class ToolParameter:
    """Mirrors ToolParameter in Rust."""
    name: str
    type_: str               # Must be type_ because 'type' is a keyword.
    description: str
    required: bool = False
    default: Optional[Any] = None  # Holds any JSON‑compatible value.

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the ToolParameter to a JSON-friendly dict.
        Mirrors the Rust serde behaviour (type is emitted as "type").
        Omits fields that are None.
        """
        data = asdict(self)
        # Rename the internal field to 'type' to match JSON expectation.
        if "type_" in data:
            data["type"] = data.pop("type_")
        return {k: v for k, v in data.items() if v is not None}


@dataclass
class ToolDefinition:
    """Mirrors ToolDefinition."""
    name: str
    description: str
    parameters: List[ToolParameter] = field(default_factory=list)
    category: str = ""
    resource_locks: List[ResourceLock] = field(default_factory=list)

    def to_ollama_format(self) -> Dict[str, Any]:
        """
        Serialize the tool definition into the JSON structure expected by
        the Ollama LLM tool-call API.
        """
        properties: Dict[str, Dict[str, Any]] = {}
        required: List[str] = []

        for p in self.parameters:
            prop: Dict[str, Any] = {"type": p.type_, "description": p.description}
            if p.default is not None:
                prop["default"] = p.default
            if p.required:
                required.append(p.name)
            properties[p.name] = prop

        params_dict = {
            "type": "object",
            "properties": properties,
            "required": required,
        }

        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": params_dict,
            },
        }

    def validate(self) -> List[str]:
        """
        Validate the tool definition for consistency.
        Returns a list of error messages; empty list means validation passed.
        """
        errors: List[str] = []

        # Check for duplicate parameter names
        param_names = [p.name for p in self.parameters]
        if len(param_names) != len(set(param_names)):
            errors.append("Duplicate parameter names found")

        # Validate parameter types
        valid_types = {"string", "number", "boolean", "array", "object", "integer", "null"}
        for param in self.parameters:
            if param.type_ not in valid_types:
                errors.append(f"Invalid type '{param.type_}' for parameter '{param.name}'")

        return errors


@dataclass
class ToolResult:
    """
    Mirrors ToolResult. Includes serialization helper matching serde behavior.
    """
    success: bool
    output: str = ""
    error: Optional[str] = None
    execution_time_ms: int = 0
    metadata: Optional[Dict[str, Any]] = None
    recovery_context: Optional[Dict[str, Any]] = None

    @classmethod
    def success(cls, output: str, execution_time_ms: int = 0) -> "ToolResult":
        """Convenient constructor for a successful result."""
        return cls(success=True, output=output, execution_time_ms=execution_time_ms)

    @classmethod
    def error(cls, error: str, execution_time_ms: int = 0) -> "ToolResult":
        """Convenient constructor for a failed result."""
        return cls(success=False, output="", error=error, execution_time_ms=execution_time_ms)

    def __str__(self) -> str:
        """Display result – mirrors the Rust Display impl."""
        if self.success:
            return self.output
        return f"Error: {self.error or 'Unknown error'}"

    def to_dict(self, *, exclude_none: bool = True) -> Dict[str, Any]:
        """
        Convert the result to a plain dict suitable for json.dumps.
        If exclude_none is True, fields that are None are omitted to mirror the
        Rust skip_serializing_if attribute.
        """
        data = asdict(self)
        if exclude_none:
            return {k: v for k, v in data.items() if v is not None}
        return data


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class ToolError(Exception):
    """
    Mirrors ToolError – a custom exception that carries an ErrorType and
    optional detail map.
    """
    def __init__(
        self,
        message: str,
        error_type: ErrorType,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_type = error_type
        self.details = details or {}

    def __str__(self) -> str:
        return self.message


# ---------------------------------------------------------------------------
# Centralised error handling utilities
# ---------------------------------------------------------------------------

class ErrorHandler:
    """
    Mirrors the Rust ErrorHandler – static helpers that turn arbitrary
    exceptions into ToolResult objects with consistent categorization.
    """

    @staticmethod
    def _is_valid_type(value: Any, expected_type: str) -> bool:
        """
        More robust type validation for JSON-like data.
        Supports "integer" and "null" explicitly in addition to standard JSON types.
        """
        type_map = {
            "string": (str,),
            "number": (int, float),
            "boolean": (bool,),
            "array": (list,),
            "object": (dict,),
            "integer": (int,),
            "null": (type(None),),
        }

        if expected_type not in type_map:
            # Unknown or extended types are considered valid to avoid false positives.
            return True

        # Special case: value None is valid for 'null' and also acceptable for optional fields.
        if value is None and expected_type == "null":
            return True
        return isinstance(value, type_map[expected_type])

    @staticmethod
    def handle_error(error: BaseException, context: str) -> ToolResult:
        """
        Convert any exception into a ToolResult with sensible metadata.
        More specific error classification than the original translation.
        """
        metadata: Dict[str, Any] = {"context": context}

        # Specific error classification
        if isinstance(error, ToolError):
            metadata["error_type"] = str(error.error_type)
            if error.details:
                metadata.update(error.details)
            error_msg = str(error)
        elif isinstance(error, (OSError, IOError)):
            metadata["error_type"] = str(ErrorType.RESOURCE_ERROR)
            error_msg = f"I/O error: {error}"
        elif isinstance(error, TimeoutError):
            metadata["error_type"] = str(ErrorType.TIMEOUT_ERROR)
            error_msg = f"Timeout: {error}"
        else:
            metadata["error_type"] = str(ErrorType.INTERNAL_ERROR)
            metadata["exception_type"] = type(error).__name__
            error_msg = f"Unexpected error: {error}"

        logger.error("Tool error in %s: %s", context, error_msg)
        return ToolResult.error(error_msg, 0, metadata=metadata)

    @staticmethod
    def validate_required_params(
        kwargs: Dict[str, Any],
        required_params: List[str],
    ) -> Optional[ToolResult]:
        """Check that all required keys are present in kwargs."""
        missing = [p for p in required_params if p not in kwargs]
        if missing:
            err_msg = f"Missing required parameters: {', '.join(missing)}"
            metadata = {
                "error_type": str(ErrorType.VALIDATION_ERROR),
                "missing_params": missing,
            }
            return ToolResult(
                success=False,
                output="",
                error=err_msg,
                execution_time_ms=0,
                metadata=metadata,
            )
        return None

    @staticmethod
    def validate_string_param(
        value: Any,
        param_name: str,
        min_length: int,
        max_length: int,
        pattern: Optional[str] = None,
    ) -> Optional[ToolResult]:
        """Validate that value is a string and respects optional constraints."""
        if not isinstance(value, str):
            err_msg = f"Parameter '{param_name}' must be a string, got {type(value).__name__}"
            metadata = {
                "error_type": str(ErrorType.VALIDATION_ERROR),
                "param_name": param_name,
                "actual_type": type(value).__name__,
            }
            return ToolResult(
                success=False,
                output="",
                error=err_msg,
                execution_time_ms=0,
                metadata=metadata,
            )

        if len(value) < min_length:
            err_msg = (
                f"Parameter '{param_name}' must be at least {min_length} characters, "
                f"got {len(value)}"
            )
            metadata = {
                "error_type": str(ErrorType.VALIDATION_ERROR),
                "param_name": param_name,
                "actual_length": len(value),
                "min_length": min_length,
            }
            return ToolResult(
                success=False,
                output="",
                error=err_msg,
                execution_time_ms=0,
                metadata=metadata,
            )

        if len(value) > max_length:
            err_msg = (
                f"Parameter '{param_name}' must be at most {max_length} characters, "
                f"got {len(value)}"
            )
            metadata = {
                "error_type": str(ErrorType.VALIDATION_ERROR),
                "param_name": param_name,
                "actual_length": len(value),
                "max_length": max_length,
            }
            return ToolResult(
                success=False,
                output="",
                error=err_msg,
                execution_time_ms=0,
                metadata=metadata,
            )

        if pattern is not None:
            try:
                regex = re.compile(pattern)
            except re.error as e:
                err_msg = f"Invalid regex pattern for parameter '{param_name}': {e}"
                metadata = {
                    "error_type": str(ErrorType.VALIDATION_ERROR),
                    "param_name": param_name,
                    "pattern": pattern,
                    "pattern_error": str(e),
                }
                return ToolResult(
                    success=False,
                    output="",
                    error=err_msg,
                    execution_time_ms=0,
                    metadata=metadata,
                )
            if not regex.search(value):
                err_msg = f"Parameter '{param_name}' does not match required pattern"
                metadata = {
                    "error_type": str(ErrorType.VALIDATION_ERROR),
                    "param_name": param_name,
                    "pattern": pattern,
                }
                return ToolResult(
                    success=False,
                    output="",
                    error=err_msg,
                    execution_time_ms=0,
                    metadata=metadata,
                )
        return None

    @staticmethod
    def create_success_result(
        output: str,
        execution_time_ms: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """Factory for a successful ToolResult."""
        return ToolResult(
            success=True,
            output=output,
            execution_time_ms=execution_time_ms,
            metadata=metadata,
        )

    @staticmethod
    def create_error_result(
        error_msg: str,
        execution_time_ms: int,
        error_type: ErrorType,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ToolResult:
        """Factory for a failed ToolResult – always records the ErrorType."""
        result_metadata = dict(metadata or {})
        result_metadata["error_type"] = str(error_type)
        return ToolResult(
            success=False,
            output="",
            error=error_msg,
            execution_time_ms=execution_time_ms,
            metadata=result_metadata,
        )


# ---------------------------------------------------------------------------
# Tool abstraction
# ---------------------------------------------------------------------------

class Tool(ABC):
    """
    Abstract base class mirroring the Rust Tool trait.
    All concrete tools must implement definition and execute.
    """

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        ...

    @abstractmethod
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        ...

    @property
    def name(self) -> str:
        """Convenient shortcut – mirrors Rust fn name(&self) -> String."""
        return self.definition.name

    def validate_parameters(self, kwargs: Dict[str, Any]) -> bool:
        """
        Mirrors the Rust validate_parameters implementation.
        Checks required params and basic type assertions using improved validation.
        """
        definition = self.definition

        # 1️⃣ Required fields must be present.
        for p in definition.parameters:
            if p.required and p.name not in kwargs:
                return False

        # 2️⃣ Type checks for supplied arguments.
        for param_name, value in kwargs.items():
            param_def = next((p for p in definition.parameters if p.name == param_name), None)
            if param_def is None:
                continue  # Unknown arguments are ignored.

            # Special case in the original: ignore 'value' if its description says JSON-serializable.
            if param_name == "value" and "JSON-serializable" in param_def.description:
                continue

            # Use improved type validation
            if not ErrorHandler._is_valid_type(value, param_def.type_):
                return False
        return True


# ---------------------------------------------------------------------------
# Tool registry trait and implementation
# ---------------------------------------------------------------------------

class ToolRegistryTrait(ABC):
    """Interface mirroring Rust's ToolRegistryTrait."""
    @abstractmethod
    def has_tool(self, name: str) -> bool:
        pass


@dataclass
class ToolConfig:
    """Configuration for ToolRegistry behavior."""
    validate_parameters: bool = True
    strict_mode: bool = False
    default_timeout_ms: int = 30000


class ToolRegistry(ToolRegistryTrait):
    """
    Mirrors ToolRegistry – a container for Tool instances.
    Supports context manager usage, configuration, and robust operations.
    """

    def __init__(self, config: Optional[ToolConfig] = None) -> None:
        self._tools: Dict[str, Tool] = {}
        self.config = config or ToolConfig()

    # Context manager support
    def __enter__(self) -> "ToolRegistry":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.clear()

    # Registration
    def register(self, tool: Tool) -> None:
        """Register a concrete tool under its name."""
        self._tools[tool.name] = tool

    def register_core_tools(self) -> None:
        """
        Mirrors the Rust implementation – no built-in tools supplied,
        only a log entry. Real applications would import concrete tool
        classes and call register here.
        """
        logger.info(
            "Core tools registration structure prepared – individual tool "
            "implementations would be registered here"
        )

    # Querying
    def get_tool(self, name: str) -> Optional[Tool]:
        """Retrieve a tool by name (or None if not registered)."""
        return self._tools.get(name)

    def get_all_tools(self) -> List[Tool]:
        """Return a list view of all registered tools (order arbitrary)."""
        return list(self._tools.values())

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Produce the Ollama-style JSON for every registered tool."""
        return [tool.definition.to_ollama_format() for tool in self._tools.values()]

    # Execution
    async def execute_tool(
        self,
        tool_name: str,
        kwargs: Dict[str, Any],
    ) -> ToolResult:
        """
        Resolve, validate (if enabled), and run a tool asynchronously.
        Mirrors the Rust execute_tool implementation with config support.
        """
        tool = self.get_tool(tool_name)
        if tool is None:
            return ToolResult(
                success=False,
                output="",
                error=f"Tool '{tool_name}' not found",
                execution_time_ms=0,
            )

        if self.config.validate_parameters and not tool.validate_parameters(kwargs):
            return ToolResult(
                success=False,
                output="",
                error=f"Invalid parameters for tool '{tool_name}'",
                execution_time_ms=0,
            )

        return await tool.execute(kwargs)

    # House-keeping
    def tool_count(self) -> int:
        return len(self._tools)

    def has_tool(self, name: str) -> bool:
        return name in self._tools

    def unregister(self, name: str) -> bool:
        """Remove a tool; returns True if it was present."""
        return self._tools.pop(name, None) is not None

    def clear(self) -> None:
        self._tools.clear()


# ---------------------------------------------------------------------------
# Helper factories (mirrors Rust helper functions)
# ---------------------------------------------------------------------------

def create_tool_parameter(
    name: str,
    type_: str,
    description: str,
    required: bool,
) -> ToolParameter:
    """Factory for a ToolParameter without a default value."""
    return ToolParameter(name=name, type_=type_, description=description, required=required)


def create_tool_parameter_with_default(
    name: str,
    type_: str,
    description: str,
    required: bool,
    default: Any,
) -> ToolParameter:
    """Factory for a ToolParameter with a default JSON value."""
    return ToolParameter(name=name, type_=type_, description=description, required=required, default=default)


def create_tool_definition(
    name: str,
    description: str,
    category: str,
    parameters: List[ToolParameter],
) -> ToolDefinition:
    """Factory for a ToolDefinition without resource locks."""
    return ToolDefinition(
        name=name,
        description=description,
        parameters=parameters,
        category=category,
        resource_locks=[],
    )


def create_tool_definition_with_locks(
    name: str,
    description: str,
    category: str,
    parameters: List[ToolParameter],
    resource_locks: List[ResourceLock],
) -> ToolDefinition:
    """Factory for a ToolDefinition with resource-lock metadata."""
    return ToolDefinition(
        name=name,
        description=description,
        parameters=parameters,
        category=category,
        resource_locks=resource_locks,
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

__all__ = [
    "ToolParameter",
    "ResourceLock",
    "ToolDefinition",
    "ToolResult",
    "ErrorType",
    "ToolError",
    "ErrorHandler",
    "Tool",
    "ToolRegistryTrait",
    "ToolConfig",
    "ToolRegistry",
    "create_tool_parameter",
    "create_tool_parameter_with_default",
    "create_tool_definition",
    "create_tool_definition_with_locks",
]


# ---------------------------------------------------------------------------
# Tests (mirrors the Rust #[cfg(test)] block)
# ---------------------------------------------------------------------------

def test_tool_parameter_creation():
    param = create_tool_parameter("test", "string", "A test parameter", True)
    assert param.name == "test"
    assert param.type_ == "string"
    assert param.required is True


def test_tool_definition_ollama_format():
    param = create_tool_parameter("path", "string", "Path to file", True)
    definition = create_tool_definition(
        name="file_read",
        description="Read file contents",
        category="File Operations",
        parameters=[param],
    )
    ollama_format = definition.to_ollama_format()
    assert isinstance(ollama_format, dict)
    assert ollama_format["type"] == "function"
    assert "function" in ollama_format
    func = ollama_format["function"]
    assert func["name"] == "file_read"
    assert func["description"] == "Read file contents"
    assert "parameters" in func
    params = func["parameters"]
    assert params["type"] == "object"
    assert "properties" in params
    assert "path" in params["properties"]
    assert "required" in params
    assert "path" in params["required"]


def test_tool_registry_operations():
    registry = ToolRegistry()
    assert registry.tool_count() == 0
    assert not registry.has_tool("test_tool")


def test_error_handler_validation():
    kwargs = {"param1": "value1"}
    result = ErrorHandler.validate_required_params(kwargs, ["param1", "param2"])
    assert result is not None
    assert not result.success


def test_tool_result_display():
    success_result = ToolResult(success=True, output="Success output")
    assert str(success_result) == "Success output"
    error_result = ToolResult(success=False, output="", error="Error message")
    assert str(error_result) == "Error: Error message"


def test_tool_definition_validate():
    # Duplicate parameter names
    d1 = ToolDefinition(
        name="bad_tool",
        description="test",
        parameters=[
            ToolParameter(name="a", type_="string", description=""),
            ToolParameter(name="a", type_="number", description=""),
        ],
    )
    assert "Duplicate parameter names found" in d1.validate()

    # Invalid type
    d2 = ToolDefinition(
        name="bad_tool2",
        description="test",
        parameters=[ToolParameter(name="b", type_="uuid", description="")],
    )
    assert any("Invalid type 'uuid'" in e for e in d2.validate())


if __name__ == "__main__":
    test_tool_parameter_creation()
    test_tool_definition_ollama_format()
    test_tool_registry_operations()
    test_error_handler_validation()
    test_tool_result_display()
    test_tool_definition_validate()
    print("✅ All internal tests passed.")
