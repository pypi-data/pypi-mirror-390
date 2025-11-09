from __future__ import annotations

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Type, TypeVar, Union
from dataclasses import dataclass, field
import sys


# Exceptions mirroring Rust Result/Error
class TodoziError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class ValidationError(TodoziError):
    pass


# Priority Enum
class SummaryPriority(str, Enum):
    Low = "Low"
    Medium = "Medium"
    High = "High"
    Critical = "Critical"

    @classmethod
    def from_string(cls, s: str) -> SummaryPriority:
        s_lower = s.strip().lower()
        for variant in cls:
            if variant.value.lower() == s_lower:
                return variant
        raise ValueError(f"Invalid SummaryPriority: {s}")


# Summary model
@dataclass
class Summary:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    content: str = ""
    context: Optional[str] = None
    priority: SummaryPriority = SummaryPriority.Medium
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


# SummaryUpdate builder
@dataclass
class SummaryUpdate:
    content: Optional[str] = None
    context: Optional[str] = None
    priority: Optional[SummaryPriority] = None
    tags: Optional[List[str]] = None

    def content_set(self, content: str) -> "SummaryUpdate":
        self.content = content
        return self

    def context_set(self, context: str) -> "SummaryUpdate":
        self.context = context
        return self

    def priority_set(self, priority: SummaryPriority) -> "SummaryUpdate":
        self.priority = priority
        return self

    def tags_set(self, tags: List[str]) -> "SummaryUpdate":
        self.tags = tags
        return self

    # Optional fluent API (Rust-like chaining)
    def with_content(self, content: str) -> "SummaryUpdate":
        return self.content_set(content)

    def with_context(self, context: str) -> "SummaryUpdate":
        return self.context_set(context)

    def with_priority(self, priority: SummaryPriority) -> "SummaryUpdate":
        return self.priority_set(priority)

    def with_tags(self, tags: List[str]) -> "SummaryUpdate":
        return self.tags_set(tags)


# Summary statistics
@dataclass
class SummaryStatistics:
    total_summaries: int
    high_priority_summaries: int
    unique_tags: int

    def high_priority_percentage(self) -> float:
        if self.total_summaries == 0:
            return 0.0
        return (self.high_priority_summaries / self.total_summaries) * 100.0


# Manager
class SummaryManager:
    def __init__(self) -> None:
        self.summaries: Dict[str, Summary] = {}
        self.summary_tags: Dict[str, List[str]] = {}

    # Async-like API in Rust, synchronous in Python
    def create_summary(self, summary: Summary) -> str:
        summary.id = str(uuid.uuid4())
        summary.created_at = datetime.now(timezone.utc)
        summary.updated_at = datetime.now(timezone.utc)
        self.summary_tags[summary.id] = list(summary.tags)
        self.summaries[summary.id] = summary
        return summary.id

    def get_summary(self, summary_id: str) -> Optional[Summary]:
        return self.summaries.get(summary_id)

    def get_all_summaries(self) -> List[Summary]:
        # Return copies to avoid external mutation
        return [s.copy() for s in self.summaries.values()]

    def update_summary(self, summary_id: str, updates: SummaryUpdate) -> None:
        summary = self.summaries.get(summary_id)
        if summary is None:
            raise ValidationError(f"Summary {summary_id} not found")

        if updates.content is not None:
            summary.content = updates.content
        if updates.context is not None:
            summary.context = updates.context
        if updates.priority is not None:
            summary.priority = updates.priority
        if updates.tags is not None:
            summary.tags = list(updates.tags)
            self.summary_tags[summary_id] = list(updates.tags)
        summary.updated_at = datetime.now(timezone.utc)

    def delete_summary(self, summary_id: str) -> None:
        if self.summaries.pop(summary_id, None) is not None:
            self.summary_tags.pop(summary_id, None)
        else:
            raise ValidationError(f"Summary {summary_id} not found")

    def search_summaries(self, query: str) -> List[Summary]:
        q = query.lower()
        results: List[Summary] = []
        for s in self.summaries.values():
            if q in s.content.lower():
                results.append(s.copy())
                continue
            if any(q in tag.lower() for tag in s.tags):
                results.append(s.copy())
                continue
            if s.context is not None and q in s.context.lower():
                results.append(s.copy())
        return results

    def get_summaries_by_priority(self, priority: SummaryPriority) -> List[Summary]:
        return [s.copy() for s in self.summaries.values() if s.priority == priority]

    def get_summaries_by_tag(self, tag: str) -> List[Summary]:
        tag_lower = tag.lower()
        return [s.copy() for s in self.summaries.values() if any(t.lower() == tag_lower for t in s.tags)]

    def get_recent_summaries(self, limit: int) -> List[Summary]:
        # Sort by created_at descending
        sorted_summaries = sorted(
            self.summaries.values(),
            key=lambda s: s.created_at,
            reverse=True,
        )
        return [s.copy() for s in sorted_summaries[:limit]]

    def get_high_priority_summaries(self) -> List[Summary]:
        return [
            s.copy()
            for s in self.summaries.values()
            if s.priority in (SummaryPriority.High, SummaryPriority.Critical)
        ]

    def get_all_tags(self) -> List[str]:
        tags_set: Set[str] = set()
        for tags in self.summary_tags.values():
            for t in tags:
                tags_set.add(t)
        return sorted(tags_set)

    def get_tag_statistics(self) -> Dict[str, int]:
        stats: Dict[str, int] = {}
        for tags in self.summary_tags.values():
            for tag in tags:
                stats[tag] = stats.get(tag, 0) + 1
        return stats

    def get_summary_statistics(self) -> SummaryStatistics:
        total = len(self.summaries)
        high_priority = len(self.get_high_priority_summaries())
        unique_tags = len(self.get_all_tags())
        return SummaryStatistics(
            total_summaries=total,
            high_priority_summaries=high_priority,
            unique_tags=unique_tags,
        )


