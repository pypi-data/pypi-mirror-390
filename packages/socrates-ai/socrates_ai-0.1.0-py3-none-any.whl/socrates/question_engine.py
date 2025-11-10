"""
Question Generation Engine - Pure Business Logic

This module contains the core logic for generating Socratic questions.
It has ZERO database dependencies - pure functions that work with dataclass models.

This enables:
- Unit testing without database
- Library extraction without rework
- Performance optimization (no database per question)
- Easy understanding of question generation logic
"""

import json
import logging
from typing import Dict, List, Any, Optional

from .models import ProjectData, SpecificationData, QuestionData, UserBehaviorData


# Question categories and their priorities
QUESTION_CATEGORIES = [
    'goals',
    'requirements',
    'tech_stack',
    'scalability',
    'security',
    'performance',
    'testing',
    'monitoring',
    'data_retention',
    'disaster_recovery'
]

# Target spec count per category for 100% maturity
CATEGORY_TARGETS = {
    'goals': 10,
    'requirements': 15,
    'tech_stack': 12,
    'scalability': 8,
    'security': 10,
    'performance': 8,
    'testing': 8,
    'monitoring': 6,
    'data_retention': 5,
    'disaster_recovery': 8
}


class QuestionGenerator:
    """
    Pure logic engine for generating Socratic questions.

    This class contains the core question generation logic, completely
    separated from database operations and API handling.

    Usage:
        engine = QuestionGenerator(logger)
        question = engine.generate(
            project=project_data,
            specs=spec_data_list,
            previous_questions=question_data_list,
            user_behavior=user_behavior_data
        )
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the question generator.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

    def calculate_coverage(self, specs: List[SpecificationData]) -> Dict[str, float]:
        """
        Calculate coverage percentage per category.

        Pure logic: works with plain data, no database access.

        Args:
            specs: List of SpecificationData instances

        Returns:
            Dictionary mapping category to coverage percentage (0-100)
        """
        # Count specs per category
        spec_counts = {}
        for spec in specs:
            category = spec.category
            spec_counts[category] = spec_counts.get(category, 0) + 1

        # Calculate coverage percentage
        coverage = {}
        for category in QUESTION_CATEGORIES:
            target = CATEGORY_TARGETS[category]
            count = spec_counts.get(category, 0)
            coverage[category] = min(count / target, 1.0) * 100

        return coverage

    def identify_next_category(self, coverage: Dict[str, float]) -> str:
        """
        Identify category with lowest coverage.

        Pure logic: finds the next area to focus question generation on.

        Args:
            coverage: Dictionary mapping category to coverage percentage

        Returns:
            Category name with lowest coverage
        """
        if not coverage:
            return 'goals'  # Start with goals

        # Find category with lowest coverage
        return min(coverage, key=coverage.get)

    def build_question_generation_prompt(
        self,
        project: ProjectData,
        specs: List[SpecificationData],
        previous_questions: List[QuestionData],
        next_category: str,
        user_behavior: Optional[UserBehaviorData] = None
    ) -> str:
        """
        Build prompt for Claude to generate question.

        Pure logic: constructs prompt based on plain data.
        The actual Claude API call happens outside this engine (in the agent).

        Args:
            project: ProjectData instance
            specs: List of SpecificationData instances
            previous_questions: List of QuestionData instances
            next_category: Category to focus on
            user_behavior: Optional UserBehaviorData for personalization

        Returns:
            Prompt string for Claude API
        """
        # Format user learning context if available
        user_learning_context = ""
        if user_behavior:
            total_q = user_behavior.total_questions_asked
            quality = user_behavior.overall_response_quality
            if total_q > 0:
                user_learning_context = f"""
USER LEARNING PROFILE:
- Experience: {total_q} questions answered previously
- Response quality: {quality:.0%}
- Known patterns: {len(user_behavior.patterns)} learned behavior patterns

Adapt your question style based on this user's experience level and communication style.
"""

        prompt = f"""You are a Socratic counselor helping gather requirements for a software project.

