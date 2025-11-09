"""Illustrator role implementation."""

from typing import Any

from .base import Role, RoleContext, RoleResult


class Illustrator(Role):
    """
    Illustrator: Produce visual assets that match narrative intent.

    The Illustrator creates illustrations based on Art Director's plans,
    iterates to match composition intent, and maintains determinism logs
    for reproducibility when promised.

    Key responsibilities:
    - Produce renders from art plans
    - Iterate to match composition intent
    - Record determinism parameters (seed, model, settings)
    - Generate alt text for accessibility
    - Maintain visual consistency across assets
    """

    @property
    def role_name(self) -> str:
        """Role identifier matching spec/01-roles/briefs/illustrator.md"""
        return "illustrator"

    @property
    def display_name(self) -> str:
        """Human-readable role name"""
        return "Illustrator"

    def execute_task(self, context: RoleContext) -> RoleResult:
        """
        Execute an illustrator task.

        Supported tasks:
        - 'create_render': Produce illustration from art plan
        - 'iterate_render': Refine illustration based on feedback
        - 'generate_determinism_log': Record reproduction parameters
        - 'create_variants': Generate multiple versions for selection
        - 'generate_image': Generate image (alias for create_render)

        Args:
            context: Execution context

        Returns:
            Result with render artifacts and metadata
        """
        task = context.task.lower()

        if task == "create_render":
            return self._create_render(context)
        elif task == "iterate_render":
            return self._iterate_render(context)
        elif task == "generate_determinism_log":
            return self._generate_determinism_log(context)
        elif task == "create_variants":
            return self._create_variants(context)
        # New tasks for loops
        elif task == "generate_image":
            return self._create_render(context)
        else:
            return RoleResult(
                success=False,
                output="",
                error=f"Unknown task: {task}",
            )

    def _create_render(self, context: RoleContext) -> RoleResult:
        """Produce illustration from art plan."""
        system_prompt = self.build_system_prompt(context)

        art_plan = context.additional_context.get("art_plan", {})

        user_prompt = f"""# Task: Create Render

{self.format_artifacts(context.artifacts)}

## Art Plan
{self._format_dict(art_plan)}

Produce a candidate render following the art plan's:
- Composition intent (framing, focal points, motion)
- Constraints (aspect, palette, negative constraints)
- Style alignment with house motifs

Note: In a real implementation, this would interface with image generation.
For now, provide a detailed rendering specification.

Respond in JSON format:
```json
{{
  "render_spec": {{
    "composition": "Detailed composition description",
    "style_notes": "How house style is reflected",
    "technical_params": {{
      "seed": "deterministic seed if applicable",
      "aspect_ratio": "ratio",
      "palette": ["color1", "color2"]
    }}
  }},
  "alt_text": "Accessibility description",
  "determinism_achievable": true|false
}}
```
"""

        try:
            response = self._call_llm(
                system_prompt, user_prompt, max_tokens=1500
            )

            data = self._parse_json_from_response(response)

            return RoleResult(
                success=True,
                output=response,
                metadata={
                    "content_type": "render",
                    "render_spec": data.get("render_spec", {}),
                    "alt_text": data.get("alt_text", ""),
                },
            )

        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error creating render: {e}",
            )

    def _iterate_render(self, context: RoleContext) -> RoleResult:
        """Refine illustration based on feedback."""
        system_prompt = self.build_system_prompt(context)

        current_render = context.additional_context.get("current_render", {})
        feedback = context.additional_context.get("feedback", {})

        user_prompt = f"""# Task: Iterate Render

{self.format_artifacts(context.artifacts)}

## Current Render
{self._format_dict(current_render)}

## Feedback
{self._format_dict(feedback)}

Refine the render to address feedback while maintaining:
- Core composition intent
- Style consistency
- Technical quality

Respond in JSON format with updated render_spec.
"""

        try:
            response = self._call_llm(
                system_prompt, user_prompt, max_tokens=1500
            )

            data = self._parse_json_from_response(response)

            return RoleResult(
                success=True,
                output=response,
                metadata={
                    "content_type": "render_iteration",
                    "updated_render": data,
                },
            )

        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error iterating render: {e}",
            )

    def _generate_determinism_log(self, context: RoleContext) -> RoleResult:
        """Record reproduction parameters."""
        system_prompt = self.build_system_prompt(context)

        render_info = context.additional_context.get("render_info", {})

        user_prompt = f"""# Task: Generate Determinism Log

{self.format_artifacts(context.artifacts)}

## Render Information
{self._format_dict(render_info)}

Create determinism log with:
- Seed value (if applicable)
- Model name and version
- Prompt/version used
- Aspect ratio
- Generation parameters (steps, CFG, sampler)
- Post-processing chain
- Any other reproduction requirements

Respond in JSON format:
```json
{{
  "determinism_log": {{
    "seed": "value or null",
    "model": "name and version",
    "prompt_version": "identifier",
    "technical_params": {{}},
    "post_processing": [],
    "reproducible": true|false,
    "notes": "Any caveats"
  }}
}}
```
"""

        try:
            response = self._call_llm(
                system_prompt, user_prompt, max_tokens=1000
            )

            data = self._parse_json_from_response(response)

            return RoleResult(
                success=True,
                output=response,
                metadata={
                    "content_type": "determinism_log",
                    "log": data.get("determinism_log", {}),
                },
            )

        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error generating determinism log: {e}",
            )

    def _create_variants(self, context: RoleContext) -> RoleResult:
        """Generate multiple versions for selection."""
        system_prompt = self.build_system_prompt(context)

        art_plan = context.additional_context.get("art_plan", {})
        variant_count = context.additional_context.get("variant_count", 3)

        user_prompt = f"""# Task: Create Render Variants

{self.format_artifacts(context.artifacts)}

## Art Plan
{self._format_dict(art_plan)}

## Variant Count
{variant_count}

Generate {variant_count} variants exploring different:
- Framing angles
- Lighting moods
- Color treatments

All must satisfy the art plan's constraints and intent.

Respond in JSON format with array of variant specs.
"""

        try:
            response = self._call_llm(
                system_prompt, user_prompt, max_tokens=2000
            )

            data = self._parse_json_from_response(response)

            return RoleResult(
                success=True,
                output=response,
                metadata={
                    "content_type": "render_variants",
                    "variants": data.get("variants", []),
                    "count": len(data.get("variants", [])),
                },
            )

        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error creating variants: {e}",
            )

    def _format_dict(self, d: dict[str, Any]) -> str:
        """Format dictionary as bullet list."""
        if not d:
            return "(empty)"
        return "\n".join(f"- {k}: {v}" for k, v in d.items())
