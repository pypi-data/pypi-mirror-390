from __future__ import annotations

import asyncio
import uuid
import threading
from collections import defaultdict
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Union, Literal
from dataclasses import dataclass, field, asdict
from typing_extensions import TypeAlias

# Thread safety
_lock = threading.Lock()

# =============================================================================
# Errors
# =============================================================================

class TodoziError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)

# =============================================================================
# Enumerations and Data Models
# =============================================================================

class MemoryImportance(Enum):
    Low = auto()
    Medium = auto()
    High = auto()
    Critical = auto()

class MemoryTerm(Enum):
    Short = auto()
    Long = auto()

# Using union type approach for memory type
MemoryTypeUnion: TypeAlias = Union[
    Literal["Standard", "Secret", "Human", "Short", "Long"],
    'EmotionalMemoryType'
]

@dataclass(frozen=True)  # Make immutable
class EmotionalMemoryType:
    emotion: str
    
    def __post_init__(self) -> None:
        # Validation in post-init
        EMOTIONS = [
            "happy", "sad", "angry", "fearful", "surprised", "disgusted", "excited",
            "anxious", "confident", "frustrated", "motivated", "overwhelmed", "curious",
            "satisfied", "disappointed", "grateful", "proud", "ashamed", "hopeful",
            "resigned"
        ]
        if self.emotion not in EMOTIONS:
            raise ValueError(f"Invalid emotion: {self.emotion}")

    def __repr__(self) -> str:
        return f"EmotionalMemoryType(emotion={self.emotion!r})"


EMOTIONS = [
    "happy", "sad", "angry", "fearful", "surprised", "disgusted", "excited",
    "anxious", "confident", "frustrated", "motivated", "overwhelmed", "curious",
    "satisfied", "disappointed", "grateful", "proud", "ashamed", "hopeful",
    "resigned"
]


@dataclass
class Memory:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    project_id: Optional[str] = None
    status: str = "Active"
    moment: str = ""
    meaning: str = ""
    reason: str = ""
    importance: MemoryImportance = MemoryImportance.Medium
    term: MemoryTerm = MemoryTerm.Short
    memory_type: MemoryTypeUnion = "Standard"
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __str__(self) -> str:
        return f"Memory(id={self.id}, moment={self.moment[:20]}...)"
    
    def __repr__(self) -> str:
        return (f"Memory(id={self.id!r}, user_id={self.user_id!r}, "
                f"moment={self.moment!r}, meaning={self.meaning!r}, "
                f"reason={self.reason!r}, importance={self.importance!r}, "
                f"term={self.term!r}, memory_type={self.memory_type!r}, "
                f"tags={self.tags!r}, created_at={self.created_at!r})")

@dataclass
class MemoryUpdate:
    moment: Optional[str] = None
    meaning: Optional[str] = None
    reason: Optional[str] = None
    importance: Optional[MemoryImportance] = None
    term: Optional[MemoryTerm] = None
    tags: Optional[List[str]] = None

    @classmethod
    def builder(cls) -> "MemoryUpdate":
        return cls()

@dataclass
class MemoryStatistics:
    total_memories: int
    short_term_memories: int
    long_term_memories: int
    critical_memories: int
    unique_tags: int
    secret_memories: int
    human_memories: int
    emotional_memories: int
    standard_memories: int

    @property
    def short_term_percentage(self) -> float:
        return 0.0 if self.total_memories == 0 else (self.short_term_memories / self.total_memories) * 100.0

    @property
    def long_term_percentage(self) -> float:
        return 0.0 if self.total_memories == 0 else (self.long_term_memories / self.total_memories) * 100.0

    @property
    def critical_percentage(self) -> float:
        return 0.0 if self.total_memories == 0 else (self.critical_memories / self.total_memories) * 100.0

    def __str__(self) -> str:
        return f"MemoryStatistics(total={self.total_memories}, critical={self.critical_memories})"

# =============================================================================
# Memory Manager with Optimizations
# =============================================================================

