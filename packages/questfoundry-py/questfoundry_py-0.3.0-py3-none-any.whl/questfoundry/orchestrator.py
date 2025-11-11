"""Orchestrator for QuestFoundry loop execution."""

import re
from pathlib import Path
from typing import Any

from .loops.base import Loop, LoopContext, LoopResult
from .loops.registry import LoopRegistry
from .models.artifact import Artifact
from .providers.base import TextProvider
from .providers.config import ProviderConfig
from .providers.registry import ProviderRegistry
from .roles.base import Role, RoleContext
from .roles.registry import RoleRegistry
from .state.workspace import WorkspaceManager


class Orchestrator:
    """
    Orchestrates QuestFoundry workflow execution.

    The Orchestrator coordinates between the Showrunner role, loop registry,
    and role registry to execute appropriate loops based on user goals.

    It manages:
    - Loop selection based on project state and goals
    - Role instantiation and lifecycle
    - Loop execution and coordination
    - Artifact management
    """

    def __init__(
        self,
        workspace: WorkspaceManager,
        provider_registry: ProviderRegistry | None = None,
        role_registry: RoleRegistry | None = None,
        loop_registry: LoopRegistry | None = None,
        spec_path: Path | None = None,
    ):
        """
        Initialize orchestrator.

        Args:
            workspace: Workspace manager for project
            provider_registry: Provider registry (creates default if None)
            role_registry: Role registry (creates default if None)
            loop_registry: Loop registry (creates default if None)
            spec_path: Path to spec directory
        """
        self.workspace = workspace
        self.spec_path = spec_path or Path.cwd() / "spec"

        # Initialize registries
        self.provider_registry = provider_registry or ProviderRegistry(
            config=ProviderConfig()
        )
        self.role_registry = role_registry or RoleRegistry(
            self.provider_registry, spec_path=self.spec_path
        )
        self.loop_registry = loop_registry or LoopRegistry(spec_path=self.spec_path)

        # Initialize showrunner and provider (type annotations for mypy)
        self.showrunner: Role | None = None
        self.provider: TextProvider | None = None
        self.provider_name: str | None = None

    def initialize(
        self,
        provider: TextProvider | None = None,
        provider_name: str | None = None,
    ) -> None:
        """
        Initialize orchestrator with LLM provider.

        Args:
            provider: Text provider to use
            provider_name: Name of provider in registry
        """
        # Save provider for later use
        self.provider = provider
        self.provider_name = provider_name

        # Get showrunner instance
        self.showrunner = self.role_registry.get_role(
            "showrunner",
            provider=provider,
            provider_name=provider_name,
        )

    def select_loop(
        self,
        goal: str,
        project_state: dict[str, Any] | None = None,
        artifacts: list[Artifact] | None = None,
    ) -> str:
        """
        Select appropriate loop for the given goal.

        Args:
            goal: User's goal or request
            project_state: Current project state
            artifacts: Existing artifacts

        Returns:
            Loop ID to execute

        Raises:
            RuntimeError: If showrunner not initialized or selection fails
        """
        if self.showrunner is None:
            raise RuntimeError("Orchestrator not initialized. Call initialize() first.")

        # Get available loops
        loops = self.loop_registry.list_loops()
        loop_data = [
            {
                "loop_id": metadata.loop_id,
                "description": metadata.description,
                "typical_duration": metadata.typical_duration,
                "primary_roles": metadata.primary_roles,
                "entry_conditions": metadata.entry_conditions,
            }
            for metadata in loops
        ]

        # Create context for showrunner
        project_info = self.workspace.get_project_info()
        context = RoleContext(
            task="select_loop",
            artifacts=artifacts or [],
            project_metadata=project_info.model_dump(),
            additional_context={
                "goal": goal,
                "project_state": project_state or {},
                "available_loops": loop_data,
            },
        )

        # Call showrunner to select loop
        result = self.showrunner.execute_task(context)

        if not result.success:
            raise RuntimeError(f"Loop selection failed: {result.error}")

        # Parse loop_id from response
        # For now, extract from output (in production, would parse structured response)
        loop_id = self._extract_loop_id(result.output)

        return loop_id

    def execute_loop(
        self,
        loop_id: str,
        project_id: str,
        artifacts: list[Artifact] | None = None,
        config: dict[str, Any] | None = None,
    ) -> LoopResult:
        """
        Execute a specific loop.

        Args:
            loop_id: Loop identifier
            project_id: Project identifier
            artifacts: Existing artifacts
            config: Loop configuration

        Returns:
            Loop execution result

        Raises:
            KeyError: If loop not found
            RuntimeError: If required roles not available
        """
        # Get loop metadata (raises KeyError if not found)
        metadata = self.loop_registry.get_loop_metadata(loop_id)

        # Instantiate required roles
        role_instances = {}
        required_roles = set(metadata.primary_roles + metadata.consulted_roles)

        for role_name in required_roles:
            try:
                role_instances[role_name] = self.role_registry.get_role(
                    role_name,
                    provider=self.provider,
                    provider_name=self.provider_name,
                )
            except KeyError:
                # Role not implemented yet - skip it
                pass

        # Create loop context
        project_info = self.workspace.get_project_info()
        loop_context = LoopContext(
            loop_id=loop_id,
            project_id=project_id,
            workspace=self.workspace,
            role_instances=role_instances,
            artifacts=artifacts or [],
            project_metadata=project_info.model_dump(),
            config=config or {},
        )

        # Get loop class and instantiate
        loop_class = self._get_loop_class(loop_id)
        loop_instance = loop_class(loop_context)

        # Execute loop
        result = loop_instance.execute()

        return result

    def execute_goal(
        self,
        goal: str,
        project_id: str,
        project_state: dict[str, Any] | None = None,
        artifacts: list[Artifact] | None = None,
        config: dict[str, Any] | None = None,
    ) -> LoopResult:
        """
        Execute workflow for a given goal (select loop + execute).

        Args:
            goal: User's goal or request
            project_id: Project identifier
            project_state: Current project state
            artifacts: Existing artifacts
            config: Loop configuration

        Returns:
            Loop execution result
        """
        # Select appropriate loop
        loop_id = self.select_loop(goal, project_state, artifacts)

        # Execute the selected loop
        result = self.execute_loop(
            loop_id=loop_id,
            project_id=project_id,
            artifacts=artifacts,
            config=config,
        )

        return result

    def _extract_loop_id(self, output: str) -> str:
        """
        Extract loop ID from showrunner output.

        For now, looks for common patterns like "Selected Loop: loop_id"
        or "**Selected Loop**: loop_id".

        Args:
            output: Showrunner output text

        Returns:
            Extracted loop ID

        Raises:
            RuntimeError: If loop ID cannot be extracted
        """
        # Look for patterns like "Selected Loop: story_spark"
        # or "**Selected Loop**: story_spark"
        patterns = [
            r"Selected Loop:?\s*[*]*\s*([a-z_]+)",
            r"\*\*Selected Loop\*\*:?\s*([a-z_]+)",
            r"Loop ID:?\s*[*]*\s*([a-z_]+)",
            r"loop_id:?\s*[`'\"]*([a-z_]+)[`'\"]*",
        ]

        for pattern in patterns:
            match = re.search(pattern, output, re.IGNORECASE)
            if match:
                loop_id = match.group(1).lower()
                # Verify it's a valid loop
                try:
                    self.loop_registry.get_loop_metadata(loop_id)
                    return loop_id
                except KeyError:
                    continue

        # Fallback: check if any loop_id appears in the output
        for loop_metadata in self.loop_registry.list_loops():
            if loop_metadata.loop_id in output.lower():
                return loop_metadata.loop_id

        raise RuntimeError(
            f"Could not extract loop ID from showrunner output:\n{output}"
        )

    def _get_loop_class(self, loop_id: str) -> type[Loop]:
        """
        Get loop class for the given loop ID.

        Args:
            loop_id: Loop identifier

        Returns:
            Loop class

        Raises:
            KeyError: If loop not implemented
        """
        # Map loop IDs to loop classes
        # For now, only story_spark is implemented
        loop_classes = {
            "story_spark": self._import_story_spark_loop,
        }

        if loop_id not in loop_classes:
            raise KeyError(
                f"Loop '{loop_id}' not yet implemented. "
                f"Available loops: {list(loop_classes.keys())}"
            )

        return loop_classes[loop_id]()

    def _import_story_spark_loop(self) -> type[Loop]:
        """Import and return StorySparkLoop class."""
        from .loops.story_spark import StorySparkLoop

        return StorySparkLoop

    def __repr__(self) -> str:
        """String representation of orchestrator."""
        initialized = "initialized" if self.showrunner else "not initialized"
        return (
            f"Orchestrator({initialized}, "
            f"loops={len(self.loop_registry.list_loops())}, "
            f"roles={len(self.role_registry.list_roles())})"
        )
