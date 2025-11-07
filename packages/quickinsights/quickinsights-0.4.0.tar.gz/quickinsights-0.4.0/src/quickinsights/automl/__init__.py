"""
AutoML Module - Intelligent Machine Learning Automation

This module provides intelligent model selection, hyperparameter tuning,
and automated machine learning capabilities.
"""

from .model_selection import intelligent_model_selection
from .hyperparameter_tuning import auto_hyperparameter_tuning
from .explainability import explainable_ai
from .meta_learning import meta_learner
from .continuous_learning import continuous_learner

__all__ = [
    'intelligent_model_selection',
    'auto_hyperparameter_tuning', 
    'explainable_ai',
    'meta_learner',
    'continuous_learner'
]
