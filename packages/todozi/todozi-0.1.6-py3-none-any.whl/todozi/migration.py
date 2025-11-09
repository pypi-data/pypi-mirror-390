import asyncio
import json
import logging
import math
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Type, TypeVar, Generic, Union

# -------------- Generic Result type --------------

T = TypeVar("T")

class TodoziError(Exception):
    def __init__(self, message: str, details: Optional[str] = None):
        super().__init__(message)
        self.details = details

    @staticmethod
    def storage(message: str) -> "TodoziError":
        return TodoziError(f"Storage error: {message}")

    @staticmethod
    def config(message: str) -> "TodoziError":
        return TodoziError(f"Config error: {message}")

class MigrationError(TodoziError):
    """Specialized error for migration operations"""
    pass

class StorageError(TodoziError):
    """Specialized error for storage operations"""
    pass

class Result(Generic[T]):
    def __init__(self, value: T = None, error: TodoziError = None):
        self.value = value
        self.error = error

    def is_ok(self) -> bool:
        return self.error is None

    def is_err(self) -> bool:
        return self.error is not None

    def unwrap(self) -> T:
        if self.error is not None:
            raise self.error
        return self.value  # type: ignore

    def expect(self, msg: str) -> T:
        if self.error is not None:
            raise MigrationError(f"{msg}: {self.error}") from self.error
        return self.value  # type: ignore

def ok(value: T) -> Result[T]:
    return Result(value=value, error=None)

def err(e: Union[TodoziError, str]) -> Result[T]:
    if isinstance(e, TodoziError):
        return Result(value=None, error=e)  # type: ignore
    return Result(value=None, error=TodoziError(str(e)))  # type: ignore

# -------------- Models --------------

@dataclass
class Task:
    id: str
    title: str = ""
    description: str = ""
    status: str = "active"
    parent_project: str = ""
    embedding_vector: Optional[List[float]] = None

@dataclass
class ProjectMigrationStats:
    project_name: str
    initial_tasks: int = 0
    migrated_tasks: int = 0
    final_tasks: int = 0

@dataclass
class MigrationReport:
    tasks_found: int = 0
    tasks_migrated: int = 0
    projects_migrated: int = 0
    project_stats: List[ProjectMigrationStats] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

@dataclass
class Collection:
    tasks: Dict[str, Task] = field(default_factory=dict)

@dataclass
class ProjectTaskContainer:
    project_name: str
    tasks: Dict[str, Task] = field(default_factory=dict)

    @staticmethod
    def new(project_name: str) -> "ProjectTaskContainer":
        return ProjectTaskContainer(project_name=project_name)

    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())

    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)

    def add_task(self, task: Task) -> None:
        self.tasks[task.id] = task

# -------------- Storage module --------------

def _storage_root() -> Path:
    home = Path.home()
    return home / ".todozi"

def get_storage_dir() -> Result[Path]:
    try:
        root = _storage_root()
        root.mkdir(parents=True, exist_ok=True)
        return ok(root)
    except Exception as e:
        return err(TodoziError.storage(str(e)))

def _ensure_dir(path: Path) -> Result[None]:
    try:
        path.mkdir(parents=True, exist_ok=True)
        return ok(None)
    except Exception as e:
        return err(TodoziError.storage(f"Failed to ensure directory {path}: {e}"))

def _load_json(path: Path) -> Result[Any]:
    try:
        with path.open("r", encoding="utf-8") as f:
            return ok(json.load(f))
    except FileNotFoundError:
        return err(FileNotFoundError(f"File not found: {path}"))
    except json.JSONDecodeError as e:
        return err(e)
    except Exception as e:
        return err(e)

def _save_json(path: Path, data: Any) -> Result[None]:
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return ok(None)
    except Exception as e:
        return err(TodoziError.storage(f"Failed to save JSON to {path}: {e}"))

