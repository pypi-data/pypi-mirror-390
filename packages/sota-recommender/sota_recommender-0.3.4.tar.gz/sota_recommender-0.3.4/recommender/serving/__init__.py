"""
Model serving utilities.
"""
try:
    from .api import RecommenderService, create_service
    __all__ = ['RecommenderService', 'create_service']
except ImportError:
    __all__ = []

