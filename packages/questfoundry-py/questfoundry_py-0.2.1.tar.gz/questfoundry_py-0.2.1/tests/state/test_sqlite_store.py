"""Tests for SQLite state store"""

import tempfile
from pathlib import Path

import pytest

from questfoundry.models.artifact import Artifact
from questfoundry.state import ProjectInfo, SnapshotInfo, SQLiteStore, TUState


@pytest.fixture
def temp_db():
    """Create a temporary database file"""
    with tempfile.NamedTemporaryFile(suffix=".qfproj", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def store(temp_db):
    """Create and initialize a SQLiteStore"""
    store = SQLiteStore(temp_db)
    store.init_database()
    yield store
    store.close()


def test_init_database(temp_db):
    """Test database initialization"""
    store = SQLiteStore(temp_db)
    store.init_database()

    # Should have schema version
    version = store.get_schema_version()
    assert version == 1

    store.close()


def test_project_info_crud(store):
    """Test project info save and retrieve"""
    # Save project info
    info = ProjectInfo(
        name="Test Project",
        description="A test project",
        version="1.0.0",
        author="test_user",
    )
    store.save_project_info(info)

    # Retrieve and verify
    retrieved = store.get_project_info()
    assert retrieved.name == "Test Project"
    assert retrieved.description == "A test project"
    assert retrieved.version == "1.0.0"
    assert retrieved.author == "test_user"


def test_project_info_not_found(store):
    """Test get_project_info raises when no project exists"""
    # Fresh database with no project info
    with pytest.raises(FileNotFoundError, match="Project metadata not found"):
        store.get_project_info()


def test_artifact_save_and_retrieve(store):
    """Test artifact save and retrieval"""
    # Create artifact with ID in metadata
    artifact = Artifact(
        type="hook_card",
        data={"name": "Test Hook", "trigger": "scene_start"},
        metadata={"id": "HOOK-001", "author": "alice"},
    )

    # Save
    store.save_artifact(artifact)

    # Retrieve
    retrieved = store.get_artifact("HOOK-001")
    assert retrieved is not None
    assert retrieved.type == "hook_card"
    assert retrieved.data["name"] == "Test Hook"
    assert retrieved.metadata["id"] == "HOOK-001"


def test_artifact_without_id_fails(store):
    """Test that saving artifact without ID raises ValueError"""
    artifact = Artifact(
        type="hook_card",
        data={"name": "Test"},
        metadata={},  # No ID!
    )

    with pytest.raises(ValueError, match="must have an 'id'"):
        store.save_artifact(artifact)


def test_get_nonexistent_artifact(store):
    """Test retrieving non-existent artifact returns None"""
    result = store.get_artifact("NONEXISTENT")
    assert result is None


def test_list_artifacts_by_type(store):
    """Test listing artifacts filtered by type"""
    # Save multiple artifacts
    hook1 = Artifact(type="hook_card", data={}, metadata={"id": "HOOK-001"})
    hook2 = Artifact(type="hook_card", data={}, metadata={"id": "HOOK-002"})
    canon = Artifact(type="canon", data={}, metadata={"id": "CANON-001"})

    store.save_artifact(hook1)
    store.save_artifact(hook2)
    store.save_artifact(canon)

    # List hooks only
    hooks = store.list_artifacts("hook_card")
    assert len(hooks) == 2
    assert all(a.type == "hook_card" for a in hooks)

    # List all
    all_artifacts = store.list_artifacts()
    assert len(all_artifacts) == 3


def test_list_artifacts_with_filters(store):
    """Test listing artifacts with JSON filters"""
    # Save artifacts with different statuses
    hook1 = Artifact(
        type="hook_card",
        data={"status": "proposed"},
        metadata={"id": "HOOK-001"},
    )
    hook2 = Artifact(
        type="hook_card",
        data={"status": "approved"},
        metadata={"id": "HOOK-002"},
    )

    store.save_artifact(hook1)
    store.save_artifact(hook2)

    # Filter by status
    proposed = store.list_artifacts("hook_card", {"status": "proposed"})
    assert len(proposed) == 1
    assert proposed[0].data["status"] == "proposed"


def test_delete_artifact(store):
    """Test artifact deletion"""
    artifact = Artifact(type="hook_card", data={}, metadata={"id": "HOOK-001"})
    store.save_artifact(artifact)

    # Delete
    deleted = store.delete_artifact("HOOK-001")
    assert deleted is True

    # Verify gone
    retrieved = store.get_artifact("HOOK-001")
    assert retrieved is None

    # Delete non-existent returns False
    deleted_again = store.delete_artifact("HOOK-001")
    assert deleted_again is False


def test_tu_save_and_retrieve(store):
    """Test TU state save and retrieval"""
    tu = TUState(
        tu_id="TU-2024-01-15-SR01",
        status="open",
        data={"header": {"short_name": "Test TU"}},
    )

    store.save_tu(tu)

    # Retrieve
    retrieved = store.get_tu("TU-2024-01-15-SR01")
    assert retrieved is not None
    assert retrieved.tu_id == "TU-2024-01-15-SR01"
    assert retrieved.status == "open"
    assert retrieved.data["header"]["short_name"] == "Test TU"


def test_get_nonexistent_tu(store):
    """Test retrieving non-existent TU returns None"""
    result = store.get_tu("NONEXISTENT")
    assert result is None


def test_list_tus_with_filters(store):
    """Test listing TUs with filters"""
    tu1 = TUState(tu_id="TU-001", status="open", data={})
    tu2 = TUState(tu_id="TU-002", status="completed", data={})
    tu3 = TUState(tu_id="TU-003", status="open", data={})

    store.save_tu(tu1)
    store.save_tu(tu2)
    store.save_tu(tu3)

    # Filter by status
    open_tus = store.list_tus({"status": "open"})
    assert len(open_tus) == 2
    assert all(tu.status == "open" for tu in open_tus)

    # List all
    all_tus = store.list_tus()
    assert len(all_tus) == 3


def test_snapshot_save_and_retrieve(store):
    """Test snapshot save and retrieval"""
    snapshot = SnapshotInfo(
        snapshot_id="SNAP-001",
        tu_id="TU-2024-01-15-SR01",
        description="Initial snapshot",
    )

    store.save_snapshot(snapshot)

    # Retrieve
    retrieved = store.get_snapshot("SNAP-001")
    assert retrieved is not None
    assert retrieved.snapshot_id == "SNAP-001"
    assert retrieved.tu_id == "TU-2024-01-15-SR01"
    assert retrieved.description == "Initial snapshot"


def test_get_nonexistent_snapshot(store):
    """Test retrieving non-existent snapshot returns None"""
    result = store.get_snapshot("NONEXISTENT")
    assert result is None


def test_list_snapshots_by_tu(store):
    """Test listing snapshots filtered by TU"""
    snap1 = SnapshotInfo(
        snapshot_id="SNAP-001", tu_id="TU-001", description="Snap 1"
    )
    snap2 = SnapshotInfo(
        snapshot_id="SNAP-002", tu_id="TU-001", description="Snap 2"
    )
    snap3 = SnapshotInfo(
        snapshot_id="SNAP-003", tu_id="TU-002", description="Snap 3"
    )

    store.save_snapshot(snap1)
    store.save_snapshot(snap2)
    store.save_snapshot(snap3)

    # Filter by TU
    tu1_snaps = store.list_snapshots({"tu_id": "TU-001"})
    assert len(tu1_snaps) == 2
    assert all(s.tu_id == "TU-001" for s in tu1_snaps)

    # List all
    all_snaps = store.list_snapshots()
    assert len(all_snaps) == 3


def test_tu_with_snapshot_reference(store):
    """Test TU with snapshot foreign key"""
    # Create snapshot first
    snapshot = SnapshotInfo(
        snapshot_id="SNAP-001", tu_id="TU-001", description="Test"
    )
    store.save_snapshot(snapshot)

    # Create TU referencing snapshot
    tu = TUState(
        tu_id="TU-001", status="in_progress", snapshot_id="SNAP-001", data={}
    )
    store.save_tu(tu)

    # Retrieve and verify
    retrieved = store.get_tu("TU-001")
    assert retrieved.snapshot_id == "SNAP-001"


def test_context_manager(temp_db):
    """Test SQLiteStore as context manager"""
    store = SQLiteStore(temp_db)
    store.init_database()

    with store as s:
        info = ProjectInfo(name="Test Project")
        s.save_project_info(info)

    # Connection should be closed after context
    assert store._conn is None  # noqa: SLF001


def test_artifact_update(store):
    """Test updating an existing artifact"""
    # Create initial artifact
    artifact = Artifact(
        type="hook_card",
        data={"version": 1},
        metadata={"id": "HOOK-001"},
    )
    store.save_artifact(artifact)

    # Update it
    updated = Artifact(
        type="hook_card",
        data={"version": 2},
        metadata={"id": "HOOK-001"},
    )
    store.save_artifact(updated)

    # Retrieve and verify it was updated
    retrieved = store.get_artifact("HOOK-001")
    assert retrieved.data["version"] == 2


def test_transaction_rollback(temp_db):
    """Test that each operation commits independently"""
    store = SQLiteStore(temp_db)
    store.init_database()

    # Save artifact (commits automatically)
    artifact = Artifact(
        type="hook_card",
        data={},
        metadata={"id": "HOOK-001"},
    )
    store.save_artifact(artifact)

    # Artifact should exist (auto-committed)
    retrieved = store.get_artifact("HOOK-001")
    assert retrieved is not None

    store.close()


def test_modified_timestamp_updates(store):
    """Test that modified timestamp updates on save"""
    # Save TU
    tu = TUState(tu_id="TU-001", status="open", data={})
    store.save_tu(tu)

    original_modified = store.get_tu("TU-001").modified

    # Update after a moment
    import time

    time.sleep(0.01)
    tu.status = "in_progress"
    store.save_tu(tu)

    # Modified should be newer
    updated_modified = store.get_tu("TU-001").modified
    assert updated_modified > original_modified


def test_list_artifacts_invalid_filter_key(store):
    """Test that invalid filter keys raise ValueError"""
    # Save an artifact
    artifact = Artifact(type="hook_card", data={}, metadata={"id": "HOOK-001"})
    store.save_artifact(artifact)

    # Try to filter with invalid key (SQL injection attempt)
    with pytest.raises(ValueError, match="Invalid filter key"):
        store.list_artifacts(
            "hook_card", {"malicious'; DROP TABLE artifacts--": "value"}
        )


def test_snapshot_immutability(store):
    """Test that snapshots cannot be overwritten"""
    # Save initial snapshot
    snapshot = SnapshotInfo(
        snapshot_id="SNAP-001", tu_id="TU-001", description="Initial"
    )
    store.save_snapshot(snapshot)

    # Try to save again with same ID
    snapshot2 = SnapshotInfo(
        snapshot_id="SNAP-001", tu_id="TU-001", description="Modified"
    )

    with pytest.raises(ValueError, match="already exists.*immutable"):
        store.save_snapshot(snapshot2)

    # Verify original is unchanged
    retrieved = store.get_snapshot("SNAP-001")
    assert retrieved.description == "Initial"


def test_artifact_created_timestamp_preserved(store):
    """Test that created timestamp is preserved on update"""
    import time

    # Create artifact
    artifact = Artifact(
        type="hook_card",
        data={"version": 1},
        metadata={"id": "HOOK-001"},
    )
    store.save_artifact(artifact)

    # Get the created timestamp from metadata
    retrieved1 = store.get_artifact("HOOK-001")
    original_created = retrieved1.metadata.get("created")
    assert original_created is not None

    # Wait and update
    time.sleep(0.01)
    artifact.data["version"] = 2
    store.save_artifact(artifact)

    # Created timestamp should be preserved in metadata
    retrieved2 = store.get_artifact("HOOK-001")
    assert retrieved2.metadata.get("created") == original_created