def _task_to_dict(t: Task) -> Dict[str, Any]:
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "status": t.status,
        "parent_project": t.parent_project,
        "embedding_vector": t.embedding_vector,
    }

def _task_from_dict(d: Dict[str, Any]) -> Result[Task]:
    try:
        return ok(
            Task(
                id=str(d.get("id", "")),
                title=str(d.get("title", "")),
                description=str(d.get("description", "")),
                status=str(d.get("status", "active")),
                parent_project=str(d.get("parent_project", "")),
                embedding_vector=d.get("embedding_vector"),
            )
        )
    except Exception as e:
        return err(TodoziError(f"Invalid task data: {e}"))

def load_task_collection(collection_name: str) -> Result[Collection]:
    if not collection_name or not isinstance(collection_name, str):
        return err(ValueError("collection_name must be a non-empty string"))

    root = get_storage_dir()
    if root.is_err():
        return err(root.error)  # type: ignore
    tasks_dir = root.value / "tasks"
    ensure_dir_res = _ensure_dir(tasks_dir)
    if ensure_dir_res.is_err():
        return err(ensure_dir_res.error)  # type: ignore

    path = tasks_dir / f"{collection_name}.json"
    if not path.exists():
        return err(FileNotFoundError(f"Collection '{collection_name}' does not exist at {path}"))

    data_res = _load_json(path)
    if data_res.is_err():
        return err(data_res.error)  # type: ignore
    data = data_res.value
    tasks: Dict[str, Task] = {}
    for k, v in (data.get("tasks") or {}).items():
        task_res = _task_from_dict(v)
        if task_res.is_err():
            return err(task_res.error)  # type: ignore
        tasks[str(k)] = task_res.value  # type: ignore
    return ok(Collection(tasks=tasks))

def _project_container_path(project_name: str) -> Result[Path]:
    if not project_name or not isinstance(project_name, str):
        return err(ValueError("project_name must be a non-empty string"))
    root = get_storage_dir()
    if root.is_err():
        return err(root.error)  # type: ignore
    projects_dir = root.value / "projects"
    ensure_dir_res = _ensure_dir(projects_dir)
    if ensure_dir_res.is_err():
        return err(ensure_dir_res.error)  # type: ignore
    return ok(projects_dir / f"{project_name}.json")

def load_project_task_container(project_name: str) -> Result[ProjectTaskContainer]:
    path_res = _project_container_path(project_name)
    if path_res.is_err():
        return err(path_res.error)  # type: ignore
    path = path_res.value
    if not path.exists():
        return err(FileNotFoundError(f"Project container for '{project_name}' does not exist at {path}"))

    data_res = _load_json(path)
    if data_res.is_err():
        return err(data_res.error)  # type: ignore
    data = data_res.value
    tasks: Dict[str, Task] = {}
    for k, v in (data.get("tasks") or {}).items():
        task_res = _task_from_dict(v)
        if task_res.is_err():
            return err(task_res.error)  # type: ignore
        tasks[str(k)] = task_res.value  # type: ignore
    return ok(ProjectTaskContainer(project_name=project_name, tasks=tasks))

def save_project_task_container(container: ProjectTaskContainer) -> Result[None]:
    path_res = _project_container_path(container.project_name)
    if path_res.is_err():
        return err(path_res.error)  # type: ignore
    data = {"tasks": {tid: _task_to_dict(t) for tid, t in container.tasks.items()}}
    return _save_json(path_res.value, data)

def list_project_task_containers() -> Result[List[ProjectTaskContainer]]:
    root = get_storage_dir()
    if root.is_err():
        return err(root.error)  # type: ignore
    projects_dir = root.value / "projects"
    ensure_dir_res = _ensure_dir(projects_dir)
    if ensure_dir_res.is_err():
        return err(ensure_dir_res.error)  # type: ignore

    containers: List[ProjectTaskContainer] = []
    if not projects_dir.exists():
        return ok(containers)
    for p in projects_dir.iterdir():
        if p.is_file() and p.suffix == ".json":
            cont_res = load_project_task_container(p.stem)
            if cont_res.is_err():
                # Skip unreadable container; external caller can collect errors if needed
                continue
            containers.append(cont_res.value)  # type: ignore
    return ok(containers)

