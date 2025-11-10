"""
Plain Data Models for Core Business Logic

These are database-agnostic dataclass models used by all core engines.
They enable:
- Pure business logic (no database dependencies)
- Easy unit testing (no database needed)
- Library extraction (can move to separate package)
- Type safety and IDE support

Unlike SQLAlchemy models, these have:
- No database sessions
- No lazy loading
- No relationship management
- Just plain data structures

Conversion from/to database models happens at the API/Agent layer.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============================================================================
# PROJECT & SPECIFICATION MODELS
# ============================================================================

@dataclass
class ProjectData:
    """Plain project data - used by all core engines"""
    id: str
    name: str
    description: str
    current_phase: str  # 'discovery', 'design', 'implementation', etc.
    maturity_score: float  # 0-100
    user_id: str
    created_at: Optional[str] = None  # ISO format if needed
    updated_at: Optional[str] = None


@dataclass
class SpecificationData:
    """Plain specification data - used by conflict/quality/maturity engines"""
    id: str
    project_id: str
    category: str  # 'goals', 'requirements', 'tech_stack', etc.
    key: str  # e.g., 'framework'
    value: str  # e.g., 'FastAPI'
    confidence: float  # 0.0-1.0
    source: str = 'user_input'  # 'user_input', 'extracted', 'imported'
    is_current: bool = True
    created_at: Optional[str] = None


# ============================================================================
# QUESTION & INTERACTION MODELS
# ============================================================================

@dataclass
class QuestionData:
    """Plain question data - used by question generator and bias detector"""
    id: str
    text: str
    category: str  # 'goals', 'requirements', etc.
    context: str  # Why this question matters
    quality_score: float  # 0.0-1.0 (1.0 = no bias)
    created_at: Optional[str] = None


@dataclass
class ConflictData:
    """Plain conflict data - used by conflict detector/resolver"""
    id: str
    type: str  # 'contradiction', 'inconsistency', 'dependency'
    severity: str  # 'low', 'medium', 'high'
    description: str
    spec1_id: str
    spec2_id: str
    resolution_suggestion: Optional[str] = None
    created_at: Optional[str] = None


# ============================================================================
# ANALYSIS RESULT MODELS
# ============================================================================

@dataclass
class BiasAnalysisResult:
    """Result of bias analysis"""
    bias_score: float  # 0.0 (no bias) to 1.0 (extreme bias)
    bias_types: List[str] = field(default_factory=list)  # ['solution_bias', 'leading_question', etc.]
    is_blocking: bool = False  # True if score > 0.5
    reason: Optional[str] = None  # Why it's blocked
    suggested_alternatives: List[str] = field(default_factory=list)  # Better question alternatives


@dataclass
class CoverageAnalysisResult:
    """Result of coverage analysis"""
    coverage_score: float  # 0.0-1.0 (percentage)
    coverage_by_category: Dict[str, int] = field(default_factory=dict)  # {'goals': 5, 'requirements': 8, ...}
    gaps: List[str] = field(default_factory=list)  # Categories with insufficient specs
    is_sufficient: bool = False  # True if score >= 0.7
    suggested_actions: List[str] = field(default_factory=list)  # What to ask next


@dataclass
class MaturityScore:
    """Maturity score calculation result"""
    current_score: float
    delta: float
    new_score: float
    next_category: str  # Next focus area for questions


# ============================================================================
# USER & BEHAVIOR MODELS
# ============================================================================

@dataclass
class UserBehaviorData:
    """User learning profile data"""
    user_id: str
    total_questions_asked: int
    overall_response_quality: float  # 0.0-1.0
    patterns: Dict[str, Any] = field(default_factory=dict)  # {'communication_style': 'detailed', ...}
    learned_from_projects: int = 0  # Number of projects analyzed


# ============================================================================
# CONVERSION FUNCTIONS (Keep at API/Agent Layer, Not in Core)
# ============================================================================

def project_db_to_data(db_project) -> ProjectData:
    """
    Convert SQLAlchemy Project to ProjectData.

    Args:
        db_project: SQLAlchemy Project model instance

    Returns:
        ProjectData instance with same information
    """
    return ProjectData(
        id=str(db_project.id),
        name=db_project.name,
        description=db_project.description,
        current_phase=db_project.current_phase,
        maturity_score=float(db_project.maturity_score),
        user_id=str(db_project.user_id),
        created_at=db_project.created_at.isoformat() if db_project.created_at else None,
        updated_at=db_project.updated_at.isoformat() if db_project.updated_at else None
    )


def spec_db_to_data(db_spec) -> SpecificationData:
    """
    Convert SQLAlchemy Specification to SpecificationData.

    Args:
        db_spec: SQLAlchemy Specification model instance

    Returns:
        SpecificationData instance with same information
    """
    return SpecificationData(
        id=str(db_spec.id),
        project_id=str(db_spec.project_id),
        category=db_spec.category,
        key=db_spec.key,
        value=db_spec.value,
        confidence=float(db_spec.confidence),
        source=db_spec.source,
        is_current=db_spec.is_current,
        created_at=db_spec.created_at.isoformat() if db_spec.created_at else None
    )


def question_db_to_data(db_question) -> QuestionData:
    """
    Convert SQLAlchemy Question to QuestionData.

    Args:
        db_question: SQLAlchemy Question model instance

    Returns:
        QuestionData instance with same information
    """
    return QuestionData(
        id=str(db_question.id),
        text=db_question.text,
        category=db_question.category,
        context=db_question.context,
        quality_score=float(db_question.quality_score),
        created_at=db_question.created_at.isoformat() if db_question.created_at else None
    )


def conflict_db_to_data(db_conflict) -> ConflictData:
    """
    Convert SQLAlchemy Conflict to ConflictData.

    Args:
        db_conflict: SQLAlchemy Conflict model instance

    Returns:
        ConflictData instance with same information
    """
    return ConflictData(
        id=str(db_conflict.id),
        type=db_conflict.type,
        severity=db_conflict.severity,
        description=db_conflict.description,
        spec1_id=str(db_conflict.spec1_id),
        spec2_id=str(db_conflict.spec2_id),
        resolution_suggestion=db_conflict.resolution_suggestion,
        created_at=db_conflict.created_at.isoformat() if db_conflict.created_at else None
    )


def specs_db_to_data(db_specs: list) -> List[SpecificationData]:
    """
    Batch convert specifications.

    Args:
        db_specs: List of SQLAlchemy Specification model instances

    Returns:
        List of SpecificationData instances
    """
    return [spec_db_to_data(s) for s in db_specs]


def questions_db_to_data(db_questions: list) -> List[QuestionData]:
    """
    Batch convert questions.

    Args:
        db_questions: List of SQLAlchemy Question model instances

    Returns:
        List of QuestionData instances
    """
    return [question_db_to_data(q) for q in db_questions]


def conflicts_db_to_data(db_conflicts: list) -> List[ConflictData]:
    """
    Batch convert conflicts.

    Args:
        db_conflicts: List of SQLAlchemy Conflict model instances

    Returns:
        List of ConflictData instances
    """
    return [conflict_db_to_data(c) for c in db_conflicts]
