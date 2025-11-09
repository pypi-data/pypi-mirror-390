from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Dict, List, Set, Optional, Generic, TypeVar, Union
import re
from enum import Enum

# Simple Result/Ok/Err types to mirror Rust's Result<T, E>
T = TypeVar('T')
E = TypeVar('E')

class Ok(Generic[T]):
    def __init__(self, value: T):
        self.value = value

class Err(Generic[E]):
    def __init__(self, error: E):
        self.error = error

Result = Union[Ok[T], Err[E]]

class ChunkingLevel(Enum):
    """Represents the different levels of code chunking granularity."""
    PROJECT = "project"
    MODULE = "module"
    CLASS = "class"
    METHOD = "method"
    BLOCK = "block"

    def max_tokens(self) -> int:
        """Returns the maximum token count for this chunking level."""
        return {
            ChunkingLevel.PROJECT: 100,
            ChunkingLevel.MODULE: 500,
            ChunkingLevel.CLASS: 1000,
            ChunkingLevel.METHOD: 300,
            ChunkingLevel.BLOCK: 100
        }[self]

    def description(self) -> str:
        """Returns a description of this chunking level."""
        return {
            ChunkingLevel.PROJECT: "High-level project planning and architecture",
            ChunkingLevel.MODULE: "Major system components and interfaces",
            ChunkingLevel.CLASS: "Class definitions and major functions",
            ChunkingLevel.METHOD: "Individual methods and helper functions",
            ChunkingLevel.BLOCK: "Small code blocks and error handling"
        }[self]

    def example(self) -> str:
        """Returns an example use case for this chunking level."""
        return {
            ChunkingLevel.PROJECT: "Build web scraper with database storage",
            ChunkingLevel.MODULE: "Create database handler module",
            ChunkingLevel.CLASS: "Implement DatabaseConnection class",
            ChunkingLevel.METHOD: "Write insert_record method",
            ChunkingLevel.BLOCK: "Add error handling for connection timeout"
        }[self]

    def __str__(self) -> str:
        return self.value

    @classmethod
    def from_string(cls, s: str) -> 'ChunkingLevel':
        """Converts a string to a ChunkingLevel enum member."""
        s_lower = s.lower()
        for level in cls:
            if level.value == s_lower:
                return level
        raise ValueError(f"Invalid chunking level: {s}")


class ChunkStatus(Enum):
    """Represents the current status of a code chunk."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VALIDATED = "validated"
    FAILED = "failed"

    def __str__(self) -> str:
        return self.value


BLOCK = "block"
CLASS = "class"
COMPLETED = "completed"
FAILED = "failed"
IN_PROGRESS = "in_progress"
METHOD = "method"
MODULE = "module"
PENDING = "pending"
PROJECT = "project"
VALIDATED = "validated"


class TodoziError(Exception):
    """Base exception for the Todozi project."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


