"""Gatekeeper role implementation."""

import json

from .base import Role, RoleContext, RoleResult


class Gatekeeper(Role):
    """
    Gatekeeper: Quality validation specialist.

    The Gatekeeper checks artifacts against the 8 quality bars,
    protecting player surfaces while unblocking creators with specific,
    actionable feedback. They focus on lightweight, targeted checks
    rather than exhaustive reviews.

    Key responsibilities:
    - Validate artifacts against quality bars
    - Provide specific, actionable feedback
    - Block merges only on failing bars
    - Protect player-neutral boundaries
    - Enable rapid iteration with pre-gate checks
    """

    @property
    def role_name(self) -> str:
        """Role identifier matching spec/01-roles/briefs/gatekeeper.md"""
        return "gatekeeper"

    @property
    def display_name(self) -> str:
        """Human-readable role name"""
        return "Gatekeeper"

    def execute_task(self, context: RoleContext) -> RoleResult:
        """
        Execute a gatekeeper task.

        Supported tasks:
        - 'pre_gate': Quick check for likely issues
        - 'gate_check': Full quality bar validation
        - 'validate_bar': Check specific quality bar
        - 'export_check': Validate export/view formatting
        - 'evaluate_quality_bars': Evaluate all quality bars (alias for gate_check)
        - 'collect_findings': Collect quality findings (delegates to gate_check)
        - 'triage_blockers': Triage findings by severity (delegates to gate_check)
        - 'create_gatecheck_report': Create comprehensive report
          (delegates to gate_check)

        Args:
            context: Execution context

        Returns:
            Result with validation report
        """
        task = context.task.lower()

        if task == "pre_gate":
            return self._pre_gate(context)
        elif task == "gate_check":
            return self._gate_check(context)
        elif task == "validate_bar":
            return self._validate_bar(context)
        elif task == "export_check":
            return self._export_check(context)
        # New tasks for gatecheck loop
        elif task == "evaluate_quality_bars":
            return self._gate_check(context)
        elif task == "collect_findings":
            return self._gate_check(context)
        elif task == "triage_blockers":
            return self._gate_check(context)
        elif task == "create_gatecheck_report":
            return self._gate_check(context)
        # New tasks for post_mortem loop
        elif task == "final_validation":
            return self._gate_check(context)
        elif task == "create_post_mortem_report":
            return self._gate_check(context)
        # New tasks for archive_snapshot loop
        elif task == "validate_snapshot":
            return self._gate_check(context)
        else:
            return RoleResult(
                success=False,
                output="",
                error=f"Unknown task: {task}",
            )

    def _pre_gate(self, context: RoleContext) -> RoleResult:
        """Quick pre-gate check for obvious issues."""
        system_prompt = self.build_system_prompt(context)

        user_prompt = f"""# Task: Pre-Gate Check

{self.format_artifacts(context.artifacts)}

Perform a quick 5-10 minute pre-gate check. Identify:

1. **Obvious Blockers**: Clear violations of quality bars
2. **Quick Wins**: Easy fixes that improve quality
3. **Likely Issues**: Areas that need deeper review

Focus on:
- Player-Neutral boundary violations (spoilers in player-facing text)
- Structural problems (dead ends, railroading)
- Diegetic gate violations (meta/mechanical checks)

Provide brief, actionable feedback. Don't deep-dive; flag for later review.

Format as JSON:
{{
  "status": "pass|warning|fail",
  "blockers": ["Issue 1", "Issue 2"],
  "quick_wins": ["Suggestion 1", "Suggestion 2"],
  "review_needed": ["Area 1", "Area 2"]
}}
"""

        response = ""
        try:
            response = self._call_llm(
                system_prompt, user_prompt, max_tokens=1500
            )

            # Parse JSON from response (handles markdown code blocks)
            data = self._parse_json_from_response(response)

            return RoleResult(
                success=True,
                output=response,
                metadata={
                    "check_type": "pre_gate",
                    "status": data.get("status", "unknown"),
                    "blockers": data.get("blockers", []),
                    "quick_wins": data.get("quick_wins", []),
                    "review_needed": data.get("review_needed", []),
                },
            )

        except json.JSONDecodeError as e:
            return RoleResult(
                success=False,
                output=response,
                error=f"Failed to parse JSON response: {e}",
            )
        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error in pre-gate check: {e}",
            )

    def _gate_check(self, context: RoleContext) -> RoleResult:
        """Full gate check against all quality bars."""
        system_prompt = self.build_system_prompt(context)

        # Get which bars to check (default: all 8)
        bars = context.additional_context.get(
            "bars",
            [
                "integrity",
                "reachability",
                "style_consistency",
                "gateway_design",
                "nonlinearity",
                "determinism",
                "presentation",
                "spoiler_hygiene",
            ],
        )

        user_prompt = f"""# Task: Full Gate Check

{self.format_artifacts(context.artifacts)}

Validate these artifacts against the following quality bars:

{', '.join(f'**{bar}**' for bar in bars)}

For each bar, provide:
- **Status**: pass/fail
- **Issues**: Specific problems found (with line/section references)
- **Fixes**: Concrete suggestions to address issues

Quality Bar Definitions:
1. **Integrity**: Schema conformance, no missing required fields
2. **Reachability**: All choices lead somewhere, no dead ends
3. **Style Consistency**: Tone, voice, formatting match project style
4. **Gateway Design**: Checks are diegetic (world-based), not meta/mechanical
5. **Nonlinearity**: Multiple meaningful paths, not railroading
6. **Determinism**: Outcomes follow from choices, not random
7. **Presentation**: Formatting, readability, polish
8. **Spoiler Hygiene**: Player-neutral boundaries maintained

Format as JSON:
{{
  "overall_status": "pass|fail",
  "merge_safe": true|false,
  "bars": {{
    "bar_name": {{
      "status": "pass|fail",
      "issues": ["Issue 1", "Issue 2"],
      "fixes": ["Fix 1", "Fix 2"]
    }}
  }}
}}
"""

        response = ""
        try:
            response = self._call_llm(
                system_prompt, user_prompt, max_tokens=3000
            )

            # Parse JSON from response (handles markdown code blocks)
            data = self._parse_json_from_response(response)

            return RoleResult(
                success=True,
                output=response,
                metadata={
                    "check_type": "gate_check",
                    "overall_status": data.get("overall_status", "unknown"),
                    "merge_safe": data.get("merge_safe", False),
                    "bars": data.get("bars", {}),
                },
            )

        except json.JSONDecodeError as e:
            return RoleResult(
                success=False,
                output=response,
                error=f"Failed to parse JSON response: {e}",
            )
        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error in gate check: {e}",
            )

    def _validate_bar(self, context: RoleContext) -> RoleResult:
        """Validate a specific quality bar."""
        bar_name = context.additional_context.get("bar_name")
        if not bar_name:
            return RoleResult(
                success=False,
                output="",
                error="bar_name required in additional_context",
            )

        system_prompt = self.build_system_prompt(context)

        user_prompt = f"""# Task: Validate Quality Bar - {bar_name}

{self.format_artifacts(context.artifacts)}

Validate these artifacts against the **{bar_name}** quality bar only.

Provide:
- Specific issues found (with line/section references)
- Concrete fixes for each issue
- Overall pass/fail assessment

Focus deeply on this one bar; ignore other quality aspects.
"""

        try:
            response = self._call_llm(
                system_prompt, user_prompt, max_tokens=2000
            )

            return RoleResult(
                success=True,
                output=response,
                metadata={
                    "check_type": "validate_bar",
                    "bar_name": bar_name,
                },
            )

        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error validating bar {bar_name}: {e}",
            )

    def _export_check(self, context: RoleContext) -> RoleResult:
        """Check export/view formatting."""
        system_prompt = self.build_system_prompt(context)

        user_prompt = f"""# Task: Export/View Check

{self.format_artifacts(context.artifacts)}

Check the export/view formatting:

1. **Front Matter**: Title, author, metadata present and correct
2. **Navigation**: TOC, links, structure clear
3. **Labels**: Section headers, artifact IDs consistent
4. **Formatting**: Markdown/HTML valid, no broken elements
5. **Player Safety**: No spoilers in Cold view

Provide specific issues and fixes.
"""

        try:
            response = self._call_llm(
                system_prompt, user_prompt, max_tokens=1500
            )

            return RoleResult(
                success=True,
                output=response,
                metadata={"check_type": "export_check"},
            )

        except Exception as e:
            return RoleResult(
                success=False,
                output="",
                error=f"Error in export check: {e}",
            )
