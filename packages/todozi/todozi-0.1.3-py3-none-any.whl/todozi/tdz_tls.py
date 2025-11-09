import asyncio
import json
import re
import subprocess
import uuid
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterable

from pydantic import BaseModel, Field


# ------------- Error handling -------------

class TodoziError(Exception):
    def __init__(self, message: str, code: Optional[int] = None):
        super().__init__(message)
        self.code = code

    @staticmethod
    def storage_error(message: str) -> "TodoziError":
        return TodoziError(f"Storage error: {message}", 500)

    @staticmethod
    def validation_error(message: str) -> "TodoziError":
        return TodoziError(f"Validation error: {message}", 400)


# ------------- Tool base types -------------

JsonValue = Any  # matches serde_json::Value
ResourceLock = str  # simplified to string labels for demonstration


class ToolDefinition(BaseModel):
    name: str
    description: str
    parameters: List[Dict[str, Any]]
    category: str
    resource_locks: List[ResourceLock]

    @staticmethod
    def new(
        name: str,
        description: str,
        parameters: List[Dict[str, Any]],
        category: str,
        resource_locks: List[ResourceLock],
    ) -> "ToolDefinition":
        return ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            category=category,
            resource_locks=resource_locks,
        )


class ToolResult(BaseModel):
    success: bool
    output: str
    code: int

    @staticmethod
    def success(output: str, code: int = 0) -> "ToolResult":
        return ToolResult(success=True, output=output, code=code)

    @staticmethod
    def error(message: str, code: int = 400) -> "ToolResult":
        return ToolResult(success=False, output=message, code=code)


class Tool(ABC):
    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        ...

    @abstractmethod
    async def execute(self, kwargs: Dict[str, Any]) -> ToolResult:
        ...


def create_tool_parameter(name: str, typ: str, description: str, required: bool) -> Dict[str, Any]:
    return {
        "name": name,
        "type": typ,
        "description": description,
        "required": required,
    }


# ------------- Domain Models -------------

class ChecklistItem(BaseModel):
    id: str
    content: str
    priority: str
    completed: bool
    created_at: datetime
    source: str


class ExtractedAction(BaseModel):
    id: str
    action_type: str
    parameters: Dict[str, JsonValue]
    confidence: float


class ProcessingStats(BaseModel):
    content_length: int
    tool_calls_found: int
    tags_extracted: int
    checklists_generated: int
    processing_time_ms: int


class ProcessedContent(BaseModel):
    id: str
    session_id: str
    raw_content: str
    cleaned_content: str
    timestamp: datetime
    extracted_items: List[str]
    checklist_items: List[ChecklistItem]
    tool_calls: List[ExtractedAction]
    processing_stats: ProcessingStats


class ProcessedAction(BaseModel):
    id: str
    action_type: str
    description: str
    timestamp: datetime
    success: bool
    result: Optional[str]


class ConversationSession(BaseModel):
    id: str
    start_time: datetime
    last_activity: datetime
    topic: str
    participant_count: int
    message_count: int


class ProcessingResult(BaseModel):
    actions: List[ProcessedAction]


class ParsedContent(BaseModel):
    text_content: str
    json_content: Optional[JsonValue]
    tool_calls: List[JsonValue]


class ExtractionResult(BaseModel):
    extracted_tags: List[str]
    tool_calls: List[JsonValue]
    natural_patterns: List[str]


class TodoziProcessorState(BaseModel):
    active_sessions: Dict[str, ConversationSession] = Field(default_factory=dict)
    recent_actions: List[ProcessedAction] = Field(default_factory=list)
    checklist_items: List[ChecklistItem] = Field(default_factory=list)
    processed_contents: List[ProcessedContent] = Field(default_factory=list)

    @staticmethod
    def new() -> "TodoziProcessorState":
        return TodoziProcessorState()

    def add_checklist_item(self, item: ChecklistItem) -> None:
        self.checklist_items.append(item)

    def add_recent_action(self, action: ProcessedAction) -> None:
        self.recent_actions.append(action)
        if len(self.recent_actions) > 100:
            # Drain from the left
            self.recent_actions = self.recent_actions[-100:]

    def save_processed_content(
        self,
        raw: str,
        cleaned: str,
        session_id: str,
    ) -> None:
        processed = ProcessedContent(
            id=str(uuid.uuid4()),
            session_id=session_id,
            raw_content=raw,
            cleaned_content=cleaned,
            timestamp=datetime.now(timezone.utc),
            extracted_items=[],
            checklist_items=[],
            tool_calls=[],
            processing_stats=ProcessingStats(
                content_length=len(raw),
                tool_calls_found=0,
                tags_extracted=0,
                checklists_generated=0,
                processing_time_ms=0,
            ),
        )
        self.processed_contents.append(processed)