class MemoryManager:
    def __init__(self) -> None:
        self.memories: Dict[str, Memory] = {}
        self.memory_tags: Dict[str, List[str]] = {}
        self.search_index: Dict[str, Set[str]] = defaultdict(set)  # word -> memory_ids
        
    def _update_search_index(self, memory_id: str, memory: Memory) -> None:
        # Remove old entry if exists
        for word_set in self.search_index.values():
            word_set.discard(memory_id)
        
        # Create searchable text
        searchable_text = " ".join([
            memory.moment.lower(),
            memory.meaning.lower(),
            memory.reason.lower(),
            " ".join(tag.lower() for tag in memory.tags)
        ])
        
        # Update index
        for word in searchable_text.split():
            self.search_index[word].add(memory_id)

    async def create_memory(self, memory: Memory) -> str:
        async with asyncio.Lock():  # Use asyncio.Lock for async context
            # Generate ID only if not provided
            if not memory.id:
                memory.id = str(uuid.uuid4())
            
            memory.created_at = datetime.now(timezone.utc)
            memory.updated_at = memory.created_at
            
            self.memory_tags[memory.id] = list(memory.tags)
            self.memories[memory.id] = memory
            self._update_search_index(memory.id, memory)
            
            return memory.id

    def get_memory(self, memory_id: str) -> Optional[Memory]:
        with _lock:  # Thread safety for read operations
            return self.memories.get(memory_id)

    def get_all_memories(self) -> List[Memory]:
        with _lock:
            return list(self.memories.values())

    async def update_memory(self, memory_id: str, updates: MemoryUpdate) -> Memory:
        async with asyncio.Lock():
            if memory := self.memories.get(memory_id):
                # Create updated memory with functional approach
                updated_data = asdict(memory)
                
                if updates.moment is not None:
                    updated_data["moment"] = updates.moment
                if updates.meaning is not None:
                    updated_data["meaning"] = updates.meaning
                if updates.reason is not None:
                    updated_data["reason"] = updates.reason
                if updates.importance is not None:
                    updated_data["importance"] = updates.importance
                if updates.term is not None:
                    updated_data["term"] = updates.term
                if updates.tags is not None:
                    updated_data["tags"] = list(updates.tags)
                
                updated_data["updated_at"] = datetime.now(timezone.utc)
                
                # Create new memory object
                updated_memory = Memory(**updated_data)
                self.memories[memory_id] = updated_memory
                self.memory_tags[memory_id] = list(updated_data["tags"])
                self._update_search_index(memory_id, updated_memory)
                
                return updated_memory
            else:
                raise TodoziError(f"Memory {memory_id} not found")

    async def delete_memory(self, memory_id: str) -> None:
        async with asyncio.Lock():
            if self.memories.remove(memory_id) if hasattr(dict, 'remove') else self.memories.pop(memory_id, None) is not None:
                self.memory_tags.pop(memory_id, None)
                # Update search index
                for word_set in self.search_index.values():
                    word_set.discard(memory_id)
            else:
                raise TodoziError(f"Memory {memory_id} not found")

    def search_memories(self, query: str) -> List[Memory]:
        # Optimized search using pre-built index
        query_words = query.lower().split()
        matching_ids: Set[str] = set()
        
        for word in query_words:
            matching_ids.update(self.search_index.get(word, set()))
        
        with _lock:
            return [mem for mem_id, mem in self.memories.items() if mem_id in matching_ids]

    def get_memories_by_importance(self, importance: MemoryImportance) -> List[Memory]:
        with _lock:
            return [m for m in self.memories.values() if m.importance == importance]

    def get_memories_by_term(self, term: MemoryTerm) -> List[Memory]:
        with _lock:
            return [m for m in self.memories.values() if m.term == term]

    def get_memories_by_tag(self, tag: str) -> List[Memory]:
        tag_lower = tag.lower()
        with _lock:
            return [m for m in self.memories.values() 
                   if any(t.lower() == tag_lower for t in m.tags)]

    def get_recent_memories(self, limit: int) -> List[Memory]:
        with _lock:
            memories = list(self.memories.values())
            memories.sort(key=lambda m: m.created_at, reverse=True)
            return memories[:limit]

    def get_critical_memories(self) -> List[Memory]:
        with _lock:
            return [m for m in self.memories.values() 
                   if m.importance in (MemoryImportance.High, MemoryImportance.Critical)]

    def get_short_term_memories(self) -> List[Memory]:
        with _lock:
            return [m for m in self.memories.values() if m.term == MemoryTerm.Short]

    def get_long_term_memories(self) -> List[Memory]:
        with _lock:
            return [m for m in self.memories.values() if m.term == MemoryTerm.Long]

    def get_memories_by_type(self, memory_type: MemoryTypeUnion) -> List[Memory]:
        with _lock:
            return [m for m in self.memories.values() if m.memory_type == memory_type]

    def get_secret_memories(self) -> List[Memory]:
        return self.get_memories_by_type("Secret")

    def get_human_memories(self) -> List[Memory]:
        return self.get_memories_by_type("Human")

    def get_emotional_memories(self, emotion: str) -> List[Memory]:
        target = EmotionalMemoryType(emotion)
        with _lock:
            return [m for m in self.memories.values() if m.memory_type == target]

    def get_all_tags(self) -> List[str]:
        with _lock:
            all_tags = set()
            for tags in self.memory_tags.values():
                all_tags.update(tags)
            return sorted(all_tags)

    def get_tag_statistics(self) -> Dict[str, int]:
        with _lock:
            stats: Dict[str, int] = defaultdict(int)
            for tags in self.memory_tags.values():
                for tag in tags:
                    stats[tag] += 1
            return dict(stats)

    def get_memory_statistics(self) -> MemoryStatistics:
        with _lock:
            total_memories = len(self.memories)
            short_term = len([m for m in self.memories.values() if m.term == MemoryTerm.Short])
            long_term = len([m for m in self.memories.values() if m.term == MemoryTerm.Long])
            critical = len([m for m in self.memories.values() 
                           if m.importance in (MemoryImportance.High, MemoryImportance.Critical)])
            unique_tags = len(self.get_all_tags())
            secret = len([m for m in self.memories.values() if m.memory_type == "Secret"])
            human = len([m for m in self.memories.values() if m.memory_type == "Human"])
            standard = len([m for m in self.memories.values() if m.memory_type == "Standard"])
            
            # Efficient emotional count in single pass
            emotional = len([m for m in self.memories.values() 
                            if isinstance(m.memory_type, EmotionalMemoryType)])

            return MemoryStatistics(
                total_memories=total_memories,
                short_term_memories=short_term,
                long_term_memories=long_term,
                critical_memories=critical,
                unique_tags=unique_tags,
                secret_memories=secret,
                human_memories=human,
                emotional_memories=emotional,
                standard_memories=standard,
            )

