from __future__ import annotations

import threading
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Dict, FrozenSet, Iterator, List, Optional, Set

# The Rust equivalent used &str, Vec, HashMap; adapt to Python's built-in types.
# Below, types used only for type hints are excluded from runtime import to optimize startup.
if TYPE_CHECKING:
    pass


# -------------------------
# Errors
# -------------------------

class TodoziError(Exception):
    """Base exception for the module."""
    pass


class ValidationError(TodoziError):
    """Raised when data fails validation."""
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


# -------------------------
# Enums
# -------------------------

class ShareLevel(Enum):
    Public = "Public"
    Team = "Team"
    Private = "Private"


class IdeaImportance(Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"
    Breakthrough = "Breakthrough"


class ItemStatus(Enum):
    Active = "Active"
    Archived = "Archived"


# -------------------------
# Data models
# -------------------------

@dataclass(frozen=True)
class Idea:
    id: str
    idea: str
    project_id: Optional[str] = None
    status: ItemStatus = ItemStatus.Active
    share: ShareLevel = ShareLevel.Private
    importance: IdeaImportance = IdeaImportance.Medium
    tags: FrozenSet[str] = field(default_factory=frozenset)
    context: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class IdeaUpdate:
    idea: Optional[str] = None
    share: Optional[ShareLevel] = None
    importance: Optional[IdeaImportance] = None
    tags: Optional[List[str]] = None
    context: Optional[str] = None

    # Builder methods (immutable style) - using 'with_' prefix to avoid shadowing fields
    def with_idea(self, idea: str) -> "IdeaUpdate":
        new = replace(self, idea=idea)
        return new

    def with_share(self, share: ShareLevel) -> "IdeaUpdate":
        new = replace(self, share=share)
        return new

    def with_importance(self, importance: IdeaImportance) -> "IdeaUpdate":
        new = replace(self, importance=importance)
        return new

    def with_tags(self, tags: List[str]) -> "IdeaUpdate":
        new = replace(self, tags=[t.strip() for t in (tags or []) if t and t.strip()])
        return new

    def with_context(self, context: str) -> "IdeaUpdate":
        new = replace(self, context=context)
        return new


@dataclass(frozen=True)
class IdeaStatistics:
    total_ideas: int
    public_ideas: int
    team_ideas: int
    private_ideas: int
    breakthrough_ideas: int
    unique_tags: int

    def public_percentage(self) -> float:
        if self.total_ideas == 0:
            return 0.0
        return (self.public_ideas / self.total_ideas) * 100.0

    def team_percentage(self) -> float:
        if self.total_ideas == 0:
            return 0.0
        return (self.team_ideas / self.total_ideas) * 100.0

    def private_percentage(self) -> float:
        if self.total_ideas == 0:
            return 0.0
        return (self.private_ideas / self.total_ideas) * 100.0

    def breakthrough_percentage(self) -> float:
        if self.total_ideas == 0:
            return 0.0
        return (self.breakthrough_ideas / self.total_ideas) * 100.0


# -------------------------
# Manager (thread-safe)
# -------------------------

class IdeaManager:
    """Manages a collection of ideas with thread-safe operations."""
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.ideas: Dict[str, Idea] = {}
        self.idea_tags: Dict[str, List[str]] = {}

    def _now(self) -> datetime:
        return datetime.utcnow()

    def _new_uuid(self) -> str:
        return str(uuid.uuid4())

    def create_idea(self, idea: Idea) -> str:
        """Create a new idea with auto-generated ID and timestamps.

        This method does not mutate the input; it returns the new idea's ID.
        The stored idea is a new instance with normalized tags.

        Args:
            idea: Idea object (its id will be ignored and overwritten).

        Returns:
            str: The generated idea ID.

        Raises:
            ValidationError: If the provided idea is invalid.
        """
        if not isinstance(idea, Idea):
            raise TypeError("idea must be an Idea instance")
        now = self._now()
        tags = [t.strip() for t in (idea.tags or []) if t and t.strip()]
        new_idea = replace(
            idea,
            id=self._new_uuid(),
            created_at=now,
            updated_at=now,
            tags=frozenset(tags),
        )
        with self._lock:
            self.ideas[new_idea.id] = new_idea
            self.idea_tags[new_idea.id] = list(new_idea.tags)
        return new_idea.id

    def get_idea(self, idea_id: str) -> Optional[Idea]:
        """Get an idea by ID (read-only copy)."""
        with self._lock:
            idea = self.ideas.get(idea_id)
            return idea if idea is None else replace(idea)

    def get_all_ideas(self) -> List[Idea]:
        """Get a list of all ideas (as copies)."""
        with self._lock:
            return [replace(i) for i in self.ideas.values()]

    def update_idea(self, idea_id: str, updates: IdeaUpdate) -> None:
        """Update an existing idea.

        Args:
            idea_id: The ID of the idea to update.
            updates: Changes to apply.

        Raises:
            TypeError: If updates is not an IdeaUpdate instance.
            ValidationError: If the idea_id does not exist.
        """
        if not isinstance(updates, IdeaUpdate):
            raise TypeError("updates must be an IdeaUpdate instance")

        with self._lock:
            if idea_id not in self.ideas:
                raise ValidationError(f"Idea {idea_id} not found")

            idea = self.ideas[idea_id]
            changed_idea = idea

            if updates.idea is not None:
                changed_idea = replace(changed_idea, idea=updates.idea)

            if updates.share is not None:
                changed_idea = replace(changed_idea, share=updates.share)

            if updates.importance is not None:
                changed_idea = replace(changed_idea, importance=updates.importance)

            if updates.tags is not None:
                new_tags = frozenset(t.strip() for t in updates.tags if t and t.strip())
                changed_idea = replace(changed_idea, tags=new_tags)
                self.idea_tags[idea_id] = list(new_tags)

            if updates.context is not None:
                changed_idea = replace(changed_idea, context=updates.context)

            changed_idea = replace(changed_idea, updated_at=self._now())

            self.ideas[idea_id] = changed_idea

    def delete_idea(self, idea_id: str) -> None:
        """Delete an idea by ID.

        Raises:
            ValidationError: If the idea_id does not exist.
        """
        with self._lock:
            if idea_id not in self.ideas:
                raise ValidationError(f"Idea {idea_id} not found")
            del self.ideas[idea_id]
            self.idea_tags.pop(idea_id, None)

    def search_ideas(self, query: str) -> Iterator[Idea]:
        """Search ideas by substring in idea text, tags, or context.

        This method is generator-based for memory efficiency on large datasets.

        Yields:
            Idea: Matching idea objects.
        """
        q = query.lower()
        with self._lock:
            for idea in self.ideas.values():
                if (
                    q in idea.idea.lower()
                    or any(q in t.lower() for t in idea.tags)
                    or (idea.context is not None and q in idea.context.lower())
                ):
                    yield replace(idea)

    def get_ideas_by_importance(self, importance: IdeaImportance) -> List[Idea]:
        """Get ideas filtered by importance (as copies)."""
        with self._lock:
            return [replace(i) for i in self.ideas.values() if i.importance == importance]

    def get_ideas_by_share_level(self, share_level: ShareLevel) -> List[Idea]:
        """Get ideas filtered by share level (as copies)."""
        with self._lock:
            return [replace(i) for i in self.ideas.values() if i.share == share_level]

    def get_ideas_by_tag(self, tag: str) -> List[Idea]:
        """Get ideas by a specific tag (case-insensitive, as copies)."""
        tag_l = tag.lower()
        with self._lock:
            return [replace(i) for i in self.ideas.values() if any(t.lower() == tag_l for t in i.tags)]

    def get_public_ideas(self) -> List[Idea]:
        """Get all public ideas (as copies)."""
        return self.get_ideas_by_share_level(ShareLevel.Public)

    def get_team_ideas(self) -> List[Idea]:
        """Get all team ideas (as copies)."""
        return self.get_ideas_by_share_level(ShareLevel.Team)

    def get_private_ideas(self) -> List[Idea]:
        """Get all private ideas (as copies)."""
        return self.get_ideas_by_share_level(ShareLevel.Private)

    def get_breakthrough_ideas(self) -> List[Idea]:
        """Get all breakthrough ideas (as copies)."""
        return self.get_ideas_by_importance(IdeaImportance.Breakthrough)

    def get_recent_ideas(self, limit: int) -> List[Idea]:
        """Get the most recent ideas by creation time (as copies)."""
        if limit <= 0:
            return []
        with self._lock:
            ideas = sorted(self.ideas.values(), key=lambda i: i.created_at, reverse=True)
            return [replace(i) for i in ideas[:limit]]

    def get_all_tags(self) -> List[str]:
        """Get a sorted list of all unique tags across ideas."""
        with self._lock:
            tags_set: Set[str] = set()
            for tags in self.idea_tags.values():
                for t in tags:
                    tags_set.add(t)
            return sorted(tags_set)

    def get_tag_statistics(self) -> Dict[str, int]:
        """Get a mapping of tag -> usage count."""
        stats: Dict[str, int] = {}
        with self._lock:
            for tags in self.idea_tags.values():
                for t in tags:
                    stats[t] = stats.get(t, 0) + 1
            return stats

    def get_idea_statistics(self) -> IdeaStatistics:
        """Compute statistics over all ideas."""
        with self._lock:
            total_ideas = len(self.ideas)
            public_ideas = sum(1 for i in self.ideas.values() if i.share == ShareLevel.Public)
            team_ideas = sum(1 for i in self.ideas.values() if i.share == ShareLevel.Team)
            private_ideas = sum(1 for i in self.ideas.values() if i.share == ShareLevel.Private)
            breakthrough_ideas = sum(1 for i in self.ideas.values() if i.importance == IdeaImportance.Breakthrough)
            unique_tags = len(set(t for tags in self.idea_tags.values() for t in tags))
            return IdeaStatistics(
                total_ideas=total_ideas,
                public_ideas=public_ideas,
                team_ideas=team_ideas,
                private_ideas=private_ideas,
                breakthrough_ideas=breakthrough_ideas,
                unique_tags=unique_tags,
            )


# -------------------------
# Parser
# -------------------------

def parse_idea_format(idea_text: str) -> Idea:
    """Parse an idea from a custom string format.

    Expected format:
        <idea>idea text; share; importance; tags; context</idea>

    share can be one of: "share", "don't share"/"dont share"/"private", "team"
    importance must match an IdeaImportance name.
    tags is a comma-separated list (optional).
    context is optional.

    Returns:
        Idea: A fully formed Idea with generated ID and timestamps.

    Raises:
        ValidationError: On malformed input.
    """
    start_tag = "<idea>"
    end_tag = "</idea>"

    start_idx = idea_text.find(start_tag)
    if start_idx == -1:
        raise ValidationError("Missing <idea> start tag")
    end_idx = idea_text.find(end_tag)
    if end_idx == -1:
        raise ValidationError("Missing </idea> end tag")

    content = idea_text[start_idx + len(start_tag): end_idx]
    parts = [p.strip() for p in content.split(";")]
    if len(parts) < 3:
        raise ValidationError(
            "Invalid idea format: need at least 3 parts (idea; share; importance)"
        )

    share_raw = parts[1].lower()
    if share_raw in ("share",):
        share = ShareLevel.Public
    elif share_raw in ("dont share", "don't share", "private"):
        share = ShareLevel.Private
    elif share_raw == "team":
        share = ShareLevel.Team
    else:
        share = ShareLevel.Private

    tags: FrozenSet[str] = frozenset()
    if len(parts) > 3 and parts[3]:
        tags = frozenset(t.strip() for t in parts[3].split(",") if t and t.strip())

    context: Optional[str] = None
    if len(parts) > 4 and parts[4]:
        context = parts[4]

    try:
        importance = IdeaImportance(parts[2].strip())
    except Exception:
        raise ValidationError("Invalid idea importance")

    now = datetime.utcnow()
    return Idea(
        id=str(uuid.uuid4()),
        idea=parts[0],
        project_id=None,
        status=ItemStatus.Active,
        share=share,
        importance=importance,
        tags=tags,
        context=context,
        created_at=now,
        updated_at=now,
    )


# -------------------------
# Tests
# -------------------------

def test_idea_manager_creation():
    manager = IdeaManager()
    assert len(manager.ideas) == 0
    assert len(manager.idea_tags) == 0


def test_idea_update_builder():
    update = IdeaUpdate().with_idea("New idea").with_share(ShareLevel.Public).with_importance(IdeaImportance.High)
    assert update.idea == "New idea"
    assert update.share == ShareLevel.Public
    assert update.importance == IdeaImportance.High


def test_idea_statistics_percentages():
    stats = IdeaStatistics(
        total_ideas=10,
        public_ideas=4,
        team_ideas=3,
        private_ideas=3,
        breakthrough_ideas=2,
        unique_tags=8,
    )
    assert abs(stats.public_percentage() - 40.0) < 1e-6
    assert abs(stats.team_percentage() - 30.0) < 1e-6
    assert abs(stats.private_percentage() - 30.0) < 1e-6
    assert abs(stats.breakthrough_percentage() - 20.0) < 1e-6

    empty = IdeaStatistics(
        total_ideas=0,
        public_ideas=0,
        team_ideas=0,
        private_ideas=0,
        breakthrough_ideas=0,
        unique_tags=0,
    )
    assert empty.public_percentage() == 0.0
    assert empty.team_percentage() == 0.0
    assert empty.private_percentage() == 0.0
    assert empty.breakthrough_percentage() == 0.0


def test_parse_idea_format():
    idea_text = "<idea>Use microservices for better scalability; share; high; architecture,microservices,scalability; This will improve deployment speed</idea>"
    idea = parse_idea_format(idea_text)
    assert idea.idea == "Use microservices for better scalability"
    assert idea.share == ShareLevel.Public
    assert idea.importance == IdeaImportance.High
    assert set(idea.tags) == {"architecture", "microservices", "scalability"}
    assert idea.context == "This will improve deployment speed"


def test_parse_idea_format_minimal():
    idea_text = "<idea>Simple idea; private; low</idea>"
    idea = parse_idea_format(idea_text)
    assert idea.idea == "Simple idea"
    assert idea.share == ShareLevel.Private
    assert idea.importance == IdeaImportance.Low
    assert len(idea.tags) == 0
    assert idea.context is None


if __name__ == "__main__":
    # Optional: run a quick demo
    m = IdeaManager()
    idea = Idea(
        id="",
        idea="Try async Python",
        share=ShareLevel.Team,
        importance=IdeaImportance.High,
        tags=["python", "async"],
    )
    uid = m.create_idea(idea)
    print("Created idea:", uid)
    print("All ideas:", [i.idea for i in m.get_all_ideas()])
    print("Search 'python':", [i.idea for i in m.search_ideas("python")])
    m.update_idea(uid, IdeaUpdate().with_context("Learn asyncio"))
    updated = m.get_idea(uid)
    print("Updated context:", updated.context if updated else None)
    print("Stats:", m.get_idea_statistics())
