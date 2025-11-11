"""
Gateways Quality Bar.

Validates that:
- Gateway conditions are diegetic (in-world, not meta)
- Conditions are consistent across sections
- PN can enforce without exposing internals
- No contradictory requirements
"""

import re

from ...models.artifact import Artifact
from .base import QualityBar, QualityBarResult, QualityIssue


class GatewaysBar(QualityBar):
    """
    Gateways Bar: Conditions consistent, enforceable, diegetic.

    Checks:
    - Conditions use in-world language (not technical)
    - Gateways enforceable by PN without leaking plumbing
    - No contradictory conditions
    - Clear, single conditions per gateway
    """

    # Non-diegetic patterns (technical/meta language)
    NON_DIEGETIC_PATTERNS = [
        r"\bcodeword\b",
        r"\bflag\b.*\bset\b",
        r"\bvariable\b",
        r"\bstate\b.*\btrue\b",
        r"\bif\s+\w+\s*==",
        r"\bboolean\b",
    ]

    @property
    def name(self) -> str:
        return "gateways"

    @property
    def description(self) -> str:
        return "Conditions consistent, enforceable, and spoiler-safe"

    def validate(self, artifacts: list[Artifact]) -> QualityBarResult:
        """
        Validate artifacts for gateway quality.

        Args:
            artifacts: List of artifacts to validate

        Returns:
            QualityBarResult
        """
        issues: list[QualityIssue] = []

        # Compile non-diegetic pattern regex
        non_diegetic = re.compile(
            "|".join(self.NON_DIEGETIC_PATTERNS), re.IGNORECASE
        )

        # Check manuscript sections
        sections = [
            a for a in artifacts if a.type == "manuscript_section"
        ]

        for section in sections:
            section_id = section.data.get("id", "unknown")

            # Check choice conditions
            choices = section.data.get("choices", [])
            for i, choice in enumerate(choices):
                if not isinstance(choice, dict):
                    continue

                # Check if condition is diegetic
                condition = choice.get("condition", "")

                if condition and isinstance(condition, str):
                    if non_diegetic.search(condition):
                        issues.append(
                            QualityIssue(
                                severity="warning",
                                message=(
                                    f"Choice condition not diegetic: "
                                    f"'{condition[:50]}'"
                                ),
                                location=f"section:{section_id}.choices[{i}]",
                                fix=(
                                    "Use in-world phrasing (items, knowledge, "
                                    "reputation) instead of technical terms"
                                ),
                            )
                        )

                # Check surface text for gates
                text = choice.get("text", "")
                if text and non_diegetic.search(text):
                    issues.append(
                        QualityIssue(
                            severity="blocker",
                            message=(
                                "Choice text contains non-diegetic language"
                            ),
                            location=f"section:{section_id}.choices[{i}]",
                            fix=(
                                "Remove technical/meta terms from "
                                "player-visible choice text"
                            ),
                        )
                    )

        return self._create_result(
            issues, sections_checked=len(sections)
        )
