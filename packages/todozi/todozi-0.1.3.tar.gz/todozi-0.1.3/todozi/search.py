from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    Union,
)


# =========================
# Domain enums and aliases
# =========================

class Status(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


class Priority(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class MemoryImportance(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class MemoryTerm(Enum):
    SHORT_TERM = "SHORT_TERM"
    LONG_TERM = "LONG_TERM"


class IdeaImportance(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class ShareLevel(Enum):
    PRIVATE = "PRIVATE"
    TEAM = "TEAM"
    PUBLIC = "PUBLIC"


class ErrorSeverity(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ErrorCategory(Enum):
    LOGIC = "LOGIC"
    RUNTIME = "RUNTIME"
    SYSTEM = "SYSTEM"
    NETWORK = "NETWORK"
    DATA = "DATA"


Assignee = str


CRITICAL = "CRITICAL"
DATA = "DATA"
DONE = "DONE"
ERRORS = "errors"
HIGH = "HIGH"
IDEAS = "ideas"
IN_PROGRESS = "IN_PROGRESS"
LOGIC = "LOGIC"
LONG_TERM = "LONG_TERM"
LOW = "LOW"
MEDIUM = "MEDIUM"
MEMORIES = "memories"
NETWORK = "NETWORK"
PRIVATE = "PRIVATE"
PUBLIC = "PUBLIC"
RUNTIME = "RUNTIME"
SHORT_TERM = "SHORT_TERM"
SYSTEM = "SYSTEM"
TASKS = "tasks"
TEAM = "TEAM"
TODO = "TODO"
TRAINING = "training"


# =========================
# Domain models
# =========================

@dataclass
class Task:
    action: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    assignee: Optional[Assignee] = None
    id: str = ""


@dataclass
class Memory:
    moment: str
    meaning: str
    reason: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    importance: Optional[MemoryImportance] = None
    term: Optional[MemoryTerm] = None
    id: str = ""


@dataclass
class Idea:
    idea: str
    context: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    share_level: Optional[ShareLevel] = None
    importance: Optional[IdeaImportance] = None
    id: str = ""


@dataclass
class Error:
    title: str
    description: str
    source: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    severity: Optional[ErrorSeverity] = None
    category: Optional[ErrorCategory] = None
    resolved: Optional[bool] = None
    context: Optional[str] = None
    id: str = ""


@dataclass
class TrainingData:
    prompt: str
    completion: str
    source: str
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    context: Optional[str] = None
    id: str = ""


# =========================
# ChatContent protocol interface
# =========================

class ChatContent(Protocol):
    tasks: Sequence[Task]
    memories: Sequence[Memory]
    ideas: Sequence[Idea]
    errors: Sequence[Error]
    training_data: Sequence[TrainingData]


# =========================
# Search enums and options
# =========================

class SearchDataType(Enum):
    TASKS = "TASKS"
    MEMORIES = "MEMORIES"
    IDEAS = "IDEAS"
    ERRORS = "ERRORS"
    TRAINING = "TRAINING"


@dataclass
class SearchOptions:
    """
    Options used to configure search behavior including filters and limits.

    Args:
        data_types: If provided, only these data types are included in results.
        since: If provided, only items created at or after this time are included.
        until: If provided, only items created at or before this time are included.
        limit: If provided, limit the number of results per data type.
        page: If provided (1-based), used with page_size to paginate results.
        page_size: If provided, enables pagination with the given page size.
    """
    data_types: Optional[List[SearchDataType]] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None
    limit: Optional[int] = None
    page: Optional[int] = None
    page_size: Optional[int] = None

    @staticmethod
    def default() -> SearchOptions:
        return SearchOptions(limit=50)


# =========================
# Result types (dataclasses for convenience and clarity)
# =========================

@dataclass
class TaskResult:
    task: Task
    score: float


@dataclass
class MemoryResult:
    memory: Memory
    score: float


@dataclass
class IdeaResult:
    idea: Idea
    score: float


@dataclass
class ErrorResult:
    error: Error
    score: float


@dataclass
class TrainingResult:
    training_data: TrainingData
    score: float


@dataclass
class SearchResults:
    task_results: List[TaskResult] = field(default_factory=list)
    memory_results: List[MemoryResult] = field(default_factory=list)
    idea_results: List[IdeaResult] = field(default_factory=list)
    error_results: List[ErrorResult] = field(default_factory=list)
    training_results: List[TrainingResult] = field(default_factory=list)

    def total_results(self) -> int:
        return (
            len(self.task_results)
            + len(self.memory_results)
            + len(self.idea_results)
            + len(self.error_results)
            + len(self.training_results)
        )

    def has_results(self) -> bool:
        return self.total_results() > 0


@dataclass
class SearchAnalytics:
    total_indexed_items: int
    tasks_count: int
    memories_count: int
    ideas_count: int
    errors_count: int
    training_count: int


# =========================
# Advanced search criteria
# =========================

@dataclass
class TaskSearchCriteria:
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    assignee: Optional[Assignee] = None
    required_tag: Optional[str] = None


@dataclass
class MemorySearchCriteria:
    importance: Optional[MemoryImportance] = None
    term: Optional[MemoryTerm] = None
    required_tag: Optional[str] = None


@dataclass
class IdeaSearchCriteria:
    share_level: Optional[ShareLevel] = None
    importance: Optional[IdeaImportance] = None
    required_tag: Optional[str] = None


@dataclass
class ErrorSearchCriteria:
    severity: Optional[ErrorSeverity] = None
    category: Optional[ErrorCategory] = None
    resolved: Optional[bool] = None
    required_tag: Optional[str] = None


@dataclass
class AdvancedSearchCriteria:
    task_criteria: TaskSearchCriteria = field(default_factory=TaskSearchCriteria)
    memory_criteria: MemorySearchCriteria = field(default_factory=MemorySearchCriteria)
    idea_criteria: IdeaSearchCriteria = field(default_factory=IdeaSearchCriteria)
    error_criteria: ErrorSearchCriteria = field(default_factory=ErrorSearchCriteria)


# =========================
# Search Engine
# =========================

class SearchEngine:
    """
    A simple in-memory search engine across tasks, memories, ideas, errors, and training data.

    The engine supports keyword search with relevance scoring, advanced structured filters,
    analytics, and suggestion generation.

    All public methods are documented; private methods are for internal use only.
    """

    # Configuration constants
    SCORE_EXACT_MATCH: float = 1.0
    SCORE_WORD_MATCH: float = 0.7
    SCORE_TAG_MATCH: float = 0.5
    MIN_KEYWORD_LENGTH: int = 3
    LENGTH_PENALTY_BASE: float = 100.0

    def __init__(self) -> None:
        self.tasks: List[Task] = []
        self.memories: List[Memory] = []
        self.ideas: List[Idea] = []
        self.errors: List[Error] = []
        self.training_data: List[TrainingData] = []
        self.tags: List[str] = []  # Not actively used, reserved for future indexing

    def update_index(self, content: ChatContent) -> None:
        """
        Merge a ChatContent payload into the search index.

        Args:
            content: An object implementing the ChatContent protocol with sequences
                     of domain models.

        Raises:
            TypeError: If content does not match the ChatContent protocol or its fields
                       are not sequences as expected.
        """
        if not hasattr(content, "tasks") or not isinstance(content.tasks, Sequence):
            raise TypeError("ChatContent.tasks must be a Sequence[Task]")
        if not hasattr(content, "memories") or not isinstance(content.memories, Sequence):
            raise TypeError("ChatContent.memories must be a Sequence[Memory]")
        if not hasattr(content, "ideas") or not isinstance(content.ideas, Sequence):
            raise TypeError("ChatContent.ideas must be a Sequence[Idea]")
        if not hasattr(content, "errors") or not isinstance(content.errors, Sequence):
            raise TypeError("ChatContent.errors must be a Sequence[Error]")
        if not hasattr(content, "training_data") or not isinstance(content.training_data, Sequence):
            raise TypeError("ChatContent.training_data must be a Sequence[TrainingData]")

        self.tasks.extend(content.tasks)
        self.memories.extend(content.memories)
        self.ideas.extend(content.ideas)
        self.errors.extend(content.errors)
        self.training_data.extend(content.training_data)

    def search(self, query: str, options: SearchOptions) -> SearchResults:
        """
        Perform a keyword-based search across all indexed content types.

        Args:
            query: Search query string.
            options: SearchOptions including filters, limit, and pagination.

        Returns:
            SearchResults object containing matching items sorted by relevance.
        """
        query_lower = query.lower()
        results = SearchResults()

        for task in self.tasks:
            if self._matches_query(query_lower, task.action, None, task.tags):
                score = self._calculate_relevance_score(query_lower, task.action, task.tags)
                results.task_results.append(TaskResult(task=task, score=score))

        for memory in self.memories:
            if self._matches_query(query_lower, memory.moment, memory.meaning, memory.tags) or \
               self._matches_query(query_lower, memory.reason, None, memory.tags):
                score = self._calculate_relevance_score(query_lower, memory.meaning, memory.tags)
                results.memory_results.append(MemoryResult(memory=memory, score=score))

        for idea in self.ideas:
            if self._matches_query(query_lower, idea.idea, idea.context, idea.tags):
                score = self._calculate_relevance_score(query_lower, idea.idea, idea.tags)
                results.idea_results.append(IdeaResult(idea=idea, score=score))

        for error in self.errors:
            if self._matches_query(query_lower, error.title, error.description, error.tags) or \
               self._matches_query(query_lower, error.source, error.context, error.tags):
                score = self._calculate_relevance_score(query_lower, error.title, error.tags)
                results.error_results.append(ErrorResult(error=error, score=score))

        for training in self.training_data:
            if self._matches_query(query_lower, training.prompt, training.completion, training.tags) or \
               self._matches_query(query_lower, training.source, training.context, training.tags):
                score = self._calculate_relevance_score(query_lower, training.prompt, training.tags)
                results.training_results.append(TrainingResult(training_data=training, score=score))

        # Filter by data types if provided
        if options.data_types is not None:
            allowed = set(options.data_types)
            if SearchDataType.TASKS not in allowed:
                results.task_results.clear()
            if SearchDataType.MEMORIES not in allowed:
                results.memory_results.clear()
            if SearchDataType.IDEAS not in allowed:
                results.idea_results.clear()
            if SearchDataType.ERRORS not in allowed:
                results.error_results.clear()
            if SearchDataType.TRAINING not in allowed:
                results.training_results.clear()

        # Filter by since/until (time range)
        if options.since is not None or options.until is not None:
            self._apply_time_filters(results, options.since, options.until)

        # Sort by score descending per data type
        results.task_results.sort(key=lambda r: r.score, reverse=True)
        results.memory_results.sort(key=lambda r: r.score, reverse=True)
        results.idea_results.sort(key=lambda r: r.score, reverse=True)
        results.error_results.sort(key=lambda r: r.score, reverse=True)
        results.training_results.sort(key=lambda r: r.score, reverse=True)

        # Apply limit per data type
        if options.limit is not None and options.limit > 0:
            limit = options.limit
            results.task_results = results.task_results[:limit]
            results.memory_results = results.memory_results[:limit]
            results.idea_results = results.idea_results[:limit]
            results.error_results = results.error_results[:limit]
            results.training_results = results.training_results[:limit]

        # Apply pagination if requested
        if options.page is not None and options.page_size is not None:
            self._apply_pagination(results, options.page, options.page_size)

        return results

    def _apply_time_filters(self, results: SearchResults, since: Optional[datetime], until: Optional[datetime]) -> None:
        cutoff_since = since
        cutoff_until = until

        def by_time(item: Any, field: str, inclusive: bool, is_upper: bool) -> bool:
            ts = getattr(item, field).created_at if hasattr(item, field) else getattr(item, field).created_at
            # Ensure timezone-awareness
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)
            if cutoff_since is not None and ts < cutoff_since:
                return False
            if cutoff_until is not None:
                if is_upper:
                    return ts <= cutoff_until if inclusive else ts < cutoff_until
            return True

        # Use in-place filtering via slice to avoid creating many intermediate lists
        if cutoff_since is not None or cutoff_until is not None:
            results.task_results[:] = [r for r in results.task_results if by_time(r, "task", True, True)]
            results.memory_results[:] = [r for r in results.memory_results if by_time(r, "memory", True, True)]
            results.idea_results[:] = [r for r in results.idea_results if by_time(r, "idea", True, True)]
            results.error_results[:] = [r for r in results.error_results if by_time(r, "error", True, True)]
            results.training_results[:] = [r for r in results.training_results if by_time(r, "training_data", True, True)]

    def _apply_pagination(self, results: SearchResults, page: int, page_size: int) -> None:
        """
        Apply simple pagination across all result types.

        Args:
            results: SearchResults to paginate in-place.
            page: 1-based page index.
            page_size: Number of items per page.
        """
        start = (max(page, 1) - 1) * page_size
        end = start + page_size
        results.task_results = results.task_results[start:end]
        results.memory_results = results.memory_results[start:end]
        results.idea_results = results.idea_results[start:end]
        results.error_results = results.error_results[start:end]
        results.training_results = results.training_results[start:end]

    def _matches_query(
        self,
        query_lower: str,
        primary_text: Optional[str],
        secondary_text: Optional[str],
        tags: List[str],
    ) -> bool:
        """
        Check if the query matches in primary/secondary text or tags.

        Performs case-insensitive matching to avoid extra lower() calls per tag.
        """
        if primary_text and query_lower in primary_text.lower():
            return True
        if secondary_text and query_lower in secondary_text.lower():
            return True
        return any(query_lower in tag.lower() for tag in tags)

    def _calculate_relevance_score(self, query_lower: str, text: Optional[str], tags: List[str]) -> float:
        """
        Compute a relevance score for a piece of text against a query.

        Strategy:
        - +1.0 if the full query appears (exact match)
        - +0.7 for each query word appearing as a whole word in the text
        - +0.5 for each tag containing the query
        - Apply a length penalty to normalize scores for long texts

        Returns 0.0 if text is None or empty.
        """
        if not text:
            return 0.0

        text_lower = text.lower()
        score = 0.0

        if query_lower in text_lower:
            score += self.SCORE_EXACT_MATCH

        # Word-in-text scoring with a single padded string allocation
        text_with_spaces = f" {text_lower} "
        for word in query_lower.split():
            if word and f" {word} " in text_with_spaces:
                score += self.SCORE_WORD_MATCH

        for tag in tags:
            if query_lower in tag.lower():
                score += self.SCORE_TAG_MATCH

        # Length penalty: penalize very long texts; base around 100 chars
        length_penalty = 1.0 / max(len(text) / self.LENGTH_PENALTY_BASE, 1.0)
        return score * length_penalty

    def get_search_analytics(self) -> SearchAnalytics:
        """
        Return analytics on the current index.

        Returns:
            SearchAnalytics summarizing counts of indexed items.
        """
        total_tasks = len(self.tasks)
        total_memories = len(self.memories)
        total_ideas = len(self.ideas)
        total_errors = len(self.errors)
        total_training = len(self.training_data)
        total_items = total_tasks + total_memories + total_ideas + total_errors + total_training

        return SearchAnalytics(
            total_indexed_items=total_items,
            tasks_count=total_tasks,
            memories_count=total_memories,
            ideas_count=total_ideas,
            errors_count=total_errors,
            training_count=total_training,
        )

    def get_search_suggestions(self, query: str, limit: int) -> List[str]:
        """
        Generate keyword/tag suggestions based on the current index.

        The suggestions are filtered by the query substring and sorted by frequency.

        Args:
            query: The query string to filter suggestions.
            limit: Maximum number of suggestions to return.

        Returns:
            List of suggestion keywords.
        """
        suggestions: Dict[str, int] = defaultdict(int)

        for task in self.tasks:
            self._extract_keywords(task.action, suggestions)
            for tag in task.tags:
                suggestions[tag] += 1

        for memory in self.memories:
            self._extract_keywords(memory.meaning, suggestions)
            for tag in memory.tags:
                suggestions[tag] += 1

        query_lower = query.lower()
        filtered = [(kw, cnt) for kw, cnt in suggestions.items() if query_lower in kw.lower()]
        filtered.sort(key=lambda x: x[1], reverse=True)
        return [kw for kw, _ in filtered[:limit]]

    def _extract_keywords(self, text: str, keywords: Dict[str, int]) -> None:
        """
        Extract keywords from text and update frequency map.

        Keywords are lowercase, alphanumeric, and longer than MIN_KEYWORD_LENGTH.
        """
        # Split on whitespace, filter by length
        words = [w for w in text.split() if len(w) > self.MIN_KEYWORD_LENGTH]
        for word in words:
            clean_word = "".join(ch for ch in word.lower() if ch.isalnum())
            if len(clean_word) > self.MIN_KEYWORD_LENGTH:
                keywords[clean_word] = keywords.get(clean_word, 0) + 1

    def advanced_search(self, criteria: AdvancedSearchCriteria) -> SearchResults:
        """
        Perform structured search using advanced criteria.

        Currently supports tasks and memories. For tasks: status, priority, assignee, required_tag.
        For memories: importance, term, required_tag.

        Args:
            criteria: AdvancedSearchCriteria with per-type criteria.

        Returns:
            SearchResults with score 1.0 for matches (unsorted).
        """
        results = SearchResults()

        for task in self.tasks:
            if self._matches_advanced_criteria(task, criteria.task_criteria):
                results.task_results.append(TaskResult(task=task, score=1.0))

        for memory in self.memories:
            if self._matches_advanced_memory_criteria(memory, criteria.memory_criteria):
                results.memory_results.append(MemoryResult(memory=memory, score=1.0))

        return results

    def _matches_advanced_criteria(self, task: Task, criteria: TaskSearchCriteria) -> bool:
        if criteria.status is not None and task.status != criteria.status:
            return False
        if criteria.priority is not None and task.priority != criteria.priority:
            return False
        if criteria.assignee is not None and task.assignee != criteria.assignee:
            return False
        if criteria.required_tag is not None and criteria.required_tag not in task.tags:
            return False
        return True

    def _matches_advanced_memory_criteria(self, memory: Memory, criteria: MemorySearchCriteria) -> bool:
        if criteria.importance is not None and memory.importance != criteria.importance:
            return False
        if criteria.term is not None and memory.term != criteria.term:
            return False
        if criteria.required_tag is not None and criteria.required_tag not in memory.tags:
            return False
        return True


# =========================
# Simple ChatContent implementation for testing/demo
# =========================

class SimpleChatContent:
    """
    A simple concrete implementation of ChatContent for demo/testing.
    Replace with your own implementation as needed.
    """
    def __init__(
        self,
        tasks: Optional[List[Task]] = None,
        memories: Optional[List[Memory]] = None,
        ideas: Optional[List[Idea]] = None,
        errors: Optional[List[Error]] = None,
        training_data: Optional[List[TrainingData]] = None,
    ):
        self.tasks: List[Task] = tasks or []
        self.memories: List[Memory] = memories or []
        self.ideas: List[Idea] = ideas or []
        self.errors: List[Error] = errors or []
        self.training_data: List[TrainingData] = training_data or []


# =========================
# Tests (equivalent to the Rust module tests)
# =========================

def test_search_engine_creation():
    engine = SearchEngine()
    assert len(engine.tasks) == 0
    assert len(engine.memories) == 0


def test_search_results():
    results = SearchResults()
    assert results.total_results() == 0
    assert not results.has_results()


def test_search_options_default():
    options = SearchOptions.default()
    assert options.limit == 50
    assert options.data_types is None


def test_search_analytics():
    engine = SearchEngine()
    engine.tasks = [Task(action="a"), Task(action="b")]
    engine.memories = [Memory(moment="x", meaning="y", reason="z")]
    engine.ideas = [Idea(idea="i"), Idea(idea="j"), Idea(idea="k")]
    engine.errors = [Error(title="e1", description="d", source="s"), Error(title="e2", description="d", source="s")]
    engine.training_data = [TrainingData(prompt="p", completion="c", source="s")]

    analytics = engine.get_search_analytics()
    assert analytics.total_indexed_items == 9  # 2 tasks + 1 memory + 3 ideas + 2 errors + 1 training = 9
    assert analytics.tasks_count == 2
    assert analytics.memories_count == 1
    assert analytics.ideas_count == 3
    assert analytics.errors_count == 2
    assert analytics.training_count == 1


def test_keyword_extraction():
    engine = SearchEngine()
    keywords: Dict[str, int] = {}
    engine._extract_keywords("This is a test sentence with keywords", keywords)
    assert "test" in keywords
    assert "sentence" in keywords
    assert "keywords" in keywords
    assert "is" not in keywords
    assert "a" not in keywords


def test_time_filtering():
    engine = SearchEngine()
    now = datetime.now(timezone.utc)
    earlier = now - timedelta(seconds=10)
    later = now + timedelta(seconds=10)

    t1 = Task(action="alpha", created_at=earlier)
    t2 = Task(action="beta", created_at=later)
    engine.tasks = [t1, t2]

    opts = SearchOptions(since=earlier)
    res = engine.search("alpha", opts)
    assert len(res.task_results) == 1

    opts = SearchOptions(until=earlier)
    res = engine.search("alpha", opts)
    assert len(res.task_results) == 1

    opts = SearchOptions(until=earlier)
    res = engine.search("beta", opts)
    assert len(res.task_results) == 0


def test_pagination():
    engine = SearchEngine()
    engine.tasks = [Task(action=f"Task {i}") for i in range(25)]

    opts = SearchOptions(page=2, page_size=10)
    res = engine.search("task", opts)
    assert len(res.task_results) == 10
    # Verify order is descending by score (all scores equal) but slice is correct
    # Page 2 (1-indexed) with page_size 10 should return items 10-19 (0-indexed)
    assert res.task_results[0].task.action == "Task 10"


def test_matches_query_optimization():
    engine = SearchEngine()
    # Primary/secondary/tag coverage
    assert engine._matches_query("urgent", "URGENT notice", None, ["news"])
    assert engine._matches_query("urgent", "Notice", "urgent:", ["news"])
    assert engine._matches_query("urgent", "Notice", "desc:", ["urgent tag"])
    assert not engine._matches_query("urgent", "No match", None, ["news"])


if __name__ == "__main__":
    # Run basic tests
    test_search_engine_creation()
    test_search_results()
    test_search_options_default()
    test_search_analytics()
    test_keyword_extraction()
    test_time_filtering()
    test_pagination()
    test_matches_query_optimization()
    print("All tests passed.")