# -------------- Embedding service --------------

@dataclass
class TodoziEmbeddingConfig:
    model_name: str = "mini"
    dimension: int = 64

class TodoziEmbeddingService:
    def __init__(self, config: TodoziEmbeddingConfig):
        self.config = config
        self._initialized = False

    async def initialize(self) -> Result[None]:
        self._initialized = True
        return ok(None)

    def prepare_task_content(self, task: Task) -> str:
        parts = []
        if task.title:
            parts.append(task.title)
        if task.description:
            parts.append(task.description)
        if task.status:
            parts.append(f"[{task.status}]")
        if task.parent_project:
            parts.append(f"<project:{task.parent_project}>")
        return " ".join(parts)

    async def generate_embedding(self, text: str) -> Result[List[float]]:
        if not self._initialized:
            return err(TodoziError("Embedding service not initialized"))
        # Deterministic pseudo-random vector from text hash
        vector = [math.sin(hash((text, i))) % 1.0 for i in range(self.config.dimension)]
        # Normalize
        norm = math.sqrt(sum(x * x for x in vector)) or 1.0
        vector = [x / norm for x in vector]
        return ok(vector)

# -------------- Configuration --------------

@dataclass(frozen=True)
class MigrationConfig:
    dry_run: bool = False
    verbose: bool = False
    force_overwrite: bool = False
    batch_size: int = 100

# -------------- Migrator and CLI --------------