@dataclass
class ProjectState:
    """Manages the state of the overall project."""
    total_lines: int = 0
    max_lines: int = 0
    current_module: str = ""
    dependencies: List[str] = field(default_factory=list)
    completed_modules: Set[str] = field(default_factory=set)
    pending_modules: Set[str] = field(default_factory=set)
    global_variables: Dict[str, str] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)
        if self.updated_at.tzinfo is None:
            self.updated_at = self.updated_at.replace(tzinfo=timezone.utc)

    def to_state_string(self) -> str:
        """Returns a formatted string representation of the project state."""
        globals_str = ", ".join([f"{k}={v}" for k, v in self.global_variables.items()])
        return f"""<project_state>
- Total lines written: {self.total_lines}/{self.max_lines}
- Current module: {self.current_module}
- Dependencies: {", ".join(self.dependencies)}
- Completed modules: {", ".join(sorted(self.completed_modules))}
- Pending modules: {", ".join(sorted(self.pending_modules))}
- Global variables: {globals_str}
- Created: {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}
- Updated: {self.updated_at.strftime("%Y-%m-%d %H:%M:%S")}
</project_state>"""

    def add_completed_module(self, module: str) -> None:
        """Marks a module as completed."""
        if module not in self.completed_modules:
            self.completed_modules.add(module)
            self.updated_at = datetime.now(timezone.utc)

    def add_pending_module(self, module: str) -> None:
        """Marks a module as pending."""
        if module not in self.pending_modules:
            self.pending_modules.add(module)
            self.updated_at = datetime.now(timezone.utc)

    def set_global_variable(self, key: str, value: str) -> None:
        """Sets a global variable."""
        self.global_variables[key] = value
        self.updated_at = datetime.now(timezone.utc)

    def increment_lines(self, lines: int) -> None:
        """Increments the total line count."""
        self.total_lines += lines
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class ContextWindow:
    """Manages the context window for code generation."""
    previous_class: str = ""
    current_class: str = ""
    next_planned: str = ""
    global_vars_in_scope: List[str] = field(default_factory=list)
    imports_used: List[str] = field(default_factory=list)
    function_signatures: Dict[str, str] = field(default_factory=dict)
    error_patterns_seen: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self):
        if self.created_at.tzinfo is None:
            self.created_at = self.created_at.replace(tzinfo=timezone.utc)
        if self.updated_at.tzinfo is None:
            self.updated_at = self.updated_at.replace(tzinfo=timezone.utc)

    def to_context_string(self) -> str:
        """Returns a formatted string representation of the context window."""
        func_sigs = ", ".join([f"{k}: {v}" for k, v in self.function_signatures.items()])
        return f"""<context_window>
- Previous class: {self.previous_class}
- Current class: {self.current_class}
- Next planned: {self.next_planned}
- Global variables in scope: {", ".join(self.global_vars_in_scope)}
- Imports used: {", ".join(self.imports_used)}
- Function signatures: {func_sigs}
- Error patterns seen: {", ".join(self.error_patterns_seen)}
- Created: {self.created_at.strftime("%Y-%m-%d %H:%M:%S")}
- Updated: {self.updated_at.strftime("%Y-%m-%d %H:%M:%S")}
</context_window>"""

    def add_import(self, import_stmt: str) -> None:
        """Adds an import to the list of used imports."""
        if import_stmt not in self.imports_used:
            self.imports_used.append(import_stmt)
            self.updated_at = datetime.now(timezone.utc)

    def add_function_signature(self, name: str, signature: str) -> None:
        """Adds a function signature to the context."""
        self.function_signatures[name] = signature
        self.updated_at = datetime.now(timezone.utc)

    def add_error_pattern(self, pattern: str) -> None:
        """Adds an error pattern to the list of seen patterns."""
        if pattern not in self.error_patterns_seen:
            self.error_patterns_seen.append(pattern)
            self.updated_at = datetime.now(timezone.utc)

    def set_current_class(self, class_name: str) -> None:
        """Updates the current class and sets the previous class to the old current class."""
        self.previous_class = self.current_class
        self.current_class = class_name
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class CodeChunk:
    """Represents a single chunk of code with its metadata."""
    chunk_id: str
    status: ChunkStatus = ChunkStatus.PENDING
    dependencies: Set[str] = field(default_factory=set)
    code: str = ""
    tests: str = ""
    validated: bool = False
    level: ChunkingLevel = ChunkingLevel.BLOCK
    estimated_tokens: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def add_dependency(self, dep: str) -> None:
        """Adds a dependency to this chunk."""
        if dep not in self.dependencies:
            self.dependencies.add(dep)
            self.updated_at = datetime.now(timezone.utc)

    def set_code(self, code: str) -> None:
        """Sets the code and estimates the token count."""
        self.estimated_tokens = len(code.split())
        self.code = code
        self.updated_at = datetime.now(timezone.utc)

    def set_tests(self, tests: str) -> None:
        """Sets the test code."""
        self.tests = tests
        self.updated_at = datetime.now(timezone.utc)

    def mark_completed(self) -> None:
        """Marks the chunk as completed."""
        self.status = ChunkStatus.COMPLETED
        self.updated_at = datetime.now(timezone.utc)

    def mark_validated(self) -> None:
        """Marks the chunk as validated."""
        self.validated = True
        self.status = ChunkStatus.VALIDATED
        self.updated_at = datetime.now(timezone.utc)

    def mark_failed(self) -> None:
        """Marks the chunk as failed."""
        self.status = ChunkStatus.FAILED
        self.updated_at = datetime.now(timezone.utc)


