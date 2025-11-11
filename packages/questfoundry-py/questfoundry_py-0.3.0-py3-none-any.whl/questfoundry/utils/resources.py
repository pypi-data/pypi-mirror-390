"""Resource loading utilities for schemas and prompts"""

import json
from pathlib import Path
from typing import Any


def _validate_safe_path(base_dir: Path, target_path: Path, resource_type: str) -> None:
    """
    Validate that target path is within base directory (prevent path traversal).

    Args:
        base_dir: Base directory that should contain the target
        target_path: Path to validate
        resource_type: Type of resource for error message

    Raises:
        ValueError: If path traversal is detected
    """
    try:
        # resolve() follows symlinks and normalizes the path
        resolved_target = target_path.resolve()
        resolved_base = base_dir.resolve()

        # Check if target is relative to base
        resolved_target.relative_to(resolved_base)
    except (ValueError, RuntimeError):
        raise ValueError(
            f"Invalid {resource_type} path: path traversal detected. "
            f"Path must be within the resources directory."
        )


def get_schema(schema_name: str) -> dict[str, Any]:
    """
    Load a schema from bundled resources.

    Args:
        schema_name: Name of the schema (without .schema.json extension)

    Returns:
        Schema dictionary

    Raises:
        FileNotFoundError: If schema doesn't exist
        ValueError: If path traversal is detected
    """
    resource_dir = Path(__file__).parent.parent / "resources" / "schemas"
    schema_file = resource_dir / f"{schema_name}.schema.json"

    # Validate path to prevent directory traversal
    _validate_safe_path(resource_dir, schema_file, "schema")

    if not schema_file.exists():
        raise FileNotFoundError(f"Schema not found: {schema_name}")

    with open(schema_file) as f:
        schema: dict[str, Any] = json.load(f)
        return schema


def get_prompt(role_name: str) -> str:
    """
    Load a prompt from bundled resources.

    Args:
        role_name: Name of the role

    Returns:
        Prompt text

    Raises:
        FileNotFoundError: If prompt doesn't exist
        ValueError: If path traversal is detected
    """
    resource_dir = Path(__file__).parent.parent / "resources" / "prompts"
    prompt_file = resource_dir / role_name / "system_prompt.md"

    # Validate path to prevent directory traversal
    _validate_safe_path(resource_dir, prompt_file, "prompt")

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt not found: {role_name}")

    return prompt_file.read_text()

def list_schemas() -> list[str]:
    """List available schemas"""
    resource_dir = Path(__file__).parent.parent / "resources" / "schemas"
    return [f.stem for f in resource_dir.glob("*.schema.json")]

def list_prompts() -> list[str]:
    """List available prompt roles"""
    resource_dir = Path(__file__).parent.parent / "resources" / "prompts"
    return [d.name for d in resource_dir.iterdir() if d.is_dir()]
