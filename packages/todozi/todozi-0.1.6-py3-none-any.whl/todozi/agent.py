from __future__ import annotations

import copy
import json
import os
import uuid
import sys
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Iterable

# -----------------------------
# Errors
# -----------------------------

class TodoziError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


# -----------------------------
# Enums and Data Models
# -----------------------------

class AgentStatus(Enum):
    AVAILABLE = "Available"
    BUSY = "Busy"
    INACTIVE = "Inactive"


class AssignmentStatus(Enum):
    ASSIGNED = "Assigned"
    COMPLETED = "Completed"


ASSIGNED = "Assigned"
AVAILABLE = "Available"
BUSY = "Busy"
COMPLETED = "Completed"
INACTIVE = "Inactive"


@dataclass
class AgentMetadata:
    status: AgentStatus = AgentStatus.AVAILABLE


@dataclass
class Agent:
    id: str
    name: str
    description: str
    capabilities: List[str]
    specializations: List[str]
    metadata: AgentMetadata
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def new(name: str, description: str = "") -> "Agent":
        now = datetime.now(timezone.utc)
        return Agent(
            id="",
            name=name,
            description=description,
            capabilities=[],
            specializations=[],
            metadata=AgentMetadata(status=AgentStatus.AVAILABLE),
            created_at=now,
            updated_at=now,
        )


@dataclass
class AgentAssignment:
    agent_id: str
    task_id: str
    project_id: str
    assigned_at: datetime
    status: AssignmentStatus


@dataclass
class AgentUpdate:
    name: Optional[str] = None
    description: Optional[str] = None
    capabilities: Optional[List[str]] = None
    specializations: Optional[List[str]] = None
    status: Optional[AgentStatus] = None

    def with_name(self, name: str) -> "AgentUpdate":
        self.name = name
        return self

    def with_description(self, description: str) -> "AgentUpdate":
        self.description = description
        return self

    def with_capabilities(self, capabilities: List[str]) -> "AgentUpdate":
        self.capabilities = capabilities
        return self

    def with_specializations(self, specializations: List[str]) -> "AgentUpdate":
        self.specializations = specializations
        return self

    def with_status(self, status: AgentStatus) -> "AgentUpdate":
        self.status = status
        return self


@dataclass
class AgentStatistics:
    total_agents: int
    available_agents: int
    busy_agents: int
    inactive_agents: int
    total_assignments: int
    completed_assignments: int

    def completion_rate(self) -> float:
        if self.total_assignments == 0:
            return 0.0
        return (self.completed_assignments / self.total_assignments) * 100.0


# -----------------------------
# Storage Layer (JSON-backed with atomic operations)
# -----------------------------

_AGENTS_JSON = "agents.json"

@contextmanager
def json_file_transaction(path: str):
    """Context manager for atomic JSON file operations"""
    tmp_path = path + ".tmp"
    try:
        yield tmp_path
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise


