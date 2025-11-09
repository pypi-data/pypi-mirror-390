# todozi_embedding.py
# Fully working Python translation of the Rust embedding service using sentence-transformers.
# Requirements:
#   pip install sentence-transformers torch transformers tokenizers pydantic datetime uuid tqdm

from __future__ import annotations

import os
import uuid
import json
import time
import math
import shutil
import random
from collections import deque, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Set

import numpy as np

# Optional ML backend for embeddings
SENTENCE_TRANSFORMERS_AVAILABLE = True
try:
    from sentence_transformers import SentenceTransformer, util  # type: ignore
except Exception:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# --------------- Enums and Constants ---------------

class TodoziContentType:
    Task = "Task"
    Tag = "Tag"
    Memory = "Memory"
    Idea = "Idea"
    Chunk = "Chunk"
    Feel = "Feel"
    Train = "Train"
    Error = "Error"
    Summary = "Summary"
    Reminder = "Reminder"
    Tdz = "Tdz"


class Priority:
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class Status:
    TODO = "todo"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    REVIEW = "review"
    DONE = "done"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    DEFERRED = "deferred"


# --------------- Configuration and Data Models ---------------

@dataclass
class TodoziEmbeddingConfig:
    model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    dimensions: int = 384
    similarity_threshold: float = 0.7
    max_results: int = 50
    cache_ttl_seconds: int = 3600 * 24
    enable_clustering: bool = True
    clustering_threshold: float = 0.8


@dataclass
class TodoziEmbeddingCache:
    vector: List[float]
    content_type: str
    content_id: str
    text_content: str
    tags: List[str]
    created_at: datetime
    ttl_seconds: int


@dataclass
class SimilarityResult:
    content_id: str
    content_type: str
    similarity_score: float
    text_content: str
    tags: List[str]
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClusteringResult:
    cluster_id: str
    content_items: List[SimilarityResult]
    cluster_center: List[float]
    cluster_size: int
    average_similarity: float


class AggregationType:
    AVERAGE = "Average"
    MAX = "Max"
    MIN = "Min"
    WEIGHTED = "Weighted"


@dataclass
class SearchFilters:
    tags: Optional[List[str]] = None
    priority: Optional[List[str]] = None
    status: Optional[List[str]] = None
    assignee: Optional[List[str]] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_progress: Optional[int] = None
    max_progress: Optional[int] = None


@dataclass
class HierarchicalCluster:
    cluster_id: str
    level: int
    content_items: List[SimilarityResult]
    cluster_center: List[float]
    children: List["HierarchicalCluster"]
    parent_id: Optional[str]
    average_similarity: float


@dataclass
class LabeledCluster:
    cluster_id: str
    label: str
    description: Optional[str]
    confidence: float
    content_items: List[SimilarityResult]


@dataclass
class DriftReport:
    content_id: str
    current_similarity_to_original: float
    drift_percentage: float
    significant_drift: bool
    history: List["DriftSnapshot"]


@dataclass
class DriftSnapshot:
    timestamp: datetime
    similarity_to_original: float
    text_sample: str


@dataclass
class SimilarityGraph:
    nodes: List["GraphNode"]
    edges: List["GraphEdge"]


@dataclass
class GraphNode:
    id: str
    content_type: str
    label: str
    metadata: Dict[str, Any]


@dataclass
class GraphEdge:
    from_id: str
    to_id: str
    similarity: float
    bidirectional: bool


@dataclass
class ModelComparisonResult:
    text: str
    models: Dict[str, "ModelEmbeddingResult"]


@dataclass
class ModelEmbeddingResult:
    model_name: str
    embedding: List[float]
    dimensions: int
    generation_time_ms: int


@dataclass
class ValidationReport:
    total_embeddings: int
    invalid_embeddings: int
    nan_count: int
    infinity_count: int
    zero_vector_count: int
    abnormal_distributions: List[str]
    issues: List["ValidationIssue"]


@dataclass
class ValidationIssue:
    content_id: str
    issue_type: str
    severity: str
    description: str


@dataclass
class PerformanceMetrics:
    query: str
    iterations: int
    avg_time_ms: float
    min_time_ms: int
    max_time_ms: int
    std_dev_ms: float
    results_per_iteration: int


@dataclass
class DiagnosticReport:
    timestamp: datetime
    cache_hit_rate: float
    avg_similarity_score: float
    embedding_distribution_stats: "EmbeddingStats"
    content_type_breakdown: Dict[str, int]
    top_similar_pairs: List[Tuple[str, str, float]]


@dataclass
class EmbeddingStats:
    mean: List[float]
    std_dev: List[float]
    min: List[float]
    max: List[float]


# --------------- Simple LRU Cache ---------------

class LRUEmbeddingCache:
    def __init__(self, max_memory_mb: int):
        self.max_memory_mb: int = max_memory_mb
        self.cache: deque[Tuple[str, TodoziEmbeddingCache]] = deque()
        self.access_counts: Dict[str, int] = defaultdict(int)
        self.current_memory_bytes: int = 0

    @staticmethod
    def _estimate_size(entry: TodoziEmbeddingCache) -> int:
        # Rough estimate: vector size + text + overhead
        return len(entry.vector) * 4 + len(entry.text_content) + 200

    def get(self, key: str) -> Optional[TodoziEmbeddingCache]:
        # Update access count
        self.access_counts[key] += 1

        # Find and move to front
        for i, (k, v) in enumerate(self.cache):
            if k == key:
                item = self.cache.remove((k, v))
                self.cache.appendleft((k, v))  # type: ignore
                return v
        return None

    def insert(self, key: str, value: TodoziEmbeddingCache):
        entry_size = self._estimate_size(value)

        # Evict if needed
        while (self.current_memory_bytes + entry_size) > self.max_memory_mb * 1024 * 1024 and self.cache:
            old_key, old_value = self.cache.pop()
            self.current_memory_bytes -= self._estimate_size(old_value)
            del self.access_counts[old_key]

        self.cache.appendleft((key, value))
        self.current_memory_bytes += entry_size
        self.access_counts[key] += 1

    def len(self) -> int:
        return len(self.cache)

    def is_empty(self) -> bool:
        return len(self.cache) == 0

    def items(self):
        return list(self.cache)


# --------------- Core Embedding Model (Python) ---------------