# =============================================================================
# Robust Parser with Improved Error Handling
# =============================================================================

def parse_memory_format(memory_text: str, user_id: str) -> Memory:
    start_tag = "<memory>"
    end_tag = "</memory>"
    
    # More robust error handling
    if start_tag not in memory_text:
        raise TodoziError("Missing <memory> start tag")
    if end_tag not in memory_text:
        raise TodoziError("Missing </memory> end tag")

    start_idx = memory_text.find(start_tag) + len(start_tag)
    end_idx = memory_text.find(end_tag)
    content = memory_text[start_idx:end_idx].strip()
    
    parts = [p.strip() for p in content.split(";")]
    if len(parts) < 6:
        raise TodoziError(
            "Invalid memory format: need at least 6 parts (type; moment; meaning; reason; importance; term)"
        )

    # More robust parsing with mappings
    importance_map = {
        "low": MemoryImportance.Low,
        "medium": MemoryImportance.Medium, 
        "high": MemoryImportance.High,
        "critical": MemoryImportance.Critical
    }
    
    term_map = {
        "short": MemoryTerm.Short,
        "long": MemoryTerm.Long,
    }
    
    # Parse memory type with emotion detection
    memory_type_str = parts[0].strip().lower()
    if memory_type_str in ["happy", "sad", "angry", "fearful", "surprised", "disgusted", "excited",
                          "anxious", "confident", "frustrated", "motivated", "overwhelmed", "curious",
                          "satisfied", "disappointed", "grateful", "proud", "ashamed", "hopeful",
                          "resigned"]:
        memory_type = EmotionalMemoryType(memory_type_str)
    else:
        type_map = {
            "standard": "Standard",
            "secret": "Secret", 
            "human": "Human",
            "short": "Short",
            "long": "Long"
        }
        memory_type = type_map.get(memory_type_str, "Standard")

    # Parse tags if present
    tags = []
    if len(parts) > 6 and parts[6]:
        tags = [t.strip() for t in parts[6].split(",") if t.strip()]

    # Robust importance and term parsing
    try:
        importance = importance_map.get(parts[4].strip().lower())
        if importance is None:
            raise ValueError("Invalid memory importance")
    except Exception:
        raise TodoziError("Invalid memory importance")
    
    try:
        term = term_map.get(parts[5].strip().lower())
        if term is None:
            raise ValueError("Invalid memory term")
    except Exception:
        raise TodoziError("Invalid memory term")

    now = datetime.now(timezone.utc)
    return Memory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        project_id=None,
        status="Active",
        moment=parts[1],
        meaning=parts[2], 
        reason=parts[3],
        importance=importance,
        term=term,
        memory_type=memory_type,
        tags=tags,
        created_at=now,
        updated_at=now,
    )

