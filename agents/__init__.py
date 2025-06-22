"""
EduMate AI Agents Package

This package contains various AI agents for the EduMate application:
- SummarizerAgent: Document summarization functionality
- FlashcardAgent: Flashcard generation functionality
- QuizAgent: Quiz generation functionality
- PlannerAgent: Study plan generation functionality
- TrackerAgent: Progress tracking functionality
"""

from .summarizer_agent import SummarizerAgent
from .flashcard_agent import FlashcardAgent
from .quiz_agent import QuizAgent
from .planner_agent import PlannerAgent
from .tracker_agent import TrackerAgent

__all__ = [
    'SummarizerAgent',
    'FlashcardAgent',
    'QuizAgent',
    'PlannerAgent',
    'TrackerAgent'
]