@dataclass
class CodeGenerationGraph:
    """Manages the graph of code chunks and their dependencies."""
    project_state: ProjectState
    context_window: ContextWindow
    chunks: Dict[str, CodeChunk] = field(default_factory=dict)

    def __init__(self, max_lines: int = 0):
        # Initialize components using the provided parameters
        now = datetime.now(timezone.utc)
        self.project_state = ProjectState(
            total_lines=0,
            max_lines=max_lines,
            current_module="",
            dependencies=[],
            completed_modules=set(),
            pending_modules=set(),
            global_variables={},
            created_at=now,
            updated_at=now
        )
        self.context_window = ContextWindow(
            previous_class="",
            current_class="",
            next_planned="",
            global_vars_in_scope=[],
            imports_used=[],
            function_signatures={},
            error_patterns_seen=[],
            created_at=now,
            updated_at=now
        )
        self.chunks = {}

    def add_chunk(self, chunk_id: str, level: ChunkingLevel, deps: List[str]) -> None:
        """Adds a new chunk to the graph."""
        chunk = CodeChunk(chunk_id=chunk_id, level=level)
        for dep in deps:
            chunk.add_dependency(dep)
        self.chunks[chunk_id] = chunk

    def get_ready_chunks(self) -> List[str]:
        """
        Returns chunk IDs that have all dependencies satisfied.

        A chunk is ready when:
        - Its status is PENDING
        - All its dependencies are either COMPLETED or VALIDATED

        Returns:
            List of chunk IDs ready for processing
        """
        ready = []
        for chunk_id, chunk in self.chunks.items():
            if chunk.status == ChunkStatus.PENDING:
                deps_satisfied = all(
                    self.chunks.get(dep) and
                    self.chunks[dep].status in [ChunkStatus.COMPLETED, ChunkStatus.VALIDATED]
                    for dep in chunk.dependencies
                )
                if deps_satisfied:
                    ready.append(chunk_id)
        return ready

    def get_chunk(self, chunk_id: str) -> Optional[CodeChunk]:
        """Returns the chunk with the given ID, or None if not found."""
        return self.chunks.get(chunk_id)

    def get_chunk_mut(self, chunk_id: str) -> Optional[CodeChunk]:
        """Returns a mutable reference to the chunk with the given ID, or None if not found."""
        return self.chunks.get(chunk_id)

    def update_chunk_code(self, chunk_id: str, code: str) -> Result[None, str]:
        """Updates the code for the given chunk and increments the project line count."""
        chunk = self.get_chunk_mut(chunk_id)
        if chunk:
            chunk.set_code(code)
            # Match Rust behavior: code.lines().count()
            self.project_state.increment_lines(len(code.splitlines()))
            return Ok(None)
        return Err(f"Chunk {chunk_id} not found")

    def update_chunk_tests(self, chunk_id: str, tests: str) -> Result[None, str]:
        """Updates the tests for the given chunk."""
        chunk = self.get_chunk_mut(chunk_id)
        if chunk:
            chunk.set_tests(tests)
            return Ok(None)
        return Err(f"Chunk {chunk_id} not found")

    def mark_chunk_completed(self, chunk_id: str) -> Result[None, str]:
        """Marks the given chunk as completed and adds it to completed modules."""
        chunk = self.get_chunk_mut(chunk_id)
        if chunk:
            chunk.mark_completed()
            self.project_state.add_completed_module(chunk_id)
            return Ok(None)
        return Err(f"Chunk {chunk_id} not found")

    def mark_chunk_validated(self, chunk_id: str) -> Result[None, str]:
        """Marks the given chunk as validated."""
        chunk = self.get_chunk_mut(chunk_id)
        if chunk:
            chunk.mark_validated()
            return Ok(None)
        return Err(f"Chunk {chunk_id} not found")

    def get_project_summary(self) -> str:
        """Returns a formatted summary of the project state."""
        completed_count = sum(1 for c in self.chunks.values()
                            if c.status in [ChunkStatus.COMPLETED, ChunkStatus.VALIDATED])
        total_count = len(self.chunks)
        pending_count = sum(1 for c in self.chunks.values() if c.status == ChunkStatus.PENDING)
        in_progress_count = sum(1 for c in self.chunks.values() if c.status == ChunkStatus.IN_PROGRESS)

        return f"""<project_summary>
- Total chunks: {total_count}
- Completed: {completed_count}
- In progress: {in_progress_count}
- Pending: {pending_count}
- Project state: {self.project_state.to_state_string()}
- Context window: {self.context_window.to_context_string()}
</project_summary>"""

    def get_next_chunk_to_work_on(self) -> Optional[str]:
        """Returns the next chunk ID that should be worked on."""
        ready = self.get_ready_chunks()
        return ready[0] if ready else None

    def get_chunks_by_level(self, level: ChunkingLevel) -> List[CodeChunk]:
        """Returns a list of chunks at the specified level."""
        return [chunk for chunk in self.chunks.values() if chunk.level == level]

    def get_dependency_chain(self, chunk_id: str) -> List[str]:
        """Returns the dependency chain for the given chunk ID."""
        chain = []
        visited: Set[str] = set()
        self._build_dependency_chain(chunk_id, chain, visited)
        return chain

    def _build_dependency_chain(self, chunk_id: str, chain: List[str], visited: Set[str]) -> None:
        """Helper method to build the dependency chain recursively."""
        if chunk_id in visited:
            return
        visited.add(chunk_id)

        chunk = self.chunks.get(chunk_id)
        if chunk:
            for dep in chunk.dependencies:
                self._build_dependency_chain(dep, chain, visited)
            chain.append(chunk_id)