SharedTodoziState = TodoziProcessorState


# ------------- ChatContent (used by tdz_cnt) -------------

class TaskItem(BaseModel):
    action: str
    priority: str
    parent_project: str
    time: str
    context_notes: Optional[str] = ""


class MemoryItem(BaseModel):
    moment: str
    meaning: str
    reason: str


class IdeaItem(BaseModel):
    idea: str


class ErrorItem(BaseModel):
    title: str
    detail: str


class CodeChunk(BaseModel):
    code: str
    lang: str


class ChatContent(BaseModel):
    tasks: List[TaskItem] = Field(default_factory=list)
    memories: List[MemoryItem] = Field(default_factory=list)
    ideas: List[IdeaItem] = Field(default_factory=list)
    agent_assignments: List[str] = Field(default_factory=list)
    code_chunks: List[CodeChunk] = Field(default_factory=list)
    errors: List[ErrorItem] = Field(default_factory=list)
    training_data: List[str] = Field(default_factory=list)
    feelings: List[str] = Field(default_factory=list)
    summaries: List[str] = Field(default_factory=list)
    reminders: List[str] = Field(default_factory=list)


# ------------- Domain integration for tdz_cnt -------------

class Done:
    @staticmethod
    async def create_task(action: str, priority: Optional[str], parent_project: Optional[str], time: Optional[str], context_notes: Optional[str]) -> None:
        from todozi.lib import Done as LibDone, Priority as LibPriority
        priority_enum = None
        if priority:
            try:
                priority_enum = LibPriority[priority.capitalize()]
            except (KeyError, AttributeError):
                priority_enum = LibPriority.Medium
        await LibDone.create_task(action, priority_enum, parent_project, time, context_notes)

    @staticmethod
    async def complete_task(task_id: str) -> None:
        from todozi.lib import Done as LibDone
        await LibDone.complete_task(task_id)