class EmbeddingModel:
    def __init__(self, model_name: str, device: str = "cpu"):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise RuntimeError(
                "sentence-transformers is required for EmbeddingModel. "
                "Install with: pip install sentence-transformers torch"
            )
        self.model_name = model_name
        self.device = device
        self._model: Optional[SentenceTransformer] = None
        self.dimensions: Optional[int] = None

    def _ensure_model(self):
        if self._model is None:
            # Use local model cache in user cache dir
            cache_folder = os.path.expanduser("~/.cache/todozi/models")
            os.makedirs(cache_folder, exist_ok=True)
            self._model = SentenceTransformer(self.model_name, cache_folder=cache_folder)
            # Infer dimensions from a dummy embedding
            dummy = self._model.encode(["hello"])
            self.dimensions = int(dummy.shape[1])

    def encode(self, texts: List[str]) -> List[List[float]]:
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            # Fallback: random normalized vectors (for demo only)
            rng = np.random.default_rng(abs(hash((self.model_name, tuple(texts)))))
            vectors = rng.normal(size=(len(texts), self.dimensions or 384)).astype(np.float32)
            # L2 normalize rows
            norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10
            vectors = (vectors / norms).tolist()
            return vectors

        self._ensure_model()
        assert self._model is not None
        vectors = self._model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)
        # Ensure dtype float32
        if vectors.dtype != np.float32:
            vectors = vectors.astype(np.float32)
        return [v.tolist() for v in vectors]

    def encode_single(self, text: str) -> List[float]:
        return self.encode([text])[0]


# --------------- Simplified Storage and Tag Manager ---------------

@dataclass
class Project:
    name: str
    description: Optional[str] = None


@dataclass
class Task:
    id: str
    action: str
    parent_project: str
    priority: str = Priority.MEDIUM
    status: str = Status.TODO
    tags: List[str] = field(default_factory=list)
    time: Optional[float] = None
    assignee: Optional[str] = None
    context_notes: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    progress: Optional[int] = None
    embedding_vector: Optional[List[float]] = None


@dataclass
class TaskUpdate:
    action: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    assignee: Optional[str] = None
    context_notes: Optional[str] = None
    dependencies: Optional[List[str]] = None
    progress: Optional[int] = None
    embedding_vector: Optional[List[float]] = None


@dataclass
class Tag:
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    color: Optional[str] = None
    usage_count: int = 0


@dataclass
class Idea:
    id: str
    idea: str
    importance: Optional[str] = None
    share: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    context: Optional[str] = None


@dataclass
class Memory:
    id: str
    moment: str
    meaning: str
    reason: str
    importance: Optional[str] = None
    term: Optional[str] = None
    memory_type: Optional[str] = None
    tags: List[str] = field(default_factory=list)


class TaskFilters:
    def __init__(self):
        pass


class TagManager:
    def __init__(self):
        self.tags: Dict[str, Tag] = {}

    def upsert(self, tag: Tag):
        self.tags[tag.id] = tag


class Storage:
    def __init__(self):
        self.projects: Dict[str, Project] = {}
        self.tasks: Dict[str, Task] = {}
        self.tasks_by_project: Dict[str, List[str]] = defaultdict(list)

    async def create_project(self, name: str, description: Optional[str]) -> str:
        self.projects[name] = Project(name=name, description=description)
        return name

    async def add_task_to_project(self, task: Task):
        self.tasks[task.id] = task
        self.tasks_by_project[task.parent_project].append(task.id)

    async def update_task_in_project(self, task_id: str, updates: TaskUpdate):
        task = self.tasks.get(task_id)
        if task is None:
            raise KeyError(f"Task not found: {task_id}")
        if updates.action is not None:
            task.action = updates.action
        if updates.priority is not None:
            task.priority = updates.priority
        if updates.status is not None:
            task.status = updates.status
        if updates.tags is not None:
            task.tags = updates.tags
        if updates.assignee is not None:
            task.assignee = updates.assignee
        if updates.context_notes is not None:
            task.context_notes = updates.context_notes
        if updates.dependencies is not None:
            task.dependencies = updates.dependencies
        if updates.progress is not None:
            task.progress = updates.progress
        if updates.embedding_vector is not None:
            task.embedding_vector = updates.embedding_vector

    def get_project(self, name: str) -> Project:
        if name not in self.projects:
            raise KeyError(f"Project not found: {name}")
        return self.projects[name]

    def get_task_from_any_project(self, task_id: str) -> Task:
        if task_id not in self.tasks:
            raise KeyError(f"Task not found: {task_id}")
        return self.tasks[task_id]

    def list_tasks_across_projects(self, _filters: TaskFilters) -> List[Task]:
        return list(self.tasks.values())


# --------------- Embedding Service ---------------

