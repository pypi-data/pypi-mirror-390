"""
Conflict Detection and Analysis Engine - Pure Business Logic

This module handles specification conflict detection.
It has ZERO database dependencies - pure functions that work with dataclass models.

Capabilities:
- Analyze specifications for conflicts
- Detect contradiction patterns
- Assess conflict severity
- Generate resolution suggestions
- Format prompts for Claude API

This logic is extracted from ConflictDetectorAgent for:
- Unit testing without database
- Library extraction without rework
- Reusability across multiple agents
"""

import json
import logging
from typing import Dict, List, Any, Optional
from enum import Enum

from .models import SpecificationData, ConflictData


class ConflictType(str, Enum):
    """Types of conflicts that can be detected"""
    CONTRADICTION = "contradiction"  # Opposite specifications
    INCONSISTENCY = "inconsistency"  # Conflicting definitions
    DEPENDENCY = "dependency"  # One spec depends on excluding another
    REDUNDANCY = "redundancy"  # Overlapping specifications


class ConflictSeverity(str, Enum):
    """Severity levels of detected conflicts"""
    LOW = "low"  # Minor inconsistency, can coexist
    MEDIUM = "medium"  # Meaningful conflict, needs resolution
    HIGH = "high"  # Critical conflict, blocks implementation


class ConflictDetectionEngine:
    """
    Pure logic engine for detecting and analyzing specification conflicts.

    This class contains the core conflict detection logic, completely
    separated from database operations and API handling.

    Usage:
        engine = ConflictDetectionEngine(logger)
        conflicts = engine.detect_conflicts(
            new_specs=new_specs_data,
            existing_specs=existing_specs_data,
            project_context=project_data
        )
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the conflict detection engine.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

    def build_conflict_detection_prompt(
        self,
        new_specs: List[SpecificationData],
        existing_specs: List[SpecificationData],
        project_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build prompt for Claude to analyze conflicts.

        Pure logic: constructs prompt based on specification data.

        Args:
            new_specs: List of new SpecificationData to check
            existing_specs: List of existing SpecificationData to compare against
            project_context: Optional project context for analysis

        Returns:
            Prompt string for Claude API
        """
        # Format new specs for prompt
        new_specs_text = self._format_specs(new_specs)
        existing_specs_text = self._format_specs(existing_specs)

        project_info = ""
        if project_context:
            project_info = f"""
PROJECT CONTEXT:
- Name: {project_context.get('name', 'Unknown')}
- Phase: {project_context.get('current_phase', 'Unknown')}
- Maturity: {project_context.get('maturity_score', 0)}%
"""

        prompt = f"""You are analyzing software specifications for conflicts.

{project_info}
NEW SPECIFICATIONS (to be checked):
{new_specs_text}

EXISTING SPECIFICATIONS (already recorded):
{existing_specs_text}

TASK:
Analyze the new specifications against existing ones and identify any conflicts.

CONFLICT TYPES TO DETECT:
1. CONTRADICTION: New spec directly contradicts existing spec
   - Example: "API rate limit: 1000 req/min" vs "API rate limit: 100 req/min"

2. INCONSISTENCY: New spec conflicts with existing spec intent
   - Example: "Support all users" vs "Only support premium users"

3. DEPENDENCY: New spec implies exclusion of existing spec
   - Example: "Use PostgreSQL" vs "Use MongoDB"

4. REDUNDANCY: New spec duplicates/overlaps existing spec
   - Example: "Support mobile" (already stated)

ANALYSIS REQUIREMENTS:
1. Check each new spec against ALL existing specs
2. Assess severity: low (minor), medium (fixable), high (blocking)
3. For each conflict found, provide:
   - Type of conflict
   - Severity level
   - Specific specs involved
   - Clear description of the conflict
   - Suggested resolutions if applicable

Return ONLY valid JSON in this EXACT format (no additional text):
{{
  "conflicts_detected": true/false,
  "total_conflicts": number,
  "conflicts": [
    {{
      "type": "contradiction|inconsistency|dependency|redundancy",
      "severity": "low|medium|high",
      "description": "clear description of conflict",
      "new_spec_keys": ["key1", "key2"],
      "existing_spec_keys": ["existing_key1"],
      "resolution_suggestions": ["suggestion1", "suggestion2"]
    }}
  ],
  "summary": "overall analysis summary"
}}"""

        return prompt

    def parse_conflict_analysis(
        self,
        response_text: str,
        new_specs: List[SpecificationData],
        existing_specs: List[SpecificationData]
    ) -> Dict[str, Any]:
        """
        Parse Claude's JSON conflict analysis response.

        Pure logic: parses and validates JSON response.

        Args:
            response_text: Raw response from Claude API
            new_specs: List of new specs (for context)
            existing_specs: List of existing specs (for context)

        Returns:
            Dictionary with parsed conflict analysis
            Raises json.JSONDecodeError if response is invalid
        """
        # Strip markdown code fences if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]

        response_text = response_text.strip()

        # Parse JSON
        analysis = json.loads(response_text)

        # Validate required fields
        if 'conflicts_detected' not in analysis:
            raise ValueError("Analysis response missing 'conflicts_detected' field")

        return analysis

    def create_conflict_from_analysis(
        self,
        conflict_id: str,
        project_id: str,
        conflict_data: Dict[str, Any]
    ) -> ConflictData:
        """
        Create a ConflictData instance from parsed analysis.

        Pure logic: assembles plain data object.

        Args:
            conflict_id: Unique identifier for this conflict
            project_id: Project this conflict belongs to
            conflict_data: Parsed conflict data from analysis

        Returns:
            ConflictData instance
        """
        return ConflictData(
            id=conflict_id,
            type=conflict_data.get('type', 'inconsistency'),
            severity=conflict_data.get('severity', 'medium'),
            description=conflict_data.get('description', ''),
            spec1_id=conflict_data.get('new_spec_keys', [''])[0],
            spec2_id=conflict_data.get('existing_spec_keys', [''])[0],
            resolution_suggestion=conflict_data.get('resolution_suggestions', [None])[0] if conflict_data.get('resolution_suggestions') else None
        )

    def assess_severity(self, conflict_data: Dict[str, Any]) -> ConflictSeverity:
        """
        Assess conflict severity from analysis.

        Pure logic: determines severity level.

        Args:
            conflict_data: Conflict data from analysis

        Returns:
            ConflictSeverity enum value
        """
        severity_str = conflict_data.get('severity', 'medium').lower()
        try:
            return ConflictSeverity[severity_str.upper()]
        except KeyError:
            return ConflictSeverity.MEDIUM

    def should_block_operation(self, conflicts: List[Dict[str, Any]]) -> bool:
        """
        Determine if operation should be blocked based on conflicts.

        Pure logic: decides if high-severity conflicts prevent action.

        Args:
            conflicts: List of detected conflicts

        Returns:
            True if any HIGH severity conflict exists, False otherwise
        """
        for conflict in conflicts:
            severity = conflict.get('severity', 'medium').lower()
            if severity == 'high':
                return True
        return False

    # =========================================================================
    # PRIVATE HELPERS (Pure Logic)
    # =========================================================================

    def _format_specs(self, specs: List[SpecificationData]) -> str:
        """
        Format specifications for conflict analysis prompt.

        Args:
            specs: List of SpecificationData instances

        Returns:
            Formatted string of specifications
        """
        if not specs:
            return "None yet"

        lines = []
        for spec in specs[:30]:  # Limit to prevent huge prompts
            lines.append(f"- [{spec.category}] {spec.key}: {spec.value} (confidence: {spec.confidence:.0%})")

        return "\n".join(lines)


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_conflict_detection_engine(
    logger: Optional[logging.Logger] = None
) -> ConflictDetectionEngine:
    """
    Factory function to create conflict detection engine.

    Args:
        logger: Optional logger instance

    Returns:
        ConflictDetectionEngine instance
    """
    return ConflictDetectionEngine(logger)
