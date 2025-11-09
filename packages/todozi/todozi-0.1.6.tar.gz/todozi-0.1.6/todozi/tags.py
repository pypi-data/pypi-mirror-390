from __future__ import annotations

import asyncio
import re
import uuid
from dataclasses import dataclass, field, replace
from datetime import datetime, timezone as dt_timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Tuple, Union

# ---------------------- Exceptions ---------------------- #


class TodoziError(Exception):
    """Base exception for all errors raised by this module."""


class TagNotFoundError(TodoziError):
    """Raised when an expected tag does not exist."""


class ValidationError(TodoziError):
    """Raised when a validation check fails."""


# ---------------------- Data Models ---------------------- #


@dataclass(frozen=True)
class Tag:
    id: str
    name: str
    description: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None
    usage_count: int = 0
    created_at: datetime = field(default_factory=lambda: datetime.now(dt_timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(dt_timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "color": self.color,
            "category": self.category,
            "usage_count": self.usage_count,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Tag:
        return Tag(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            color=data.get("color"),
            category=data.get("category"),
            usage_count=int(data.get("usage_count") or 0),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
        )


@dataclass
class TagUpdate:
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    category: Optional[str] = None

    # Fluent builder for convenience
    def with_name(self, name: str) -> TagUpdate:
        self.name = name
        return self

    def with_description(self, description: str) -> TagUpdate:
        self.description = description
        return self

    def with_color(self, color: str) -> TagUpdate:
        self.color = color
        return self

    def with_category(self, category: str) -> TagUpdate:
        self.category = category
        return self


@dataclass
class TagStatistics:
    __slots__ = ["total_tags", "total_categories", "total_relationships", "average_usage"]
    total_tags: int
    total_categories: int
    total_relationships: int
    average_usage: float

    def relationships_per_tag(self) -> float:
        if self.total_tags == 0:
            return 0.0
        return self.total_relationships / self.total_tags


class TagSortBy(Enum):
    Name = auto()
    Usage = auto()
    Created = auto()
    Updated = auto()


@dataclass
class TagSearchQuery:
    name_contains: Optional[str] = None
    description_contains: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    min_usage: Optional[int] = None
    max_usage: Optional[int] = None
    sort_by: TagSortBy = TagSortBy.Name
    limit: Optional[int] = None


# ---------------------- Utilities ---------------------- #


_WORD_RE = re.compile(r"[A-Za-z0-9_]+")


def _now_utc() -> datetime:
    return datetime.now(dt_timezone.utc)


def _generate_id() -> str:
    return str(uuid.uuid4())


def _tokenize(text: str) -> Set[str]:
    """Tokenize a string into lowercase words for indexing."""
    if not text:
        return set()
    return {t.lower() for t in _WORD_RE.findall(text)}


def _copy_tag(tag: Tag) -> Tag:
    # Frozen dataclass with immutable fields; return as-is.
    # If you need deep copies, replace with copy.deepcopy(tag).
    return tag


# ---------------------- Core Manager ---------------------- #


class TagManager:
    """
    Thread-safe tag manager with search indexing.

    - Uses asyncio.Lock to protect shared mutable state.
    - Avoids defaultdict(list) to prevent memory leaks from persistent empty lists.
    - Maintains indexes for fast name and token-based lookup.
    - Returns copies of Tag instances to avoid external mutation.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        # Core storage
        self.tags: Dict[str, Tag] = {}
        # Relationships map: tag_id -> [related_tag_id, ...]
        self.tag_relationships: Dict[str, List[str]] = {}
        # Category map: category -> [tag_id, ...]
        self.category_tags: Dict[str, List[str]] = {}

        # Indexes for performance
        self._name_index: Dict[str, str] = {}  # name (lower) -> tag_id
        self._search_index: Dict[str, Set[str]] = {}  # token (lower) -> set(tag_id)

    # ---------------------- Internal helpers ---------------------- #

    def _ensure_list_and_get(self, d: Dict[str, List[str]], key: str) -> List[str]:
        lst = d.get(key)
        if lst is None:
            lst = []
            d[key] = lst
        return lst

    def _add_category_index(self, category: str, tag_id: str) -> None:
        self._ensure_list_and_get(self.category_tags, category).append(tag_id)

    def _remove_category_index(self, category: str, tag_id: str) -> None:
        lst = self.category_tags.get(category)
        if lst is not None:
            lst[:] = [t for t in lst if t != tag_id]
            if not lst:
                del self.category_tags[category]

    def _add_name_index(self, name: str, tag_id: str) -> None:
        self._name_index[name.lower()] = tag_id

    def _remove_name_index(self, name: str) -> None:
        self._name_index.pop(name.lower(), None)

    def _add_search_index(self, token: str, tag_id: str) -> None:
        s = self._search_index.get(token)
        if s is None:
            s = set()
            self._search_index[token] = s
        s.add(tag_id)

    def _remove_search_index(self, token: str, tag_id: str) -> None:
        s = self._search_index.get(token)
        if s is not None:
            s.discard(tag_id)
            if not s:
                del self._search_index[token]

    def _rebuild_search_index_for_tag(self, tag: Tag) -> None:
        # Add token indexes from name and description
        tokens = set()
        tokens |= _tokenize(tag.name)
        if tag.description:
            tokens |= _tokenize(tag.description)
        for token in tokens:
            self._add_search_index(token, tag.id)

    def _remove_search_index_for_tag(self, tag: Tag) -> None:
        tokens = set()
        tokens |= _tokenize(tag.name)
        if tag.description:
            tokens |= _tokenize(tag.description)
        for token in tokens:
            self._remove_search_index(token, tag.id)

    def _unique_name(self, name: str) -> bool:
        return name.lower() not in self._name_index

    # ---------------------- Public API ---------------------- #

    async def create_tag(
        self,
        name: str,
        *,
        description: Optional[str] = None,
        color: Optional[str] = None,
        category: Optional[str] = None,
    ) -> str:
        """
        Create a new tag. Pythonic alternative to passing a mutable Tag object.
        Returns the created tag id.
        """
        if not name or not name.strip():
            raise ValidationError("Tag name cannot be empty")

        async with self._lock:
            if not self._unique_name(name):
                raise ValidationError(f"Tag name '{name}' already exists")

            now = _now_utc()
            tag = Tag(
                id=_generate_id(),
                name=name,
                description=description,
                color=color,
                category=category,
                usage_count=0,
                created_at=now,
                updated_at=now,
            )

            # Update core stores
            self.tags[tag.id] = tag
            if category is not None:
                self._add_category_index(category, tag.id)

            # Update indexes
            self._add_name_index(tag.name, tag.id)
            self._rebuild_search_index_for_tag(tag)

            return tag.id

    def get_tag(self, tag_id: str) -> Optional[Tag]:
        """Get a tag by id. Returns a copy to avoid external mutation."""
        tag = self.tags.get(tag_id)
        return _copy_tag(tag) if tag is not None else None

    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """Get a tag by name. Returns a copy to avoid external mutation."""
        tag_id = self._name_index.get(name.lower())
        if tag_id is None:
            return None
        tag = self.tags.get(tag_id)
        return _copy_tag(tag) if tag is not None else None

    def get_all_tags(self) -> List[Tag]:
        """Return a list of all tags (copies)."""
        return [_copy_tag(t) for t in self.tags.values()]

    async def update_tag(self, tag_id: str, updates: TagUpdate) -> None:
        async with self._lock:
            tag = self.tags.get(tag_id)
            if tag is None:
                raise TagNotFoundError(f"Tag {tag_id} not found")

            old_category = tag.category
            old_name = tag.name
            old_desc = tag.description

            changed_name = False
            changed_desc = False

            # Build update kwargs for replace()
            update_kwargs = {}

            if updates.name is not None:
                if not updates.name or not updates.name.strip():
                    raise ValidationError("Tag name cannot be empty")
                if updates.name.lower() != tag.name.lower() and not self._unique_name(updates.name):
                    raise ValidationError(f"Tag name '{updates.name}' already exists")
                update_kwargs["name"] = updates.name
                changed_name = True

            if updates.description is not None:
                update_kwargs["description"] = updates.description
                changed_desc = True

            if updates.color is not None:
                update_kwargs["color"] = updates.color

            if updates.category is not None:
                # Remove from old category
                if old_category is not None:
                    self._remove_category_index(old_category, tag_id)
                # Add to new category
                update_kwargs["category"] = updates.category
                self._add_category_index(updates.category, tag_id)

            # Update timestamps
            update_kwargs["updated_at"] = _now_utc()

            # Create new tag instance with updates
            tag = replace(tag, **update_kwargs)

            # Update indexes
            if changed_name:
                self._remove_name_index(old_name)
                self._add_name_index(tag.name, tag.id)
            if changed_name or changed_desc:
                # Remove old tokens, add new tokens
                self._remove_search_index_for_tag(Tag(
                    id=tag.id,
                    name=old_name,
                    description=old_desc,
                    color=tag.color,
                    category=tag.category,
                    usage_count=tag.usage_count,
                    created_at=tag.created_at,
                    updated_at=tag.updated_at,
                ))
                self._rebuild_search_index_for_tag(tag)

            # Store the updated tag
            self.tags[tag_id] = tag

    async def delete_tag(self, tag_id: str) -> None:
        async with self._lock:
            tag = self.tags.get(tag_id)
            if tag is None:
                raise TagNotFoundError(f"Tag {tag_id} not found")

            # Remove from category index
            if tag.category is not None:
                self._remove_category_index(tag.category, tag_id)

            # Remove relationships pointing to this tag
            self.tag_relationships.pop(tag_id, None)
            for rel_list in self.tag_relationships.values():
                rel_list[:] = [rid for rid in rel_list if rid != tag_id]

            # Remove name and search index
            self._remove_name_index(tag.name)
            self._remove_search_index_for_tag(tag)

            # Remove from core storage
            del self.tags[tag_id]

    async def add_tag_relationship(self, tag_id: str, related_tag_id: str) -> None:
        async with self._lock:
            if tag_id not in self.tags:
                raise TagNotFoundError(f"Tag {tag_id} not found")
            if related_tag_id not in self.tags:
                raise TagNotFoundError(f"Related tag {related_tag_id} not found")
            if tag_id == related_tag_id:
                raise ValidationError("Cannot relate a tag to itself")
            rel_list = self._ensure_list_and_get(self.tag_relationships, tag_id)
            if related_tag_id not in rel_list:
                rel_list.append(related_tag_id)

    def get_related_tags(self, tag_id: str) -> List[Tag]:
        """Return a list of tags related to the given tag id (copies)."""
        related_ids = self.tag_relationships.get(tag_id, [])
        result: List[Tag] = []
        for rid in related_ids:
            tag = self.tags.get(rid)
            if tag is not None:
                result.append(_copy_tag(tag))
        return result

    def search_tags(self, query: str) -> List[Tag]:
        """
        Search tags by name/description substring (case-insensitive).
        Uses search index (token-based) for tokens and falls back to scan for other substrings.
        """
        q = query.strip().lower()
        if not q:
            return self.get_all_tags()

        # Try token-based search
        tokens = _tokenize(q)
        candidates: Optional[Set[str]] = None
        if tokens:
            # Intersect sets per token (AND semantics)
            token_sets = [self._search_index.get(t, set()) for t in tokens]
            non_empty = [s for s in token_sets if s]
            if non_empty:
                candidates = set.intersection(*non_empty)
            else:
                candidates = set()

        results: List[Tag] = []
        if candidates is not None and candidates:
            for tid in candidates:
                t = self.tags.get(tid)
                if t is None:
                    continue
                lc_name = t.name.lower()
                lc_desc = t.description.lower() if t.description else ""
                if q in lc_name or q in lc_desc:
                    results.append(_copy_tag(t))
        else:
            # Fallback: linear scan
            for t in self.tags.values():
                lc_name = t.name.lower()
                lc_desc = t.description.lower() if t.description else ""
                if q in lc_name or q in lc_desc:
                    results.append(_copy_tag(t))
        return results

    def get_tags_by_category(self, category: str) -> List[Tag]:
        """Get all tags in a category (copies)."""
        tag_ids = self.category_tags.get(category, [])
        result: List[Tag] = []
        for tid in tag_ids:
            t = self.tags.get(tid)
            if t is not None:
                result.append(_copy_tag(t))
        return result

    def get_all_categories(self) -> List[str]:
        return list(self.category_tags.keys())

    async def increment_tag_usage(self, tag_name: str) -> None:
        async with self._lock:
            for tag_id, tag in self.tags.items():
                if tag.name.lower() == tag_name.lower():
                    updated_tag = replace(tag, usage_count=tag.usage_count + 1, updated_at=_now_utc())
                    self.tags[tag_id] = updated_tag
                    break

    def get_most_used_tags(self, limit: int) -> List[Tag]:
        if limit <= 0:
            return []
        tags = list(self.tags.values())
        tags.sort(key=lambda t: t.usage_count, reverse=True)
        return [_copy_tag(t) for t in tags[:limit]]

    def get_recent_tags(self, limit: int) -> List[Tag]:
        if limit <= 0:
            return []
        tags = list(self.tags.values())
        tags.sort(key=lambda t: t.created_at, reverse=True)
        return [_copy_tag(t) for t in tags[:limit]]

    def get_tag_statistics(self) -> TagStatistics:
        total_tags = len(self.tags)
        total_categories = len(self.category_tags)
        total_relationships = sum(len(v) for v in self.tag_relationships.values())
        if total_tags > 0:
            avg_usage = sum(t.usage_count for t in self.tags.values()) / total_tags
        else:
            avg_usage = 0.0
        return TagStatistics(
            total_tags=total_tags,
            total_categories=total_categories,
            total_relationships=total_relationships,
            average_usage=avg_usage,
        )

    async def bulk_create_tags(
        self,
        tag_names: Union[List[str], Tuple[str, ...]],
        category: Optional[str] = None,
    ) -> List[str]:
        created_ids: List[str] = []
        for name in tag_names:
            if not isinstance(name, str) or not name.strip():
                raise ValidationError("Tag name cannot be empty")
        async with self._lock:
            for name in tag_names:
                # Reuse logic of create_tag but under a single lock to avoid repeated acquisitions
                if not self._unique_name(name):
                    raise ValidationError(f"Tag name '{name}' already exists")
                now = _now_utc()
                tag = Tag(
                    id=_generate_id(),
                    name=name,
                    description=None,
                    color=None,
                    category=category,
                    usage_count=0,
                    created_at=now,
                    updated_at=now,
                )
                self.tags[tag.id] = tag
                if category is not None:
                    self._add_category_index(category, tag.id)
                self._add_name_index(tag.name, tag.id)
                self._rebuild_search_index_for_tag(tag)
                created_ids.append(tag.id)
        return created_ids

    async def merge_tags(self, primary_tag_id: str, duplicate_tag_ids: List[str]) -> None:
        async with self._lock:
            primary = self.tags.get(primary_tag_id)
            if primary is None:
                raise TagNotFoundError(f"Primary tag {primary_tag_id} not found")

            total_usage = primary.usage_count
            for dup_id in duplicate_tag_ids:
                dup_tag = self.tags.get(dup_id)
                if dup_tag is None:
                    continue

                # Accumulate usage count
                total_usage += dup_tag.usage_count

                # Move relationships
                dup_rels = self.tag_relationships.pop(dup_id, [])
                if dup_rels:
                    primary_rel_list = self._ensure_list_and_get(self.tag_relationships, primary_tag_id)
                    for r in dup_rels:
                        if r not in primary_rel_list and r != primary_tag_id:
                            primary_rel_list.append(r)

                # Remove duplicates from core and indexes
                if dup_tag.category is not None:
                    self._remove_category_index(dup_tag.category, dup_id)
                self._remove_name_index(dup_tag.name)
                self._remove_search_index_for_tag(dup_tag)
                self.tags.pop(dup_id, None)

            # Update primary tag with accumulated usage count
            primary = replace(primary, usage_count=total_usage, updated_at=_now_utc())
            self.tags[primary_tag_id] = primary


# ---------------------- Search Engine ---------------------- #


def levenshtein_distance(s1: str, s2: str) -> int:
    # Iterative DP to keep memory O(min(n, m))
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    prev = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1, 1):
        curr = [i]
        for j, c2 in enumerate(s2, 1):
            insertions = prev[j] + 1
            deletions = curr[j - 1] + 1
            substitutions = prev[j - 1] + (0 if c1 == c2 else 1)
            curr.append(min(insertions, deletions, substitutions))
        prev = curr
    return prev[-1]


class TagSearchEngine:
    def __init__(self, tag_manager: TagManager) -> None:
        self.tag_manager = tag_manager

    def advanced_search(self, query: TagSearchQuery) -> List[Tag]:
        results: List[Tag] = list(self.tag_manager.tags.values())

        if query.name_contains is not None:
            nq = query.name_contains.lower()
            results = [t for t in results if nq in t.name.lower()]

        if query.description_contains is not None:
            dq = query.description_contains.lower()
            results = [t for t in results if t.description is not None and dq in t.description.lower()]

        if query.category is not None:
            results = [t for t in results if t.category == query.category]

        if query.min_usage is not None:
            results = [t for t in results if t.usage_count >= query.min_usage]

        if query.max_usage is not None:
            results = [t for t in results if t.usage_count <= query.max_usage]

        if query.color is not None:
            results = [t for t in results if t.color == query.color]

        reverse = True
        key: Optional[TagSortBy] = query.sort_by
        sort_key: Any = None
        if key == TagSortBy.Name:
            sort_key = lambda t: t.name
            reverse = False
        elif key == TagSortBy.Usage:
            sort_key = lambda t: t.usage_count
        elif key == TagSortBy.Created:
            sort_key = lambda t: t.created_at
        elif key == TagSortBy.Updated:
            sort_key = lambda t: t.updated_at

        if sort_key is not None:
            results.sort(key=sort_key, reverse=reverse)

        if query.limit is not None and query.limit > 0:
            results = results[: query.limit]

        return [_copy_tag(t) for t in results]

    def fuzzy_search(self, query: str, max_distance: int) -> List[Tuple[Tag, int]]:
        q = query.lower()
        results: List[Tuple[Tag, int]] = []
        for tag in self.tag_manager.tags.values():
            d = levenshtein_distance(q, tag.name.lower())
            if d <= max_distance:
                results.append((_copy_tag(tag), d))
        results.sort(key=lambda x: x[1])
        return results

    def get_suggestions(self, current_tags: List[str], limit: int) -> List[str]:
        """
        Suggest related tags by aggregating the relationships of the provided tag names.
        Returns a list of tag names sorted by frequency of co-occurrence.
        """
        if limit <= 0:
            return []
        counts: Dict[str, int] = {}
        for name in current_tags:
            t = self.tag_manager.get_tag_by_name(name)
            if t is None:
                continue
            for related in self.tag_manager.get_related_tags(t.id):
                counts[related.name] = counts.get(related.name, 0) + 1
        return [name for name, _ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:limit]]


# ---------------------- Tests ---------------------- #

if __name__ == "__main__":
    import json

    async def _run_tests():
        # 1) Basic creation
        manager = TagManager()
        assert len(manager.get_all_tags()) == 0
        assert len(manager.get_all_categories()) == 0

        # 2) TagUpdate builder style
        update = TagUpdate().with_name("New Name").with_description("New Description").with_color("#FF0000")
        assert update.name == "New Name"
        assert update.description == "New Description"
        assert update.color == "#FF0000"

        # 3) TagStatistics
        stats = TagStatistics(total_tags=10, total_categories=3, total_relationships=15, average_usage=5.5)
        assert abs(stats.relationships_per_tag() - 1.5) < 1e-9
        empty_stats = TagStatistics(total_tags=0, total_categories=0, total_relationships=0, average_usage=0.0)
        assert empty_stats.relationships_per_tag() == 0.0

        # 4) Search query
        query = TagSearchQuery(
            name_contains="test",
            category="development",
            min_usage=5,
            sort_by=TagSortBy.Usage,
            limit=10,
        )
        assert query.name_contains == "test"
        assert query.category == "development"
        assert query.min_usage == 5
        assert query.limit == 10

        # 5) Levenshtein
        assert levenshtein_distance("kitten", "kitten") == 0
        assert levenshtein_distance("kitten", "kittens") == 1
        assert levenshtein_distance("kitten", "sitting") == 3
        assert levenshtein_distance("", "abc") == 3
        assert levenshtein_distance("abc", "") == 3

        # 6) Create tags
        id1 = await manager.create_tag("bug", description="A bug", color="red", category="dev")
        id2 = await manager.create_tag("feature", description="New feature", color="blue", category="dev")
        await manager.add_tag_relationship(id1, id2)

        # 7) Getters
        found = manager.get_tag(id1)
        assert found is not None and found.name == "bug"
        assert manager.get_tag_by_name("feature") is not None
        assert manager.get_tag_by_name("missing") is None

        # 8) All tags and categories
        assert len(manager.get_all_tags()) == 2
        assert len(manager.get_all_categories()) == 1
        assert "dev" in manager.get_all_categories()

        # 9) Related tags
        rels = manager.get_related_tags(id1)
        assert len(rels) == 1 and rels[0].name == "feature"

        # 10) Update tag (including category change)
        await manager.update_tag(
            id1,
            TagUpdate().with_description("Bug description").with_color("#FF0000").with_category("work"),
        )
        updated = manager.get_tag(id1)
        assert updated is not None and updated.description == "Bug description" and updated.color == "#FF0000" and updated.category == "work"
        assert len(manager.get_tags_by_category("work")) == 1
        assert len(manager.get_tags_by_category("dev")) == 1

        # 11) Usage increment
        await manager.increment_tag_usage("feature")
        feat = manager.get_tag_by_name("feature")
        assert feat is not None and feat.usage_count == 1

        # 12) Most used / recent
        assert len(manager.get_most_used_tags(1)) == 1
        assert len(manager.get_recent_tags(10)) == 2

        # 13) Advanced search
        engine = TagSearchEngine(manager)
        res = engine.advanced_search(TagSearchQuery(name_contains="bug", sort_by=TagSortBy.Name))
        assert len(res) == 1 and res[0].name == "bug"

        # 14) Fuzzy search
        fuzzy = engine.fuzzy_search("feat", 3)  # Distance between "feat" and "feature" is 3
        assert any(t.name == "feature" for t, d in fuzzy)

        # 15) Suggestions
        suggestions = engine.get_suggestions(["bug"], 5)  # get_suggestions expects tag names, not IDs
        assert "feature" in suggestions

        # 16) Merge tags
        id3 = await manager.create_tag("enhancement", description="Enhancement", category="dev")
        await manager.increment_tag_usage("enhancement")
        await manager.increment_tag_usage("enhancement")
        enh = manager.get_tag_by_name("enhancement")
        assert enh is not None and enh.usage_count == 2

        await manager.merge_tags(id1, [id3, "nonexistent-id"])
        primary = manager.get_tag(id1)
        assert primary is not None
        assert manager.get_tag_by_name("enhancement") is None
        # Primary was 0 usage, enhancement was 2, so primary should be 2 now
        assert primary.usage_count == 2

        # 17) Serialization
        t = primary
        serialized = t.to_dict()
        assert Tag.from_dict(serialized) == t

        # 18) Search tags (indexed)
        # Create some token-rich names/descriptions
        await manager.create_tag("email sending", description="Handles email sending pipeline", category="infra")
        await manager.create_tag("email validation", description="Validates email formats", category="infra")
        res = manager.search_tags("email")
        assert len(res) >= 2
        names = {t.name for t in res}
        assert "email sending" in names
        assert "email validation" in names

        # 19) Bulk create
        bulk_ids = await manager.bulk_create_tags(["task", "urgent", "blocked"], category="workflow")
        assert len(bulk_ids) == 3
        for name in ["task", "urgent", "blocked"]:
            assert manager.get_tag_by_name(name) is not None

        # 20) Statistics after more operations
        st = manager.get_tag_statistics()
        assert st.total_tags >= 4
        assert st.total_categories >= 3
        assert st.total_relationships >= 1

        print("All tests passed.")

    asyncio.run(_run_tests())
