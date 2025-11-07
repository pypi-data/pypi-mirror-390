"""
Sequential recommendation models.
"""
try:
    from .sasrec import SASRecRecommender
    __all__ = ['SASRecRecommender']
except ImportError:
    __all__ = []