class TodoziEmbeddingService:
    def __init__(
        self,
        config: TodoziEmbeddingConfig,
        tag_manager: Optional[TagManager] = None,
        storage: Optional[Storage] = None,
    ):
        self.config = config
        self.tag_manager = tag_manager or TagManager()
        self.storage = storage or Storage()
        self.cache: Dict[str, TodoziEmbeddingCache] = {}
        self._embedding_model: Optional[EmbeddingModel] = None
        self._embedding_models: Dict[str, EmbeddingModel] = {}

    # ------------- Model Loading and Defaults -------------

    async def initialize(self, device: str = "cpu"):
        model_name = self.config.model_name
        self._embedding_model = EmbeddingModel(model_name=model_name, device=device)

    @staticmethod
    def _get_todozi_dir() -> str:
        # Roughly equivalent to Rust find_todozi(None)
        home = Path.home()
        candidates = [
            home / ".todozi",
            home / ".tdz",
            home / ".config" / "todozi",
            Path.cwd() / ".todozi",
        ]
        for c in candidates:
            c.mkdir(parents=True, exist_ok=True)
            # Just pick the first writable candidate
            return str(c)
        return str(home / ".todozi")

    # ------------- Embedding and Content Preparation -------------

    def prepare_task_content(self, task: Task) -> str:
        parts = [f"Task: {task.action}"]
        if task.context_notes:
            parts.append(f"Description: {task.context_notes}")
        parts.append(f"Priority: {task.priority}")
        parts.append(f"Status: {task.status}")
        if task.tags:
            parts.append(f"Tags: {', '.join(task.tags)}")
        if task.assignee:
            parts.append(f"Assignee: {task.assignee}")
        if task.progress is not None:
            parts.append(f"Progress: {task.progress}%")
        return "\n".join(parts)

    def prepare_tag_content(self, tag: Tag) -> str:
        parts = [f"Tag: {tag.name}"]
        if tag.description:
            parts.append(f"Description: {tag.description}")
        if tag.category:
            parts.append(f"Category: {tag.category}")
        if tag.color:
            parts.append(f"Color: {tag.color}")
        parts.append(f"Usage Count: {tag.usage_count}")
        return "\n".join(parts)

    def prepare_idea_content(self, idea: Idea) -> str:
        parts = [f"Idea: {idea.idea}"]
        if idea.importance:
            parts.append(f"Importance: {idea.importance}")
        if idea.share:
            parts.append(f"Share Level: {idea.share}")
        if idea.tags:
            parts.append(f"Tags: {', '.join(idea.tags)}")
        if idea.context:
            parts.append(f"Context: {idea.context}")
        return "\n".join(parts)

    def prepare_memory_content(self, memory: Memory) -> str:
        parts = [
            f"Memory: {memory.moment}",
            f"Meaning: {memory.meaning}",
            f"Reason: {memory.reason}",
        ]
        if memory.importance:
            parts.append(f"Importance: {memory.importance}")
        if memory.term:
            parts.append(f"Term: {memory.term}")
        if memory.memory_type:
            parts.append(f"Type: {memory.memory_type}")
        if memory.tags:
            parts.append(f"Tags: {', '.join(memory.tags)}")
        return "\n".join(parts)

    async def generate_embedding(self, text: str) -> List[float]:
        if self._embedding_model is None:
            await self.initialize()
        assert self._embedding_model is not None
        return self._embedding_model.encode_single(text)

    async def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        if self._embedding_model is None:
            await self.initialize()
        assert self._embedding_model is not None
        return self._embedding_model.encode(texts)

    # ------------- Project and Task Ops -------------

    async def create_project(self, name: str, description: Optional[str] = None) -> str:
        return await self.storage.create_project(name, description)

    async def add_task(self, task: Task) -> str:
        # Auto-create project if it doesn't exist
        if task.parent_project:
            try:
                self.storage.get_project(task.parent_project)
            except Exception:
                await self.storage.create_project(task.parent_project, None)

        embedding = await self.generate_embedding(self.prepare_task_content(task))
        task.embedding_vector = embedding
        await self.storage.add_task_to_project(task)

        # Log to "mega" file
        await self._log_to_mega_file(task)
        return task.id

    async def update_task(self, id: str, updates: TaskUpdate) -> None:
        await self.storage.update_task_in_project(id, updates)

    async def get_task(self, id: str) -> Task:
        return self.storage.get_task_from_any_project(id)

    # ------------- Embedding Caching Helpers -------------

    async def get_or_generate_embedding(
        self,
        content_id: str,
        text: str,
        content_type: str,
        refresh_if_stale: bool = False,
    ) -> List[float]:
        key = f"{content_type}_{content_id}"
        now = datetime.now(timezone.utc)
        cached = self.cache.get(key)
        if cached:
            expiry = cached.created_at + timedelta(seconds=cached.ttl_seconds)
            if expiry > now:
                return cached.vector
            if not refresh_if_stale:
                return cached.vector

        embedding = await self.generate_embedding(text)
        entry = TodoziEmbeddingCache(
            vector=embedding,
            content_type=content_type,
            content_id=content_id,
            text_content=text,
            tags=[],
            created_at=now,
            ttl_seconds=self.config.cache_ttl_seconds,
        )
        self.cache[key] = entry
        return embedding

    async def embed_tag(self, tag: Tag) -> str:
        content = self.prepare_tag_content(tag)
        embedding = await self.generate_embedding(content)
        now = datetime.now(timezone.utc)
        entry = TodoziEmbeddingCache(
            vector=embedding,
            content_type=TodoziContentType.Tag,
            content_id=tag.id,
            text_content=content,
            tags=[tag.name],
            created_at=now,
            ttl_seconds=self.config.cache_ttl_seconds,
        )
        self.cache[f"tag_{tag.id}"] = entry
        return tag.id

    async def embed_idea(self, idea: Idea) -> str:
        content = self.prepare_idea_content(idea)
        embedding = await self.generate_embedding(content)
        now = datetime.now(timezone.utc)
        entry = TodoziEmbeddingCache(
            vector=embedding,
            content_type=TodoziContentType.Idea,
            content_id=idea.id,
            text_content=content,
            tags=idea.tags[:],
            created_at=now,
            ttl_seconds=self.config.cache_ttl_seconds,
        )
        self.cache[f"idea_{idea.id}"] = entry
        return idea.id

    async def embed_memory(self, memory: Memory) -> str:
        content = self.prepare_memory_content(memory)
        embedding = await self.generate_embedding(content)
        now = datetime.now(timezone.utc)
        entry = TodoziEmbeddingCache(
            vector=embedding,
            content_type=TodoziContentType.Memory,
            content_id=memory.id,
            text_content=content,
            tags=memory.tags[:],
            created_at=now,
            ttl_seconds=self.config.cache_ttl_seconds,
        )
        self.cache[f"memory_{memory.id}"] = entry
        return memory.id

    # ------------- Similarity and Search -------------

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        if len(a) != len(b) or not a or not b:
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return float(dot / (norm_a * norm_b))

    async def find_similar_tasks(
        self, task_description: str, limit: Optional[int] = None
    ) -> List[SimilarityResult]:
        query_embedding = await self.generate_embedding(task_description)
        limit = limit or self.config.max_results
        results: List[SimilarityResult] = []
        for task in self.storage.list_tasks_across_projects(TaskFilters()):
            if task.embedding_vector:
                sim = self._cosine_similarity(query_embedding, task.embedding_vector)
                if sim >= self.config.similarity_threshold:
                    results.append(
                        SimilarityResult(
                            content_id=task.id,
                            content_type=TodoziContentType.Task,
                            similarity_score=sim,
                            text_content=self.prepare_task_content(task),
                            tags=task.tags[:],
                            metadata={},
                        )
                    )
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results[:limit]

    async def find_similar_tags(
        self, tag_name: str, limit: Optional[int] = None
    ) -> List[SimilarityResult]:
        query_embedding = await self.generate_embedding(tag_name)
        limit = limit or self.config.max_results
        results: List[SimilarityResult] = []
        for key, entry in self.cache.items():
            if entry.content_type == TodoziContentType.Tag:
                sim = self._cosine_similarity(query_embedding, entry.vector)
                if sim >= self.config.similarity_threshold:
                    results.append(
                        SimilarityResult(
                            content_id=entry.content_id,
                            content_type=entry.content_type,
                            similarity_score=sim,
                            text_content=entry.text_content,
                            tags=entry.tags[:],
                            metadata={},
                        )
                    )
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results[:limit]

    async def semantic_search(
        self,
        query: str,
        content_types: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> List[SimilarityResult]:
        query_embedding = await self.generate_embedding(query)
        limit = limit or self.config.max_results
        results: List[SimilarityResult] = []
        for entry in self.cache.values():
            if content_types and entry.content_type not in content_types:
                continue
            sim = self._cosine_similarity(query_embedding, entry.vector)
            if sim >= self.config.similarity_threshold:
                results.append(
                    SimilarityResult(
                        content_id=entry.content_id,
                        content_type=entry.content_type,
                        similarity_score=sim,
                        text_content=entry.text_content,
                        tags=entry.tags[:],
                        metadata={},
                    )
                )
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results[:limit]

    # ------------- Clustering -------------

    async def cluster_content(self) -> List[ClusteringResult]:
        if not self.config.enable_clustering:
            return []
        threshold = self.config.clustering_threshold
        processed: Set[str] = set()
        results: List[ClusteringResult] = []
        items = list(self.cache.items())
        for key, entry in items:
            if key in processed:
                continue
            cluster_items: List[SimilarityResult] = [
                SimilarityResult(
                    content_id=entry.content_id,
                    content_type=entry.content_type,
                    similarity_score=1.0,
                    text_content=entry.text_content,
                    tags=entry.tags[:],
                    metadata={},
                )
            ]
            for other_key, other_entry in items:
                if other_key == key or other_key in processed:
                    continue
                sim = self._cosine_similarity(entry.vector, other_entry.vector)
                if sim >= threshold:
                    cluster_items.append(
                        SimilarityResult(
                            content_id=other_entry.content_id,
                            content_type=other_entry.content_type,
                            similarity_score=sim,
                            text_content=other_entry.text_content,
                            tags=other_entry.tags[:],
                            metadata={},
                        )
                    )
                    processed.add(other_key)
            if len(cluster_items) > 1:
                cluster_id = str(uuid.uuid4())
                avg_sim = (
                    sum(i.similarity_score for i in cluster_items[1:]) / max(1, len(cluster_items) - 1)
                )
                results.append(
                    ClusteringResult(
                        cluster_id=cluster_id,
                        content_items=cluster_items,
                        cluster_center=entry.vector[:],
                        cluster_size=len(cluster_items),
                        average_similarity=avg_sim,
                    )
                )
            processed.add(key)
        return results

    async def hierarchical_clustering(
        self,
        content_types: List[str],
        max_depth: int = 2,
    ) -> List[HierarchicalCluster]:
        # Filter items
        items: List[Tuple[str, TodoziEmbeddingCache]] = [
            (k, v) for (k, v) in self.cache.items() if v.content_type in content_types
        ]
        if not items:
            return []

        threshold = self.config.clustering_threshold
        clusters: List[HierarchicalCluster] = []

        def cosine_fn(a: List[float], b: List[float]) -> float:
            return self._cosine_similarity(a, b)

        def build_cluster_recursive(
            items: List[Tuple[str, TodoziEmbeddingCache]],
            level: int,
            max_depth: int,
            threshold: float,
            parent_id: Optional[str],
        ) -> Optional[HierarchicalCluster]:
            if not items or level >= max_depth:
                return None
            key, seed = items.pop(0)
            seed_vector = seed.vector
            cluster_items = [
                SimilarityResult(
                    content_id=seed.content_id,
                    content_type=seed.content_type,
                    similarity_score=1.0,
                    text_content=seed.text_content,
                    tags=seed.tags[:],
                    metadata={},
                )
            ]
            similar_bucket: List[Tuple[str, TodoziEmbeddingCache]] = []
            remaining: List[Tuple[str, TodoziEmbeddingCache]] = []
            for (k, v) in items:
                sim = cosine_fn(seed_vector, v.vector)
                if sim >= threshold:
                    cluster_items.append(
                        SimilarityResult(
                            content_id=v.content_id,
                            content_type=v.content_type,
                            similarity_score=sim,
                            text_content=v.text_content,
                            tags=v.tags[:],
                            metadata={},
                        )
                    )
                    similar_bucket.append((k, v))
                else:
                    remaining.append((k, v))
            avg_sim = (
                sum(i.similarity_score for i in cluster_items[1:]) / max(1, len(cluster_items) - 1)
                if len(cluster_items) > 1
                else 1.0
            )
            children: List[HierarchicalCluster] = []
            if level + 1 < max_depth and similar_bucket:
                # Slightly lower threshold for sub-clusters
                while similar_bucket:
                    child = build_cluster_recursive(similar_bucket, level + 1, max_depth, threshold * 0.9, None)
                    if child:
                        children.append(child)
                    else:
                        break
            return HierarchicalCluster(
                cluster_id=str(uuid.uuid4()),
                level=level,
                content_items=cluster_items,
                cluster_center=seed_vector[:],
                children=children,
                parent_id=parent_id,
                average_similarity=avg_sim,
            )

        # Build clusters greedily
        while items:
            cluster = build_cluster_recursive(items, 0, max_depth, threshold, None)
            if cluster:
                clusters.append(cluster)
            else:
                break
        return clusters

    # ------------- Advanced Search and Analytics -------------

    async def hybrid_search(
        self,
        query: str,
        keywords: List[str],
        content_types: Optional[List[str]],
        semantic_weight: float = 0.7,
        limit: int = 20,
    ) -> List[SimilarityResult]:
        semantic_weight = max(0.0, min(1.0, semantic_weight))
        keyword_weight = 1.0 - semantic_weight
        query_embedding = await self.generate_embedding(query)
        results: List[SimilarityResult] = []
        for entry in self.cache.values():
            if content_types and entry.content_type not in content_types:
                continue
            sim = self._cosine_similarity(query_embedding, entry.vector)
            # Simple keyword scoring
            kscore = 0.0
            text_lower = entry.text_content.lower()
            query_lower = query.lower()
            if query_lower in text_lower:
                kscore += 0.5
            for kw in keywords:
                if kw.lower() in text_lower:
                    kscore += 0.3
            kscore = min(1.0, kscore)
            combined = (sim * semantic_weight) + (kscore * keyword_weight)
            if combined >= self.config.similarity_threshold:
                md = {
                    "semantic_score": sim,
                    "keyword_score": kscore,
                    "combined_score": combined,
                }
                results.append(
                    SimilarityResult(
                        content_id=entry.content_id,
                        content_type=entry.content_type,
                        similarity_score=combined,
                        text_content=entry.text_content,
                        tags=entry.tags[:],
                        metadata=md,
                    )
                )
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results[:limit]

    async def multi_query_search(
        self,
        queries: List[str],
        aggregation: str,
        content_types: Optional[List[str]],
        limit: int = 20,
    ) -> List[SimilarityResult]:
        # Generate embeddings for all queries
        query_embeddings = [await self.generate_embedding(q) for q in queries]
        results_map: Dict[str, Tuple[SimilarityResult, List[float]]] = {}
        for entry in self.cache.values():
            if content_types and entry.content_type not in content_types:
                continue
            similarities = [self._cosine_similarity(qe, entry.vector) for qe in query_embeddings]
            if aggregation == AggregationType.AVERAGE:
                score = sum(similarities) / len(similarities) if similarities else 0.0
            elif aggregation == AggregationType.MAX:
                score = max(similarities) if similarities else 0.0
            elif aggregation == AggregationType.MIN:
                score = min(similarities) if similarities else 0.0
            elif aggregation == AggregationType.WEIGHTED:
                # Fallback to average if no weights provided
                score = sum(similarities) / len(similarities) if similarities else 0.0
            else:
                score = sum(similarities) / len(similarities) if similarities else 0.0

            if score >= self.config.similarity_threshold:
                res = SimilarityResult(
                    content_id=entry.content_id,
                    content_type=entry.content_type,
                    similarity_score=score,
                    text_content=entry.text_content,
                    tags=entry.tags[:],
                    metadata={},
                )
                results_map[entry.content_id] = (res, similarities)

        results = [r for (r, _) in results_map.values()]
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results[:limit]

    async def filtered_semantic_search(
        self, query: str, filters: SearchFilters, limit: int = 20
    ) -> List[SimilarityResult]:
        query_embedding = await self.generate_embedding(query)
        results: List[SimilarityResult] = []
        for task in self.storage.list_tasks_across_projects(TaskFilters()):
            # Apply filters
            if filters.tags and not any(t in filters.tags for t in task.tags):
                continue
            if filters.priority and task.priority not in filters.priority:
                continue
            if filters.status and task.status not in filters.status:
                continue
            if filters.assignee:
                if not task.assignee or task.assignee not in filters.assignee:
                    continue
            if filters.min_progress is not None:
                if task.progress is None or task.progress < filters.min_progress:
                    continue
            if filters.max_progress is not None:
                if task.progress is None or task.progress > filters.max_progress:
                    continue

            if task.embedding_vector:
                sim = self._cosine_similarity(query_embedding, task.embedding_vector)
                if sim >= self.config.similarity_threshold:
                    results.append(
                        SimilarityResult(
                            content_id=task.id,
                            content_type=TodoziContentType.Task,
                            similarity_score=sim,
                            text_content=self.prepare_task_content(task),
                            tags=task.tags[:],
                            metadata={},
                        )
                    )
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results[:limit]

    async def find_outliers(self, content_type: str, threshold: float) -> List[str]:
        items = [e for e in self.cache.values() if e.content_type == content_type]
        outliers: List[str] = []
        for item in items:
            max_sim = 0.0
            for other in items:
                if item.content_id == other.content_id:
                    continue
                sim = self._cosine_similarity(item.vector, other.vector)
                if sim > max_sim:
                    max_sim = sim
            if max_sim < threshold:
                outliers.append(item.content_id)
        return outliers

    async def find_cross_content_relationships(
        self, content_id: str, content_type: str, min_similarity: float
    ) -> Dict[str, List[SimilarityResult]]:
        source_key = f"{content_type}_{content_id}"
        source = self.cache.get(source_key)
        if not source:
            return {}
        results: Dict[str, List[SimilarityResult]] = defaultdict(list)
        for entry in self.cache.values():
            if entry.content_id == content_id and entry.content_type == content_type:
                continue
            sim = self._cosine_similarity(source.vector, entry.vector)
            if sim >= min_similarity:
                results[entry.content_type].append(
                    SimilarityResult(
                        content_id=entry.content_id,
                        content_type=entry.content_type,
                        similarity_score=sim,
                        text_content=entry.text_content,
                        tags=entry.tags[:],
                        metadata={},
                    )
                )
        for k in results:
            results[k].sort(key=lambda r: r.similarity_score, reverse=True)
        return dict(results)

    async def build_similarity_graph(self, threshold: float) -> SimilarityGraph:
        nodes: List[GraphNode] = []
        edges: List[GraphEdge] = []
        for entry in self.cache.values():
            label = (entry.text_content.splitlines() or [""])[0][:50]
            nodes.append(
                GraphNode(
                    id=entry.content_id,
                    content_type=entry.content_type,
                    label=label,
                    metadata={"tags": entry.tags[:], "text_sample": entry.text_content[:100]},
                )
            )
        items = list(self.cache.values())
        n = len(items)
        for i in range(n):
            for j in range(i + 1, n):
                sim = self._cosine_similarity(items[i].vector, items[j].vector)
                if sim >= threshold:
                    edges.append(
                        GraphEdge(
                            from_id=items[i].content_id,
                            to_id=items[j].content_id,
                            similarity=sim,
                            bidirectional=True,
                        )
                    )
        return SimilarityGraph(nodes=nodes, edges=edges)

    async def recommend_similar(
        self, based_on: List[str], exclude: List[str], limit: int = 20
    ) -> List[SimilarityResult]:
        exclude_set = set(exclude)
        based_on_set = set(based_on)
        base_vectors: List[List[float]] = []
        for cid in based_on:
            for entry in self.cache.values():
                if entry.content_id == cid:
                    base_vectors.append(entry.vector[:])
                    break
        if not base_vectors:
            return []
        dim = len(base_vectors[0])
        centroid = [0.0] * dim
        for v in base_vectors:
            for i, val in enumerate(v):
                centroid[i] += val
        for i in range(dim):
            centroid[i] /= len(base_vectors)

        results: List[SimilarityResult] = []
        for entry in self.cache.values():
            if entry.content_id in exclude_set or entry.content_id in based_on_set:
                continue
            sim = self._cosine_similarity(centroid, entry.vector)
            if sim >= self.config.similarity_threshold:
                results.append(
                    SimilarityResult(
                        content_id=entry.content_id,
                        content_type=entry.content_type,
                        similarity_score=sim,
                        text_content=entry.text_content,
                        tags=entry.tags[:],
                        metadata={},
                    )
                )
        results.sort(key=lambda r: r.similarity_score, reverse=True)
        return results[:limit]

    async def suggest_tags(self, content_id: str, top_k: int = 5) -> List[str]:
        target = None
        for entry in self.cache.values():
            if entry.content_id == content_id:
                target = entry
                break
        if not target:
            return []
        similar: List[Tuple[float, List[str]]] = []
        for entry in self.cache.values():
            if entry.content_id == content_id:
                continue
            sim = self._cosine_similarity(target.vector, entry.vector)
            similar.append((sim, entry.tags[:]))
        similar.sort(key=lambda x: x[0], reverse=True)
        similar = similar[:top_k]
        scores: Dict[str, float] = defaultdict(float)
        for sim, tags in similar:
            for t in tags:
                scores[t] += sim
        ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
        return [t for (t, _) in ranked[:top_k]]

    async def track_embedding_drift(self, content_id: str, current_text: str) -> DriftReport:
        # Find original
        original = None
        for entry in self.cache.values():
            if entry.content_id == content_id:
                original = entry
                break
        if not original:
            raise KeyError(f"Content not found: {content_id}")
        original_vector = original.vector[:]
        current_vector = await self.generate_embedding(current_text)
        sim = self._cosine_similarity(original_vector, current_vector)
        drift = (1.0 - sim) * 100.0
        significant = drift > 20.0
        history = [
            DriftSnapshot(
                timestamp=datetime.now(timezone.utc),
                similarity_to_original=sim,
                text_sample=current_text[:200],
            )
        ]
        return DriftReport(
            content_id=content_id,
            current_similarity_to_original=sim,
            drift_percentage=drift,
            significant_drift=significant,
            history=history,
        )

    async def validate_embeddings(self) -> ValidationReport:
        total = 0
        invalid = 0
        nan_count = 0
        inf_count = 0
        zero_count = 0
        issues: List[ValidationIssue] = []
        for entry in self.cache.values():
            total += 1
            has_issue = False
            # NaN
            if any(math.isnan(v) for v in entry.vector):
                nan_count += 1
                has_issue = True
                issues.append(
                    ValidationIssue(
                        content_id=entry.content_id,
                        issue_type="NaN",
                        severity="HIGH",
                        description="Embedding contains NaN values",
                    )
                )
            # Infinity
            if any(math.isinf(v) for v in entry.vector):
                inf_count += 1
                has_issue = True
                issues.append(
                    ValidationIssue(
                        content_id=entry.content_id,
                        issue_type="Infinity",
                        severity="HIGH",
                        description="Embedding contains infinite values",
                    )
                )
            # Zero vector magnitude
            mag = math.sqrt(sum(v * v for v in entry.vector))
            if mag < 1e-6:
                zero_count += 1
                has_issue = True
                issues.append(
                    ValidationIssue(
                        content_id=entry.content_id,
                        issue_type="ZeroVector",
                        severity="MEDIUM",
                        description="Embedding is zero or near-zero vector",
                    )
                )
            if has_issue:
                invalid += 1
        return ValidationReport(
            total_embeddings=total,
            invalid_embeddings=invalid,
            nan_count=nan_count,
            infinity_count=inf_count,
            zero_vector_count=zero_count,
            abnormal_distributions=[],
            issues=issues,
        )

    async def profile_search_performance(self, query: str, iterations: int = 10) -> PerformanceMetrics:
        times: List[int] = []
        results_count = 0
        for _ in range(iterations):
            start = time.perf_counter_ns()
            res = await self.semantic_search(query, None, 10)
            elapsed_ms = (time.perf_counter_ns() - start) // 1_000_000
            times.append(elapsed_ms)
            results_count = len(res)
        avg = sum(times) / len(times)
        min_t = min(times)
        max_t = max(times)
        # std dev
        variance = sum((t - avg) ** 2 for t in times) / len(times)
        std_dev = math.sqrt(variance)
        return PerformanceMetrics(
            query=query,
            iterations=iterations,
            avg_time_ms=avg,
            min_time_ms=min_t,
            max_time_ms=max_t,
            std_dev_ms=std_dev,
            results_per_iteration=results_count,
        )

    async def export_diagnostics(self) -> DiagnosticReport:
        # Basic stats
        total = len(self.cache)
        # Content type breakdown
        type_breakdown: Dict[str, int] = defaultdict(int)
        for entry in self.cache.values():
            type_breakdown[entry.content_type] += 1
        # Similarity stats
        items = list(self.cache.values())
        sims: List[float] = []
        pairs: List[Tuple[str, str, float]] = []
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                s = self._cosine_similarity(items[i].vector, items[j].vector)
                sims.append(s)
                pairs.append((items[i].content_id, items[j].content_id, s))
        avg_sim = sum(sims) / len(sims) if sims else 0.0
        pairs.sort(key=lambda x: x[2], reverse=True)
        top_pairs = pairs[:10]
        # Distribution stats (mean/std/min/max per dimension)
        if items:
            dim = len(items[0].vector)
            means = [0.0] * dim
            mins = [float("inf")] * dim
            maxs = [float("-inf")] * dim
            for e in items:
                for i, v in enumerate(e.vector):
                    means[i] += v
                    if v < mins[i]:
                        mins[i] = v
                    if v > maxs[i]:
                        maxs[i] = v
            for i in range(dim):
                means[i] /= total
            stds = [0.0] * dim
            for e in items:
                for i, v in enumerate(e.vector):
                    stds[i] += (v - means[i]) ** 2
            for i in range(dim):
                stds[i] = math.sqrt(stds[i] / total)
            dist_stats = EmbeddingStats(mean=means, std_dev=stds, min=mins, max=maxs)
        else:
            dist_stats = EmbeddingStats(mean=[], std_dev=[], min=[], max=[])
        return DiagnosticReport(
            timestamp=datetime.now(timezone.utc),
            cache_hit_rate=0.0,
            avg_similarity_score=avg_sim,
            embedding_distribution_stats=dist_stats,
            content_type_breakdown=dict(type_breakdown),
            top_similar_pairs=top_pairs,
        )

    # ------------- Multi-Model Support and Comparison -------------

    async def load_additional_model(self, model_name: str, model_alias: str):
        device = "cpu"
        model = EmbeddingModel(model_name=model_name, device=device)
        self._embedding_models[model_alias] = model

    async def compare_models(self, text: str, model_aliases: List[str]) -> ModelComparisonResult:
        results: Dict[str, ModelEmbeddingResult] = {}
        for alias in model_aliases:
            start = time.perf_counter_ns()
            if alias in self._embedding_models:
                emb = self._embedding_models[alias].encode_single(text)
            else:
                # Fall back to default model
                if self._embedding_model is None:
                    await self.initialize()
                assert self._embedding_model is not None
                emb = self._embedding_model.encode_single(text)
            elapsed_ms = int((time.perf_counter_ns() - start) // 1_000_000)
            results[alias] = ModelEmbeddingResult(
                model_name=alias, embedding=emb, dimensions=len(emb), generation_time_ms=elapsed_ms
            )
        return ModelComparisonResult(text=text, models=results)

    # ------------- Labeling, Diversity, Projections -------------

    async def auto_label_clusters(self, clusters: List[ClusteringResult]) -> List[LabeledCluster]:
        labeled: List[LabeledCluster] = []
        for c in clusters:
            tag_counts: Dict[str, int] = defaultdict(int)
            for item in c.content_items:
                for t in item.tags:
                    tag_counts[t] += 1
            ranked = sorted(tag_counts.items(), key=lambda kv: kv[1], reverse=True)
            if ranked:
                label = f"Cluster: {ranked[0][0]}"
            else:
                label = "Unlabeled Cluster"
            desc = f"Contains {c.cluster_size} items with avg similarity of {c.average_similarity:.2f}"
            labeled.append(
                LabeledCluster(
                    cluster_id=c.cluster_id,
                    label=label,
                    description=desc,
                    confidence=c.average_similarity,
                    content_items=c.content_items[:],
                )
            )
        return labeled

    async def calculate_diversity(self, content_ids: List[str]) -> float:
        if len(content_ids) < 2:
            return 0.0
        id_to_vec: Dict[str, List[float]] = {}
        for entry in self.cache.values():
            if entry.content_id in content_ids:
                id_to_vec[entry.content_id] = entry.vector[:]
        ids = [cid for cid in content_ids if cid in id_to_vec]
        if len(ids) < 2:
            return 0.0
        total = 0.0
        count = 0
        n = len(ids)
        for i in range(n):
            for j in range(i + 1, n):
                s = self._cosine_similarity(id_to_vec[ids[i]], id_to_vec[ids[j]])
                total += 1.0 - s
                count += 1
        return total / count if count else 0.0

    async def get_tsne_coordinates(self, content_ids: List[str], dimensions: int = 2) -> List[Tuple[str, List[float]]]:
        if dimensions not in (2, 3):
            raise ValueError("Only 2D or 3D projections supported")
        data: List[Tuple[str, List[float]]] = []
        for entry in self.cache.values():
            if entry.content_id in content_ids:
                data.append((entry.content_id, entry.vector[:]))
        if not data:
            return []
        # Simplified projection: average-pool segments of the vector
        base_dim = len(data[0][1])
        projections: List[Tuple[str, List[float]]] = []
        for cid, vec in data:
            proj = [0.0] * dimensions
            for i in range(dimensions):
                start = i * (base_dim // dimensions)
                end = min((i + 1) * (base_dim // dimensions), base_dim)
                seg = vec[start:end]
                proj[i] = sum(seg) / len(seg) if seg else 0.0
            # Normalize
            norm = math.sqrt(sum(x * x for x in proj)) or 1.0
            proj = [x / norm for x in proj]
            projections.append((cid, proj))
        return projections

    # ------------- Preload, Backup/Restore, Explain, Versioning, Export -------------

    async def preload_related_embeddings(self, content_id: str, depth: int = 1):
        # Iterative BFS preload of similar embeddings
        to_process = [(content_id, depth)]
        processed: Set[str] = set()
        while to_process:
            cid, d = to_process.pop()
            if d == 0 or cid in processed:
                continue
            processed.add(cid)
            source = None
            for entry in self.cache.values():
                if entry.content_id == cid:
                    source = entry
                    break
            if not source:
                continue
            source_vec = source.vector[:]
            # Find top 5 similar
            sims: List[Tuple[str, float]] = []
            for entry in self.cache.values():
                if entry.content_id == cid:
                    continue
                sim = self._cosine_similarity(source_vec, entry.vector)
                sims.append((entry.content_id, sim))
            sims.sort(key=lambda x: x[1], reverse=True)
            for sid, _ in sims[:5]:
                if d > 1 and sid not in processed:
                    to_process.append((sid, d - 1))

    async def backup_embeddings(self, backup_path: Optional[str] = None) -> str:
        tdz = self._get_todozi_dir()
        backup_dir = Path(tdz) / "backups" / "embeddings"
        backup_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = backup_path or f"embeddings_backup_{ts}.json"
        full_path = backup_dir / filename
        payload = {k: {
            "vector": v.vector,
            "content_type": v.content_type,
            "content_id": v.content_id,
            "text_content": v.text_content,
            "tags": v.tags,
            "created_at": v.created_at.isoformat(),
            "ttl_seconds": v.ttl_seconds,
        } for k, v in self.cache.items()}
        full_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return str(full_path)

    async def restore_embeddings(self, backup_path: str) -> int:
        data = json.loads(Path(backup_path).read_text(encoding="utf-8"))
        count = 0
        for k, v in data.items():
            entry = TodoziEmbeddingCache(
                vector=v["vector"],
                content_type=v["content_type"],
                content_id=v["content_id"],
                text_content=v["text_content"],
                tags=v.get("tags", []),
                created_at=datetime.fromisoformat(v["created_at"]),
                ttl_seconds=v["ttl_seconds"],
            )
            self.cache[k] = entry
            count += 1
        return count

    async def explain_search_result(self, query: str, result: SimilarityResult) -> str:
        query_emb = await self.generate_embedding(query)
        # Find the entry
        source_entry = None
        for entry in self.cache.values():
            if entry.content_id == result.content_id:
                source_entry = entry
                break
        if not source_entry:
            return "Result not found in cache."
        # Top contributing dimensions
        contrib = [(i, query_emb[i] * source_entry.vector[i]) for i in range(len(query_emb))]
        contrib.sort(key=lambda x: x[1], reverse=True)
        top_dims = [str(i) for i, _ in contrib[:5]]
        return (
            f"Match Explanation for '{result.content_id}' (similarity: {result.similarity_score:.3}):\n"
            f"- Content Type: {result.content_type}\n"
            f"- Matched Tags: {', '.join(result.tags)}\n"
            f"- Top Contributing Dimensions: {', '.join(top_dims)}\n"
            f"- Semantic Overlap: {result.similarity_score * 100:.1f}%\n"
            f"- Text Preview: {result.text_content[:100]}..."
        )

    async def create_embedding_version(
        self, content_id: str, version_label: str
    ) -> str:
        tdz = self._get_todozi_dir()
        versions_dir = Path(tdz) / "embed" / "versions"
        versions_dir.mkdir(parents=True, exist_ok=True)
        version_file = versions_dir / f"{content_id}.jsonl"
        entry = self.cache.get(f"Task_{content_id}") or self.cache.get(f"Tag_{content_id}") or self.cache.get(f"Idea_{content_id}") or self.cache.get(f"Memory_{content_id}")
        if entry is None:
            raise KeyError(f"Content not found: {content_id}")
        version_id = str(uuid.uuid4())
        record = {
            "version_id": version_id,
            "version_label": version_label,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content_id": content_id,
            "embedding": entry.vector,
            "text_content": entry.text_content,
            "tags": entry.tags,
        }
        with version_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        return version_id

    async def get_version_history(self, content_id: str) -> List[Dict[str, Any]]:
        tdz = self._get_todozi_dir()
        version_file = Path(tdz) / "embed" / "versions" / f"{content_id}.jsonl"
        if not version_file.exists():
            return []
        records: List[Dict[str, Any]] = []
        with version_file.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                records.append(json.loads(line))
        return records

    async def export_for_fine_tuning(self, output_path: str) -> int:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        count = 0
        with Path(output_path).open("w", encoding="utf-8") as f:
            for entry in self.cache.values():
                record = {
                    "text": entry.text_content,
                    "embedding": entry.vector,
                    "metadata": {
                        "content_type": entry.content_type,
                        "tags": entry.tags,
                        "content_id": entry.content_id,
                    },
                }
                f.write(json.dumps(record) + "\n")
                count += 1
        return count

    # ------------- Mega Log -------------

    async def _log_to_mega_file(self, task: Task):
        tdz = self._get_todozi_dir()
        embed_dir = Path(tdz) / "embed"
        embed_dir.mkdir(parents=True, exist_ok=True)
        mega_file = embed_dir / "embedding_mega_log.jsonl"
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "task_id": task.id,
            "project": task.parent_project,
            "action": task.action,
            "priority": task.priority,
            "status": task.status,
            "tags": task.tags,
            "time": task.time,
            "assignee": task.assignee,
            "embedding_vector": task.embedding_vector,
            "embedding_dimensions": len(task.embedding_vector) if task.embedding_vector else None,
            "context_notes": task.context_notes,
            "dependencies": task.dependencies,
            "progress": task.progress,
        }
        with mega_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps(log_entry) + "\n")


# --------------- Minimal Tool Wrapper ---------------

class TodoziEmbeddingTool:
    def __init__(self, config: TodoziEmbeddingConfig):
        self.service = TodoziEmbeddingService(config)

    async def initialize(self):
        await self.service.initialize()

    async def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        # Minimal tool-style wrapper over service methods
        if action == "find_similar":
            content = kwargs.get("content") or ""
            limit = kwargs.get("limit") or 10
            results = await self.service.find_similar_tasks(content, int(limit))
            return {"results": [self._serialize_result(r) for r in results]}
        elif action == "semantic_search":
            content = kwargs.get("content") or ""
            limit = kwargs.get("limit") or 10
            types = kwargs.get("content_types")
            results = await self.service.semantic_search(content, types, int(limit))
            return {"results": [self._serialize_result(r) for r in results]}
        elif action == "cluster":
            clusters = await self.service.cluster_content()
            return {"clusters": [self._serialize_cluster(c) for c in clusters]}
        elif action == "stats":
            stats = await self.service.export_diagnostics()
            return {
                "total_embeddings": len(self.service.cache),
                "avg_similarity_score": stats.avg_similarity_score,
                "content_type_breakdown": stats.content_type_breakdown,
            }
        else:
            return {"error": f"Unknown action: {action}"}

    @staticmethod
    def _serialize_result(r: SimilarityResult) -> Dict[str, Any]:
        return {
            "content_id": r.content_id,
            "content_type": r.content_type,
            "similarity_score": r.similarity_score,
            "text_content": r.text_content,
            "tags": r.tags,
            "metadata": r.metadata,
        }

    @staticmethod
    def _serialize_cluster(c: ClusteringResult) -> Dict[str, Any]:
        return {
            "cluster_id": c.cluster_id,
            "cluster_size": c.cluster_size,
            "average_similarity": c.average_similarity,
            "content_items": [TodoziEmbeddingTool._serialize_result(i) for i in c.content_items],
        }


# --------------- Tests (simple sanity checks) ---------------

async def _run_tests():
    config = TodoziEmbeddingConfig()
    service = TodoziEmbeddingService(config)
    await service.initialize()

    # Basic content
    t1 = Task(id="t1", action="Write unit tests", parent_project="dev")
    t2 = Task(id="t2", action="Refactor embedding module", parent_project="dev")
    await service.add_task(t1)
    await service.add_task(t2)

    # Search
    res = await service.find_similar_tasks("testing and QA", 5)
    assert isinstance(res, list)

    # Embed tag
    tag = Tag(id="tag1", name="testing", description="QA related")
    await service.embed_tag(tag)
    tag_res = await service.find_similar_tags("qa", 5)
    assert isinstance(tag_res, list)

    # Cluster
    clusters = await service.cluster_content()
    assert isinstance(clusters, list)

    # Diagnostics
    diag = await service.export_diagnostics()
    assert isinstance(diag.avg_similarity_score, float)

    # Validate
    val = await service.validate_embeddings()
    assert isinstance(val.total_embeddings, int)

    print("All basic tests passed!")


if __name__ == "__main__":
    import asyncio

    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        print("WARNING: sentence-transformers not available. Install with: pip install sentence-transformers torch")
    asyncio.run(_run_tests())