PROJECT CONTEXT:
- Name: {project.name}
- Description: {project.description or 'None provided yet'}
- Phase: {project.current_phase}
- Maturity: {project.maturity_score:.0f}%

EXISTING SPECIFICATIONS:
{self._format_specs(specs)}

PREVIOUS QUESTIONS ASKED:
{self._format_questions(previous_questions)}
{user_learning_context}NEXT FOCUS AREA: {next_category}

TASK:
Generate the next question focusing on: {next_category}

REQUIREMENTS:
1. Ask about ONE specific aspect of {next_category}
2. Keep question concise and clear (max 2 sentences)
3. Avoid assuming solutions (no "should we use X?" questions)
4. Make it open-ended to encourage detailed answers
5. Provide context about why this question matters
6. Do NOT repeat or rephrase previous questions

IMPORTANT:
- If user hasn't described their project yet, ask about project goals/purpose
- If basic goals are known, ask progressively deeper questions
- Focus on understanding WHAT they want, not HOW to build it (yet)

Return ONLY valid JSON in this EXACT format (no additional text):
{{
  "text": "the question text",
  "category": "{next_category}",
  "context": "brief explanation of why this question matters"
}}"""

        return prompt

    def parse_question_response(self, response_text: str, category: str) -> Dict[str, Any]:
        """
        Parse Claude's JSON response into question data.

        Pure logic: parses and validates JSON response.

        Args:
            response_text: Raw response from Claude API
            category: Category this question should be in

        Returns:
            Dictionary with keys: text, category, context
            Raises json.JSONDecodeError if response is invalid
        """
        # Strip markdown code fences if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]  # Remove ```json
        if response_text.startswith('```'):
            response_text = response_text[3:]  # Remove ```
        if response_text.endswith('```'):
            response_text = response_text[:-3]  # Remove ```

        response_text = response_text.strip()

        # Parse JSON
        question_data = json.loads(response_text)

        # Validate required fields
        if 'text' not in question_data:
            raise ValueError("Question response missing 'text' field")
        if 'category' not in question_data:
            question_data['category'] = category
        if 'context' not in question_data:
            question_data['context'] = ""

        return question_data

    def create_question_data(
        self,
        question_id: str,
        text: str,
        category: str,
        context: str,
        quality_score: float = 1.0
    ) -> QuestionData:
        """
        Create a QuestionData instance from parsed response.

        Pure logic: assembles plain data object.

        Args:
            question_id: Unique identifier for this question
            text: The question text
            category: Question category
            context: Why this question matters
            quality_score: Quality score (0-1, 1.0 = no bias)

        Returns:
            QuestionData instance
        """
        return QuestionData(
            id=question_id,
            text=text,
            category=category,
            context=context,
            quality_score=quality_score
        )

    # =========================================================================
    # PRIVATE HELPERS (Pure Logic)
    # =========================================================================

    def _format_specs(self, specs: List[SpecificationData]) -> str:
        """
        Format specifications for prompt.

        Args:
            specs: List of SpecificationData instances

        Returns:
            Formatted string of specifications
        """
        if not specs:
            return "None yet - this is the first interaction"

        lines = []
        for spec in specs[:20]:  # Limit to prevent huge prompts
            lines.append(f"- [{spec.category}] {spec.key}: {spec.value}")

        return "\n".join(lines)

    def _format_questions(self, questions: List[QuestionData]) -> str:
        """
        Format previous questions for prompt.

        Args:
            questions: List of QuestionData instances

        Returns:
            Formatted string of questions
        """
        if not questions:
            return "None yet - this is the first question"

        lines = []
        for q in questions[:10]:  # Limit to most recent 10
            lines.append(f"- [{q.category}] {q.text}")

        return "\n".join(lines)


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_question_generator(logger: Optional[logging.Logger] = None) -> QuestionGenerator:
    """
    Factory function to create question generator.

    Args:
        logger: Optional logger instance

    Returns:
        QuestionGenerator instance
    """
    return QuestionGenerator(logger)