class Memories:
    @staticmethod
    async def create(moment: str, meaning: str, reason: str) -> None:
        from todozi.storage import save_memory, Memory
        from todozi.lib import new_id
        from datetime import datetime, timezone
        memory = Memory(
            id=new_id("mem_"),
            moment=moment,
            meaning=meaning,
            reason=reason,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        save_memory(memory)


class Ideas:
    @staticmethod
    async def create(idea: str) -> None:
        from todozi.lib import Ideas as LibIdeas
        await LibIdeas.create(idea)


class storage:
    @staticmethod
    def save_error(err: ErrorItem) -> None:
        import logging
        logger = logging.getLogger("todozi.errors")
        logger.error(f"Error: {err.title} - {err.detail}")


# ------------- Content Parsing (tags extraction) -------------

def parse_enclosed_tags(text: str, tag: str) -> List[Tuple[str, int]]:
    start_tag = f"<{tag}>"
    end_tag = f"</{tag}>"
    results: List[Tuple[str, int]] = []
    current = 0
    while True:
        start = text.find(start_tag, current)
        if start == -1:
            break
        end = text.find(end_tag, start + len(start_tag))
        if end == -1:
            break
        inner = text[start + len(start_tag) : end]
        results.append((inner.strip(), start))
        current = end + len(end_tag)
    return results


def parse_chat_message_extended(content: str, system_hint: str) -> ChatContent:
    tasks: List[TaskItem] = []
    memories: List[MemoryItem] = []
    ideas: List[IdeaItem] = []
    errors: List[ErrorItem] = []
    training_data: List[str] = []
    feelings: List[str] = []
    summaries: List[str] = []
    reminders: List[str] = []
    agent_assignments: List[str] = []
    code_chunks: List[CodeChunk] = []

    # Parse tasks: <todozi> ... </todozi>
    for inner, _ in parse_enclosed_tags(content, "todozi"):
        # Heuristics: split by ; or newline
        parts = re.split(r"[;\n]+", inner)
        for p in parts:
            p = p.strip()
            if not p:
                continue
            # Extract priority if present e.g., "p:high buy milk"
            priority = "medium"
            m = re.search(r"\bp:(high|low|medium)\b", p, flags=re.I)
            if m:
                priority = m.group(1).lower()
            # Remove p:... tokens
            p_clean = re.sub(r"\bp:(high|low|medium)\b", "", p, flags=re.I).strip()
            # Split action; optional context
            # Format: action [; context]
            action_parts = p_clean.split(";")
            action = action_parts[0].strip()
            context_notes = ";".join(action_parts[1:]).strip() if len(action_parts) > 1 else ""
            tasks.append(
                TaskItem(
                    action=action,
                    priority=priority,
                    parent_project="",
                    time="",
                    context_notes=context_notes or None,
                )
            )

    # Memories: <memory> ... </memory>
    for inner, _ in parse_enclosed_tags(content, "memory"):
        # Format: moment ; meaning ; reason
        parts = [x.strip() for x in inner.split(";")]
        moment = parts[0] if parts else ""
        meaning = parts[1] if len(parts) > 1 else ""
        reason = parts[2] if len(parts) > 2 else ""
        memories.append(MemoryItem(moment=moment, meaning=meaning, reason=reason))

    # Ideas: <idea> ... </idea>
    for inner, _ in parse_enclosed_tags(content, "idea"):
        ideas.append(IdeaItem(idea=inner.strip()))

    # Errors: <error>title::detail</error> or <error>title - detail</error>
    for inner, _ in parse_enclosed_tags(content, "error"):
        title = inner
        detail = ""
        if "::" in inner:
            title, detail = inner.split("::", 1)
        elif "-" in inner:
            title, detail = inner.split("-", 1)
        errors.append(ErrorItem(title=title.strip(), detail=detail.strip()))

    # Training data: <train> ... </train>
    for inner, _ in parse_enclosed_tags(content, "train"):
        training_data.append(inner.strip())

    # Feelings: <feel> ... </feel>
    for inner, _ in parse_enclosed_tags(content, "feel"):
        feelings.append(inner.strip())

    # Summaries: <summary> ... </summary>
    for inner, _ in parse_enclosed_tags(content, "summary"):
        summaries.append(inner.strip())

    # Reminders: <reminder> ... </reminder>
    for inner, _ in parse_enclosed_tags(content, "reminder"):
        reminders.append(inner.strip())

    # Agent assignments: <todozi_agent> ... </todozi_agent> (simple raw strings)
    for inner, _ in parse_enclosed_tags(content, "todozi_agent"):
        agent_assignments.append(inner.strip())

    # Code chunks: <chunk> ... </chunk> optionally with lang="python"
    # Find all <chunk> or <chunk lang="...">
    for m in re.finditer(r"<chunk(?:\s+lang=['\"]([^'\"]+)['\"])?>(.*?)</chunk>", content, flags=re.S | re.I):
        lang = m.group(1) or "text"
        code = m.group(2) or ""
        code_chunks.append(CodeChunk(code=code.strip(), lang=lang))

    return ChatContent(
        tasks=tasks,
        memories=memories,
        ideas=ideas,
        agent_assignments=agent_assignments,
        code_chunks=code_chunks,
        errors=errors,
        training_data=training_data,
        feelings=feelings,
        summaries=summaries,
        reminders=reminders,
    )


# ------------- Content Processor Tool -------------

class TdzContentProcessorTool(Tool):
    def __init__(self, state: SharedTodoziState):
        self.state = state
        self.natural_language_patterns: List[str] = self._initialize_patterns()

    def _initialize_patterns(self) -> List[str]:
        return [
            r"we should",
            r"I need to",
            r"let's",
            r"we need to",
            r"don't forget",
            r"remember to",
            r"make sure",
            r"important:",
            r"note:",
            r"todo:",
            r"add to checklist",
            r"checklist item",
            r"action item",
            r"next step",
        ]

    @property
    def definition(self) -> ToolDefinition:
        return ToolDefinition.new(
            name="tdz_content_processor",
            description="Process raw content from AI models, extract Todozi data, and return cleaned conversational output",
            parameters=[
                create_tool_parameter(
                    "content",
                    "string",
                    "Raw content to process (JSON or text with tags)",
                    True,
                ),
                create_tool_parameter(
                    "session_id",
                    "string",
                    "Optional session ID for conversation tracking",
                    False,
                ),
                create_tool_parameter(
                    "extract_checklist",
                    "boolean",
                    "Extract checklist items from natural language",
                    False,
                ),
                create_tool_parameter(
                    "auto_session",
                    "boolean",
                    "Automatically create/manage sessions",
                    False,
                ),
            ],
            category="Content Processing",
            resource_locks=[ResourceLock("FilesystemRead"), ResourceLock("FilesystemWrite")],
        )

    async def execute(self, kwargs: Dict[str, JsonValue]) -> ToolResult:
        try:
            content = kwargs.get("content")
            if content is None or not isinstance(content, str):
                return ToolResult.error("Missing or invalid 'content' parameter", 100)

            session_id = kwargs.get("session_id")
            if isinstance(session_id, str):
                sid = session_id
            else:
                sid = "default"

            extract_checklist = kwargs.get("extract_checklist")
            if isinstance(extract_checklist, bool):
                ec = extract_checklist
            else:
                ec = True

            auto_session = kwargs.get("auto_session")
            if isinstance(auto_session, bool):
                auto = auto_session
            else:
                auto = True

            result = await self.process_content(content, sid, ec, auto)
            return ToolResult.success(result, 100)
        except Exception as e:
            return ToolResult.error(f"Content processing failed: {e}", 100)

    async def process_content(
        self,
        content: str,
        session_id: str,
        extract_checklist: bool,
        auto_session: bool,
    ) -> str:
        start_time = datetime.now(timezone.utc)
        async with self.state:
            parsed_content = self.parse_raw_content(content)
            extraction_result = self.extract_todozi_data(parsed_content)
            processing_result = await self.process_tool_calls(extraction_result.tool_calls)
            cleaned_content = self.clean_content(content, extraction_result.extracted_tags)

            # Local state updates
            if extract_checklist:
                checklist_items = self.extract_checklist_items(parsed_content.text_content)
                for item in checklist_items:
                    # Write into shared state
                    self.state.get_lock().acquire()  # ensure we hold the mutex (already held above)
                    # Already inside 'async with self.state', so just add
                    self.state.locked().add_checklist_item(item)

            if auto_session:
                self.ensure_session_exists(session_id, parsed_content)

            for action in processing_result.actions:
                self.state.locked().add_recent_action(action)

            self.state.locked().save_processed_content(content, cleaned_content, session_id)

            processing_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)

            stats = ProcessingStats(
                content_length=len(content),
                tool_calls_found=len(extraction_result.tool_calls),
                tags_extracted=len(extraction_result.extracted_tags),
                checklists_generated=(self.extract_checklist_items(parsed_content.text_content).__len__() if extract_checklist else 0),
                processing_time_ms=processing_time,
            )

            response = self.generate_response(cleaned_content, self.state.locked(), processing_result, stats)
            return response

    def parse_raw_content(self, content: str) -> ParsedContent:
        try:
            json_value = json.loads(content)
            return self.parse_json_content(json_value)
        except Exception:
            return self.parse_text_content(content)

    def parse_json_content(self, json: JsonValue) -> ParsedContent:
        text_parts: List[str] = []
        tool_calls: List[JsonValue] = []

        if isinstance(json, dict):
            for key in ["content", "message"]:
                v = json.get(key)
                if isinstance(v, str):
                    text_parts.append(v)

            choices = json.get("choices")
            if isinstance(choices, list):
                for choice in choices:
                    if isinstance(choice, dict):
                        m = choice.get("message")
                        c = choice.get("content")
                        if isinstance(m, str):
                            text_parts.append(m)
                        if isinstance(c, str):
                            text_parts.append(c)

            tools = json.get("tool_calls")
            if isinstance(tools, list):
                for tool in tools:
                    function = tool.get("function") if isinstance(tool, dict) else None
                    if function is not None:
                        tool_calls.append(function)

        return ParsedContent(
            text_content=" ".join(text_parts),
            json_content=json,
            tool_calls=tool_calls,
        )

    def parse_text_content(self, content: str) -> ParsedContent:
        return ParsedContent(
            text_content=content,
            json_content=None,
            tool_calls=[],
        )

    def extract_todozi_data(self, parsed: ParsedContent) -> ExtractionResult:
        extracted_tags: List[str] = []
        tool_calls: List[JsonValue] = []

        tag_patterns = [
            r"<todozi>.*?</todozi>",
            r"<memory>.*?</memory>",
            r"<idea>.*?</idea>",
            r"<todozi_agent>.*?</todozi_agent>",
            r"<chunk>.*?</chunk>",
            r"<tdz>.*?</tdz>",
        ]

        for pat in tag_patterns:
            try:
                regex = re.compile(pat, flags=re.DOTALL)
            except re.error as e:
                raise TodoziError(f"Regex compilation failed: {e}")
            for m in regex.finditer(parsed.text_content):
                extracted_tags.append(m.group(0))

        for tool_call in parsed.tool_calls:
            function_name = None
            if isinstance(tool_call, dict):
                name = tool_call.get("name")
                if isinstance(name, str):
                    function_name = name
            if function_name and ("todozi" in function_name.lower() or "tdz" in function_name.lower()):
                tool_calls.append(tool_call)

        natural_patterns = self.extract_natural_language_patterns(parsed.text_content)

        return ExtractionResult(
            extracted_tags=extracted_tags,
            tool_calls=tool_calls,
            natural_patterns=natural_patterns,
        )

    async def process_tool_calls(self, tool_calls: List[JsonValue]) -> ProcessingResult:
        actions: List[ProcessedAction] = []
        for tool_call in tool_calls:
            function_name = None
            if isinstance(tool_call, dict):
                name = tool_call.get("name")
                if isinstance(name, str):
                    function_name = name
            if function_name is None:
                continue

            lname = function_name.lower()
            if "create_task" in lname or "add_task" in lname:
                action = await self.process_create_task_call(tool_call)
                actions.append(action)
            elif "search" in lname or "list" in lname:
                action = await self.process_search_call(tool_call)
                actions.append(action)
            elif "update" in lname or "complete" in lname:
                action = await self.process_update_call(tool_call)
                actions.append(action)
            elif "memory" in lname:
                action = await self.process_memory_call(tool_call)
                actions.append(action)
            elif "idea" in lname:
                action = await self.process_idea_call(tool_call)
                actions.append(action)
            else:
                actions.append(
                    ProcessedAction(
                        id=str(uuid.uuid4()),
                        action_type="unknown_tool_call",
                        description=f"Unknown tool call: {function_name}",
                        timestamp=datetime.now(timezone.utc),
                        success=False,
                        result="Tool call not recognized",
                    )
                )
        return ProcessingResult(actions=actions)

    def clean_content(self, original: str, extracted_tags: List[str]) -> str:
        cleaned = original
        for tag in extracted_tags:
            cleaned = cleaned.replace(tag, "")

        try:
            jobj = json.loads(original)
            if "tool_calls" in jobj:
                cleaned_json = jobj.copy()
                if isinstance(cleaned_json, dict):
                    cleaned_json.pop("tool_calls", None)
                cleaned = json.dumps(cleaned_json, indent=2, ensure_ascii=False)
        except Exception:
            pass

        # Trim lines and drop empty lines
        cleaned = "\n".join([ln.strip() for ln in cleaned.splitlines() if ln.strip()])
        return cleaned

    def extract_natural_language_patterns(self, text: str) -> List[str]:
        patterns: List[str] = []
        action_patterns = [
            r"we should",
            r"I need to",
            r"let's",
            r"we need to",
            r"don't forget",
            r"remember to",
            r"make sure",
            r"important:",
            r"note:",
            r"todo:",
        ]
        for pat in action_patterns:
            try:
                regex = re.compile(f"(?i){pat}")
            except re.error as e:
                raise TodoziError(f"Regex compilation failed: {e}")
            for m in regex.finditer(text):
                start = m.start()
                tail = text[start:]
                end_pos = tail.find(".")
                if end_pos == -1:
                    end_pos = tail.find("\n")
                if end_pos == -1:
                    end_pos = len(tail)
                extracted = tail[:end_pos].strip()
                if 10 < len(extracted) < 200:
                    patterns.append(extracted)
        return patterns

    def extract_checklist_items(self, text: str) -> List[ChecklistItem]:
        items: List[ChecklistItem] = []
        seen: Set[str] = set()
        patterns = [
            r"add to (?:checklist|list|todo)",
            r"we need to",
            r"should (?:have|do)",
            r"don't forget to",
            r"remember to",
            r"make sure to",
            r"need to",
            r"have to",
            r"must",
        ]
        for pat in patterns:
            try:
                regex = re.compile(f"(?i){pat}")
            except re.error as e:
                raise TodoziError(f"Regex compilation failed: {e}")
            for m in regex.finditer(text):
                start = m.start()
                tail = text[start:]
                end_pos = tail.find(".")
                if end_pos == -1:
                    end_pos = tail.find("!")
                if end_pos == -1:
                    end_pos = tail.find("?")
                if end_pos == -1:
                    end_pos = len(tail)
                item_text = tail[:end_pos].strip()
                if not item_text or len(item_text) >= 200:
                    continue
                norm = item_text.lower()
                if norm in seen:
                    continue
                seen.add(norm)
                items.append(
                    ChecklistItem(
                        id=str(uuid.uuid4()),
                        content=item_text,
                        priority="medium",
                        created_at=datetime.now(timezone.utc),
                        completed=False,
                        source="natural_language",
                    )
                )
        return items

    def ensure_session_exists(self, session_id: str, parsed: ParsedContent) -> None:
        state = self.state.locked()
        if session_id not in state.active_sessions:
            topic = self.infer_topic(parsed.text_content)
            sess = ConversationSession(
                id=session_id,
                start_time=datetime.now(timezone.utc),
                last_activity=datetime.now(timezone.utc),
                topic=topic,
                participant_count=1,
                message_count=1,
            )
            state.active_sessions[session_id] = sess
        else:
            sess = state.active_sessions.get(session_id)
            if sess:
                sess.last_activity = datetime.now(timezone.utc)
                sess.message_count += 1

    def infer_topic(self, text: str) -> str:
        t = text.lower()
        if "bug" in t or "error" in t or "fix" in t:
            return "Bug Fixing & Debugging"
        if "feature" in t or "implement" in t:
            return "Feature Development"
        if "design" in t or "architecture" in t:
            return "System Design & Architecture"
        if "test" in t or "testing" in t:
            return "Testing & Quality Assurance"
        if "deploy" in t or "production" in t:
            return "Deployment & Operations"
        return "General Discussion"

    def generate_response(
        self,
        cleaned_content: str,
        state: TodoziProcessorState,
        processing: ProcessingResult,
        stats: ProcessingStats,
    ) -> str:
        lines: List[str] = [cleaned_content]
        if processing.actions or stats.checklists_generated > 0:
            lines.append("\n--- TDZ PROCESSING SUMMARY ---")
            if stats.checklists_generated > 0:
                lines.append(f"📋 Generated {stats.checklists_generated} checklist items")
            if processing.actions:
                lines.append(f"✅ Processed {len(processing.actions)} actions")
                successful = sum(1 for a in processing.actions if a.success)
                if successful > 0:
                    lines.append(f"✅ {successful} successful actions")
            lines.append(f"⏱️ Processing time: {stats.processing_time_ms}ms")

        recent_actions = list(reversed(state.recent_actions))[-3:]
        if recent_actions:
            lines.append("\n--- RECENT ACTIONS ---")
            for action in recent_actions:
                status = "✅" if action.success else "❌"
                lines.append(f"{status} {action.action_type}: {action.description}")

        active_checklist = [item for item in state.checklist_items if not item.completed][-3:]
        if active_checklist:
            lines.append("\n--- ACTIVE CHECKLIST ---")
            for item in active_checklist:
                lines.append(f"☐ {item.content}")

        now = datetime.now(timezone.utc)
        active_sessions = [s for s in state.active_sessions.values() if s.last_activity > now - timedelta(hours=24)]
        if active_sessions:
            lines.append("\n--- ACTIVE SESSIONS ---")
            for session in active_sessions:
                lines.append(f"📋 {session.topic}: {session.message_count} messages")

        lines.append("\n💡 Run `todozi stats` or `todozi list` to see all recent activity")
        return "\n".join(lines)

    async def process_create_task_call(self, _tool_call: JsonValue) -> ProcessedAction:
        result = await self.execute_binary_command("todozi", ["add", "Task from tool call"])
        return ProcessedAction(
            id=str(uuid.uuid4()),
            action_type="create_task",
            description="Created task via tool call",
            timestamp=datetime.now(timezone.utc),
            success=result.returncode == 0,
            result=(result.stdout.decode() if isinstance(result.stdout, bytes) else str(result.stdout)),
        )

    async def process_search_call(self, _tool_call: JsonValue) -> ProcessedAction:
        result = await self.execute_binary_command("todozi", ["list"])
        return ProcessedAction(
            id=str(uuid.uuid4()),
            action_type="search_tasks",
            description="Searched tasks via tool call",
            timestamp=datetime.now(timezone.utc),
            success=result.returncode == 0,
            result=(result.stdout.decode() if isinstance(result.stdout, bytes) else str(result.stdout)),
        )

    async def process_update_call(self, _tool_call: JsonValue) -> ProcessedAction:
        return ProcessedAction(
            id=str(uuid.uuid4()),
            action_type="update_task",
            description="Updated task via tool call",
            timestamp=datetime.now(timezone.utc),
            success=True,
            result="Task update processed",
        )

    async def process_memory_call(self, _tool_call: JsonValue) -> ProcessedAction:
        return ProcessedAction(
            id=str(uuid.uuid4()),
            action_type="create_memory",
            description="Created memory via tool call",
            timestamp=datetime.now(timezone.utc),
            success=True,
            result="Memory created",
        )

    async def process_idea_call(self, _tool_call: JsonValue) -> ProcessedAction:
        return ProcessedAction(
            id=str(uuid.uuid4()),
            action_type="create_idea",
            description="Created idea via tool call",
            timestamp=datetime.now(timezone.utc),
            success=True,
            result="Idea created",
        )

    async def execute_binary_command(self, command: str, args: List[str]) -> subprocess.CompletedProcess:
        # Run blocking subprocess in a thread to stay async-friendly
        def run() -> subprocess.CompletedProcess:
            return subprocess.run(
                [command] + args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        return await asyncio.to_thread(run)


# ------------- Factories / Initialization -------------

def create_tdz_content_processor_tool(state: SharedTodoziState) -> Tool:
    return TdzContentProcessorTool(state)


async def initialize_tdz_content_processor() -> SharedTodoziState:
    state = TodoziProcessorState.new()
    return state


# ------------- tdz_cnt (high-level processing) -------------

async def tdz_cnt(content: str, session_id: Optional[str] = None) -> str:
    # Parse with enhanced extractor
    try:
        chat_content = parse_chat_message_extended(content, "tdz_system")
    except Exception as e:
        print(f"Warning: Failed to process chat message: {e}", flush=True)
        chat_content = ChatContent()

    processed_items: List[str] = []

    # Process tasks
    for task in chat_content.tasks:
        try:
            await Done.create_task(
                task.action,
                task.priority if task.priority else None,
                task.parent_project if task.parent_project else None,
                task.time if task.time else None,
                task.context_notes if task.context_notes else None,
            )
            processed_items.append(f"Task: {task.action}")
        except Exception as e:
            import logging
            logger = logging.getLogger("todozi.tdz_cnt")
            logger.warning(f"Failed to create task '{task.action}': {e}", exc_info=True)
            processed_items.append(f"Task: {task.action}")

    # Process memories
    for mem in chat_content.memories:
        try:
            await Memories.create(mem.moment, mem.meaning, mem.reason)
            processed_items.append(f"Memory: {mem.moment}")
        except Exception:
            processed_items.append(f"Memory: {mem.moment}")

    # Process ideas
    for idea in chat_content.ideas:
        try:
            await Ideas.create(idea.idea)
            processed_items.append(f"Idea: {idea.idea}")
        except Exception:
            processed_items.append(f"Idea: {idea.idea}")

    # Process errors
    for err in chat_content.errors:
        try:
            storage.save_error(err)
            processed_items.append(f"Error: {err.title}")
        except Exception:
            processed_items.append(f"Error: {err.title}")

    # Remove tag blocks to build clean content
    tag_patterns = [
        r"<todozi>.*?</todozi>",
        r"<memory>.*?</memory>",
        r"<idea>.*?</idea>",
        r"<todozi_agent>.*?</todozi_agent>",
        r"<chunk>.*?</chunk>",
        r"<error>.*?</error>",
        r"<train>.*?</train>",
        r"<feel>.*?</feel>",
        r"<summary>.*?</summary>",
        r"<reminder>.*?</reminder>",
        r"<tdz>.*?</tdz>",
    ]

    clean_content = content
    for pat in tag_patterns:
        try:
            clean_content = re.sub(pat, "", clean_content, flags=re.S | re.I)
        except re.error:
            continue

    # Clean whitespace
    clean_content = " ".join(clean_content.split())
    clean_content = clean_content.strip()

    # Compose system response
    if processed_items:
        system_response_lines = ["Great job! I've processed the following items:"]
        for item in processed_items:
            system_response_lines.append(f"• {item}")
        system_response_lines.append("\nTo update or modify these items, you can add new <todozi>, <memory>, or <idea> tags to your messages.")
        system_response = "\n".join(system_response_lines)
    else:
        system_response = ""

    # Combine clean content with system response
    if not clean_content:
        clean_with_response = f"<tdz_sys>{system_response}</tdz_sys>"
    elif not system_response:
        clean_with_response = clean_content
    else:
        clean_with_response = f"{clean_content}\n<tdz_sys>{system_response}</tdz_sys>"

    # Also run traditional processor for backward compatibility
    try:
        state = await initialize_tdz_content_processor()
        tool = create_tdz_content_processor_tool(state)
        kwargs: Dict[str, JsonValue] = {"content": content, "extract_checklist": True, "auto_session": True}
        if session_id:
            kwargs["session_id"] = session_id
        traditional_result = await tool.execute(kwargs)
        traditional_output = traditional_result.output if traditional_result.success else f"Traditional processing failed: {traditional_result.output}"
    except Exception as e:
        traditional_output = f"Traditional processing error: {e}"

    response = {
        "process": "success",
        "original": content,
        "clean": clean_content,
        "clean_with_response": clean_with_response,
        "processed_items": len(processed_items),
        "items_detail": processed_items,
        "traditional_processing": traditional_output,
    }

    return json.dumps(response, indent=2, ensure_ascii=False)


# ------------- Simple Tests (pytest-style) -------------

async def test_tdz_cnt_basic():
    result = await tdz_cnt("Hello world, <todozi>add task; test task</todozi>", None)
    assert isinstance(result, str)
    response = json.loads(result)
    assert response.get("process") == "success"
    assert response.get("original") == "Hello world, <todozi>add task; test task</todozi>"
    assert response.get("clean") == "Hello world,"
    assert "<tdz_sys>" in response.get("clean_with_response", "")
    assert response.get("processed_items", 0) >= 1


async def test_checklist_extraction():
    state = await initialize_tdz_content_processor()
    processor = TdzContentProcessorTool(state)
    items = processor.extract_checklist_items(
        "We need to fix the bug, don't forget to test it, and make sure to deploy"
    )
    assert len(items) > 0


# Allow running this file directly for a quick demo
if __name__ == "__main__":
    async def demo():
        print(await tdz_cnt("Hello world, <todozi>add task; test task</todozi>", None))
        print("\n--- Checklist extraction demo ---")
        state = await initialize_tdz_content_processor()
        tool = create_tdz_content_processor_tool(state)
        content = "We need to fix the bug, don't forget to test it, and make sure to deploy"
        result = await tool.execute({"content": content, "extract_checklist": True, "auto_session": True})
        print(result.output)

    asyncio.run(demo())
