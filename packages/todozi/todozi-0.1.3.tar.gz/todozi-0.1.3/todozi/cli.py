from __future__ import annotations

import sys
import warnings
from pathlib import Path

# Suppress annoying warnings
warnings.filterwarnings("ignore", category=UserWarning, module="urllib3")
warnings.filterwarnings("ignore", message=".*triton.*")
warnings.filterwarnings("ignore", message=".*Redirects are currently not supported.*")
# Suppress urllib3 OpenSSL warnings
try:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.NotOpenSSLWarning)
except ImportError:
    pass  # urllib3 not installed, no need to suppress

# Ensure the parent directory is in the path so imports work when running directly
# This needs to happen before other imports
_cli_file = Path(__file__).resolve()
_parent_dir = _cli_file.parent.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))

import argparse
import asyncio
import json
import os
import re
import socket
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Awaitable, Callable, Dict, List, Optional, Set, Tuple, Union

# Import from existing modules
from todozi.error import TodoziError, TaskNotFoundError, Error, ErrorManager
from todozi.storage import Storage, load_config, save_config, get_storage_dir
from todozi.models import (
    Task, TaskUpdate, TaskFilters, Priority, Status, Assignee, Project,
    QueueItem, QueueSession, QueueStatus, ApiKey, ApiKeyCollection, Err, Ok, Result
)
from todozi.agent import Agent, AgentManager, AgentStatus, AgentAssignment
from todozi.memory import Memory, MemoryManager
from todozi.idea import Idea, IdeaManager
from todozi.emb import TodoziEmbeddingService, TodoziEmbeddingConfig
from todozi.search import SearchEngine, SearchOptions, SearchResults
from todozi.api import ApiKey as ApiKeyType, ApiKeyCollection as ApiKeyCollectionType
from todozi.tags import Tag, TagManager
from todozi.summary import Summary, SummaryManager
from todozi.reminder import Reminder, ReminderManager
from todozi.chunking import CodeChunk, CodeGenerationGraph
from todozi.extract import TodoziAPIClient, ExtractResponse
from todozi.tdz_tls import TdzContentProcessorTool
from todozi.todozi import parse_todozi_format, process_chat_message_extended
from todozi.server import TodoziServer, ServerConfig

# Result type imported from models.py
# -----------------------------
# API Keys
# -----------------------------
# ApiKeysStore functionality provided by api.py functions
from todozi.api import (
    create_api_key, create_api_key_with_user_id, list_api_keys, list_active_api_keys,
    deactivate_api_key, activate_api_key, remove_api_key, check_api_key_auth
)

from todozi.types import( 
    CodeChunk,AgentAssignment,Error,ChatContent,Register,ListKeys,CheckKeys,DeactivateKey,
    ActivateKey,RemoveKey,PlanQueue,ListQueue,BacklogQueue,ActiveQueue,CompleteQueue,StartQueue,
    EndQueue,StartServer,ServerStatus,ServerEndpoints,SearchAll,Chat,CreateError,ListErrors,
    ShowError,ResolveError,DeleteError,CreateTraining,ListTraining,ShowTraining,TrainingStats,
    ExportTraining,CollectTraining,UpdateTraining,DeleteTraining,CreateAgent,ListAgents,
    ShowAgent,AssignAgent,UpdateAgent,DeleteAgent,SetModel,ShowModel,ListModels,CreateIdea,
    ListIdeas,ShowIdea,CreateMemory,CreateSecretMemory,CreateHumanMemory,CreateEmotionalMemory,
    ListMemories,ShowMemory,MemoryTypes,CreateProject,ListProjects,ShowProject,ArchiveProject,
    DeleteProject,UpdateProject,ShowTask,ListTasks,AddTask,UpdateTask,Stats,SearchTasks,StepsShow,
    StepsAdd,StepsUpdate,StepsDone,StepsArchive
)


API_KEYS = "api_keys"





# Grouped Commands
ApiCommands = Union[Register, ListKeys, CheckKeys, DeactivateKey, ActivateKey, RemoveKey]
QueueCommands = Union[
    PlanQueue, ListQueue, BacklogQueue, ActiveQueue, CompleteQueue, StartQueue, EndQueue
]
ServerCommands = Union[StartServer, ServerStatus, ServerEndpoints]
Commands = Union[
    SearchAll, Chat,
    CreateError, ListErrors, ShowError, ResolveError, DeleteError,
    CreateTraining, ListTraining, ShowTraining, TrainingStats, ExportTraining, CollectTraining, UpdateTraining, DeleteTraining,
    CreateAgent, ListAgents, ShowAgent, AssignAgent, UpdateAgent, DeleteAgent,
    SetModel, ShowModel, ListModels,
    CreateIdea, ListIdeas, ShowIdea,
    CreateMemory, CreateSecretMemory, CreateHumanMemory, CreateEmotionalMemory, ListMemories, ShowMemory, MemoryTypes,
    CreateProject, ListProjects, ShowProject, ArchiveProject, DeleteProject, UpdateProject,
    ShowTask, ListTasks, AddTask, UpdateTask,
    Stats, SearchTasks,
    StepsShow, StepsAdd, StepsUpdate, StepsDone, StepsArchive,
]

ErrorCommands = Union[CreateError, ListErrors, ShowError, ResolveError, DeleteError]
TrainingCommands = Union[CreateTraining, ListTraining, ShowTraining, TrainingStats, ExportTraining, CollectTraining, UpdateTraining, DeleteTraining]
IdeaCommands = Union[CreateIdea, ListIdeas, ShowIdea]
MemoryCommands = Union[CreateMemory, CreateSecretMemory, CreateHumanMemory, CreateEmotionalMemory, ListMemories, ShowMemory, MemoryTypes]
ProjectCommands = Union[CreateProject, ListProjects, ShowProject, ArchiveProject, DeleteProject, UpdateProject]
ShowCommands = Union[ShowTask]
ListCommands = Union[ListTasks]
AddCommands = Union[AddTask]
SearchCommands = Union[SearchTasks]
StatsCommands = Union[Stats]
StepsCommands = Union[StepsShow, StepsAdd, StepsUpdate, StepsDone, StepsArchive]


# -----------------------------
# SearchEngine - using from search.py
# -----------------------------
# SearchEngine and SearchOptions imported from search.py
# Simplified result types for CLI display
@dataclass
class TaskSearchResult:
    action: str
    status: str


@dataclass
class MemorySearchResult:
    moment: str
    meaning: str


# -----------------------------
# Embedding Service
# -----------------------------
# TodoziEmbeddingService and TodoziEmbeddingConfig imported from emb.py
# EmbeddingModel imported from emb.py


# -----------------------------
# Extract/Strategy
# -----------------------------
async def extract_content(content: Optional[str], file: Optional[str], output_format: str, human: bool) -> str:
    from todozi.extract import TodoziConfig, get_api_client, parse_extract_response, format_as_markdown, format_as_csv
    
    if not content and not file:
        raise TodoziError.validation("Either --content or --file must be provided")
    
    if file:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
    
    if not content:
        raise TodoziError.validation("No content to extract")
    
    try:
        config = await TodoziConfig.load()
        async with get_api_client(config) as client:
            response_data = await client.extract_content(
                endpoint="extract",
                content=content,
                user_id=config.user_id,
                fingerprint=config.fingerprint,
            )
            response = parse_extract_response(response_data)
            
            if output_format == "json":
                return response.to_json()
            elif output_format == "csv":
                return format_as_csv(response)
            else:
                return format_as_markdown(response)
    except Exception as e:
        raise TodoziError(f"Extraction failed: {e}")


async def strategy_content(content: Optional[str], file: Optional[str], output_format: str, human: bool) -> str:
    from todozi.extract import TodoziConfig, get_api_client, parse_extract_response, format_as_markdown, format_as_csv
    
    if not content and not file:
        raise TodoziError.validation("Either --content or --file must be provided")
    
    if file:
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()
    
    if not content:
        raise TodoziError.validation("No content to process")
    
    try:
        config = await TodoziConfig.load()
        async with get_api_client(config) as client:
            response_data = await client.extract_content(
                endpoint="strategy",
                content=content,
                user_id=config.user_id,
                fingerprint=config.fingerprint,
            )
            response = parse_extract_response(response_data)
            
            if output_format == "json":
                return response.to_json()
            elif output_format == "csv":
                return format_as_csv(response)
            else:
                return format_as_markdown(response)
    except Exception as e:
        raise TodoziError(f"Strategy generation failed: {e}")