def _load_json_list(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        if isinstance(data, list):
            return data
        return []


def _save_json_list(path: str, data: List[Dict[str, Any]]) -> None:
    with json_file_transaction(path) as tmp_path:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def create_default_agents() -> None:
    # Create an empty agents file if it doesn't exist
    if not os.path.exists(_AGENTS_JSON):
        _save_json_list(_AGENTS_JSON, [])


def list_agents() -> List[Agent]:
    raw = _load_json_list(_AGENTS_JSON)
    agents: List[Agent] = []
    for item in raw:
        meta = item.get("metadata") or {}
        # Convert string to enum
        try:
            status = AgentStatus(meta.get("status", AgentStatus.AVAILABLE.value))
        except ValueError:
            status = AgentStatus.AVAILABLE
            
        agents.append(
            Agent(
                id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                capabilities=item.get("capabilities", []),
                specializations=item.get("specializations", []),
                metadata=AgentMetadata(status=status),
                created_at=datetime.fromisoformat(item["created_at"]),
                updated_at=datetime.fromisoformat(item["updated_at"]),
            )
        )
    return agents


def save_agent(agent: Agent) -> None:
    agents = _load_json_list(_AGENTS_JSON)
    found = False
    for i, a in enumerate(agents):
        if a.get("id") == agent.id:
            found = True
            agents[i] = {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "specializations": agent.specializations,
                "metadata": {"status": agent.metadata.status.value},
                "created_at": agent.created_at.isoformat(),
                "updated_at": agent.updated_at.isoformat(),
            }
            break
    if not found:
        agents.append(
            {
                "id": agent.id,
                "name": agent.name,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "specializations": agent.specializations,
                "metadata": {"status": agent.metadata.status.value},
                "created_at": agent.created_at.isoformat(),
                "updated_at": agent.updated_at.isoformat(),
            }
        )
    _save_json_list(_AGENTS_JSON, agents)


# -----------------------------
# Manager
# -----------------------------

class AgentManager:
    """Manages AI agents and their task assignments."""
    
    def __init__(self) -> None:
        self.agents: Dict[str, Agent] = {}
        self.agent_assignments: List[AgentAssignment] = []

    async def load_agents(self) -> None:
        """Load agents from storage into the manager."""
        if not self.agents:
            create_default_agents()
        agent_list = list_agents()
        for agent in agent_list:
            self.agents[agent.id] = agent

    async def create_agent(self, agent: Agent) -> str:
        """
        Create a new agent and save it to storage.
        
        Args:
            agent: Agent data to create
            
        Returns:
            The unique ID of the created agent
        """
        agent_copy = copy.copy(agent)  # Work with a copy to avoid mutations
        agent_copy.id = str(uuid.uuid4())
        now = datetime.now(timezone.utc)
        agent_copy.created_at = now
        agent_copy.updated_at = now
        save_agent(agent_copy)
        self.agents[agent_copy.id] = agent_copy
        return agent_copy.id

    async def update_agent(self, agent_id: str, updates: AgentUpdate) -> None:
        """Update an existing agent's information."""
        agent = self.agents.get(agent_id)
        if agent is None:
            raise TodoziError(f"Agent {agent_id} not found")

        if updates.name is not None:
            agent.name = updates.name
        if updates.description is not None:
            agent.description = updates.description
        if updates.capabilities is not None:
            agent.capabilities = updates.capabilities
        if updates.specializations is not None:
            agent.specializations = updates.specializations
        if updates.status is not None:
            agent.metadata.status = updates.status

        agent.updated_at = datetime.now(timezone.utc)
        save_agent(agent)

    async def delete_agent(self, agent_id: str) -> None:
        """Remove an agent from the system."""
        removed = self.agents.pop(agent_id, None)
        if removed is None:
            raise TodoziError(f"Agent {agent_id} not found")

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get an agent by ID."""
        return self.agents.get(agent_id)

    def get_all_agents(self) -> List[Agent]:
        """Get all agents in the system."""
        return list(self.agents.values())

    def get_available_agents(self) -> List[Agent]:
        """Get all agents with AVAILABLE status."""
        return [a for a in self.agents.values() if a.metadata.status == AgentStatus.AVAILABLE]

    def get_agents_by_specialization(self, specialization: str) -> List[Agent]:
        """Get agents by specialization."""
        return [a for a in self.agents.values() if specialization in a.specializations]

    def get_agents_by_capability(self, capability: str) -> List[Agent]:
        """Get agents by capability."""
        return [a for a in self.agents.values() if capability in a.capabilities]

    async def assign_task_to_agent(self, task_id: str, agent_id: str, project_id: str) -> str:
        """
        Assign a task to an available agent.
        
        Args:
            task_id: Unique identifier for the task
            agent_id: ID of the agent to assign
            project_id: Project context for the assignment
            
        Returns:
            The task_id that was assigned
            
        Raises:
            TodoziError: If agent not found or not available
        """
        if agent_id not in self.agents:
            raise TodoziError(f"Agent {agent_id} not found")
        
        agent = self.agents[agent_id]
        if agent.metadata.status != AgentStatus.AVAILABLE:
            raise TodoziError(f"Agent {agent_id} is not available (status: {agent.metadata.status})")

        assignment = AgentAssignment(
            agent_id=agent_id,
            task_id=task_id,
            project_id=project_id,
            assigned_at=datetime.now(timezone.utc),
            status=AssignmentStatus.ASSIGNED,
        )

        # Update the same agent reference
        agent.metadata.status = AgentStatus.BUSY
        agent.updated_at = datetime.now(timezone.utc)
        save_agent(agent)

        self.agent_assignments.append(assignment)
        return assignment.task_id

    async def complete_agent_assignment(self, task_id: str) -> None:
        """Mark an assignment as completed and return the agent to available status."""
        idx = None
        for i, a in enumerate(self.agent_assignments):
            if a.task_id == task_id:
                idx = i
                break
        if idx is None:
            raise TodoziError(f"Assignment for task {task_id} not found")

        assignment = self.agent_assignments[idx]
        assignment.status = AssignmentStatus.COMPLETED
        agent = self.agents.get(assignment.agent_id)
        if agent is not None:
            agent.metadata.status = AgentStatus.AVAILABLE
            agent.updated_at = datetime.now(timezone.utc)
            save_agent(agent)

    def get_agent_assignments(self, agent_id: str) -> List[AgentAssignment]:
        """Get all assignments for a specific agent."""
        return [a for a in self.agent_assignments if a.agent_id == agent_id]

    def get_task_assignments(self, task_id: str) -> List[AgentAssignment]:
        """Get all assignments for a specific task."""
        return [a for a in self.agent_assignments if a.task_id == task_id]

    def find_best_agent(
        self,
        required_specialization: str,
        preferred_capability: Optional[str] = None,
    ) -> Optional[Agent]:
        """
        Find the best available agent for a task.
        
        Args:
            required_specialization: Required specialization for the task
            preferred_capability: Preferred capability (optional)
            
        Returns:
            Best matching agent or None if no candidates found
        """
        candidates: List[Agent] = [
            a for a in self.agents.values()
            if a.metadata.status == AgentStatus.AVAILABLE 
            and required_specialization in a.specializations
        ]
        
        if preferred_capability is not None:
            # Prioritize agents with the preferred capability
            candidates.sort(key=lambda a: (
                preferred_capability not in a.capabilities,  # False (has capability) sorts first
                -len(a.capabilities),  # Secondary: more capabilities
                a.id  # Tertiary: consistent ordering
            ))
        
        return candidates[0] if candidates else None

    async def update_agent_status(self, agent_id: str, status: AgentStatus) -> None:
        """Update an agent's status."""
        agent = self.agents.get(agent_id)
        if agent is None:
            raise TodoziError(f"Agent {agent_id} not found")
        agent.metadata.status = status
        agent.updated_at = datetime.now(timezone.utc)
        save_agent(agent)

    def get_agent_statistics(self) -> AgentStatistics:
        """Get statistics about agents and assignments."""
        total_agents = len(self.agents)
        available_agents = sum(1 for a in self.agents.values() if a.metadata.status == AgentStatus.AVAILABLE)
        busy_agents = sum(1 for a in self.agents.values() if a.metadata.status == AgentStatus.BUSY)
        inactive_agents = sum(1 for a in self.agents.values() if a.metadata.status == AgentStatus.INACTIVE)
        total_assignments = len(self.agent_assignments)
        completed_assignments = sum(1 for a in self.agent_assignments if a.status == AssignmentStatus.COMPLETED)
        return AgentStatistics(
            total_agents=total_agents,
            available_agents=available_agents,
            busy_agents=busy_agents,
            inactive_agents=inactive_agents,
            total_assignments=total_assignments,
            completed_assignments=completed_assignments,
        )


# -----------------------------
# Parser
# -----------------------------

def parse_agent_assignment_format(agent_text: str) -> AgentAssignment:
    """
    Parse agent assignment from formatted text.
    
    Args:
        agent_text: Text containing agent assignment in format: <todozi_agent>agent_id; task_id; project_id</todozi_agent>
        
    Returns:
        Parsed AgentAssignment object
        
    Raises:
        TodoziError: If format is invalid
    """
    start_tag = "<todozi_agent>"
    end_tag = "</todozi_agent>"
    start = agent_text.find(start_tag)
    if start == -1:
        raise TodoziError("Missing <todozi_agent> start tag")
    end = agent_text.find(end_tag)
    if end == -1:
        raise TodoziError("Missing </todozi_agent> end tag")
    content = agent_text[start + len(start_tag): end]
    parts = [s.strip() for s in content.split(";")]
    if len(parts) < 3:
        raise TodoziError("Invalid agent assignment format: need at least 3 parts (agent_id; task_id; project_id)")
    return AgentAssignment(
        agent_id=parts[0],
        task_id=parts[1],
        project_id=parts[2],
        assigned_at=datetime.now(timezone.utc),
        status=AssignmentStatus.ASSIGNED,
    )


# -----------------------------
# Tests
# -----------------------------

def test_agent_manager_creation():
    manager = AgentManager()
    assert len(manager.agents) == 0
    assert len(manager.agent_assignments) == 0


def test_parse_agent_assignment_format():
    agent_text = "<todozi_agent>planner; task_001; project_planning</todozi_agent>"
    assignment = parse_agent_assignment_format(agent_text)
    assert assignment.agent_id == "planner"
    assert assignment.task_id == "task_001"
    assert assignment.project_id == "project_planning"
    assert assignment.status == AssignmentStatus.ASSIGNED


def test_agent_update_builder():
    update = AgentUpdate().with_name("New Name").with_description("New Description").with_status(AgentStatus.AVAILABLE)
    assert update.name == "New Name"
    assert update.description == "New Description"
    assert update.status == AgentStatus.AVAILABLE


def test_agent_statistics_completion_rate():
    stats = AgentStatistics(
        total_agents=5,
        available_agents=3,
        busy_agents=1,
        inactive_agents=1,
        total_assignments=10,
        completed_assignments=8,
    )
    assert stats.completion_rate() == 80.0
    empty_stats = AgentStatistics(
        total_agents=5,
        available_agents=3,
        busy_agents=1,
        inactive_agents=1,
        total_assignments=0,
        completed_assignments=0,
    )
    assert empty_stats.completion_rate() == 0.0


if __name__ == "__main__":
    # Optional manual run of tests
    try:
        test_agent_manager_creation()
        test_parse_agent_assignment_format()
        test_agent_update_builder()
        test_agent_statistics_completion_rate()
        print("All tests passed.")
    except Exception as e:
        print(f"Test failed: {e}", file=sys.stderr)
        sys.exit(1)
