"""
Quality Control and Bias Detection Engine - Pure Business Logic

This module handles quality assurance and anti-bias checking.
It has ZERO database dependencies - pure functions that work with dataclass models.

Capabilities:
- Detect bias in questions and specifications
- Analyze coverage completeness
- Generate quality metrics
- Recommend improvements
- Make decisions (block vs. pass)

This logic is extracted from QualityControllerAgent for:
- Unit testing without database
- Library extraction without rework
- Consistency across all agents
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple

from .models import BiasAnalysisResult, CoverageAnalysisResult, SpecificationData


class BiasDetectionEngine:
    """
    Pure logic engine for detecting bias in text.

    This class contains pattern-based bias detection, completely
    separated from database operations and API handling.

    Usage:
        engine = BiasDetectionEngine(logger)
        result = engine.detect_bias_in_question(question_text)
        if not result.is_blocking:
            proceed_with_question()
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the bias detection engine.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

        # Bias detection patterns
        self.solution_bias_patterns = [
            "should we use", "let's use", "we need to use", "you should use",
            "must use", "have to use", "required to use"
        ]

        self.technology_bias_patterns = [
            "best framework", "industry standard", "everyone uses", "standard practice",
            "most popular", "leading solution", "state of the art"
        ]

        self.leading_question_patterns = [
            "you need", "obviously", "clearly", "of course", "the only way",
            "definitely", "certainly", "undoubtedly", "without question"
        ]

        self.solution_bias_weight = 0.3
        self.technology_bias_weight = 0.4
        self.leading_question_weight = 0.5

    def detect_bias_in_question(self, question_text: str) -> BiasAnalysisResult:
        """
        Analyze question text for various types of bias.

        Pure logic: pattern matching and scoring.

        Args:
            question_text: The question to analyze

        Returns:
            BiasAnalysisResult with score, types, and suggested alternatives
        """
        text_lower = question_text.lower()
        detected_biases = []
        total_score = 0.0

        # Check for solution bias
        solution_bias_count = sum(
            1 for pattern in self.solution_bias_patterns
            if pattern in text_lower
        )
        if solution_bias_count > 0:
            detected_biases.append('solution_bias')
            total_score += solution_bias_count * self.solution_bias_weight

        # Check for technology bias
        tech_bias_count = sum(
            1 for pattern in self.technology_bias_patterns
            if pattern in text_lower
        )
        if tech_bias_count > 0:
            detected_biases.append('technology_bias')
            total_score += tech_bias_count * self.technology_bias_weight

        # Check for leading questions
        leading_count = sum(
            1 for pattern in self.leading_question_patterns
            if pattern in text_lower
        )
        if leading_count > 0:
            detected_biases.append('leading_question')
            total_score += leading_count * self.leading_question_weight

        # Normalize score to 0-1 range
        bias_score = min(total_score / max(1.0, len(question_text) / 50), 1.0)

        # Determine if blocking
        is_blocking = bias_score > 0.5

        # Generate reason and alternatives
        reason = None
        alternatives = []

        if is_blocking:
            if 'solution_bias' in detected_biases:
                reason = "Question contains solution bias (suggests specific technology/approach)"
                alternatives.append("What are the important requirements for [feature]?")
            elif 'technology_bias' in detected_biases:
                reason = "Question shows technology bias (assumes industry standard)"
                alternatives.append("What constraints or requirements guide your technology choices?")
            elif 'leading_question' in detected_biases:
                reason = "Question is leading (assumes answer user should provide)"
                alternatives.append("What are your thoughts on [topic]?")

        return BiasAnalysisResult(
            bias_score=bias_score,
            bias_types=detected_biases,
            is_blocking=is_blocking,
            reason=reason,
            suggested_alternatives=alternatives
        )

    def detect_bias_in_specification(self, spec_value: str) -> float:
        """
        Analyze specification value for bias indicators.

        Pure logic: checks if spec contains biased language.

        Args:
            spec_value: The specification value to analyze

        Returns:
            Bias score (0.0-1.0, higher = more biased)
        """
        value_lower = spec_value.lower()

        # Check for prescriptive language
        prescriptive_words = ["must", "should", "required", "mandatory", "only"]
        prescriptive_count = sum(1 for word in prescriptive_words if f" {word} " in f" {value_lower} ")

        # Check for superlatives
        superlatives = ["best", "worst", "most", "least", "only", "never", "always"]
        superlative_count = sum(1 for sup in superlatives if sup in value_lower)

        # Calculate score
        score = (prescriptive_count * 0.3 + superlative_count * 0.2) / max(1.0, len(value_lower) / 50)
        return min(score, 1.0)

    # =========================================================================
    # QUALITY METRICS
    # =========================================================================

    def calculate_question_quality_score(
        self,
        question_text: str,
        previous_questions: List[str]
    ) -> float:
        """
        Calculate overall quality score for a question (0-1, 1=excellent).

        Pure logic: combines multiple quality factors.

        Args:
            question_text: The question to score
            previous_questions: List of previously asked questions

        Returns:
            Quality score (0.0-1.0, where 1.0 is perfect)
        """
        # Start with bias detection
        bias_result = self.detect_bias_in_question(question_text)
        bias_quality = 1.0 - bias_result.bias_score

        # Check for repetition
        similarity_scores = [
            self._calculate_text_similarity(question_text, prev)
            for prev in previous_questions
        ]
        max_similarity = max(similarity_scores) if similarity_scores else 0.0
        repetition_penalty = max_similarity * 0.5

        # Check for open-ended nature
        openness_score = self._assess_openness(question_text)

        # Check length appropriateness
        word_count = len(question_text.split())
        length_score = 1.0 if 10 <= word_count <= 40 else 0.7

        # Combine scores
        quality_score = (
            bias_quality * 0.4 +
            (1.0 - repetition_penalty) * 0.2 +
            openness_score * 0.2 +
            length_score * 0.2
        )

        return max(0.0, min(1.0, quality_score))

    # =========================================================================
    # COVERAGE ANALYSIS
    # =========================================================================

    def analyze_coverage(
        self,
        specs: List[SpecificationData],
        required_categories: List[str] = None
    ) -> CoverageAnalysisResult:
        """
        Analyze specification coverage across categories.

        Pure logic: calculates coverage percentages and gaps.

        Args:
            specs: List of SpecificationData to analyze
            required_categories: List of categories that must be covered

        Returns:
            CoverageAnalysisResult with score, gaps, and suggestions
        """
        if required_categories is None:
            required_categories = [
                'goals', 'requirements', 'tech_stack', 'scalability',
                'security', 'performance', 'testing', 'monitoring'
            ]

        # Count specs per category
        coverage_by_category = {}
        for spec in specs:
            category = spec.category
            if category in required_categories:
                coverage_by_category[category] = coverage_by_category.get(category, 0) + 1

        # Calculate coverage percentage
        covered_categories = len([c for c in required_categories if coverage_by_category.get(c, 0) > 0])
        total_categories = len(required_categories)
        coverage_score = covered_categories / total_categories if total_categories > 0 else 0.0

        # Identify gaps
        gaps = [c for c in required_categories if coverage_by_category.get(c, 0) == 0]

        # Generate suggestions
        suggestions = []
        if gaps:
            for gap in gaps[:3]:  # Top 3 gaps
                suggestions.append(f"Add specifications for: {gap}")

        # Determine if sufficient
        is_sufficient = coverage_score >= 0.7 and len(gaps) <= 2

        return CoverageAnalysisResult(
            coverage_score=coverage_score,
            coverage_by_category=coverage_by_category,
            gaps=gaps,
            is_sufficient=is_sufficient,
            suggested_actions=suggestions
        )

    # =========================================================================
    # DECISION LOGIC
    # =========================================================================

    def should_block_question(self, bias_result: BiasAnalysisResult) -> bool:
        """
        Determine if question should be blocked.

        Pure logic: decision rule based on bias score.

        Args:
            bias_result: BiasAnalysisResult from bias detection

        Returns:
            True if question should be blocked, False otherwise
        """
        return bias_result.is_blocking

    def should_continue_gathering_specs(self, coverage: CoverageAnalysisResult) -> bool:
        """
        Determine if more specifications should be gathered.

        Pure logic: decision rule based on coverage.

        Args:
            coverage: CoverageAnalysisResult from coverage analysis

        Returns:
            True if more specs needed, False if sufficient
        """
        return not coverage.is_sufficient

    # =========================================================================
    # PRIVATE HELPERS (Pure Logic)
    # =========================================================================

    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts (0.0-1.0).

        Uses simple word overlap for efficiency.

        Args:
            text1: First text
            text2: Second text

        Returns:
            Similarity score (0.0-1.0)
        """
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = len(words1 & words2)
        union = len(words1 | words2)

        return intersection / union if union > 0 else 0.0

    def _assess_openness(self, question_text: str) -> float:
        """
        Assess how open-ended a question is.

        Pure logic: pattern matching and keyword detection.

        Args:
            question_text: The question to assess

        Returns:
            Openness score (0.0-1.0, higher = more open-ended)
        """
        text_lower = question_text.lower()

        # Yes/no questions (not open-ended)
        if text_lower.strip().endswith("?") and any(
            text_lower.startswith(q) for q in ["do ", "does ", "did ", "can ", "could ", "will "]
        ):
            return 0.3

        # Wh- questions (very open-ended)
        if any(text_lower.startswith(w) for w in ["what ", "why ", "how ", "who ", "when ", "where "]):
            return 1.0

        # Partial openness
        if "what" in text_lower or "how" in text_lower:
            return 0.8

        return 0.6


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_quality_engine(logger: Optional[logging.Logger] = None) -> BiasDetectionEngine:
    """
    Factory function to create quality engine.

    Args:
        logger: Optional logger instance

    Returns:
        BiasDetectionEngine instance
    """
    return BiasDetectionEngine(logger)
