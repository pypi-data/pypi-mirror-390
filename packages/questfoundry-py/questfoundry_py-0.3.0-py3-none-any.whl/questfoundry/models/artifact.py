"""Pydantic models for QuestFoundry artifacts"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from ..validators import ValidationResult, validate_artifact


class Artifact(BaseModel):
    """
    Base artifact model for QuestFoundry.

    Artifacts are the core data units in QuestFoundry, representing
    various types of creative content (hooks, scenes, canon, etc.).

    The artifact uses a flexible schema where:
    - `type` identifies the artifact type (e.g., 'hook_card')
    - `data` contains the artifact-specific content (validated against schema)
    - `metadata` contains common fields like id, timestamps, author

    Example:
        >>> artifact = Artifact(
        ...     type="hook_card",
        ...     data={"header": {"short_name": "Test Hook", ...}},
        ...     metadata={"id": "HOOK-001"}
        ... )
        >>> result = artifact.validate_schema()
        >>> if result.is_valid:
        ...     print("Artifact is valid!")
    """

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"type": "hook_card", "data": {}, "metadata": {}}
        }
    )

    type: str = Field(..., description="Artifact type (e.g., 'hook_card')")
    data: dict[str, Any] = Field(default_factory=dict, description="Artifact data")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Artifact metadata"
    )

    # Common metadata accessors

    @property
    def artifact_id(self) -> str | None:
        """Get artifact ID from metadata"""
        return self.metadata.get("id")

    @artifact_id.setter
    def artifact_id(self, value: str) -> None:
        """Set artifact ID in metadata"""
        self.metadata["id"] = value

    @property
    def created(self) -> datetime | None:
        """
        Get creation timestamp from metadata.

        Returns:
            Datetime object if valid timestamp exists, None otherwise
        """
        created = self.metadata.get("created")
        if isinstance(created, str):
            try:
                return datetime.fromisoformat(created)
            except ValueError:
                # Invalid ISO format - return None rather than raise
                return None
        if isinstance(created, datetime):
            return created
        return None

    @created.setter
    def created(self, value: datetime) -> None:
        """Set creation timestamp in metadata"""
        self.metadata["created"] = value.isoformat()

    @property
    def modified(self) -> datetime | None:
        """
        Get modification timestamp from metadata.

        Returns:
            Datetime object if valid timestamp exists, None otherwise
        """
        modified = self.metadata.get("modified")
        if isinstance(modified, str):
            try:
                return datetime.fromisoformat(modified)
            except ValueError:
                # Invalid ISO format - return None rather than raise
                return None
        if isinstance(modified, datetime):
            return modified
        return None

    @modified.setter
    def modified(self, value: datetime) -> None:
        """Set modification timestamp in metadata"""
        self.metadata["modified"] = value.isoformat()

    @property
    def author(self) -> str | None:
        """Get author from metadata"""
        author = self.metadata.get("author")
        if isinstance(author, str):
            return author
        return None

    @author.setter
    def author(self, value: str) -> None:
        """Set author in metadata"""
        self.metadata["author"] = value

    # Validation methods

    def validate_schema(self) -> ValidationResult:
        """
        Validate artifact against its schema.

        Returns:
            ValidationResult with validation status and any errors/warnings
        """
        instance = {"type": self.type, "data": self.data, "metadata": self.metadata}
        return validate_artifact(instance, self.type)

    # Serialization methods

    def to_dict(self) -> dict[str, Any]:
        """
        Convert artifact to dictionary.

        Returns:
            Dictionary representation of the artifact
        """
        return {
            "type": self.type,
            "data": self.data,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Artifact":
        """
        Create artifact from dictionary.

        Args:
            data: Dictionary with type, data, and metadata fields

        Returns:
            New Artifact instance

        Raises:
            ValidationError: If required fields are missing or invalid
        """
        return cls.model_validate(data)


class HookCard(Artifact):
    """
    Hook Card artifact.

    Small, traceable follow-up for new needs or uncertainties.
    Hooks are classified, routed to appropriate loops, and kept player-safe.
    """

    type: str = "hook_card"


class TUBrief(Artifact):
    """
    Thematic Unit Brief artifact.

    Defines a unit of work to be performed in a loop.
    """

    type: str = "tu_brief"


class CanonPack(Artifact):
    """
    Canon Pack artifact.

    Authoritative lore and worldbuilding content.
    """

    type: str = "canon_pack"


class GatecheckReport(Artifact):
    """
    Gatecheck Report artifact.

    Quality validation report from the Gatekeeper role.
    """

    type: str = "gatecheck_report"


class CodexEntry(Artifact):
    """
    Codex Entry artifact.

    Player-facing encyclopedia entry.
    """

    type: str = "codex_entry"


class StyleAddendum(Artifact):
    """
    Style Addendum artifact.

    Style guide additions or modifications.
    """

    type: str = "style_addendum"


class ResearchMemo(Artifact):
    """
    Research Memo artifact.

    Research findings and references.
    """

    type: str = "research_memo"


class Shotlist(Artifact):
    """
    Shotlist artifact.

    Visual composition and scene direction notes.
    """

    type: str = "shotlist"


class Cuelist(Artifact):
    """
    Cuelist artifact.

    Audio cue timing and direction notes.
    """

    type: str = "cuelist"


class ViewLog(Artifact):
    """
    View Log artifact.

    Record of view generation and export operations.
    """

    type: str = "view_log"


class ArtPlan(Artifact):
    """
    Art Plan artifact.

    Planning document for visual art direction.
    """

    type: str = "art_plan"


class ArtManifest(Artifact):
    """
    Art Manifest artifact.

    Inventory of art assets.
    """

    type: str = "art_manifest"


class AudioPlan(Artifact):
    """
    Audio Plan artifact.

    Planning document for audio direction.
    """

    type: str = "audio_plan"


class EditNotes(Artifact):
    """
    Edit Notes artifact.

    Editorial feedback and revision notes.
    """

    type: str = "edit_notes"


class FrontMatter(Artifact):
    """
    Front Matter artifact.

    Book front matter content (title page, copyright, etc.).
    """

    type: str = "front_matter"


class LanguagePack(Artifact):
    """
    Language Pack artifact.

    Translated content for a specific language.
    """

    type: str = "language_pack"


class PNPlaytestNotes(Artifact):
    """
    PN Playtest Notes artifact.

    Player Narrator feedback from playtesting sessions.
    """

    type: str = "pn_playtest_notes"


class ProjectMetadata(Artifact):
    """
    Project Metadata artifact.

    Top-level project configuration and metadata.
    """

    type: str = "project_metadata"


class RegisterMap(Artifact):
    """
    Register Map artifact.

    Language register and tone mapping for characters/scenes.
    """

    type: str = "register_map"


class StyleManifest(Artifact):
    """
    Style Manifest artifact.

    Master style guide inventory.
    """

    type: str = "style_manifest"