# =============================================================================
# Comprehensive Tests
# =============================================================================

def _run_tests() -> None:
    # Synchronous test
    def test_memory_manager_creation():
        manager = MemoryManager()
        assert len(manager.memories) == 0
        assert len(manager.memory_tags) == 0
        assert len(manager.search_index) == 0

    # Test builder pattern
    def test_memory_update_builder():
        update = MemoryUpdate.builder()
        assert update is not None
        assert isinstance(update, MemoryUpdate)
    
    # Test statistics with properties
    def test_memory_statistics_percentages():
        stats = MemoryStatistics(
            total_memories=10,
            short_term_memories=6,
            long_term_memories=4,
            critical_memories=2,
            unique_tags=8,
            secret_memories=1,
            human_memories=2,
            emotional_memories=3,
            standard_memories=4,
        )
        assert abs(stats.short_term_percentage - 60.0) < 1e-6
        assert abs(stats.long_term_percentage - 40.0) < 1e-6
        assert abs(stats.critical_percentage - 20.0) < 1e-6

        empty_stats = MemoryStatistics(
            total_memories=0,
            short_term_memories=0,
            long_term_memories=0,
            critical_memories=0,
            unique_tags=0,
            secret_memories=0,
            human_memories=0,
            emotional_memories=0,
            standard_memories=0,
        )
        assert empty_stats.short_term_percentage == 0.0
        assert empty_stats.long_term_percentage == 0.0
        assert empty_stats.critical_percentage == 0.0

    # Test robust parser
    def test_parse_memory_format():
        memory_text = "<memory>standard; 2025-01-13 10:30 AM; Client prefers iterative development; Affects testing cycle; high; long; client,development,iterative</memory>"
        memory = parse_memory_format(memory_text, "user_123")
        assert memory.moment == "2025-01-13 10:30 AM"
        assert memory.meaning == "Client prefers iterative development"
        assert memory.reason == "Affects testing cycle"
        assert memory.importance == MemoryImportance.High
        assert memory.term == MemoryTerm.Long
        assert memory.memory_type == "Standard"
        assert memory.tags == ["client", "development", "iterative"]
        
        # Test emotional memory
        emotional_text = "<memory>happy; Great news!; Meeting went well; Good vibes; medium; short; celebration,success</memory>"
        emotional_memory = parse_memory_format(emotional_text, "user_456")
        assert isinstance(emotional_memory.memory_type, EmotionalMemoryType)
        assert emotional_memory.memory_type.emotion == "happy"

    # Async integration test
    async def test_async_operations():
        mm = MemoryManager()
        mem = Memory(
            user_id="u1",
            moment="A test moment",
            meaning="A meaning",
            reason="Because",
            importance=MemoryImportance.Medium,
            term=MemoryTerm.Short,
            tags=["test", "unit"],
        )
        mem_id = await mm.create_memory(mem)
        fetched = mm.get_memory(mem_id)
        assert fetched is not None
        assert fetched.id == mem_id

        # Test functional update
        updated = await mm.update_memory(mem_id, 
            MemoryUpdate(moment="Updated moment", tags=["updated", "test"]))
        assert updated.moment == "Updated moment"
        assert "updated" in updated.tags

        # Test search optimization
        search_results = mm.search_memories("test")
        assert len(search_results) > 0

        # Test statistics
        stats = mm.get_memory_statistics()
        assert stats.total_memories > 0
        
        # Test deletion
        await mm.delete_memory(mem_id)
        assert mm.get_memory(mem_id) is None

    # Run tests
    test_memory_manager_creation()
    test_memory_update_builder()
    test_memory_statistics_percentages() 
    test_parse_memory_format()
    asyncio.run(test_async_operations())
    print("All tests passed with optimizations!")

if __name__ == "__main__":
    _run_tests()
