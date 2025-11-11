"""Unified workspace manager for hot and cold storage"""

from pathlib import Path
from typing import Any

from ..models.artifact import Artifact
from .file_store import FileStore
from .sqlite_store import SQLiteStore
from .types import ProjectInfo, SnapshotInfo, TUState


class WorkspaceManager:
    """
    Unified manager for QuestFoundry workspace.

    Manages both hot workspace (file-based, .questfoundry/hot/) and
    cold storage (SQLite, .qfproj file) with methods to promote artifacts
    between hot and cold storage.

    Directory structure:
        project_dir/
            .questfoundry/
                hot/
                    hooks/
                    canon/
                    tus/
                    snapshots/
                metadata.json
            project.qfproj

    Example:
        >>> ws = WorkspaceManager("/path/to/project")
        >>> ws.init_workspace(name="My Project")
        >>> artifact = Artifact(...)
        >>> ws.save_hot_artifact(artifact)
        >>> ws.promote_to_cold("HOOK-001")
    """

    def __init__(self, project_dir: str | Path):
        """
        Initialize workspace manager.

        Args:
            project_dir: Path to project directory
        """
        self.project_dir = Path(project_dir)
        self.hot_dir = self.project_dir / ".questfoundry"
        self.cold_file = self.project_dir / "project.qfproj"

        # Initialize stores
        self.hot_store = FileStore(self.hot_dir)
        self.cold_store = SQLiteStore(self.cold_file)

    def init_workspace(
        self,
        name: str,
        description: str = "",
        version: str = "1.0.0",
        author: str | None = None,
    ) -> None:
        """
        Initialize a new workspace with hot and cold storage.

        Creates directory structure and initializes both stores with
        project metadata.

        Args:
            name: Project name
            description: Project description
            version: Project version
            author: Project author
        """
        # Initialize cold storage database
        self.cold_store.init_database()

        # Create project info
        info = ProjectInfo(
            name=name,
            description=description,
            version=version,
            author=author,
        )

        # Save to both stores
        self.hot_store.save_project_info(info)
        self.cold_store.save_project_info(info)

    def get_project_info(self, source: str = "hot") -> ProjectInfo:
        """
        Get project information.

        Args:
            source: Storage source ("hot" or "cold")

        Returns:
            ProjectInfo object

        Raises:
            ValueError: If source is invalid
            FileNotFoundError: If project metadata not found
        """
        if source == "hot":
            return self.hot_store.get_project_info()
        elif source == "cold":
            return self.cold_store.get_project_info()
        else:
            raise ValueError(f"Invalid source: {source}. Must be 'hot' or 'cold'")

    def save_project_info(self, info: ProjectInfo, target: str = "both") -> None:
        """
        Save project information.

        Args:
            info: ProjectInfo to save
            target: Where to save ("hot", "cold", or "both")

        Raises:
            ValueError: If target is invalid
        """
        # Validate target first
        if target not in ("hot", "cold", "both"):
            raise ValueError(
                f"Invalid target: {target}. Must be 'hot', 'cold', or 'both'"
            )

        if target in ("hot", "both"):
            self.hot_store.save_project_info(info)
        if target in ("cold", "both"):
            self.cold_store.save_project_info(info)

    # Hot workspace artifact operations

    def save_hot_artifact(self, artifact: Artifact) -> None:
        """Save artifact to hot workspace"""
        self.hot_store.save_artifact(artifact)

    def get_hot_artifact(self, artifact_id: str) -> Artifact | None:
        """Get artifact from hot workspace"""
        return self.hot_store.get_artifact(artifact_id)

    def list_hot_artifacts(
        self,
        artifact_type: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[Artifact]:
        """List artifacts in hot workspace"""
        return self.hot_store.list_artifacts(artifact_type, filters)

    def delete_hot_artifact(self, artifact_id: str) -> bool:
        """Delete artifact from hot workspace"""
        return self.hot_store.delete_artifact(artifact_id)

    # Cold storage artifact operations

    def save_cold_artifact(self, artifact: Artifact) -> None:
        """Save artifact to cold storage"""
        self.cold_store.save_artifact(artifact)

    def get_cold_artifact(self, artifact_id: str) -> Artifact | None:
        """Get artifact from cold storage"""
        return self.cold_store.get_artifact(artifact_id)

    def list_cold_artifacts(
        self,
        artifact_type: str | None = None,
        filters: dict[str, Any] | None = None,
    ) -> list[Artifact]:
        """List artifacts in cold storage"""
        return self.cold_store.list_artifacts(artifact_type, filters)

    def delete_cold_artifact(self, artifact_id: str) -> bool:
        """Delete artifact from cold storage"""
        return self.cold_store.delete_artifact(artifact_id)

    # Promotion operations

    def promote_to_cold(self, artifact_id: str, delete_hot: bool = True) -> bool:
        """
        Promote artifact from hot workspace to cold storage.

        Args:
            artifact_id: ID of artifact to promote
            delete_hot: Whether to delete from hot workspace after promotion

        Returns:
            True if promotion succeeded, False if artifact not found
        """
        # Get from hot
        artifact = self.hot_store.get_artifact(artifact_id)
        if artifact is None:
            return False

        # Save to cold
        self.cold_store.save_artifact(artifact)

        # Optionally delete from hot
        if delete_hot:
            self.hot_store.delete_artifact(artifact_id)

        return True

    def demote_to_hot(self, artifact_id: str, delete_cold: bool = False) -> bool:
        """
        Demote artifact from cold storage to hot workspace.

        Args:
            artifact_id: ID of artifact to demote
            delete_cold: Whether to delete from cold storage after demotion

        Returns:
            True if demotion succeeded, False if artifact not found
        """
        # Get from cold
        artifact = self.cold_store.get_artifact(artifact_id)
        if artifact is None:
            return False

        # Save to hot
        self.hot_store.save_artifact(artifact)

        # Optionally delete from cold
        if delete_cold:
            self.cold_store.delete_artifact(artifact_id)

        return True

    # TU operations (hot workspace only)

    def save_tu(self, tu: TUState) -> None:
        """Save TU state to hot workspace"""
        self.hot_store.save_tu(tu)

    def get_tu(self, tu_id: str) -> TUState | None:
        """Get TU state from hot workspace"""
        return self.hot_store.get_tu(tu_id)

    def list_tus(self, filters: dict[str, Any] | None = None) -> list[TUState]:
        """List TUs in hot workspace"""
        return self.hot_store.list_tus(filters)

    # Snapshot operations

    def save_snapshot(self, snapshot: SnapshotInfo, target: str = "both") -> None:
        """
        Save snapshot metadata.

        Args:
            snapshot: SnapshotInfo to save
            target: Where to save ("hot", "cold", or "both")

        Raises:
            ValueError: If target is invalid or snapshot already exists
        """
        # Validate target first
        if target not in ("hot", "cold", "both"):
            raise ValueError(
                f"Invalid target: {target}. Must be 'hot', 'cold', or 'both'"
            )

        if target in ("hot", "both"):
            self.hot_store.save_snapshot(snapshot)
        if target in ("cold", "both"):
            self.cold_store.save_snapshot(snapshot)

    def get_snapshot(self, snapshot_id: str, source: str = "hot") -> (
        SnapshotInfo | None
    ):
        """
        Get snapshot metadata.

        Args:
            snapshot_id: Snapshot ID
            source: Storage source ("hot" or "cold")

        Returns:
            SnapshotInfo or None if not found

        Raises:
            ValueError: If source is invalid
        """
        if source == "hot":
            return self.hot_store.get_snapshot(snapshot_id)
        elif source == "cold":
            return self.cold_store.get_snapshot(snapshot_id)
        else:
            raise ValueError(f"Invalid source: {source}. Must be 'hot' or 'cold'")

    def list_snapshots(
        self, filters: dict[str, Any] | None = None, source: str = "hot"
    ) -> list[SnapshotInfo]:
        """
        List snapshots.

        Args:
            filters: Optional filters (e.g., {"tu_id": "TU-001"})
            source: Storage source ("hot" or "cold")

        Returns:
            List of SnapshotInfo objects

        Raises:
            ValueError: If source is invalid
        """
        if source == "hot":
            return self.hot_store.list_snapshots(filters)
        elif source == "cold":
            return self.cold_store.list_snapshots(filters)
        else:
            raise ValueError(f"Invalid source: {source}. Must be 'hot' or 'cold'")

    def close(self) -> None:
        """Close database connections"""
        self.cold_store.close()

    def __enter__(self) -> "WorkspaceManager":
        """Context manager entry"""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit"""
        self.close()
