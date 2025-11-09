"""Base classes for QuestFoundry loops."""

import copy
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from ..models.artifact import Artifact
from ..roles.base import Role
from ..state.workspace import WorkspaceManager
from .registry import LoopMetadata


class StepStatus(Enum):
    """Status of a loop step."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class LoopStep:
    """
    Single step in a loop execution.

    Each step represents a discrete task performed by one or more roles.
    """

    step_id: str
    """Unique identifier for this step"""

    description: str
    """Human-readable description of what this step does"""

    assigned_roles: list[str] = field(default_factory=list)
    """RACI: Responsible roles that perform this step"""

    consulted_roles: list[str] = field(default_factory=list)
    """RACI: Consulted roles that provide input"""

    informed_roles: list[str] = field(default_factory=list)
    """RACI: Informed roles that receive updates"""

    artifacts_input: list[str] = field(default_factory=list)
    """Required artifact types for input"""

    artifacts_output: list[str] = field(default_factory=list)
    """Expected artifact types to produce"""

    validation_required: bool = True
    """Whether this step requires validation before proceeding"""

    status: StepStatus = StepStatus.PENDING
    """Current status of this step"""

    result: Any | None = None
    """Result of executing this step"""

    error: str | None = None
    """Error message if step failed"""


@dataclass
class LoopContext:
    """
    Context for active loop execution.

    This contains all information needed for a loop to execute,
    approximately ~500 lines when formatted for LLM context.
    """

    loop_id: str
    """ID of the loop being executed"""

    project_id: str
    """ID of the project"""

    workspace: WorkspaceManager
    """Workspace for artifact storage"""

    role_instances: dict[str, Role] = field(default_factory=dict)
    """Instantiated role objects keyed by role name"""

    artifacts: list[Artifact] = field(default_factory=list)
    """Artifacts available for this loop"""

    project_metadata: dict[str, Any] = field(default_factory=dict)
    """Project-level metadata"""

    current_step: int = 0
    """Index of currently executing step"""

    history: list[dict[str, Any]] = field(default_factory=list)
    """Execution history"""

    config: dict[str, Any] = field(default_factory=dict)
    """Loop-specific configuration"""


@dataclass
class LoopResult:
    """Result of loop execution."""

    success: bool
    """Whether the loop completed successfully"""

    loop_id: str
    """ID of the executed loop"""

    artifacts_created: list[Artifact] = field(default_factory=list)
    """Artifacts created during execution"""

    artifacts_modified: list[Artifact] = field(default_factory=list)
    """Artifacts modified during execution"""

    steps_completed: int = 0
    """Number of steps completed"""

    steps_failed: int = 0
    """Number of steps that failed"""

    error: str | None = None
    """Error message if loop failed"""

    metadata: dict[str, Any] = field(default_factory=dict)
    """Additional metadata about execution"""


class Loop(ABC):
    """
    Base class for all loop implementations.

    Loops are hardcoded Python classes that define workflow structure,
    not runtime playbook parsing. This reduces context usage while
    maintaining flexibility through LLM-backed roles.
    """

    # Class-level metadata (defined by subclasses)
    metadata: LoopMetadata

    # Steps for this loop (defined by subclasses)
    steps: list[LoopStep] = []

    def __init__(self, context: LoopContext):
        """
        Initialize loop with execution context.

        Args:
            context: Loop execution context
        """
        self.context = context
        self.current_step_index = context.current_step
        # Create instance-specific copy of steps to avoid shared state
        self.steps = copy.deepcopy(self.__class__.steps)

    @abstractmethod
    def execute(self) -> LoopResult:
        """
        Execute the complete loop.

        This is the main entry point for loop execution. Implementations
        should:
        1. Iterate through steps
        2. Execute each step with appropriate roles
        3. Validate outputs
        4. Handle failures
        5. Return result

        Returns:
            Result of loop execution
        """
        pass

    def execute_step(self, step: LoopStep) -> None:
        """
        Execute a single step.

        Default implementation:
        1. Mark step as in_progress
        2. Get required roles
        3. Execute role tasks
        4. Validate if required
        5. Mark step completed or failed

        Subclasses can override for custom behavior.

        Args:
            step: Step to execute

        Raises:
            ValueError: If required roles not available
        """
        step.status = StepStatus.IN_PROGRESS

        # Get assigned roles
        roles_needed = step.assigned_roles
        roles = {}
        for role_name in roles_needed:
            if role_name not in self.context.role_instances:
                step.status = StepStatus.FAILED
                step.error = f"Required role '{role_name}' not available"
                raise ValueError(step.error)
            roles[role_name] = self.context.role_instances[role_name]

        # Execute (subclass implements specific logic)
        try:
            result = self._execute_step_logic(step, roles)
            step.result = result

            # Validate if required
            if step.validation_required:
                is_valid = self.validate_step(step, result)
                if not is_valid:
                    step.status = StepStatus.FAILED
                    step.error = "Validation failed"
                else:
                    step.status = StepStatus.COMPLETED
            else:
                step.status = StepStatus.COMPLETED

        except Exception as e:
            step.status = StepStatus.FAILED
            step.error = str(e)
            raise

    def _execute_step_logic(
        self, step: LoopStep, roles: dict[str, Role]
    ) -> Any:
        """
        Execute the actual step logic.

        Subclasses should override this to implement step-specific behavior.

        Args:
            step: Step being executed
            roles: Available roles

        Returns:
            Step result
        """
        # Default: just return empty dict
        # Subclasses override for actual implementation
        return {}

    def validate_step(self, step: LoopStep, result: Any) -> bool:
        """
        Validate step completion.

        Default implementation always returns True.
        Subclasses can override for specific validation logic.

        Args:
            step: Step that was executed
            result: Result from step execution

        Returns:
            True if step is valid, False otherwise
        """
        return True

    def can_continue(self) -> bool:
        """
        Check if loop can proceed to next step.

        Returns:
            True if can continue, False otherwise
        """
        # Check if there are more steps
        if self.current_step_index >= len(self.steps):
            return False

        # Check if previous step succeeded
        if self.current_step_index > 0:
            prev_step = self.steps[self.current_step_index - 1]
            if prev_step.status == StepStatus.FAILED:
                return False

        return True

    def rollback_step(self) -> None:
        """
        Roll back to previous step.

        Default implementation just decrements step index.
        Subclasses can override for cleanup logic.
        """
        if self.current_step_index > 0:
            self.current_step_index -= 1
            self.context.current_step = self.current_step_index

            # Mark current step as pending
            if self.current_step_index < len(self.steps):
                self.steps[self.current_step_index].status = StepStatus.PENDING

    def skip_step(self, step: LoopStep) -> None:
        """
        Skip a step (mark as skipped and move on).

        Args:
            step: Step to skip
        """
        step.status = StepStatus.SKIPPED
        self.current_step_index += 1
        self.context.current_step = self.current_step_index

    def build_loop_context_summary(self) -> str:
        """
        Build detailed context for loop execution.

        This creates approximately ~500 lines of context including:
        - Loop metadata
        - Available artifacts
        - Step definitions
        - Role assignments
        - Quality gates

        Returns:
            Formatted context string
        """
        lines = [
            f"# Loop: {self.metadata.display_name}",
            "",
            f"**Purpose**: {self.metadata.description}",
            f"**Duration**: {self.metadata.typical_duration}",
            "",
            "## Steps",
            "",
        ]

        for i, step in enumerate(self.steps, 1):
            lines.append(f"{i}. **{step.description}**")
            lines.append(f"   - Assigned: {', '.join(step.assigned_roles)}")
            if step.consulted_roles:
                lines.append(f"   - Consulted: {', '.join(step.consulted_roles)}")
            if step.artifacts_input:
                lines.append(f"   - Input: {', '.join(step.artifacts_input)}")
            if step.artifacts_output:
                lines.append(f"   - Output: {', '.join(step.artifacts_output)}")
            lines.append("")

        lines.append("## Available Artifacts")
        lines.append("")
        for artifact in self.context.artifacts:
            lines.append(f"- {artifact.type}: {artifact.artifact_id}")

        return "\n".join(lines)

    def __repr__(self) -> str:
        """String representation of the loop."""
        return (
            f"{self.__class__.__name__}("
            f"loop_id='{self.metadata.loop_id}', "
            f"step={self.current_step_index}/{len(self.steps)})"
        )