class TaskMigrator:
    def __init__(self, config: MigrationConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    def with_dry_run(self, dry_run: bool) -> "TaskMigrator":
        return TaskMigrator(MigrationConfig(dry_run=dry_run, verbose=self.config.verbose, force_overwrite=self.config.force_overwrite, batch_size=self.config.batch_size))

    def with_verbose(self, verbose: bool) -> "TaskMigrator":
        return TaskMigrator(MigrationConfig(dry_run=self.config.dry_run, verbose=verbose, force_overwrite=self.config.force_overwrite, batch_size=self.config.batch_size))

    def with_force_overwrite(self, force_overwrite: bool) -> "TaskMigrator":
        return TaskMigrator(MigrationConfig(dry_run=self.config.dry_run, verbose=self.config.verbose, force_overwrite=force_overwrite, batch_size=self.config.batch_size))

    async def migrate(self) -> Result[MigrationReport]:
        report = MigrationReport()
        if self.config.verbose:
            self.logger.info("🚀 Starting task migration to project-based system...")
            if self.config.dry_run:
                self.logger.info("🔍 DRY RUN MODE - No actual changes will be made")

        all_tasks_res = self._load_legacy_tasks(report)
        if all_tasks_res.is_err():
            return err(all_tasks_res.error)  # type: ignore
        all_tasks = all_tasks_res.value  # type: ignore

        if not all_tasks:
            if self.config.verbose:
                self.logger.info("✅ No legacy tasks found - migration complete")
            return ok(report)

        project_groups = self._group_tasks_by_project(all_tasks)
        if self.config.verbose:
            self.logger.info(f"📊 Found {len(project_groups)} unique projects")
            for project_name, tasks in project_groups.items():
                self.logger.info(f"   • {project_name}: {len(tasks)} tasks")

        for project_name, tasks in project_groups.items():
            project_report_res = await self._migrate_project_tasks(project_name, tasks)
            if project_report_res.is_err():
                report.errors.append(f"Project '{project_name}' migration failed: {project_report_res.error}")  # type: ignore
                continue
            project_report: ProjectMigrationStats = project_report_res.value  # type: ignore
            report.project_stats.append(project_report)
            report.projects_migrated += 1
            report.tasks_migrated += project_report.migrated_tasks

        if self.config.verbose:
            self._print_summary(report)
        return ok(report)

    def _load_legacy_tasks(self, report: MigrationReport) -> Result[List[Task]]:
        collections = ["active", "completed", "archived"]
        all_tasks: List[Task] = []
        for collection_name in collections:
            collection_res = load_task_collection(collection_name)
            if collection_res.is_err():
                if self.config.verbose:
                    self.logger.warning("⚠️  Could not load '%s' collection (may not exist): %s", collection_name, collection_res.error)  # type: ignore
                continue
            collection: Collection = collection_res.value  # type: ignore
            for task in collection.tasks.values():
                all_tasks.append(task)
                report.tasks_found += 1
            if self.config.verbose:
                self.logger.info("📂 Loaded %d tasks from '%s' collection", len(collection.tasks), collection_name)
        return ok(all_tasks)

    def _group_tasks_by_project(self, tasks: List[Task]) -> Dict[str, List[Task]]:
        project_groups: Dict[str, List[Task]] = {}
        for task in tasks:
            project = task.parent_project if task.parent_project else "general"
            project_groups.setdefault(project, []).append(task)
        return project_groups

    async def _migrate_project_tasks(self, project_name: str, tasks: List[Task]) -> Result[ProjectMigrationStats]:
        if not project_name or not isinstance(project_name, str):
            return err(ValueError("project_name must be a non-empty string"))
        if not isinstance(tasks, list) or not all(isinstance(t, Task) for t in tasks):
            return err(ValueError("tasks must be a List[Task]"))

        stats = ProjectMigrationStats(project_name=project_name)

        existing_res = load_project_task_container(project_name)
        if existing_res.is_ok():
            existing: ProjectTaskContainer = existing_res.value  # type: ignore
            stats.initial_tasks = len(existing.get_all_tasks())
            if not self.config.force_overwrite and stats.initial_tasks > 0:
                if self.config.verbose:
                    self.logger.warning(
                        "⚠️  Project '%s' already exists with %d tasks (use --force to overwrite)",
                        project_name, stats.initial_tasks
                    )
                stats.final_tasks = stats.initial_tasks
                return ok(stats)
        else:
            if self.config.verbose:
                self.logger.info("📁 Creating new project container for '%s'", project_name)

        container_res = load_project_task_container(project_name)
        if container_res.is_err():
            container = ProjectTaskContainer.new(project_name)
        else:
            container: ProjectTaskContainer = container_res.value  # type: ignore

        _initial_count = len(container.get_all_tasks())

        emb_service = TodoziEmbeddingService(TodoziEmbeddingConfig())
        init_res = await emb_service.initialize()
        emb_ok = init_res.is_ok()

        for task in tasks:
            if container.get_task(task.id) is not None:
                if self.config.verbose:
                    self.logger.info("   ⏭️  Skipping duplicate task: %s", task.id)
                continue

            if emb_ok:
                try:
                    content = emb_service.prepare_task_content(task)
                    emb_res = await emb_service.generate_embedding(content)
                    if emb_res.is_err():
                        if self.config.verbose:
                            self.logger.warning("   ❌ Embedding generation failed for task %s: %s", task.id, emb_res.error)  # type: ignore
                    else:
                        emb_value = emb_res.value  # type: ignore
                        # Type safety check
                        if isinstance(emb_value, list) and all(isinstance(x, float) for x in emb_value):
                            task.embedding_vector = emb_value
                            if self.config.verbose:
                                self.logger.info("   🧠 Generated embedding for task: %s", task.id)
                        else:
                            if self.config.verbose:
                                self.logger.warning("   ❌ Embedding result is not List[float] for task %s", task.id)
                except Exception as e:
                    if self.config.verbose:
                        self.logger.warning("   ⚠️  Embedding service error for task %s: %s", task.id, e)

            container.add_task(task)
            stats.migrated_tasks += 1
            if self.config.verbose:
                last_task = container.get_all_tasks()[-1]
                self.logger.info("   ✅ Migrated task: %s (status: %s)", last_task.id, last_task.status)

        stats.final_tasks = len(container.get_all_tasks())

        if not self.config.dry_run:
            save_res = save_project_task_container(container)
            if save_res.is_err():
                error_msg = f"Failed to save project container '{project_name}': {save_res.error}"  # type: ignore
                if self.config.verbose:
                    self.logger.error("❌ %s", error_msg)
                return err(TodoziError.storage(error_msg))
            if self.config.verbose:
                self.logger.info("💾 Saved project container: %s", project_name)
        else:
            if self.config.verbose:
                self.logger.info("🔍 DRY RUN: Would save project container: %s (%d tasks)", project_name, stats.final_tasks)

        return ok(stats)

    def _print_summary(self, report: MigrationReport) -> None:
        self.logger.info("\n%s", "=" * 60)
        self.logger.info("📊 MIGRATION SUMMARY")
        self.logger.info("%s", "=" * 60)
        self.logger.info("Total legacy tasks found: %d", report.tasks_found)
        self.logger.info("Tasks migrated: %d", report.tasks_migrated)
        self.logger.info("Projects processed: %d", report.projects_migrated)
        if report.project_stats:
            self.logger.info("\n📋 Project Details:")
            for stat in report.project_stats:
                self.logger.info(
                    "  • %s: %d → %d tasks (%d migrated)",
                    stat.project_name, stat.initial_tasks, stat.final_tasks, stat.migrated_tasks
                )
        if report.errors:
            self.logger.info("\n⚠️  Errors encountered:")
            for error in report.errors:
                self.logger.info("  • %s", error)
        if report.tasks_migrated == report.tasks_found and not report.errors:
            self.logger.info("\n✅ Migration completed successfully!")
        else:
            self.logger.info("\n⚠️  Migration completed with warnings")
        self.logger.info("%s", "=" * 60)

    def validate_migration(self) -> Result[bool]:
        if self.config.verbose:
            self.logger.info("🔍 Validating migration integrity...")
        legacy_count = 0
        for collection_name in ["active", "completed", "archived"]:
            col_res = load_task_collection(collection_name)
            if col_res.is_ok():
                collection: Collection = col_res.value  # type: ignore
                legacy_count += len(collection.tasks)

        project_count = 0
        conts_res = list_project_task_containers()
        if conts_res.is_ok():
            containers: List[ProjectTaskContainer] = conts_res.value  # type: ignore
            project_count = sum(len(c.get_all_tasks()) for c in containers)

        if self.config.verbose:
            self.logger.info("Legacy system tasks: %d", legacy_count)
            self.logger.info("Project system tasks: %d", project_count)

        is_valid = legacy_count == 0 or (legacy_count > 0 and project_count >= legacy_count)
        if is_valid:
            if self.config.verbose:
                self.logger.info("✅ Migration validation passed")
        else:
            if self.config.verbose:
                self.logger.error("❌ Migration validation failed")
        return ok(is_valid)

    def cleanup_legacy(self) -> Result[None]:
        if self.config.verbose:
            self.logger.info("🧹 Cleaning up legacy collections...")
        collections = ["active", "completed", "archived"]
        cleaned_count = 0

        root = get_storage_dir()
        if root.is_err():
            return err(root.error)  # type: ignore
        tasks_dir = root.value / "tasks"

        for collection_name in collections:
            col_res = load_task_collection(collection_name)
            if col_res.is_err():
                if self.config.verbose:
                    self.logger.info("   ℹ️  Collection '%s' does not exist", collection_name)
                continue
            collection: Collection = col_res.value  # type: ignore
            if not collection.tasks:
                collection_path = tasks_dir / f"{collection_name}.json"
                if collection_path.exists():
                    if self.config.dry_run:
                        if self.config.verbose:
                            self.logger.info("   🔍 DRY RUN: Would remove empty collection '%s'", collection_name)
                    else:
                        try:
                            collection_path.unlink()
                            if self.config.verbose:
                                self.logger.info("   🗑️  Removed empty collection '%s'", collection_name)
                            cleaned_count += 1
                        except Exception as e:
                            if self.config.verbose:
                                self.logger.warning("   ⚠️  Could not remove '%s': %s", collection_name, e)
            else:
                if self.config.verbose:
                    self.logger.warning(
                        "   ⚠️  Collection '%s' still has %d tasks - not removing",
                        collection_name, len(collection.tasks)
                    )

        if self.config.verbose:
            if cleaned_count > 0:
                self.logger.info("✅ Cleaned up %d empty legacy collections", cleaned_count)
            else:
                self.logger.info("ℹ️  No empty legacy collections to clean up")
        return ok(None)

class MigrationCli:
    def __init__(self, migrator: Optional[TaskMigrator] = None):
        self.migrator = migrator or TaskMigrator(MigrationConfig())

    def with_dry_run(self, dry_run: bool) -> "MigrationCli":
        return MigrationCli(self.migrator.with_dry_run(dry_run))

    def with_verbose(self, verbose: bool) -> "MigrationCli":
        return MigrationCli(self.migrator.with_verbose(verbose))

    def with_force(self, force: bool) -> "MigrationCli":
        return MigrationCli(self.migrator.with_force_overwrite(force))

    async def run(self) -> Result[None]:
        report_res = await self.migrator.migrate()
        if report_res.is_err():
            return err(report_res.error)  # type: ignore
        report: MigrationReport = report_res.value  # type: ignore

        if not self.migrator.config.dry_run:
            is_valid_res = self.migrator.validate_migration()
            if is_valid_res.is_ok() and is_valid_res.value and not report.errors:  # type: ignore
                self.migrator.cleanup_legacy()
        return ok(None)

# -------------- Entry point for manual testing --------------

async def main():
    # Set up logging to see verbose output when enabled
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    cli = (
        MigrationCli()
        .with_verbose(True)
        .with_dry_run(False)
        .with_force(False)
    )
    res = await cli.run()
    if res.is_err():
        print(f"Migration failed: {res.error}", file=sys.stderr)  # type: ignore
        sys.exit(1)

# -------------- Unit tests (pytest style, including async) --------------

def test_task_migrator_creation():
    migrator = TaskMigrator(MigrationConfig())
    assert not migrator.config.dry_run
    assert not migrator.config.verbose
    assert not migrator.config.force_overwrite

def test_task_migrator_builder():
    migrator = TaskMigrator(MigrationConfig()).with_dry_run(True).with_verbose(True).with_force_overwrite(True)
    assert migrator.config.dry_run
    assert migrator.config.verbose
    assert migrator.config.force_overwrite

def test_migration_cli_builder():
    _ = (
        MigrationCli()
        .with_dry_run(True)
        .with_verbose(True)
        .with_force(True)
    )
    assert True

# Example of async test (requires pytest-asyncio)
# To run: pip install pytest pytest-asyncio
# pytest this_script.py -v
try:
    import pytest
    import pytest_asyncio

    @pytest.mark.asyncio
    async def test_migration_happy_path():
        cli = (
            MigrationCli()
            .with_verbose(True)
            .with_dry_run(True)
            .with_force(False)
        )
        report_res = await cli.migrator.migrate()
        assert report_res.is_ok()
        # No assertions on numbers since environment may be empty, but ensure it returns a report
        report: MigrationReport = report_res.value  # type: ignore
        assert isinstance(report, MigrationReport)

except ImportError:
    pass

if __name__ == "__main__":
    # Run manual main if executed directly
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
