"""Audio Producer role implementation."""

from typing import Any

from .base import Role, RoleContext, RoleResult


class AudioProducer(Role):
    """
    Audio Producer: Create audio assets that match narrative intent.

    The Audio Producer creates audio cues based on Audio Director's plans,
    mixes and exports masters, and maintains reproducibility logs when promised.

    Key responsibilities:
    - Create/arrange/mix audio assets from audio plans
    - Export masters and stems when relevant
    - Record reproducibility notes (DAW, plugins, settings)
    - Provide text equivalents and captions
    - Maintain audio consistency across assets
    - Manage normalization and loudness safety
    """

    @property
    def role_name(self) -> str:
        """Role identifier matching spec/01-roles/briefs/audio_producer.md"""
        return "audio_producer"

    @property
    def display_name(self) -> str:
        """Human-readable role name"""
        return "Audio Producer"

    def execute_task(self, context: RoleContext) -> RoleResult:
        """
        Execute an audio producer task.

        Supported tasks:
        - 'create_asset': Produce audio from plan
        - 'mix_stems': Combine audio elements
        - 'generate_reproducibility_log': Record production parameters
        - 'normalize_loudness': Apply loudness standards
        - 'generate_audio': Generate audio (alias for create_asset)

        Args:
            context: Execution context

        Returns:
            Result with audio artifacts and metadata
        """
        task = context.task.lower()

        if task == "create_asset":
            return self._create_asset(context)
        elif task == "mix_stems":
            return self._mix_stems(context)
        elif task == "generate_reproducibility_log":
            return self._generate_reproducibility_log(context)
        elif task == "normalize_loudness":
            return self._normalize_loudness(context)
        # New tasks for loops
        elif task == "generate_audio":
            return self._create_asset(context)
        else:
            return RoleResult(
                success=False,
                output="",
                error=f"Unknown task: {task}",
            )

    def _create_asset(self, context: RoleContext) -> RoleResult:
        """Produce audio from plan."""
        system_prompt = self.build_system_prompt(context)

        audio_plan = context.additional_context.get("audio_plan", {})

        user_prompt = f"""# Task: Create Audio Asset

{self.format_artifacts(context.artifacts)}

## Audio Plan
{self._format_dict(audio_plan)}

Create audio asset following the plan's:
- Type (ambience, foley, stinger, VO)
- Intensity curve and placement
- Motif ties
- Safety requirements (no sudden peaks)

Note: In a real implementation, this would interface with audio generation/DAW.
For now, provide a detailed production specification.

Respond in JSON format:
```json
{{
  "asset_spec": {{
    "description": "Production approach",
    "technical_params": {{
      "sample_rate": "44100|48000",
      "bit_depth": "16|24",
      "duration": "seconds",
      "format": "wav|mp3|ogg"
    }},
    "processing": ["reverb", "eq", "compression"],
    "loudness_target": "LUFS value"
  }},
  "text_equivalent": "[accessibility caption]",
  "reproducibility_achievable": true|false
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
                    "content_type": "audio_asset",
                    "asset_spec": data.get("asset_spec", {}),
                    "text_equivalent": data.get("text_equivalent", ""),
                },
            )

        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error creating asset: {e}",
            )

    def _mix_stems(self, context: RoleContext) -> RoleResult:
        """Combine audio elements."""
        system_prompt = self.build_system_prompt(context)

        stems = context.additional_context.get("stems", [])
        mix_intent = context.additional_context.get("mix_intent", {})

        user_prompt = f"""# Task: Mix Audio Stems

{self.format_artifacts(context.artifacts)}

## Stems
{self._format_list([f"{s.get('name')}: {s.get('description')}" for s in stems])}

## Mix Intent
{self._format_dict(mix_intent)}

Create mix specification:
- Balance levels between stems
- Apply processing chain
- Maintain intensity curve
- Ensure safety (no clipping, reasonable loudness)

Respond in JSON format with mix specification.
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
                    "content_type": "mix_spec",
                    "mix": data,
                },
            )

        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error mixing stems: {e}",
            )

    def _generate_reproducibility_log(self, context: RoleContext) -> RoleResult:
        """Record production parameters."""
        system_prompt = self.build_system_prompt(context)

        asset_info = context.additional_context.get("asset_info", {})

        user_prompt = f"""# Task: Generate Reproducibility Log

{self.format_artifacts(context.artifacts)}

## Asset Information
{self._format_dict(asset_info)}

Create reproducibility log with:
- DAW name and version
- Plugin list with versions
- Session sample rate and bit depth
- Key settings or presets used
- Normalization target (LUFS)
- Export settings
- Any manual steps taken

Respond in JSON format:
```json
{{
  "reproducibility_log": {{
    "daw": "name and version",
    "plugins": [
      {{"name": "plugin", "version": "x.y", "settings": {{}}}}
    ],
    "session_specs": {{
      "sample_rate": "Hz",
      "bit_depth": "bits"
    }},
    "normalization": "LUFS target",
    "export_settings": {{}},
    "reproducible": true|false,
    "notes": "Any caveats or manual steps"
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
                    "content_type": "reproducibility_log",
                    "log": data.get("reproducibility_log", {}),
                },
            )

        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error generating reproducibility log: {e}",
            )

    def _normalize_loudness(self, context: RoleContext) -> RoleResult:
        """Apply loudness standards."""
        system_prompt = self.build_system_prompt(context)

        asset_info = context.additional_context.get("asset_info", {})
        target_lufs = context.additional_context.get("target_lufs", -16)

        user_prompt = f"""# Task: Normalize Loudness

{self.format_artifacts(context.artifacts)}

## Asset Information
{self._format_dict(asset_info)}

## Target LUFS
{target_lufs}

Apply loudness normalization:
- Measure current loudness
- Calculate gain adjustment
- Apply normalization
- Verify no clipping
- Document final loudness

Respond in JSON format:
```json
{{
  "normalization": {{
    "current_lufs": "measured value",
    "target_lufs": "{target_lufs}",
    "gain_adjustment": "dB",
    "final_lufs": "achieved value",
    "peak_level": "dBFS",
    "clipping_detected": false
  }}
}}
```
"""

        try:
            response = self._call_llm(
                system_prompt, user_prompt, max_tokens=800
            )

            data = self._parse_json_from_response(response)

            return RoleResult(
                success=True,
                output=response,
                metadata={
                    "content_type": "loudness_normalization",
                    "normalization": data.get("normalization", {}),
                },
            )

        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error normalizing loudness: {e}",
            )

    def _format_dict(self, d: dict[str, Any]) -> str:
        """Format dictionary as bullet list."""
        if not d:
            return "(empty)"
        return "\n".join(f"- {k}: {v}" for k, v in d.items())

    def _format_list(self, items: list[str]) -> str:
        """Format list as bullet list."""
        if not items:
            return "(none)"
        return "\n".join(f"- {item}" for item in items)