# Parsing utility
def parse_summary_format(summary_text: str) -> Summary:
    start_tag = "<summary>"
    end_tag = "</summary>"

    start = summary_text.find(start_tag)
    if start == -1:
        raise ValidationError("Missing <summary> start tag")

    end = summary_text.find(end_tag)
    if end == -1:
        raise ValidationError("Missing </summary> end tag")

    if end <= start + len(start_tag):
        raise ValidationError("Invalid summary format: content missing")

    content = summary_text[start + len(start_tag) : end]
    parts = [p.strip() for p in content.split(";")]

    if len(parts) < 2:
        raise ValidationError("Invalid summary format: need at least 2 parts (content; priority)")

    try:
        priority = SummaryPriority.from_string(parts[1])
    except ValueError as e:
        raise ValidationError("Invalid summary priority") from e

    context = parts[2] if len(parts) > 2 and parts[2] else None
    tags = [t.strip() for t in parts[3].split(",")] if len(parts) > 3 and parts[3] else []

    now = datetime.now(timezone.utc)
    return Summary(
        id=str(uuid.uuid4()),
        content=parts[0],
        context=context,
        priority=priority,
        tags=tags,
        created_at=now,
        updated_at=now,
    )


# Simple shallow copy for Summary to avoid shared mutable lists
def _copy_summary(s: Summary) -> Summary:
    # Python's dataclasses.replace creates a shallow copy; ensure lists and optionals are fine
    return Summary(
        id=s.id,
        content=s.content,
        context=s.context,
        priority=s.priority,
        tags=list(s.tags),
        created_at=s.created_at,
        updated_at=s.updated_at,
    )


# Extend Summary with a copy method
if not hasattr(Summary, "copy"):

    def _summary_copy(self: Summary) -> Summary:
        return _copy_summary(self)

    Summary.copy = _summary_copy  # type: ignore


# Tests
def _run_tests() -> None:
    print("Running tests...")

    # Test: SummaryManager creation
    manager = SummaryManager()
    assert len(manager.summaries) == 0
    assert len(manager.summary_tags) == 0

    # Test: SummaryUpdate builder
    upd = SummaryUpdate().content_set("New content").priority_set(SummaryPriority.High)
    assert upd.content == "New content"
    assert upd.priority == SummaryPriority.High
    # also try with fluent
    upd2 = SummaryUpdate().with_content("Another").with_priority(SummaryPriority.Critical)
    assert upd2.content == "Another"
    assert upd2.priority == SummaryPriority.Critical

    # Test: SummaryStatistics high_priority_percentage
    stats = SummaryStatistics(total_summaries=10, high_priority_summaries=3, unique_tags=5)
    assert abs(stats.high_priority_percentage() - 30.0) < 1e-6
    empty = SummaryStatistics(total_summaries=0, high_priority_summaries=0, unique_tags=0)
    assert empty.high_priority_percentage() == 0.0

    # Test: parse_summary_format
    text1 = "<summary>Project completed successfully; high; Final project delivery; project,completion,success</summary>"
    s1 = parse_summary_format(text1)
    assert s1.content == "Project completed successfully"
    assert s1.priority == SummaryPriority.High
    assert s1.context == "Final project delivery"
    assert s1.tags == ["project", "completion", "success"]

    text2 = "<summary>Simple summary; medium</summary>"
    s2 = parse_summary_format(text2)
    assert s2.content == "Simple summary"
    assert s2.priority == SummaryPriority.Medium
    assert s2.context is None
    assert len(s2.tags) == 0

    # Additional: manager operations
    mgr = SummaryManager()
    s = Summary(content="Test", priority=SummaryPriority.Low, tags=["test", "sample"])
    sid = mgr.create_summary(s)
    assert mgr.get_summary(sid) is not None
    assert len(mgr.get_all_summaries()) == 1
    mgr.update_summary(sid, SummaryUpdate().content_set("Updated").tags_set(["updated", "tag"]))
    updated = mgr.get_summary(sid)
    assert updated is not None
    assert updated.content == "Updated"
    assert "updated" in updated.tags
    # search
    found = mgr.search_summaries("Updated")
    assert len(found) == 1
    assert found[0].id == sid
    # by priority
    by_p = mgr.get_summaries_by_priority(SummaryPriority.Low)
    assert len(by_p) == 1  # Summary still has Low priority after update (priority wasn't changed)
    assert by_p[0].id == sid
    by_p2 = mgr.get_summaries_by_priority(SummaryPriority.High)
    assert len(by_p2) == 0  # No High priority summaries created
    # by tag
    by_tag = mgr.get_summaries_by_tag("updated")
    assert len(by_tag) == 1
    # recent
    recent = mgr.get_recent_summaries(5)
    assert len(recent) == 1
    # high priority
    hp = mgr.get_high_priority_summaries()
    assert len(hp) == 0
    # stats
    stats2 = mgr.get_summary_statistics()
    assert stats2.total_summaries == 1
    assert stats2.unique_tags == 2
    # all tags
    tags_all = mgr.get_all_tags()
    assert "updated" in tags_all and "tag" in tags_all
    # tag stats
    tag_stats = mgr.get_tag_statistics()
    assert tag_stats["updated"] == 1
    assert tag_stats["tag"] == 1
    # delete
    mgr.delete_summary(sid)
    assert mgr.get_summary(sid) is None

    print("All tests passed!")


if __name__ == "__main__":
    try:
        _run_tests()
    except Exception as e:
        print("Test failed:", e, file=sys.stderr)
        raise
