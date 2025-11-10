"""
User Learning and Behavior Analysis Engine - Pure Business Logic

This module handles user learning profile management and behavior analysis.
It has ZERO database dependencies - pure functions that work with dataclass models.

Capabilities:
- Track user behavior patterns
- Calculate learning metrics
- Build user profiles
- Generate personalization hints
- Predict user preferences

This logic is extracted from UserLearningAgent for:
- Unit testing without database
- Library extraction without rework
- Personalization across all agents
"""

import logging
from typing import Dict, List, Any, Optional
from collections import Counter

from .models import UserBehaviorData


class LearningEngine:
    """
    Pure logic engine for tracking and analyzing user learning behavior.

    This class contains behavior tracking and analysis, completely
    separated from database operations and API handling.

    Usage:
        engine = LearningEngine(logger)
        profile = engine.build_user_profile(
            questions_asked=user_questions,
            responses_quality=quality_scores,
            topic_interactions=topics_visited
        )
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the learning engine.

        Args:
            logger: Optional logger instance
        """
        self.logger = logger or logging.getLogger(__name__)

    def build_user_profile(
        self,
        user_id: str,
        questions_asked: List[Dict[str, Any]],
        responses_quality: List[float],
        topic_interactions: List[str],
        projects_completed: int = 0
    ) -> UserBehaviorData:
        """
        Build comprehensive user learning profile.

        Pure logic: aggregates user behavior data.

        Args:
            user_id: Unique user identifier
            questions_asked: List of questions user was asked
            responses_quality: List of response quality scores (0.0-1.0)
            topic_interactions: List of topics user interacted with
            projects_completed: Number of projects user completed

        Returns:
            UserBehaviorData with complete profile
        """
        # Calculate overall response quality
        overall_quality = (
            sum(responses_quality) / len(responses_quality)
            if responses_quality else 0.5
        )

        # Extract behavior patterns from interactions
        patterns = self._extract_behavior_patterns(
            questions_asked,
            responses_quality,
            topic_interactions
        )

        return UserBehaviorData(
            user_id=user_id,
            total_questions_asked=len(questions_asked),
            overall_response_quality=overall_quality,
            patterns=patterns,
            learned_from_projects=projects_completed
        )

    def calculate_learning_metrics(
        self,
        user_behavior: UserBehaviorData
    ) -> Dict[str, Any]:
        """
        Calculate learning and engagement metrics.

        Pure logic: derives metrics from behavior data.

        Args:
            user_behavior: UserBehaviorData instance

        Returns:
            Dictionary with calculated metrics
        """
        metrics = {
            'experience_level': self._calculate_experience_level(user_behavior.total_questions_asked),
            'response_quality': user_behavior.overall_response_quality,
            'engagement_score': self._calculate_engagement_score(user_behavior),
            'learning_velocity': self._calculate_learning_velocity(user_behavior),
            'topics_explored': len(user_behavior.patterns.get('topics', [])),
            'communication_style': user_behavior.patterns.get('communication_style', 'unknown'),
            'detail_preference': user_behavior.patterns.get('detail_level', 'medium'),
        }

        return metrics

    def get_personalization_hints(
        self,
        user_behavior: UserBehaviorData
    ) -> Dict[str, Any]:
        """
        Generate personalization hints for question generation.

        Pure logic: adapts based on behavior patterns.

        Args:
            user_behavior: UserBehaviorData instance

        Returns:
            Dictionary with personalization hints
        """
        metrics = self.calculate_learning_metrics(user_behavior)

        hints = {
            'question_complexity': self._recommend_complexity(metrics['experience_level']),
            'question_format': self._recommend_format(user_behavior.patterns),
            'pace': self._recommend_pace(metrics['learning_velocity']),
            'focus_areas': self._recommend_focus_areas(user_behavior.patterns),
            'avoid_topics': self._identify_avoided_topics(user_behavior.patterns),
        }

        return hints

    def track_response_quality(
        self,
        question_text: str,
        response_text: str,
        quality_score: float
    ) -> Dict[str, Any]:
        """
        Track a single question-response interaction.

        Pure logic: analyzes and stores interaction data.

        Args:
            question_text: The question asked
            response_text: User's response
            quality_score: Quality of the response (0.0-1.0)

        Returns:
            Dictionary with tracked interaction data
        """
        interaction = {
            'question': question_text,
            'response': response_text,
            'quality_score': quality_score,
            'response_length': len(response_text.split()),
            'detail_level': self._assess_detail_level(response_text),
            'coherence': self._assess_coherence(question_text, response_text),
        }

        return interaction

    def predict_topic_preference(
        self,
        user_behavior: UserBehaviorData,
        available_topics: List[str]
    ) -> Dict[str, float]:
        """
        Predict which topics user might prefer next.

        Pure logic: scores topics based on user behavior.

        Args:
            user_behavior: UserBehaviorData instance
            available_topics: List of available topics

        Returns:
            Dictionary mapping topics to preference scores (0.0-1.0)
        """
        preferences = {}
        explored_topics = set(user_behavior.patterns.get('topics', []))

        for topic in available_topics:
            # Prefer unexplored topics for growth
            if topic not in explored_topics:
                base_score = 0.7
            else:
                # Slight preference for familiar topics
                base_score = 0.4

            # Adjust based on user's experience level
            experience_multiplier = 1.0 + (user_behavior.overall_response_quality * 0.5)
            preferences[topic] = min(base_score * experience_multiplier, 1.0)

        return preferences

    def assess_learning_progress(
        self,
        current_behavior: UserBehaviorData,
        previous_behavior: Optional[UserBehaviorData] = None
    ) -> Dict[str, Any]:
        """
        Assess user's learning progress over time.

        Pure logic: compares current vs. previous behavior.

        Args:
            current_behavior: Current UserBehaviorData
            previous_behavior: Optional previous UserBehaviorData for comparison

        Returns:
            Dictionary with progress assessment
        """
        if not previous_behavior:
            return {
                'is_improving': True,
                'questions_answered': current_behavior.total_questions_asked,
                'quality_trend': 'starting',
                'engagement_level': 'new_user',
            }

        quality_improvement = (
            current_behavior.overall_response_quality -
            previous_behavior.overall_response_quality
        )

        questions_growth = (
            current_behavior.total_questions_asked -
            previous_behavior.total_questions_asked
        )

        return {
            'is_improving': quality_improvement > 0,
            'quality_improvement': quality_improvement,
            'questions_answered_since_last': questions_growth,
            'quality_trend': self._determine_trend(quality_improvement),
            'engagement_level': self._determine_engagement(questions_growth),
            'estimated_expertise_gain': quality_improvement * questions_growth,
        }

    # =========================================================================
    # PRIVATE HELPERS (Pure Logic)
    # =========================================================================

    def _extract_behavior_patterns(
        self,
        questions_asked: List[Dict[str, Any]],
        responses_quality: List[float],
        topic_interactions: List[str]
    ) -> Dict[str, Any]:
        """
        Extract behavior patterns from user interactions.

        Args:
            questions_asked: List of questions
            responses_quality: List of quality scores
            topic_interactions: List of topics

        Returns:
            Dictionary of identified patterns
        """
        patterns = {
            'topics': list(set(topic_interactions)),
            'communication_style': self._infer_communication_style(responses_quality),
            'detail_level': self._infer_detail_preference(responses_quality),
            'consistency_score': self._calculate_consistency(responses_quality),
        }

        return patterns

    def _calculate_experience_level(self, questions_asked: int) -> str:
        """Calculate user's experience level based on interaction count."""
        if questions_asked < 5:
            return "novice"
        elif questions_asked < 20:
            return "intermediate"
        elif questions_asked < 50:
            return "advanced"
        else:
            return "expert"

    def _calculate_engagement_score(self, user_behavior: UserBehaviorData) -> float:
        """Calculate overall engagement score (0.0-1.0)."""
        # Factor 1: Question frequency (0.4)
        experience_level = self._calculate_experience_level(user_behavior.total_questions_asked)
        experience_scores = {"novice": 0.2, "intermediate": 0.5, "advanced": 0.8, "expert": 1.0}
        experience_score = experience_scores.get(experience_level, 0.5) * 0.4

        # Factor 2: Response quality (0.4)
        quality_score = user_behavior.overall_response_quality * 0.4

        # Factor 3: Projects completed (0.2)
        project_score = min(user_behavior.learned_from_projects / 10, 1.0) * 0.2

        return min(experience_score + quality_score + project_score, 1.0)

    def _calculate_learning_velocity(self, user_behavior: UserBehaviorData) -> float:
        """
        Calculate how quickly user is improving (0.0-1.0).

        Uses response quality as proxy for learning speed.
        """
        # If quality is high and user has many interactions, they're learning quickly
        velocity = user_behavior.overall_response_quality
        if user_behavior.total_questions_asked > 20:
            velocity *= 1.2

        return min(velocity, 1.0)

    def _recommend_complexity(self, experience_level: str) -> str:
        """Recommend question complexity based on experience."""
        complexity_map = {
            "novice": "simple",
            "intermediate": "moderate",
            "advanced": "complex",
            "expert": "expert",
        }
        return complexity_map.get(experience_level, "moderate")

    def _recommend_format(self, patterns: Dict[str, Any]) -> str:
        """Recommend question format based on patterns."""
        style = patterns.get('communication_style', 'formal')
        if style == 'casual':
            return 'conversational'
        elif style == 'technical':
            return 'detailed_technical'
        else:
            return 'standard'

    def _recommend_pace(self, velocity: float) -> str:
        """Recommend pace based on learning velocity."""
        if velocity > 0.7:
            return 'fast'
        elif velocity > 0.4:
            return 'moderate'
        else:
            return 'slow'

    def _recommend_focus_areas(self, patterns: Dict[str, Any]) -> List[str]:
        """Recommend focus areas based on explored topics."""
        topics = patterns.get('topics', [])
        if 'requirements' not in topics:
            return ['requirements', 'goals']
        elif 'tech_stack' not in topics:
            return ['tech_stack', 'architecture']
        else:
            return ['scalability', 'security']

    def _identify_avoided_topics(self, patterns: Dict[str, Any]) -> List[str]:
        """Identify topics user seems to avoid."""
        # Simple heuristic: topics not in their history
        all_topics = ['goals', 'requirements', 'tech_stack', 'scalability', 'security']
        explored = set(patterns.get('topics', []))
        return [t for t in all_topics if t not in explored]

    def _assess_detail_level(self, response_text: str) -> str:
        """Assess detail level of response."""
        words = len(response_text.split())
        if words < 20:
            return 'brief'
        elif words < 100:
            return 'moderate'
        else:
            return 'detailed'

    def _assess_coherence(self, question: str, response: str) -> float:
        """Assess coherence between question and response (0.0-1.0)."""
        # Simple heuristic: do key question words appear in response?
        question_words = set(question.lower().split())
        response_words = set(response.lower().split())
        overlap = len(question_words & response_words)
        return min(overlap / max(len(question_words), 1), 1.0)

    def _infer_communication_style(self, responses_quality: List[float]) -> str:
        """Infer communication style from response quality."""
        avg_quality = sum(responses_quality) / len(responses_quality) if responses_quality else 0.5
        if avg_quality > 0.8:
            return 'technical'
        elif avg_quality > 0.6:
            return 'professional'
        else:
            return 'casual'

    def _infer_detail_preference(self, responses_quality: List[float]) -> str:
        """Infer preferred detail level from response quality."""
        avg_quality = sum(responses_quality) / len(responses_quality) if responses_quality else 0.5
        if avg_quality > 0.75:
            return 'high'
        elif avg_quality > 0.5:
            return 'medium'
        else:
            return 'low'

    def _calculate_consistency(self, responses_quality: List[float]) -> float:
        """Calculate consistency of response quality."""
        if not responses_quality or len(responses_quality) < 2:
            return 0.5

        # Calculate standard deviation as measure of consistency
        avg = sum(responses_quality) / len(responses_quality)
        variance = sum((q - avg) ** 2 for q in responses_quality) / len(responses_quality)
        std_dev = variance ** 0.5

        # Convert to consistency score (inverse of variance)
        consistency = 1.0 - min(std_dev, 1.0)
        return consistency

    def _determine_trend(self, quality_improvement: float) -> str:
        """Determine quality improvement trend."""
        if quality_improvement > 0.1:
            return 'rapidly_improving'
        elif quality_improvement > 0.0:
            return 'improving'
        elif quality_improvement > -0.1:
            return 'stable'
        else:
            return 'declining'

    def _determine_engagement(self, questions_growth: int) -> str:
        """Determine engagement level from growth."""
        if questions_growth > 20:
            return 'highly_engaged'
        elif questions_growth > 5:
            return 'engaged'
        elif questions_growth > 0:
            return 'somewhat_engaged'
        else:
            return 'low_engagement'


# ============================================================================
# FACTORY FUNCTION
# ============================================================================

def create_learning_engine(logger: Optional[logging.Logger] = None) -> LearningEngine:
    """
    Factory function to create learning engine.

    Args:
        logger: Optional logger instance

    Returns:
        LearningEngine instance
    """
    return LearningEngine(logger)
