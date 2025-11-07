"""
Core components for recommender systems.
"""
from .base import BaseRecommender, ImplicitRecommender, ExplicitRecommender
from .data import InteractionDataset

__all__ = [
    'BaseRecommender',
    'ImplicitRecommender', 
    'ExplicitRecommender',
    'InteractionDataset'
]

# Conditionally import trainer if PyTorch is available
try:
    from .trainers import Trainer, EarlyStopping
    __all__.extend(['Trainer', 'EarlyStopping'])
except ImportError:
    pass