def parse_chunking_format(chunk_text: str) -> Result[CodeChunk, str]:
    """Parses a chunk from a formatted text string."""
    start_tag = "<chunk>"
    end_tag = "</chunk>"

    start = chunk_text.find(start_tag)
    if start == -1:
        return Err("Missing <chunk> start tag")

    end = chunk_text.find(end_tag)
    if end == -1:
        return Err("Missing </chunk> end tag")

    content = chunk_text[start + len(start_tag):end]
    parts = [part.strip() for part in content.split(';')]

    if len(parts) < 3:
        return Err("Invalid chunk format: need at least 3 parts (id; level; description)")

    chunk_id = parts[0]
    try:
        level = ChunkingLevel.from_string(parts[1])
    except ValueError as e:
        return Err(str(e))

    chunk = CodeChunk(chunk_id=chunk_id, level=level)

    if len(parts) > 3:
        dependencies = [dep.strip() for dep in parts[3].split(',') if dep.strip()]
        for dep in dependencies:
            chunk.add_dependency(dep)

    if len(parts) > 4:
        chunk.set_code(parts[4])

    return Ok(chunk)


def process_chunking_message(message: str) -> Result[List[CodeChunk], str]:
    """Processes a message and extracts chunks from it."""
    chunks = []
    pattern = r"<chunk>.*?</chunk>"
    regex = re.compile(pattern, re.DOTALL)

    for match in regex.finditer(message):
        chunk_text = match.group(0)
        match_result = parse_chunking_format(chunk_text)
        if isinstance(match_result, Ok):
            chunks.append(match_result.value)
        else:
            print(f"Warning: Failed to parse chunk: {match_result.error}")

    return Ok(chunks)


# Test functions
def test_chunking_levels():
    """Test the chunking level token limits."""
    assert ChunkingLevel.PROJECT.max_tokens() == 100
    assert ChunkingLevel.MODULE.max_tokens() == 500
    assert ChunkingLevel.CLASS.max_tokens() == 1000
    assert ChunkingLevel.METHOD.max_tokens() == 300
    assert ChunkingLevel.BLOCK.max_tokens() == 100
    print("Chunking level tests passed!")


def test_project_state():
    """Test the project state functionality."""
    state = ProjectState(max_lines=1000)
    state.add_completed_module("module1")
    state.add_pending_module("module2")
    state.set_global_variable("API_KEY", "secret123")

    assert len(state.completed_modules) == 1
    assert len(state.pending_modules) == 1
    assert len(state.global_variables) == 1
    print("Project state tests passed!")


def test_code_generation_graph():
    """Test the code generation graph functionality."""
    graph = CodeGenerationGraph(max_lines=1000)
    graph.add_chunk("chunk1", ChunkingLevel.MODULE, [])
    graph.add_chunk("chunk2", ChunkingLevel.CLASS, ["chunk1"])

    assert len(graph.chunks) == 2
    assert graph.get_ready_chunks() == ["chunk1"]
    print("Code generation graph tests passed!")


def test_parse_chunking_format():
    """Test the chunk parsing functionality."""
    chunk_text = "<chunk>chunk1; module; Create database handler; chunk0; import sqlite3</chunk>"
    chunk_result = parse_chunking_format(chunk_text)

    if isinstance(chunk_result, Err):
        assert False, f"Parsing failed: {chunk_result.error}"

    chunk = chunk_result.value
    assert chunk.chunk_id == "chunk1"
    assert chunk.level == ChunkingLevel.MODULE
    assert len(chunk.dependencies) == 1
    assert "chunk0" in chunk.dependencies
    print("Chunk parsing tests passed!")


if __name__ == "__main__":
    test_chunking_levels()
    test_project_state()
    test_code_generation_graph()
    test_parse_chunking_format()
    print("All tests passed!")
