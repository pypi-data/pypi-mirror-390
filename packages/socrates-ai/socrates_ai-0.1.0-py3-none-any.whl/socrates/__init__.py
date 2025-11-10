"""
Socrates: Socratic questioning and AI-powered specification analysis engine

A pure Python library for:
- Generating Socratic questions to guide specification gathering
- Detecting conflicts and inconsistencies in specifications
- Analyzing question quality and detecting biases
- Learning user behavior patterns and personalizing interactions

Zero database dependencies - works with any backend or as standalone tool.
"""

__version__ = "0.1.0"
__author__ = "Socrates Contributors"

# Core engines - pure business logic with zero database dependencies
from .question_engine import QuestionGenerator, create_question_generator
from .conflict_engine import ConflictDetectionEngine
from .quality_engine import BiasDetectionEngine
from .learning_engine import LearningEngine

# Data models - plain Python dataclasses for library use
from .models import (
    ProjectData,
    SpecificationData,
    QuestionData,
    ConflictData,
    MaturityScore,
    UserBehaviorData,
    BiasAnalysisResult,
    CoverageAnalysisResult,
    # Conversion functions for bridging database models to plain dataclasses
    project_db_to_data,
    spec_db_to_data,
    question_db_to_data,
    conflict_db_to_data,
    specs_db_to_data,
    questions_db_to_data,
    conflicts_db_to_data,
)

__all__ = [
    # Engines
    "QuestionGenerator",
    "create_question_generator",
    "ConflictDetectionEngine",
    "BiasDetectionEngine",
    "LearningEngine",
    # Models
    "ProjectData",
    "SpecificationData",
    "QuestionData",
    "ConflictData",
    "MaturityScore",
    "UserBehaviorData",
    "BiasAnalysisResult",
    "CoverageAnalysisResult",
    # Conversion Functions
    "project_db_to_data",
    "spec_db_to_data",
    "question_db_to_data",
    "conflict_db_to_data",
    "specs_db_to_data",
    "questions_db_to_data",
    "conflicts_db_to_data",
]