# -----------------------------
# Todozi Handler
# -----------------------------
class TodoziHandler:
    def __init__(self, storage: Storage):
        self.storage = storage

    # ---- Basic tasks ----
    def complete_task(self, id: str) -> None:
        self.storage.complete_task_in_project(id)
        print(f"✅ Task {id} completed!")

    def fix_task_consistency(self) -> None:
        print("🔧 Fixing task data consistency...")
        self.storage.fix_completed_tasks_consistency()
        print("✅ Task consistency fix completed!")

    def delete_task(self, id: str) -> None:
        self.storage.delete_task_from_project(id)
        print(f"✅ Task {id} deleted!")

    def restore_backup(self, backup_name: str) -> None:
        self.storage.restore_backup(backup_name)

    # ---- API commands ----
    async def handle_api_command(self, command: ApiCommands) -> None:
        if isinstance(command, Register):
            api_key = create_api_key_with_user_id(command.user_id) if command.user_id else create_api_key()
            print("🔑 API key created successfully!")
            print(f"🆔 User ID: {api_key.user_id}")
            print(f"🔓 Public Key: {api_key.public_key}")
            print(f"🔒 Private Key: {api_key.private_key}")
            print(f"✅ Active: {api_key.active}")
            print(f"🕒 Created: {api_key.created_at}")
            print()
            print("💡 Keep your private key secure! It provides admin access.")
            print("📖 Use public key for read-only access, both keys for admin access.")
        elif isinstance(command, ListKeys):
            keys = list_active_api_keys() if command.active_only else list_api_keys()
            if not keys:
                print("📭 No API keys found")
                return
            print("🔑 API Keys:")
            print()
            for key in keys:
                print(f"🆔 User ID: {key.user_id}")
                print(f"🔓 Public Key: {key.public_key}")
                print(f"🔒 Private Key: {key.private_key}")
                print(f"✅ Active: {key.active}")
                print(f"🕒 Created: {key.created_at}")
                print(f"🕒 Updated: {key.updated_at}")
                print("---")
        elif isinstance(command, CheckKeys):
            user_id, is_admin = check_api_key_auth(command.public_key, command.private_key)
            print("✅ API key authentication successful!")
            print(f"🆔 User ID: {user_id}")
            print(f"🔓 Public Key: {command.public_key}")
            if command.private_key:
                print(f"🔒 Private Key: {command.private_key}")
            print(f"👑 Admin Access: {is_admin}")
            access = "admin" if is_admin else "read_only"
            print(f"📖 Access Level: {access}")
        elif isinstance(command, DeactivateKey):
            deactivate_api_key(command.user_id)
            print("🔒 API key deactivated successfully!")
            print(f"🆔 User ID: {command.user_id}")
        elif isinstance(command, ActivateKey):
            activate_api_key(command.user_id)
            print("🔓 API key activated successfully!")
            print(f"🆔 User ID: {command.user_id}")
        elif isinstance(command, RemoveKey):
            key = remove_api_key(command.user_id)
            print("🗑️  API key removed successfully!")
            print(f"🆔 User ID: {command.user_id}")
            if key:
                print(f"🔓 Public Key: {key.public_key}")
                print(f"🔒 Private Key: {key.private_key}")
        else:
            raise TodoziError.validation("Unknown API command")

    # ---- Queue commands ----
    async def handle_queue_command(self, command: QueueCommands) -> None:
        if isinstance(command, PlanQueue):
            # Validate priority quickly and convert to enum
            priority_res = Priority.from_str(command.priority)
            if isinstance(priority_res, Err):
                raise TodoziError.validation(f"Invalid priority: {command.priority}")
            priority_enum = priority_res.value
            item = QueueItem.new(command.task_name, command.task_description, priority_enum, command.project_id)
            self.storage.add_queue_item(item)
            print("✅ Queue item planned successfully!")
            print(f"📋 ID: {item.id}")
            print(f"📝 Task: {item.task_name}")
            print(f"📄 Description: {item.task_description}")
            priority_str = item.priority.value if hasattr(item.priority, 'value') else str(item.priority)
            status_str = item.status.value if hasattr(item.status, 'value') else str(item.status)
            print(f"⚡ Priority: {priority_str}")
            if item.project_id:
                print(f"📁 Project: {item.project_id}")
            print(f"📊 Status: {status_str}")
        elif isinstance(command, ListQueue):
            if command.status:
                # Validate queue status and convert string to enum
                # QueueStatus enum values are: Backlog, Active, Complete
                status_map = {
                    "backlog": QueueStatus.Backlog,
                    "active": QueueStatus.Active,
                    "complete": QueueStatus.Complete,
                }
                status_lower = command.status.lower()
                if status_lower not in status_map:
                    raise TodoziError.validation(f"Invalid queue status: {command.status}. Must be one of: backlog, active, complete")
                status_enum = status_map[status_lower]
                items = self.storage.list_queue_items_by_status(status_enum)
            else:
                items = self.storage.list_queue_items()
            if not items:
                print("📭 No queue items found")
                return
            print("📋 Queue Items:")
            print()
            for item in items:
                priority_str = item.priority.value if hasattr(item.priority, 'value') else str(item.priority)
                status_str = item.status.value if hasattr(item.status, 'value') else str(item.status)
                print(f"🆔 ID: {item.id}")
                print(f"📝 Task: {item.task_name}")
                print(f"📄 Description: {item.task_description}")
                print(f"⚡ Priority: {priority_str}")
                if item.project_id:
                    print(f"📁 Project: {item.project_id}")
                print(f"📊 Status: {status_str}")
                print(f"🕒 Created: {item.created_at}")
                print("---")
        elif isinstance(command, BacklogQueue):
            items = self.storage.list_backlog_items()
            self._print_list_header("Backlog Items", items, _queue_item_summary)
        elif isinstance(command, ActiveQueue):
            items = self.storage.list_active_items()
            self._print_list_header("Active Items", items, _queue_item_summary)
        elif isinstance(command, CompleteQueue):
            items = self.storage.list_complete_items()
            self._print_list_header("Complete Items", items, _queue_item_summary)
        elif isinstance(command, StartQueue):
            session_id = self.storage.start_queue_session(command.queue_item_id)
            print("🚀 Queue session started successfully!")
            print(f"🆔 Session ID: {session_id}")
            print(f"📋 Queue Item ID: {command.queue_item_id}")
            print(f"🕒 Started at: {_now_str()}")
        elif isinstance(command, EndQueue):
            self.storage.end_queue_session(command.session_id)
            sess = self.storage.get_queue_session(command.session_id)
            print("✅ Queue session ended successfully!")
            print(f"🆔 Session ID: {command.session_id}")
            if sess:
                print(f"📋 Queue Item ID: {sess.queue_item_id}")
                print(f"🕒 Started: {sess.start_time}")
                if sess.end_time:
                    print(f"🕒 Ended: {sess.end_time}")
                if sess.duration_seconds:
                    print(f"⏱️  Duration: {sess.duration_seconds} seconds")
        else:
            raise TodoziError.validation("Unknown queue command")

    # ---- Server commands ----
    async def handle_server_command(self, command: ServerCommands) -> None:
        if isinstance(command, StartServer):
            print("🚀 Starting Todozi Enhanced Server...")
            print(f"📡 Host: {command.host}")
            print(f"🔌 Port: {command.port}")
            print(f"📋 Available at: http://{command.host}:{command.port}")
            print()
            try:
                from todozi.server import TodoziServer, ServerConfig
                config = ServerConfig(host=command.host, port=command.port)
                server = TodoziServer(config)
                await server.start()
            except Exception as e:
                print(f"❌ Failed to start server: {e}")
                raise
        elif isinstance(command, ServerStatus):
            print("🔍 Checking server status...")
            ports = [8636, 8637, 3000]
            for port in ports:
                if _is_port_open("127.0.0.1", port):
                    print(f"✅ Server is running on port {port}")
                    print(f"🌐 API available at: http://127.0.0.1:{port}")
                    print("📖 API documentation: todozi server endpoints")
                    return
            print("❌ Server is not running on common ports (8636, 8637, 3000)")
            print("💡 Start it with: todozi server start")
            print("💡 Or specify port: todozi server start --port 8636")
        elif isinstance(command, ServerEndpoints):
            print("📡 Todozi Enhanced Server API Endpoints")
            print("══════════════════════════════════════")
            print()
            print("🎯 CORE FUNCTIONALITY:")
            print("  GET  /health                    - Health check")
            print("  GET  /stats                     - System statistics")
            print("  GET  /init                      - Initialize system")
            print()
            print("📋 TASK MANAGEMENT:")
            print("  GET  /tasks                     - List all tasks")
            print("  POST /tasks                     - Create new task")
            print("  GET  /tasks/{id}                - Get task by ID")
            print("  PUT  /tasks/{id}                - Update task")
            print("  DELETE /tasks/{id}              - Delete task")
            print("  GET  /tasks/search?q={query}    - Search tasks")
            print()
            print("🤖 ENHANCED AGENT SYSTEM (26 AGENTS):")
            print("  GET  /agents                    - List all agents")
            print("  POST /agents                    - Create new agent")
            print("  GET  /agents/{id}               - Get agent by ID")
            print("  PUT  /agents/{id}               - Update agent")
            print("  DELETE /agents/{id}             - Delete agent")
            print("  GET  /agents/available          - Get available agents")
            print("  GET  /agents/{id}/status        - Get agent status")
            print()
            print("🧠 MEMORY & IDEA MANAGEMENT:")
            print("  GET  /memories                  - List all memories")
            print("  POST /memories                  - Create new memory")
            print("  GET  /memories/{id}             - Get memory by ID")
            print("  GET  /memories/secret           - Get AI-only memories")
            print("  GET  /memories/human            - Get user-visible memories")
            print("  GET  /memories/short            - Get conversation memories")
            print("  GET  /memories/long             - Get long-term memories")
            print("  GET  /memories/emotional/{emotion} - Get emotional memories")
            print("  GET  /memories/types            - List available memory types")
            print("  GET  /ideas                     - List all ideas")
            print("  POST /ideas                     - Create new idea")
            print("  GET  /ideas/{id}                - Get idea by ID")
            print()
            print("🎓 TRAINING DATA SYSTEM:")
            print("  GET  /training                  - List all training data")
            print("  POST /training                  - Create training data")
            print("  GET  /training/{id}             - Get training data by ID")
            print("  PUT  /training/{id}             - Update training data")
            print("  DELETE /training/{id}           - Delete training data")
            print("  GET  /training/export           - Export training data")
            print("  GET  /training/stats            - Training data statistics")
            print()
            print("🧩 CODE CHUNKING SYSTEM:")
            print("  GET  /chunks                    - List all code chunks")
            print("  POST /chunks                    - Create new code chunk")
            print("  GET  /chunks/{id}               - Get chunk by ID")
            print("  PUT  /chunks/{id}               - Update chunk")
            print("  DELETE /chunks/{id}             - Delete chunk")
            print("  GET  /chunks/ready              - Get ready chunks")
            print("  GET  /chunks/graph              - Get dependency graph")
            print()
            print("💬 ENHANCED CHAT PROCESSING:")
            print("  POST /chat/process              - Process chat message")
            print("  POST /chat/agent/{id}           - Chat with specific agent")
            print("  GET  /chat/history              - Get chat history")
            print()
            print("📊 ANALYTICS & TRACKING:")
            print("  GET  /analytics/tasks           - Task analytics")
            print("  GET  /analytics/agents          - Agent analytics")
            print("  GET  /analytics/performance     - System performance")
            print("  POST /time/start/{task_id}      - Start time tracking")
            print("  POST /time/stop/{task_id}       - Stop time tracking")
            print("  GET  /time/report               - Time tracking report")
            print()
            print("📁 PROJECT MANAGEMENT:")
            print("  GET  /projects                  - List all projects")
            print("  POST /projects                  - Create new project")
            print("  GET  /projects/{name}           - Get project by name")
            print("  PUT  /projects/{name}           - Update project")
            print("  DELETE /projects/{name}         - Delete project")
            print()
            print("🔧 UTILITIES:")
            print("  POST /backup                    - Create backup")
            print("  GET  /backups                   - List backups")
            print("  POST /restore/{name}            - Restore from backup")
            print()
            print("🚀 To start the server:")
            print("  todozi server start")
            print("  todozi server start --host 0.0.0.0 --port 8636")
            print()
            print("📖 For API documentation:")
            print("  todozi server endpoints")
        else:
            raise TodoziError.validation("Unknown server command")

    # ---- Search all ----
    async def handle_search_all_command(self, command: Commands) -> None:
        if not isinstance(command, SearchAll):
            return
        print("🔍 Performing unified search across all Todozi data...")
        print(f'Query: "{command.query}"')
        print(f"Types: {command.types}")
        print()
        search_engine = SearchEngine()
        tasks = self.storage.list_tasks_across_projects(TaskFilters())
        
        from todozi.memory import MemoryManager
        from todozi.idea import IdeaManager
        from todozi.error import ErrorManager
        
        memory_manager = MemoryManager()
        await memory_manager.load_memories()
        memories = memory_manager.get_all_memories()
        
        idea_manager = IdeaManager()
        await idea_manager.load_ideas()
        ideas = idea_manager.get_all_ideas()
        
        error_manager = ErrorManager()
        errors = error_manager.list_errors()
        
        training_data = self.storage.list_training_data()
        chat_content = ChatContent(
            tasks=tasks,
            memories=memories,
            ideas=ideas,
            agent_assignments=[],
            code_chunks=[],
            errors=errors,
            training_data=training_data,
            feelings=[],
        )
        search_engine.update_index(chat_content)
        types_filter: Set[str]
        if command.types == "all":
            types_filter = {"tasks", "memories", "ideas", "errors", "training"}
        else:
            types_filter = {t.strip() for t in command.types.split(",") if t.strip()}
        search_options = SearchOptions(limit=20)
        results = search_engine.search(command.query, search_options)
        print("📊 Search Results:")
        print("═══════════════════")
        total_results = 0
        if "tasks" in types_filter and results.task_results:
            print(f"\n📋 Tasks ({len(results.task_results)}):")
            total_results += len(results.task_results)
            for i, r in enumerate(results.task_results):
                if i >= 5:
                    print(f"  ... and {len(results.task_results) - 5} more")
                    break
                status_str = r.task.status.value if hasattr(r.task.status, 'value') else str(r.task.status)
                print(f"  {r.task.action} ({status_str})")
        if "memories" in types_filter and results.memory_results:
            print(f"\n🧠 Memories ({len(results.memory_results)}):")
            total_results += len(results.memory_results)
            for i, r in enumerate(results.memory_results):
                if i >= 3:
                    print(f"  ... and {len(results.memory_results) - 3} more")
                    break
                print(f"  {r.memory.moment}: {r.memory.meaning}")
        if "ideas" in types_filter and results.idea_results:
            print(f"\n💡 Ideas ({len(results.idea_results)}):")
            total_results += len(results.idea_results)
            for i, r in enumerate(results.idea_results):
                if i >= 3:
                    print(f"  ... and {len(results.idea_results) - 3} more")
                    break
                print(f"  {r.idea.idea}")
        if "errors" in types_filter and results.error_results:
            print(f"\n❌ Errors ({len(results.error_results)}):")
            total_results += len(results.error_results)
            for i, r in enumerate(results.error_results):
                if i >= 3:
                    print(f"  ... and {len(results.error_results) - 3} more")
                    break
                print(f"  {r.error.title}: {r.error.description}")
        if "training" in types_filter and results.training_results:
            print(f"\n🎓 Training Data ({len(results.training_results)}):")
            total_results += len(results.training_results)
            for i, r in enumerate(results.training_results):
                if i >= 3:
                    print(f"  ... and {len(results.training_results) - 3} more")
                    break
                print(f"  {r.training_data.prompt}")
        if total_results == 0:
            print(f'\n❌ No results found for query: "{command.query}"')
            print("💡 Try different keywords or check if data exists")
        else:
            print(f"\n✅ Found {total_results} total results")
            print("💡 Use specific type filters: tasks,memories,ideas,errors,training")

    # ---- Chat command ----
    async def handle_chat_command(self, command: Commands) -> None:
        if not isinstance(command, Chat):
            return
        content = self.process_chat_message_extended(command.message, "cli_user")
        print("✅ Chat processed successfully!")
        print("📊 Content extracted:")
        print(f"  📋 Tasks: {len(content.tasks)}")
        print(f"  🧠 Memories: {len(content.memories)}")
        print(f"  💡 Ideas: {len(content.ideas)}")
        print(f"  🤖 Agent Assignments: {len(content.agent_assignments)}")
        print(f"  🧩 Code Chunks: {len(content.code_chunks)}")
        print(f"  ❌ Errors: {len(content.errors)}")
        print(f"  🎓 Training Data: {len(content.training_data)}")
        print()
        created_items: List[str] = []
        for task in content.tasks:
            try:
                await self.storage.add_task_to_project(task)
                created_items.append(f"📋 Task: {task.action}")
            except Exception as e:
                print(f"❌ Failed to save task '{task.action}': {e}")
        # Process other content types (memories, ideas, errors already handled above)
        if not created_items:
            print("ℹ️  No structured content found in message.")
            print("💡 Try using tags like <todozi>, <memory>, <idea>, <chunk>, <error>, <train>")
        else:
            print("✅ Successfully created/processed:")
            for item in created_items:
                print(f"  {item}")
            print()
            print(f"🎉 Total items processed: {len(created_items)}")
        print()
        print("🔍 Available Tags:")
        print("  📋 <todozi>action|time|priority|project|status</todozi> - Create tasks")
        print("  🧠 <memory>moment|meaning|reason|importance|term</memory> - Store standard memories")
        print("  🔒 <memory_secret>moment|meaning|reason|importance|term</memory_secret> - AI-only memories")
        print("  👤 <memory_human>moment|meaning|reason|importance|term</memory_human> - User-visible memories")
        print("  💬 <memory_short>moment|meaning|reason|importance</memory_short> - Conversation memories")
        print("  🏛️ <memory_long>moment|meaning|reason|importance</memory_long> - Long-term memories")
        print("  😊 <memory_emotion>moment|meaning|reason|importance|term</memory_emotion> - Emotional memories")
        print("  💡 <idea>idea|share|importance</idea> - Capture ideas")
        print("  🤖 <todozi_agent>agent_id|task_id|project_id</todozi_agent> - Assign agents")
        print("  🧩 <chunk>language|code|description</chunk> - Code chunks")
        print("  ❌ <error>title|description|severity|category</error> - Track errors")
        print("  🎓 <train>prompt|completion|data_type</train> - Training data")

    def process_chat_message_extended(self, message: str, user_id: str) -> ChatContent:
        from todozi.tdz_tls import parse_chat_message_extended as parse_chat
        from todozi.models import MemoryImportance, MemoryTerm, MemoryType, IdeaImportance, ShareLevel, ItemStatus
        from todozi.error import ErrorSeverity, ErrorCategory
        
        parsed = parse_chat(message, "cli")
        
        tasks: List[Task] = []
        for task_item in parsed.tasks:
            priority_result = Priority.from_str(task_item.priority)
            if isinstance(priority_result, Err):
                priority = Priority.MEDIUM
            else:
                priority = priority_result.value
            
            task_result = Task.new_full(
                user_id=user_id,
                action=task_item.action,
                time=task_item.time or "1 hour",
                priority=priority,
                parent_project=task_item.parent_project or "general",
                status=Status.TODO,
                assignee=None,
                tags=[],
                dependencies=[],
                context_notes=task_item.context_notes,
                progress=None,
            )
            if isinstance(task_result, Ok):
                tasks.append(task_result.value)
        
        memories: List[Memory] = []
        for mem_item in parsed.memories:
            importance_result = MemoryImportance.from_str("medium")
            if isinstance(importance_result, Err):
                importance = MemoryImportance.MEDIUM
            else:
                importance = importance_result.value
            
            term_result = MemoryTerm.from_str("short")
            if isinstance(term_result, Err):
                term = MemoryTerm.SHORT
            else:
                term = term_result.value
            
            memory = Memory(
                user_id=user_id,
                project_id=None,
                status=ItemStatus.ACTIVE,
                moment=mem_item.moment,
                meaning=mem_item.meaning,
                reason=mem_item.reason,
                importance=importance,
                term=term,
                memory_type=MemoryType.STANDARD,
                tags=[],
            )
            memories.append(memory)
        
        ideas: List[Idea] = []
        for idea_item in parsed.ideas:
            importance_result = IdeaImportance.from_str("medium")
            if isinstance(importance_result, Err):
                importance = IdeaImportance.MEDIUM
            else:
                importance = importance_result.value
            
            share_result = ShareLevel.from_str("team")
            if isinstance(share_result, Err):
                share = ShareLevel.TEAM
            else:
                share = share_result.value
            
            idea = Idea(
                idea=idea_item.idea,
                project_id=None,
                status=ItemStatus.ACTIVE,
                share=share,
                importance=importance,
                tags=[],
                context=None,
            )
            ideas.append(idea)
        
        errors: List[Error] = []
        for err_item in parsed.errors:
            error = Error.new(
                title=err_item.title,
                description=err_item.detail,
                source="cli",
            )
            errors.append(error)
        
        return ChatContent(
            tasks=tasks,
            memories=memories,
            ideas=ideas,
            agent_assignments=[],
            code_chunks=parsed.code_chunks,
            errors=errors,
            training_data=[],
            feelings=[],
        )

    # ---- Error command ----
    async def handle_error_command(self, command: Commands) -> None:
        from todozi.error import ErrorManager, ErrorSeverity, ErrorCategory
        
        ec = command
        error_manager = ErrorManager()
        
        if isinstance(ec, CreateError):
            severity_result = ErrorSeverity.from_str(ec.severity)
            severity = severity_result.value if isinstance(severity_result, Ok) else ErrorSeverity.MEDIUM
            
            category_result = ErrorCategory.from_str(ec.category)
            category = category_result.value if isinstance(category_result, Ok) else ErrorCategory.RUNTIME
            
            error = Error.new(
                title=ec.title,
                description=ec.description,
                source=ec.source,
            )
            error.severity = severity
            error.category = category
            if ec.context:
                error.context = ec.context
            if ec.tags:
                error.tags = [t.strip() for t in ec.tags.split(",") if t.strip()]
            
            error_manager.save_error(error)
            print(f"✅ Error record created with ID: {error.id}")
        elif isinstance(ec, ListErrors):
            errors = error_manager.list_errors()
            
            if ec.severity:
                severity_result = ErrorSeverity.from_str(ec.severity)
                if isinstance(severity_result, Ok):
                    errors = [e for e in errors if e.severity == severity_result.value]
            
            if ec.category:
                category_result = ErrorCategory.from_str(ec.category)
                if isinstance(category_result, Ok):
                    errors = [e for e in errors if e.category == category_result.value]
            
            if ec.unresolved_only:
                errors = [e for e in errors if not e.resolved]
            
            if not errors:
                print("No error records found matching criteria.")
            else:
                print(f"Found {len(errors)} error(s):")
                for e in errors:
                    print(f"  {e.id}: {e.title} ({e.severity.value}, {e.category.value})")
        elif isinstance(ec, ShowError):
            error = error_manager.get_error(ec.id)
            if not error:
                print(f"Error {ec.id} not found.")
                return
            
            print(f"Error ID: {error.id}")
            print(f"Title: {error.title}")
            print(f"Description: {error.description}")
            print(f"Source: {error.source}")
            print(f"Severity: {error.severity.value}")
            print(f"Category: {error.category.value}")
            print(f"Context: {error.context or 'N/A'}")
            print(f"Tags: {', '.join(error.tags) if error.tags else ''}")
            print(f"Created At: {error.created_at}")
            print(f"Resolved: {'Yes' if error.resolved else 'No'}")
            if error.resolved_at:
                print(f"Resolved At: {error.resolved_at}")
            if error.resolution:
                print(f"Resolution: {error.resolution}")
        elif isinstance(ec, ResolveError):
            error = error_manager.get_error(ec.id)
            if not error:
                print(f"Error {ec.id} not found.")
                return
            
            error.resolved = True
            error.resolved_at = datetime.now(timezone.utc)
            if ec.resolution:
                error.resolution = ec.resolution
            error_manager.save_error(error)
            print(f"✅ Error {ec.id} marked as resolved!")
        elif isinstance(ec, DeleteError):
            error_manager.delete_error(ec.id)
            print(f"✅ Error {ec.id} deleted successfully!")
        else:
            raise TodoziError.validation("Unknown error command")

    # ---- Training command ----
    async def handle_train_command(self, command: TrainingCommands) -> None:
        from todozi.models import TrainingData, TrainingDataType
        
        tc = command
        if isinstance(tc, CreateTraining):
            data_type_result = TrainingDataType.from_str(tc.data_type)
            data_type = data_type_result.value if isinstance(data_type_result, Ok) else TrainingDataType.INSTRUCTION
            
            training = TrainingData.new(
                data_type=data_type.value,
                prompt=tc.prompt,
                completion=tc.completion,
                source="cli",
            )
            if tc.context:
                training.context = tc.context
            if tc.tags:
                training.tags = [t.strip() for t in tc.tags.split(",") if t.strip()]
            
            self.storage.save_training_data(training)
            print(f"✅ Training data created successfully with ID: {training.id}")
        elif isinstance(tc, ListTraining):
            all_training = self.storage.list_training_data()
            
            if tc.data_type:
                data_type_result = TrainingDataType.from_str(tc.data_type)
                if isinstance(data_type_result, Ok):
                    all_training = [t for t in all_training if t.data_type == data_type_result.value]
            
            if not all_training:
                print("No training data found matching criteria.")
            else:
                print(f"Found {len(all_training)} training data record(s):")
                for t in all_training:
                    print(f"  {t.id}: {t.data_type.value} - {t.prompt[:50]}...")
        elif isinstance(tc, ShowTraining):
            try:
                training = self.storage.load_training_data(tc.id)
                print(f"Training Data ID: {training.id}")
                print(f"Data Type: {training.data_type.value}")
                print(f"Prompt: {training.prompt}")
                print(f"Completion: {training.completion}")
                print(f"Source: {training.source}")
                print(f"Context: {training.context or 'N/A'}")
                print(f"Tags: {', '.join(training.tags) if training.tags else ''}")
                print(f"Quality Score: {training.quality_score or 'None'}")
                print(f"Created At: {training.created_at}")
            except Exception as e:
                print(f"Error loading training data: {e}")
        elif isinstance(tc, TrainingStats):
            all_training = self.storage.list_training_data()
            type_counts: Dict[str, int] = {}
            for t in all_training:
                type_str = t.data_type.value
                type_counts[type_str] = type_counts.get(type_str, 0) + 1
            
            print("Training Data Statistics:")
            print(f"  Total records: {len(all_training)}")
            print("\nBy type:")
            for t, c in type_counts.items():
                print(f"  {t}: {c}")
        elif isinstance(tc, ExportTraining):
            all_training = self.storage.list_training_data()
            output_path = Path(tc.output_path) if tc.output_path else Path("training_data_export.json")
            
            export_data = [{
                "id": t.id,
                "data_type": t.data_type.value,
                "prompt": t.prompt,
                "completion": t.completion,
                "context": t.context,
                "tags": t.tags,
                "quality_score": t.quality_score,
                "source": t.source,
                "created_at": t.created_at.isoformat(),
            } for t in all_training]
            
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Exported {len(export_data)} training data records to {output_path}")
        elif isinstance(tc, CollectTraining):
            chat_content = self.process_chat_message_extended(tc.message, "cli")
            collected = 0
            for task in chat_content.tasks:
                training = TrainingData.new(
                    data_type="instruction",
                    prompt=f"Create task: {task.action}",
                    completion=json.dumps(task.to_dict() if hasattr(task, 'to_dict') else {"action": task.action}),
                    source="cli_collect",
                )
                self.storage.save_training_data(training)
                collected += 1
            print(f"✅ Collected {collected} training data record(s) from message")
        elif isinstance(tc, UpdateTraining):
            try:
                training = self.storage.load_training_data(tc.id)
                if tc.prompt:
                    training.prompt = tc.prompt
                if tc.completion:
                    training.completion = tc.completion
                if tc.data_type:
                    data_type_result = TrainingDataType.from_str(tc.data_type)
                    if isinstance(data_type_result, Ok):
                        training.data_type = data_type_result.value
                if tc.context is not None:
                    training.context = tc.context
                if tc.tags:
                    training.tags = [t.strip() for t in tc.tags.split(",") if t.strip()]
                self.storage.save_training_data(training)
                print(f"✅ Training data {tc.id} updated successfully!")
            except Exception as e:
                print(f"Error updating training data: {e}")
        elif isinstance(tc, DeleteTraining):
            self.storage.delete_training_data(tc.id)
            print(f"✅ Training data {tc.id} deleted successfully!")
        else:
            raise TodoziError.validation("Unknown training command")

    # ---- Agent command ----
    async def handle_agent_command(self, command: Commands) -> None:
        from todozi.agent import AgentManager
        from todozi.models import ModelConfig, AgentTool, AgentBehaviors, AgentConstraints, RateLimit, AgentMetadata, AgentStatus, AssignmentStatus
        
        agent_manager = AgentManager()
        await agent_manager.load_agents()
        
        if isinstance(command, CreateAgent):
            from todozi.models import ModelConfig, AgentTool, AgentBehaviors, AgentConstraints, RateLimit, AgentMetadata
            
            model = ModelConfig(
                provider=command.model_provider,
                name=command.model_name,
                temperature=command.temperature,
                max_tokens=command.max_tokens,
            )
            
            caps = [c.strip() for c in command.capabilities.split(",")] if command.capabilities else ["general_assistance"]
            specs = [s.strip() for s in command.specializations.split(",")] if command.specializations else ["general"]
            
            agent = Agent.new(
                id=command.id,
                name=command.name,
                description=command.description,
            )
            agent.model = model
            agent.capabilities = caps
            agent.specializations = specs
            agent.metadata.category = command.category
            
            await agent_manager.create_agent(agent)
            print(f"✅ Agent '{command.id}' created successfully!")
        elif isinstance(command, ListAgents):
            agents = agent_manager.get_all_agents()
            if not agents:
                print("No agents found.")
            else:
                print("🤖 Available Agents:")
                print("════════════════════")
                for agent in agents:
                    status_emoji = "🟢" if agent.is_available() else "🔴"
                    print(f"{status_emoji} {agent.id} - {agent.name} ({agent.metadata.category}) - {agent.description}")
        elif isinstance(command, ShowAgent):
            agent = agent_manager.get_agent(command.id)
            if not agent:
                print(f"Agent '{command.id}' not found.")
                return
            
            print(f"🤖 Agent Details:")
            print("═══════════════")
            print(f"🆔 ID: {agent.id}")
            print(f"📛 Name: {agent.name}")
            print(f"📝 Description: {agent.description}")
            print(f"🏷️ Category: {agent.metadata.category}")
            print(f"📊 Status: {agent.metadata.status.value}")
            print(f"🤖 Model: {agent.model.name} ({agent.model.provider})")
            print(f"🌡️ Temperature: {agent.model.temperature}")
            print(f"🔢 Max Tokens: {agent.model.max_tokens}")
            print(f"⚡ Capabilities: {', '.join(agent.capabilities)}")
            print(f"🎯 Specializations: {', '.join(agent.specializations)}")
            print(f"🛠️ Tools: {len(agent.tools)}")
            print(f"📅 Created: {agent.created_at}")
            print(f"🔄 Updated: {agent.updated_at}")
        elif isinstance(command, AssignAgent):
            from todozi.models import AgentAssignment, AssignmentStatus
            
            assignment = AgentAssignment(
                agent_id=command.agent_id,
                task_id=command.task_id,
                project_id=command.project_id,
                status=AssignmentStatus.ASSIGNED,
            )
            await agent_manager.assign_task_to_agent(command.task_id, command.agent_id, command.project_id)
            print(f"✅ Task {command.task_id} assigned to agent {command.agent_id} in project {command.project_id}")
        elif isinstance(command, UpdateAgent):
            agent = agent_manager.get_agent(command.id)
            if not agent:
                print(f"Agent '{command.id}' not found.")
                return
            
            from todozi.agent import AgentUpdate
            updates = AgentUpdate()
            if command.name:
                updates.name = command.name
            if command.description:
                updates.description = command.description
            if command.capabilities:
                updates.capabilities = [c.strip() for c in command.capabilities.split(",")]
            if command.specializations:
                updates.specializations = [s.strip() for s in command.specializations.split(",")]
            if command.status:
                status_result = AgentStatus.from_str(command.status)
                if isinstance(status_result, Ok):
                    updates.status = status_result.value
            
            await agent_manager.update_agent(command.id, updates)
            print(f"✅ Agent '{command.id}' updated successfully!")
        elif isinstance(command, DeleteAgent):
            await agent_manager.delete_agent(command.id)
            print(f"✅ Agent '{command.id}' deleted successfully!")
        else:
            raise TodoziError.validation("Unknown agent command")

    # ---- Embeddings command ----
    async def handle_emb_command(self, command: Commands) -> None:
        from todozi.emb import EmbeddingModel, TodoziEmbeddingConfig, TodoziEmbeddingService
        
        if isinstance(command, SetModel):
            print(f"🔄 Setting embedding model to: {command.model_name}")
            print()
            print("📥 Testing model download and validation...")
            try:
                model = EmbeddingModel(model_name=command.model_name, device="cpu")
                model._ensure_model()
                print("✅ Model set successfully!")
                print("💾 Cached in: ~/.cache/todozi/models/")
                print(f"📊 Dimensions: {model.dimensions}")
            except Exception as e:
                print(f"❌ Failed to load model: {e}")
        elif isinstance(command, ShowModel):
            config = TodoziEmbeddingConfig()
            service = TodoziEmbeddingService(config)
            await service.initialize()
            print("📊 Current embedding model:")
            print(f"  Model: {config.model_name}")
            print(f"  Dimensions: {config.dimensions}")
            print(f"  Similarity Threshold: {config.similarity_threshold}")
            print()
            print("💾 Cached in: ~/.cache/todozi/models/")
        elif isinstance(command, ListModels):
            print("📚 Popular Sentence-Transformers Models:")
            print()
            print("🚀 Fast & Lightweight:")
            print("  sentence-transformers/all-MiniLM-L6-v2")
            print("    → 384 dimensions, ~90MB, good for most use cases")
            print()
            print("⚡ Balanced:")
            print("  sentence-transformers/all-mpnet-base-v2")
            print("    → 768 dimensions, ~420MB, better semantic quality")
            print()
            print("🌍 Multilingual:")
            print("  sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
            print("    → 384 dimensions, supports 50+ languages")
            print()
            print("🎯 High Performance:")
            print("  sentence-transformers/all-roberta-large-v1")
            print("    → 1024 dimensions, ~1.4GB, best quality")
            print()
            print("💡 Set a model with: todozi emb set-model <model-name>")
            print("🔍 Browse more at: https://huggingface.co/sentence-transformers")
        else:
            raise TodoziError.validation("Unknown emb command")

    # ---- Idea command ----
    async def handle_idea_command(self, command: IdeaCommands) -> None:
        from todozi.idea import IdeaManager
        from todozi.models import IdeaImportance, ShareLevel, ItemStatus
        
        idea_manager = IdeaManager()
        await idea_manager.load_ideas()
        
        if isinstance(command, CreateIdea):
            share_result = ShareLevel.from_str(command.share)
            share = share_result.value if isinstance(share_result, Ok) else ShareLevel.TEAM
            
            importance_result = IdeaImportance.from_str(command.importance)
            importance = importance_result.value if isinstance(importance_result, Ok) else IdeaImportance.MEDIUM
            
            tags = [t.strip() for t in command.tags.split(",")] if command.tags else []
            
            idea = Idea(
                idea=command.idea,
                project_id=None,
                status=ItemStatus.ACTIVE,
                share=share,
                importance=importance,
                tags=tags,
                context=command.context,
            )
            await idea_manager.create_idea(idea)
            print(f"✅ Idea created with ID: {idea.id}")
        elif isinstance(command, ListIdeas):
            ideas = idea_manager.get_all_ideas()
            
            if command.share:
                share_result = ShareLevel.from_str(command.share)
                if isinstance(share_result, Ok):
                    ideas = [i for i in ideas if i.share == share_result.value]
            
            if command.importance:
                importance_result = IdeaImportance.from_str(command.importance)
                if isinstance(importance_result, Ok):
                    ideas = [i for i in ideas if i.importance == importance_result.value]
            
            if not ideas:
                print("No ideas found matching criteria.")
            else:
                print(f"Found {len(ideas)} idea(s):")
                for idea in ideas:
                    print(f"  {idea.id}: {idea.idea[:60]}... ({idea.importance.value}, {idea.share.value})")
        elif isinstance(command, ShowIdea):
            idea = idea_manager.get_idea(command.id)
            if not idea:
                print(f"Idea {command.id} not found.")
                return
            
            print(f"Idea ID: {idea.id}")
            print(f"Idea: {idea.idea}")
            print(f"Share Level: {idea.share.value}")
            print(f"Importance: {idea.importance.value}")
            print(f"Status: {idea.status.value}")
            if idea.tags:
                print(f"Tags: {', '.join(idea.tags)}")
            if idea.context:
                print(f"Context: {idea.context}")
            print(f"Created At: {idea.created_at}")
        else:
            raise TodoziError.validation("Unknown idea command")

    # ---- Memory command ----
    async def handle_memory_command(self, command: MemoryCommands) -> None:
        from todozi.memory import MemoryManager
        from todozi.models import MemoryImportance, MemoryTerm, MemoryType, ItemStatus
        
        memory_manager = MemoryManager()
        await memory_manager.load_memories()
        
        if isinstance(command, CreateMemory):
            importance_result = MemoryImportance.from_str(command.importance)
            importance = importance_result.value if isinstance(importance_result, Ok) else MemoryImportance.MEDIUM
            
            term_result = MemoryTerm.from_str(command.term or "short")
            term = term_result.value if isinstance(term_result, Ok) else MemoryTerm.SHORT
            
            memory_type_result = MemoryType.from_str(command.memory_type)
            memory_type = memory_type_result.value if isinstance(memory_type_result, Ok) else MemoryType.STANDARD
            
            tags = [t.strip() for t in command.tags.split(",")] if command.tags else []
            
            memory = Memory(
                user_id="cli_user",
                project_id=None,
                status=ItemStatus.ACTIVE,
                moment=command.moment,
                meaning=command.meaning,
                reason=command.reason or "",
                importance=importance,
                term=term,
                memory_type=memory_type,
                tags=tags,
            )
            await memory_manager.create_memory(memory)
            print(f"✅ Memory created with ID: {memory.id}")
        elif isinstance(command, CreateSecretMemory):
            importance_result = MemoryImportance.from_str(command.importance)
            importance = importance_result.value if isinstance(importance_result, Ok) else MemoryImportance.MEDIUM
            
            term_result = MemoryTerm.from_str(command.term or "short")
            term = term_result.value if isinstance(term_result, Ok) else MemoryTerm.SHORT
            
            tags = [t.strip() for t in command.tags.split(",")] if command.tags else []
            
            memory = Memory(
                user_id="cli_user",
                project_id=None,
                status=ItemStatus.ACTIVE,
                moment=command.moment,
                meaning=command.meaning,
                reason=command.reason or "",
                importance=importance,
                term=term,
                memory_type=MemoryType.SECRET,
                tags=tags,
            )
            await memory_manager.create_memory(memory)
            print(f"✅ Secret memory created with ID: {memory.id} (visible only to AI)")
        elif isinstance(command, CreateHumanMemory):
            importance_result = MemoryImportance.from_str(command.importance)
            importance = importance_result.value if isinstance(importance_result, Ok) else MemoryImportance.MEDIUM
            
            term_result = MemoryTerm.from_str(command.term or "short")
            term = term_result.value if isinstance(term_result, Ok) else MemoryTerm.SHORT
            
            tags = [t.strip() for t in command.tags.split(",")] if command.tags else []
            
            memory = Memory(
                user_id="cli_user",
                project_id=None,
                status=ItemStatus.ACTIVE,
                moment=command.moment,
                meaning=command.meaning,
                reason=command.reason or "",
                importance=importance,
                term=term,
                memory_type=MemoryType.HUMAN,
                tags=tags,
            )
            await memory_manager.create_memory(memory)
            print(f"✅ Human-visible memory created with ID: {memory.id}")
        elif isinstance(command, CreateEmotionalMemory):
            importance_result = MemoryImportance.from_str(command.importance)
            importance = importance_result.value if isinstance(importance_result, Ok) else MemoryImportance.MEDIUM
            
            term_result = MemoryTerm.from_str(command.term or "short")
            term = term_result.value if isinstance(term_result, Ok) else MemoryTerm.SHORT
            
            tags = [t.strip() for t in command.tags.split(",")] if command.tags else []
            
            memory = Memory(
                user_id="cli_user",
                project_id=None,
                status=ItemStatus.ACTIVE,
                moment=command.moment,
                meaning=command.meaning,
                reason=command.reason or "",
                importance=importance,
                term=term,
                memory_type=MemoryType.EMOTIONAL,
                tags=tags,
            )
            await memory_manager.create_memory(memory)
            print(f"✅ Emotional memory created with ID: {memory.id}")
        elif isinstance(command, ListMemories):
            memories = memory_manager.get_all_memories()
            
            if command.importance:
                importance_result = MemoryImportance.from_str(command.importance)
                if isinstance(importance_result, Ok):
                    memories = [m for m in memories if m.importance == importance_result.value]
            
            if command.term:
                term_result = MemoryTerm.from_str(command.term)
                if isinstance(term_result, Ok):
                    memories = [m for m in memories if m.term == term_result.value]
            
            if command.memory_type:
                memory_type_result = MemoryType.from_str(command.memory_type)
                if isinstance(memory_type_result, Ok):
                    memories = [m for m in memories if m.memory_type == memory_type_result.value]
            
            if not memories:
                print("No memories found matching criteria.")
            else:
                print(f"Found {len(memories)} memory(ies):")
                for m in memories:
                    print(f"  {m.id}: {m.moment[:60]}... ({m.importance.value}, {m.memory_type.value})")
        elif isinstance(command, ShowMemory):
            memory = memory_manager.get_memory(command.id)
            if not memory:
                print(f"Memory {command.id} not found.")
                return
            
            print(f"Memory ID: {memory.id}")
            print(f"Moment: {memory.moment}")
            print(f"Meaning: {memory.meaning}")
            print(f"Reason: {memory.reason}")
            print(f"Importance: {memory.importance.value}")
            print(f"Term: {memory.term.value}")
            print(f"Type: {memory.memory_type.value}")
            print(f"Status: {memory.status.value}")
            if memory.tags:
                print(f"Tags: {', '.join(memory.tags)}")
            print(f"Created At: {memory.created_at}")
        elif isinstance(command, MemoryTypes):
            print("Available memory types:")
            print("  standard  - Regular memories")
            print("  secret    - AI-only memories")
            print("  human     - User-visible memories")
            print("  short     - Conversation-related memories")
            print("  long      - Long-term memories")
            print("  Emotional types:")
            print("    happy, sad, angry, fearful, surprised, disgusted")
            print("    excited, anxious, confident, frustrated, motivated")
            print("    overwhelmed, curious, satisfied, disappointed, grateful")
            print("    proud, ashamed, hopeful, resigned")
        else:
            raise TodoziError.validation("Unknown memory command")

    # ---- Backups ----
    async def handle_list_backups_command(self) -> None:
        backups = self.storage.list_backups()
        if not backups:
            print("No backups found.")
        else:
            print("Available backups:")
            for b in backups:
                print(f"  {b}")

    # ---- Stats ----
    async def handle_stats_command(self, _command: StatsCommands) -> None:
        all_tasks = self.storage.list_tasks_across_projects(TaskFilters())
        active_tasks = self.storage.list_tasks_across_projects(
            TaskFilters(status=Status.TODO)
        )
        completed_tasks = self.storage.list_tasks_across_projects(
            TaskFilters(status=Status.DONE)
        )
        projects = self.storage.list_projects()
        print("Todozi Statistics:")
        print(f"  Total tasks: {len(all_tasks)}")
        print(f"  Active tasks: {len(active_tasks)}")
        print(f"  Completed tasks: {len(completed_tasks)}")
        print(f"  Projects: {len(projects)}")
        priority_counts: Dict[str, int] = {}
        for t in all_tasks:
            priority_str = t.priority.value if hasattr(t.priority, 'value') else str(t.priority)
            priority_counts[priority_str] = priority_counts.get(priority_str, 0) + 1
        print("\nPriority breakdown:")
        for p, c in priority_counts.items():
            print(f"  {p}: {c}")

    # ---- Search tasks ----
    async def handle_search_command(self, command: SearchCommands) -> None:
        if isinstance(command, SearchTasks):
            tasks = self.storage.search_tasks(command.query)
            print(f"Found {len(tasks)} tasks matching '{command.query}':")
            for t in tasks:
                status_str = t.status.value if hasattr(t.status, 'value') else str(t.status)
                print(f"  {t.id}: {t.action} ({status_str})")
        else:
            raise TodoziError.validation("Unknown search command")

    # ---- Project command ----
    async def handle_project_command(self, command: ProjectCommands) -> None:
        if isinstance(command, CreateProject):
            self.storage.create_project(command.name, command.description)
            print(f"Project '{command.name}' created successfully!")
        elif isinstance(command, ListProjects):
            projects = self.storage.list_projects()
            if not projects:
                print("No projects found.")
            else:
                # Render simple ASCII table
                rows = []
                for p in projects:
                    task_count = len(self.storage.get_project_tasks(p.name))
                    rows.append([p.name, p.description or "No description", p.status, str(task_count)])
                print(_to_table(["Name", "Description", "Status", "Tasks"], rows))
        elif isinstance(command, ShowProject):
            proj = self.storage.get_project(command.name)
            tasks = self.storage.get_project_tasks(command.name)
            print(f"Project: {proj.name}")
            if proj.description:
                print(f"Description: {proj.description}")
            print(f"Status: {proj.status}")
            print(f"Tasks: {len(tasks)}")
            print(f"Created: {proj.created_at}")
            print(f"Updated: {proj.updated_at}")
            if tasks:
                print("\nTasks:")
                for t in tasks:
                    print(f"  {t.id}: {t.action} ({t.status})")
        elif isinstance(command, ArchiveProject):
            self.storage.archive_project(command.name)
            print(f"Project '{command.name}' archived!")
        elif isinstance(command, DeleteProject):
            self.storage.delete_project(command.name)
            print(f"Project '{command.name}' deleted!")
        elif isinstance(command, UpdateProject):
            proj = self.storage.get_project(command.name)
            original_name = proj.name
            if command.new_name:
                proj.name = command.new_name
            if command.description is not None:
                proj.description = command.description
            if command.status:
                proj.status = command.status
            self.storage.update_project(proj)
            print(f"✅ Project '{command.name}' updated successfully!")
            if original_name != proj.name:
                print(f"   New name: '{proj.name}'")
        else:
            raise TodoziError.validation("Unknown project command")

    # ---- Update task ----
    async def handle_update_command(
        self,
        id: str,
        action: Optional[str],
        time: Optional[str],
        priority: Optional[str],
        project: Optional[str],
        status: Optional[str],
        assignee: Optional[str],
        tags: Optional[str],
        dependencies: Optional[str],
        context: Optional[str],
        progress: Optional[int],
    ) -> None:
        updates = TaskUpdate()
        if action is not None:
            updates = updates.with_action(action)
        if time is not None:
            updates = updates.with_time(time)
        if priority is not None:
            # Convert string to Priority enum
            priority_res = Priority.from_str(priority)
            if isinstance(priority_res, Err):
                raise TodoziError.validation(f"Invalid priority: {priority}")
            updates = updates.with_priority(priority_res.value)
        if project is not None:
            updates = updates.with_parent_project(project)
        if status is not None:
            # Convert string to Status enum
            status_res = Status.from_str(status)
            if isinstance(status_res, Err):
                raise TodoziError.validation(f"Invalid status: {status}")
            updates = updates.with_status(status_res.value)
        if assignee is not None:
            updates = updates.with_assignee(assignee)
        if tags is not None:
            updates = updates.with_tags(_parse_tags(tags))
        if dependencies is not None:
            updates = updates.with_dependencies(_parse_tags(dependencies))
        if context is not None:
            updates = updates.with_context_notes(context)
        if progress is not None:
            updates = updates.with_progress(progress)
        await self.storage.update_task_in_project(id, updates)
        print(f"Task {id} updated successfully!")

    # ---- Show command ----
    async def handle_show_command(self, command: ShowCommands) -> None:
        if isinstance(command, ShowTask):
            task = self.storage.get_task_from_any_project(command.id)
            print("Task:", task.id)
            print("Action:", task.action)
            print("Time:", task.time)
            print("Priority:", task.priority.value if hasattr(task.priority, 'value') else str(task.priority))
            print("Project:", task.parent_project)
            print("Status:", task.status.value if hasattr(task.status, 'value') else str(task.status))
            if task.assignee:
                print("Assignee:", str(task.assignee))
            if task.tags:
                print("Tags:", ", ".join(task.tags))
            if task.dependencies:
                print("Dependencies:", ", ".join(task.dependencies))
            if task.context_notes:
                print("Context:", task.context_notes)
            if task.progress is not None:
                print("Progress:", f"{task.progress}%")
            print("Created:", task.created_at)
            print("Updated:", task.updated_at)
        else:
            raise TodoziError.validation("Unknown show command")

    # ---- List command ----
    async def handle_list_command(self, command: ListCommands) -> None:
        if isinstance(command, ListTasks):
            filters = TaskFilters()
            if command.project:
                filters.project = command.project
            if command.status:
                # Convert string to Status enum
                status_res = Status.from_str(command.status)
                if isinstance(status_res, Err):
                    raise TodoziError.validation(f"Invalid status: {command.status}")
                filters.status = status_res.value
            if command.priority:
                # Convert string to Priority enum
                priority_res = Priority.from_str(command.priority)
                if isinstance(priority_res, Err):
                    raise TodoziError.validation(f"Invalid priority: {command.priority}")
                filters.priority = priority_res.value
            if command.assignee:
                # Convert string to Assignee
                assignee_res = Assignee.from_str(command.assignee)
                if isinstance(assignee_res, Err):
                    raise TodoziError.validation(f"Invalid assignee: {command.assignee}")
                filters.assignee = assignee_res.value
            if command.tags:
                filters.tags = _parse_tags(command.tags)
            filters.search = command.search
            tasks = self.storage.list_tasks_across_projects(filters)
            if not tasks:
                print("No tasks found.")
            else:
                rows = []
                for t in tasks:
                    priority_str = t.priority.value if hasattr(t.priority, 'value') else str(t.priority)
                    status_str = t.status.value if hasattr(t.status, 'value') else str(t.status)
                    assignee_str = str(t.assignee) if t.assignee else "unassigned"
                    rows.append([
                        t.id,
                        t.action[:50] + ("..." if len(t.action) > 50 else ""),
                        t.parent_project,
                        priority_str,
                        status_str,
                        assignee_str,
                        f"{t.progress}%" if t.progress is not None else "N/A",
                    ])
                print(_to_table(["ID", "Action", "Project", "Priority", "Status", "Assignee", "Progress"], rows))
        else:
            raise TodoziError.validation("Unknown list command")

    # ---- Add command ----
    async def handle_add_command(self, command: AddCommands) -> None:
        if isinstance(command, AddTask):
            tags_vec = _parse_tags(command.tags or "")
            deps_vec = _parse_tags(command.dependencies or "")
            # Convert priority and status strings to enums
            priority_res = Priority.from_str(command.priority)
            if isinstance(priority_res, Err):
                raise TodoziError.validation(f"Invalid priority: {command.priority}")
            priority_enum = priority_res.value
            
            status_res = Status.from_str(command.status)
            if isinstance(status_res, Err):
                raise TodoziError.validation(f"Invalid status: {command.status}")
            status_enum = status_res.value
            
            # Convert assignee string to Assignee if provided
            assignee_obj = None
            if command.assignee:
                assignee_res = Assignee.from_str(command.assignee)
                if isinstance(assignee_res, Err):
                    raise TodoziError.validation(f"Invalid assignee: {command.assignee}")
                assignee_obj = assignee_res.value
            
            task_result = Task.new_full(
                user_id="cli_user",
                action=command.action,
                time=command.time,
                priority=priority_enum,
                parent_project=command.project,
                status=status_enum,
                assignee=assignee_obj,
                tags=tags_vec,
                dependencies=deps_vec,
                context_notes=command.context,
                progress=command.progress,
            )
            if isinstance(task_result, Err):
                raise task_result.error
            task = task_result.value
            await self.storage.add_task_to_project(task)
            print(f"Task created: {task.id}")
            # Try to retrieve task from project-based storage
            try:
                stored = self.storage.get_task_from_project(task.parent_project, task.id)
                print("Action:", stored.action)
                print("Project:", stored.parent_project)
                print("Priority:", stored.priority)
                print("Status:", stored.status)
            except TodoziError:
                pass
        else:
            raise TodoziError.validation("Unknown add command")

    # ---- IND (retired) ----
    async def handle_ind_command(self) -> None:
        print("❌ Ind functionality has been retired")

    # ---- Formatters ----
    @staticmethod
    def format_task(task: Task) -> str:
        output = f"[{task.id}] {task.action}"
        if task.tags:
            output += " " + " ".join(f"#{tag}" for tag in task.tags)
        output += f"\n  Project: {task.parent_project}"
        output += f" | Priority: {task.priority}"
        output += f" | Status: {task.status}"
        if task.assignee:
            output += f" | Assignee: {task.assignee}"
        if task.progress is not None:
            output += f" | Progress: {task.progress}%"
        if task.dependencies:
            output += f" | Depends on: {', '.join(task.dependencies)}"
        return output

    @staticmethod
    def parse_tags(tags_str: str) -> List[str]:
        return _parse_tags(tags_str)

    @staticmethod
    def parse_dependencies(deps_str: str) -> List[str]:
        return _parse_tags(deps_str)

    @staticmethod
    def validate_task_input(
        action: str,
        time: str,
        priority: str,
        project: str,
        status: str,
        assignee: Optional[str],
        progress: Optional[int],
    ) -> None:
        if not action or not action.strip():
            raise TodoziError.validation("Action cannot be empty")
        if len(action) < 3:
            raise TodoziError.validation("Action must be at least 3 characters")
        if len(action) > 500:
            raise TodoziError.validation("Action must be less than 500 characters")
        if not time or not time.strip():
            raise TodoziError.validation("Time cannot be empty")
        if not project or not project.strip():
            raise TodoziError.validation("Project cannot be empty")
        priority_res = Priority.from_str(priority)
        if isinstance(priority_res, Err):
            raise TodoziError.validation(f"Invalid priority: {priority}")
        status_res = Status.from_str(status)
        if isinstance(status_res, Err):
            raise TodoziError.validation(f"Invalid status: {status}")
        if assignee is not None:
            # Validate assignee using Assignee.from_str
            assignee_res = Assignee.from_str(assignee)
            if isinstance(assignee_res, Err):
                raise TodoziError.validation(f"Invalid assignee: {assignee}")
        if progress is not None:
            if not (0 <= progress <= 100):
                raise TodoziError.validation("Progress must be between 0 and 100")

    @staticmethod
    def create_task_filters(
        project: Optional[str],
        status: Optional[str],
        priority: Optional[str],
        assignee: Optional[str],
        tags: Optional[str],
        search: Optional[str],
    ) -> TaskFilters:
        f = TaskFilters()
        f.project = project
        if status:
            f.status = status
        if priority:
            f.priority = priority
        if assignee:
            f.assignee = assignee
        if tags:
            f.tags = _parse_tags(tags)
        f.search = search
        return f

    @staticmethod
    def format_task_list(tasks: List[Task]) -> str:
        if not tasks:
            return "No tasks found."
        lines: List[str] = []
        for i, t in enumerate(tasks, 1):
            lines.append(f"{i}. {TodoziHandler.format_task(t)}")
        return "\n".join(lines)

    @staticmethod
    def format_project_stats(project_name: str, task_count: int, completed_count: int) -> str:
        rate = (completed_count / task_count * 100.0) if task_count > 0 else 0.0
        return (
            f"Project: {project_name}\n"
            f"  Total tasks: {task_count}\n"
            f"  Completed: {completed_count}\n"
            f"  Completion rate: {rate:.1}%"
        )

    @staticmethod
    def format_time_estimate(time: str) -> str:
        return time

    @staticmethod
    def get_status_emoji(status) -> str:
        # Handle both enum and string
        status_val = status.value if hasattr(status, 'value') else str(status)
        mapping = {
            Status.TODO.value: "📝",
            Status.PENDING.value: "📝",
            Status.IN_PROGRESS.value: "🔄",
            Status.BLOCKED.value: "🚫",
            Status.REVIEW.value: "👀",
            Status.DONE.value: "✅",
            Status.COMPLETED.value: "✅",
            Status.CANCELLED.value: "❌",
            Status.DEFERRED.value: "⏸️",
        }
        return mapping.get(status_val, "❓")

    @staticmethod
    def get_priority_emoji(priority) -> str:
        # Handle both enum and string
        priority_val = priority.value if hasattr(priority, 'value') else str(priority)
        mapping = {
            Priority.LOW.value: "🟢",
            Priority.MEDIUM.value: "🟡",
            Priority.HIGH.value: "🟠",
            Priority.CRITICAL.value: "🔴",
            Priority.URGENT.value: "🚨",
        }
        return mapping.get(priority_val, "❓")

    @staticmethod
    def get_assignee_emoji(assignee) -> str:
        # Handle Assignee object or string
        if assignee is None:
            return "❓"
        if isinstance(assignee, Assignee):
            kind = assignee.kind
        else:
            kind = str(assignee)
        mapping = {
            "ai": "🤖",
            "human": "👤",
            "collaborative": "🤝",
        }
        return mapping.get(kind.lower(), "❓")

    @staticmethod
    def format_task_with_emojis(task: Task) -> str:
        status_emoji = TodoziHandler.get_status_emoji(task.status)
        priority_emoji = TodoziHandler.get_priority_emoji(task.priority)
        assignee_emoji = TodoziHandler.get_assignee_emoji(task.assignee or "")
        output = f"{status_emoji} {priority_emoji} {assignee_emoji} [{task.id}] {task.action}"
        if task.tags:
            output += " " + " ".join(f"#{tag}" for tag in task.tags)
        output += f"\n  📁 {task.parent_project} | ⏱️ {task.time} | 📊 {task.progress or 0}%"
        if task.dependencies:
            output += f" | 🔗 {', '.join(task.dependencies)}"
        return output

    @staticmethod
    def interactive_create_task() -> Task:
        try:
            action = input("Task action: ").strip()
            if not action:
                raise TodoziError.validation("Task action is required")
            
            time_input = input("Time estimate (default: 1 hour): ").strip() or "1 hour"
            
            priority_input = input("Priority (low/medium/high/critical, default: medium): ").strip().lower() or "medium"
            priority_result = Priority.from_str(priority_input)
            priority = priority_result.value if isinstance(priority_result, Ok) else Priority.MEDIUM
            
            project = input("Project (default: general): ").strip() or "general"
            
            tags_input = input("Tags (comma-separated, optional): ").strip()
            tags = [t.strip() for t in tags_input.split(",") if t.strip()] if tags_input else []
            
            context = input("Context notes (optional): ").strip() or None
            
            task_result = Task.new_full(
                user_id="cli_user",
                action=action,
                time=time_input,
                priority=priority,
                parent_project=project,
                status=Status.TODO,
                assignee=None,
                tags=tags,
                dependencies=[],
                context_notes=context,
                progress=None,
            )
            if isinstance(task_result, Err):
                raise task_result.error
            return task_result.value
        except (EOFError, KeyboardInterrupt):
            raise TodoziError.validation("Task creation cancelled by user")

    @staticmethod
    def show_task_detailed(task: Task) -> None:
        # ASCII box
        action_display = task.action
        if len(action_display) > 47:
            action_display = action_display[:44] + "..."
        print("┌─ Task Details ──────────────────────────────────────────────┐")
        print(f"│ ID: {task.id:<50} │")
        print(f"│ Action: {action_display:<47} │")
        print(f"│ Time: {task.time:<48} │")
        print(f"│ Priority: {task.priority:<44} │")
        print(f"│ Project: {task.parent_project:<45} │")
        print(f"│ Status: {task.status:<46} │")
        if task.assignee:
            print(f"│ Assignee: {task.assignee:<43} │")
        if task.tags:
            tags_str = ", ".join(task.tags)
            if len(tags_str) > 47:
                tags_str = tags_str[:44] + "..."
            print(f"│ Tags: {tags_str:<47} │")
        if task.dependencies:
            deps = ", ".join(task.dependencies)
            if len(deps) > 47:
                deps = deps[:44] + "..."
            print(f"│ Dependencies: {deps:<40} │")
        if task.context_notes:
            ctx_lines = task.context_notes.split("\n")
            for i, line in enumerate(ctx_lines):
                prefix = "│ Context: " if i == 0 else "│          "
                line_disp = line if len(line) <= 47 else line[:44] + "..."
                print(f"│{prefix:<47} │")
        if task.progress is not None:
            print(f"│ Progress: {task.progress:<43}% │")
        print(f"│ Created: {task.created_at:<45} │")
        print(f"│ Updated: {task.updated_at:<45} │")
        print("└─────────────────────────────────────────────────────────────┘")

    async def launch_gui(self) -> None:
        print("GUI not available - TUI feature not enabled in this translation")
        # In a real implementation, launch a TUI/GUI here.

    async def handle_ai_commands(self, command: str, args: List[str]) -> None:
        if command == "similar":
            if not args:
                raise TodoziError.validation("Usage: todozi similar <query>")
            query = " ".join(args)
            config = TodoziEmbeddingConfig()
            svc = TodoziEmbeddingService(config)
            await svc.initialize()
            similar = await svc.find_similar_tasks(query, 10)
            if not similar:
                print(f"No similar tasks found for: {query}")
            else:
                print(f"Similar tasks for '{query}':")
                print("══════════════════════════════════════")
                for i, s in enumerate(similar, 1):
                    print(f"{i}. {s.text_content[:80]}... (similarity: {s.similarity_score:.3f})")
        elif command == "suggest":
            config = TodoziEmbeddingConfig()
            svc = TodoziEmbeddingService(config)
            await svc.initialize()
            tasks = self.storage.list_tasks_across_projects(TaskFilters(status=Status.TODO))
            if not tasks:
                print("No active tasks to suggest from")
                return
            print("🤖 AI Task Suggestions:")
            print("═══════════════════════")
            for t in tasks:
                if t.embedding_vector:
                    similar = await svc.find_similar_tasks(t.action, limit=5)
                    print(f"\n📋 Task: {t.action}")
                    print(f"   Similar tasks found: {len(similar)}")
                    for sim in similar[:3]:
                        print(f"   - {sim.text_content[:60]}... (similarity: {sim.similarity_score:.2f})")
        elif command == "insights":
            config = TodoziEmbeddingConfig()
            svc = TodoziEmbeddingService(config)
            await svc.initialize()
            diag = await svc.export_diagnostics()
            print("🧠 AI Insights & Statistics:")
            print("═══════════════════════════")
            print(f"Total embeddings: {diag.content_type_breakdown}")
            print(f"Average similarity: {diag.avg_similarity_score:.3f}")
            clusters = await svc.cluster_content()
            print(f"\n🔗 Semantic Clusters: {len(clusters)}")
            for i, cluster in enumerate(clusters[:5], 1):
                print(f"   Cluster {i}: {cluster.cluster_size} items (avg similarity: {cluster.average_similarity:.2f})")
        else:
            raise TodoziError.validation(f"Unknown AI command: {command}")

    async def handle_extract_command(
        self,
        content: Optional[str],
        file: Optional[str],
        output_format: str,
        human: bool,
    ) -> None:
        out = await extract_content(content, file, output_format, human)
        print(out)

    async def handle_strategy_command(
        self,
        content: Optional[str],
        file: Optional[str],
        output_format: str,
        human: bool,
    ) -> None:
        out = await strategy_content(content, file, output_format, human)
        print(out)

    async def handle_steps_command(self, command: StepsCommands) -> None:
        steps_dir = _storage_dir() / "steps"
        steps_dir.mkdir(parents=True, exist_ok=True)
        if isinstance(command, StepsShow):
            fp = steps_dir / f"{command.task_id}.json"
            if not fp.exists():
                print(f"❌ No steps found for task: {command.task_id}")
                return
            data = json.loads(fp.read_text(encoding="utf-8"))
            print(f"📋 Steps for Task: {command.task_id}")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("\n📝 Summary:")
            print(data.get("summary", ""))
            print("\n📌 Steps:")
            for i, s in enumerate(data.get("steps", []), 1):
                print(f"  {i}. {s}")
            print(f"\n📊 Status: {data.get('status','active')}")
            print(f"📅 Created: {data.get('created_at','')}")
            print(f"🔄 Updated: {data.get('updated_at','')}")
        elif isinstance(command, StepsAdd):
            fp = steps_dir / f"{command.task_id}.json"
            if fp.exists():
                data = json.loads(fp.read_text(encoding="utf-8"))
            else:
                data = {
                    "task_id": command.task_id,
                    "project_id": "general",
                    "summary": "",
                    "steps": [],
                    "status": "active",
                    "created_at": _now_str(),
                    "updated_at": _now_str(),
                }
            data["steps"].append(command.step)
            data["updated_at"] = _now_str()
            fp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"✅ Added step to task: {command.task_id}")
        elif isinstance(command, StepsUpdate):
            fp = steps_dir / f"{command.task_id}.json"
            if not fp.exists():
                print(f"❌ No steps found for task: {command.task_id}")
                return
            data = json.loads(fp.read_text(encoding="utf-8"))
            steps = data.get("steps", [])
            if command.step_index <= 0 or command.step_index > len(steps):
                print(f"❌ Invalid step index: {command.step_index}. Task has {len(steps)} steps.")
                return
            steps[command.step_index - 1] = command.new_step
            data["steps"] = steps
            data["updated_at"] = _now_str()
            fp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"✅ Updated step {command.step_index} for task: {command.task_id}")
        elif isinstance(command, StepsDone):
            fp = steps_dir / f"{command.task_id}.json"
            if not fp.exists():
                print(f"❌ No steps found for task: {command.task_id}")
                return
            data = json.loads(fp.read_text(encoding="utf-8"))
            data["status"] = "done"
            data["updated_at"] = _now_str()
            fp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"✅ Marked steps as done for task: {command.task_id}")
        elif isinstance(command, StepsArchive):
            fp = steps_dir / f"{command.task_id}.json"
            if not fp.exists():
                print(f"❌ No steps found for task: {command.task_id}")
                return
            data = json.loads(fp.read_text(encoding="utf-8"))
            data["status"] = "archived"
            data["updated_at"] = _now_str()
            fp.write_text(json.dumps(data, indent=2), encoding="utf-8")
            print(f"✅ Archived steps for task: {command.task_id}")
        else:
            raise TodoziError.validation("Unknown steps command")

    # ---- Helpers ----
    def _print_list_header(self, title: str, items: List[Any], summary_fn):
        if not items:
            print(f"📭 No {title.lower()} found")
            return
        print(f"📋 {title}:")
        print()
        for item in items:
            print(summary_fn(item))
            print("---")


# -----------------------------
# Utility functions
# -----------------------------
def _now_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _parse_dt(s: str) -> datetime:
    return datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def _id(prefix: str) -> str:
    import uuid

    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def _storage_dir() -> Path:
    from todozi.storage import get_storage_dir as get_storage
    return get_storage()


def _dict_to_task(data: Dict[str, Any]) -> Task:
    return Task(**data)


def _dict_to_queue_item(data: Dict[str, Any]) -> QueueItem:
    return QueueItem(**data)


def _dict_to_session(data: Dict[str, Any]) -> QueueSession:
    return QueueSession(**data)


def _parse_tags(s: str) -> List[str]:
    return [t.strip() for t in s.split(",") if t.strip()]


def _is_port_open(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except Exception:
        return False


def _task_matches_filters(task: Task, filters: TaskFilters) -> bool:
    if filters.project and task.parent_project != filters.project:
        return False
    if filters.status:
        task_status = task.status.value if hasattr(task.status, 'value') else task.status
        filter_status = filters.status.value if hasattr(filters.status, 'value') else filters.status
        if task_status != filter_status:
            return False
    if filters.priority:
        task_priority = task.priority.value if hasattr(task.priority, 'value') else task.priority
        filter_priority = filters.priority.value if hasattr(filters.priority, 'value') else filters.priority
        if task_priority != filter_priority:
            return False
    if filters.assignee:
        task_assignee = str(task.assignee) if task.assignee else ""
        filter_assignee = str(filters.assignee) if filters.assignee else ""
        if task_assignee != filter_assignee:
            return False
    if filters.tags:
        task_tags = set(tag.lower() for tag in task.tags)
        for t in filters.tags:
            if t.lower() not in task_tags:
                return False
    if filters.search:
        q = filters.search.lower()
        if not (q in task.action.lower() or q in task.parent_project.lower()):
            return False
    return True


def _queue_item_summary(item: QueueItem) -> str:
    priority_str = item.priority.value if hasattr(item.priority, 'value') else str(item.priority)
    status_str = item.status.value if hasattr(item.status, 'value') else str(item.status)
    lines = [
        f"🆔 ID: {item.id}",
        f"📝 Task: {item.task_name}",
        f"📄 Description: {item.task_description}",
        f"⚡ Priority: {priority_str}",
    ]
    if item.project_id:
        lines.append(f"📁 Project: {item.project_id}")
    lines.append(f"📊 Status: {status_str}")
    lines.append(f"🕒 Created: {item.created_at}")
    return "\n".join(lines)


def _to_table(headers: List[str], rows: List[List[str]]) -> str:
    # Simple table renderer without external deps
    if not rows:
        return "\n".join(headers)
    col_widths = [len(h) for h in headers]
    for r in rows:
        for i, cell in enumerate(r):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    # Build separator
    sep = "+".join("-" * (w + 2) for w in col_widths)
    sep = f"+{sep}+"
    out = [sep]
    out.append("|" + "|".join(" " + h.ljust(col_widths[i]) + " " for i, h in enumerate(headers)) + "|")
    out.append(sep)
    for r in rows:
        out.append("|" + "|".join(" " + str(r[i]).ljust(col_widths[i]) + " " for i in range(len(r))) + "|")
    out.append(sep)
    return "\n".join(out)


# -----------------------------
# Argparse CLI Infrastructure (merged from tdz.py)
# -----------------------------


class CommandContext:
    def __init__(self, storage: Storage, handler: TodoziHandler, base_path: Path):
        self.storage = storage
        self.handler = handler
        self.base_path = base_path


HandlerFunc = Callable[[argparse.Namespace, CommandContext], Awaitable[Optional[int]]]


class CommandRegistry:
    def __init__(self):
        self._commands: Dict[str, Tuple[argparse.ArgumentParser, HandlerFunc]] = {}

    def register(self, name: str, parser: argparse.ArgumentParser, handler: HandlerFunc) -> None:
        self._commands[name] = (parser, handler)

    async def dispatch(self, args: argparse.Namespace, ctx: CommandContext) -> int:
        cmd = getattr(args, "command", None)
        if cmd is None or cmd not in self._commands:
            print(f"Unknown command: {cmd}")
            return 1
        parser, handler = self._commands[cmd]
        parsed = parser.parse_args(sys.argv[2:] if sys.argv and len(sys.argv) > 2 else [])
        ret = await handler(parsed, ctx)
        return 0 if ret is None else ret


def find_todozi_dir(start: Optional[Path] = None) -> Optional[Path]:
    """Search upward for tdz.hlx file or tdz directory. Returns the parent dir containing tdz."""
    if start is None:
        p = Path.cwd()
    else:
        p = start.resolve()
    while True:
        if p == p.parent:
            break
        p = p.parent
        hlx = p / "tdz.hlx"
        tdz = p / "tdz"
        if hlx.exists() or tdz.is_dir():
            return p
    return None


def ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


# Parser builders
def build_init_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser("init")


def build_add_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("add")
    p.add_argument("action", help="Task action/description")
    p.add_argument("time", help="Time estimate")
    p.add_argument("priority", choices=[p.value for p in Priority], help="Task priority")
    p.add_argument("project", help="Project name")
    p.add_argument("--status", choices=[s.value for s in Status], default=Status.TODO.value, help="Task status")
    p.add_argument("--assignee", help="Assignee")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--dependencies", help="Comma-separated task IDs")
    p.add_argument("--context", help="Context notes")
    p.add_argument("--progress", type=int, help="Progress 0-100")
    return p


def build_list_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("list")
    p.add_argument("--project", help="Filter by project")
    p.add_argument("--status", choices=[s.value for s in Status], help="Filter by status")
    p.add_argument("--priority", choices=[p.value for p in Priority], help="Filter by priority")
    p.add_argument("--assignee", help="Filter by assignee")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--search", help="Search query")
    return p


def build_show_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("show")
    p.add_argument("id", help="Task id")
    return p


def build_update_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("update")
    p.add_argument("id", help="Task id")
    p.add_argument("--action", help="Task action")
    p.add_argument("--time", help="Time estimate")
    p.add_argument("--priority", choices=[p.value for p in Priority])
    p.add_argument("--project", help="Project name")
    p.add_argument("--status", choices=[s.value for s in Status])
    p.add_argument("--assignee", help="Assignee")
    p.add_argument("--tags", help="Comma-separated tags")
    p.add_argument("--dependencies", help="Comma-separated task IDs")
    p.add_argument("--context", help="Context notes")
    p.add_argument("--progress", type=int, help="Progress 0-100")
    return p


def build_complete_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("complete")
    p.add_argument("id", help="Task id")
    return p


def build_delete_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("delete")
    p.add_argument("id", help="Task id")
    return p


def build_search_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("search")
    p.add_argument("query", help="Search query")
    return p


def build_stats_parser() -> argparse.ArgumentParser:
    return argparse.ArgumentParser("stats")


def build_project_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser("project")
    sub = p.add_subparsers(dest="project_action")
    sub.add_parser("list", help="List projects")
    create_parser = sub.add_parser("create", help="Create project")
    create_parser.add_argument("name", help="Project name")
    create_parser.add_argument("--description", help="Description")
    show_parser = sub.add_parser("show", help="Show project")
    show_parser.add_argument("name", help="Project name")
    return p


# Command wrappers
async def wrap_add(args: argparse.Namespace, ctx: CommandContext) -> Optional[int]:
    await ctx.handler.handle_add_command(AddTask(
        action=args.action,
        time=args.time,
        priority=args.priority,
        project=args.project,
        status=args.status,
        assignee=args.assignee,
        tags=args.tags,
        dependencies=args.dependencies,
        context=args.context,
        progress=args.progress,
    ))
    return None


async def wrap_list(args: argparse.Namespace, ctx: CommandContext) -> Optional[int]:
    await ctx.handler.handle_list_command(ListTasks(
        project=args.project,
        status=args.status,
        priority=args.priority,
        assignee=args.assignee,
        tags=args.tags,
        search=args.search,
    ))
    return None


async def wrap_show(args: argparse.Namespace, ctx: CommandContext) -> Optional[int]:
    await ctx.handler.handle_show_command(ShowTask(id=args.id))
    return None


async def wrap_update(args: argparse.Namespace, ctx: CommandContext) -> Optional[int]:
    await ctx.handler.handle_update_command(
        id=args.id,
        action=args.action,
        time=args.time,
        priority=args.priority,
        project=args.project,
        status=args.status,
        assignee=args.assignee,
        tags=args.tags,
        dependencies=args.dependencies,
        context=args.context,
        progress=args.progress,
    )
    return None


async def wrap_complete(args: argparse.Namespace, ctx: CommandContext) -> Optional[int]:
    ctx.handler.complete_task(args.id)
    return None


async def wrap_delete(args: argparse.Namespace, ctx: CommandContext) -> Optional[int]:
    ctx.handler.delete_task(args.id)
    return None


async def wrap_search(args: argparse.Namespace, ctx: CommandContext) -> Optional[int]:
    await ctx.handler.handle_search_command(SearchTasks(query=args.query))
    return None


async def wrap_stats(args: argparse.Namespace, ctx: CommandContext) -> Optional[int]:
    await ctx.handler.handle_stats_command(Stats())
    return None


async def wrap_project(args: argparse.Namespace, ctx: CommandContext) -> Optional[int]:
    if args.project_action == "list":
        await ctx.handler.handle_project_command(ListProjects())
    elif args.project_action == "create":
        await ctx.handler.handle_project_command(CreateProject(name=args.name, description=getattr(args, "description", None)))
    elif args.project_action == "show":
        await ctx.handler.handle_project_command(ShowProject(name=args.name))
    return None


def build_registry(handler: TodoziHandler, storage: Storage, base_path: Path) -> CommandRegistry:
    reg = CommandRegistry()
    reg.register("init", build_init_parser(), lambda args, ctx: asyncio.create_task(asyncio.sleep(0)) or None)
    reg.register("add", build_add_parser(), wrap_add)
    reg.register("list", build_list_parser(), wrap_list)
    reg.register("show", build_show_parser(), wrap_show)
    reg.register("update", build_update_parser(), wrap_update)
    reg.register("complete", build_complete_parser(), wrap_complete)
    reg.register("delete", build_delete_parser(), wrap_delete)
    reg.register("search", build_search_parser(), wrap_search)
    reg.register("stats", build_stats_parser(), wrap_stats)
    reg.register("project", build_project_parser(), wrap_project)
    return reg


async def run_cli() -> int:
    """Main CLI entry point for argparse-based command dispatch."""
    parser = argparse.ArgumentParser(prog="todozi", description="AI/Human task management system")
    sub = parser.add_subparsers(dest="command", required=False)

    parsers = {
        "init": build_init_parser(),
        "add": build_add_parser(),
        "list": build_list_parser(),
        "show": build_show_parser(),
        "update": build_update_parser(),
        "complete": build_complete_parser(),
        "delete": build_delete_parser(),
        "search": build_search_parser(),
        "stats": build_stats_parser(),
        "project": build_project_parser(),
    }

    for name, p in parsers.items():
        sub.add_parser(name, parents=[p], add_help=False)

    args = parser.parse_args()

    if not hasattr(args, "command") or args.command is None:
        # This shouldn't happen since we check in __main__, but handle it gracefully
        parser.print_help()
        return 0

    base_path = find_todozi_dir()
    if base_path is None:
        base_path = Path.cwd()

    if args.command == "init":
        ensure_dir(base_path)
        ensure_dir(base_path / "backups")
        print("✅ Todozi initialized at", base_path)
        return 0

    storage = await Storage.new()
    handler = TodoziHandler(storage)
    reg = build_registry(handler, storage, base_path)

    if args.command in parsers:
        args = parsers[args.command].parse_args(sys.argv[2:] if len(sys.argv) > 2 else [])

    ctx = CommandContext(storage, handler, base_path)
    try:
        return await reg.dispatch(args, ctx)
    except TodoziError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nInterrupted.")
        return 130
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


# -----------------------------
# Convenience "executor" to demo
# -----------------------------
async def main():
    storage = await Storage.new()
    handler = TodoziHandler(storage)

    # Example: create a task
    await handler.handle_add_command(AddTask(
        action="Write documentation",
        time="1 hour",
        priority=Priority.Medium,
        project="general",
        status=Status.Todo,
    ))

    # Example: list tasks
    await handler.handle_list_command(ListTasks())

    # Example: complete the task
    # (You may first list tasks to get the ID, then complete it)
    tasks = storage.list_tasks_across_projects(TaskFilters())
    if tasks:
        handler.complete_task(tasks[0].id)

    # Example: show stats
    await handler.handle_stats_command(Stats())

    # Example: backup listing
    await handler.handle_list_backups_command()

    # Example: API key creation
    await handler.handle_api_command(Register())

    # Example: queue plan
    await handler.handle_queue_command(PlanQueue(
        task_name="Prepare release notes",
        task_description="Draft release notes for v1.0",
        priority=Priority.High,
        project_id="release",
    ))

    # Example: server status check
    await handler.handle_server_command(ServerStatus())


if __name__ == "__main__":
    import asyncio

    # Launch TUI when no args provided (argparse will handle --help automatically)
    if len(sys.argv) == 1:
        from todozi.tui import main as tui_main
        tui_main()
        sys.exit(0)
    
    exit_code = asyncio.run(run_cli())
    sys.exit(exit_code)
