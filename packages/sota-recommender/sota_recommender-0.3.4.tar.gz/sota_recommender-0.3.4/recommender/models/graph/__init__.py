"""
Graph Neural Network based recommender models.
"""
try:
    from .lightgcn import LightGCNRecommender
    __all__ = ['LightGCNRecommender']
except ImportError:
    __all__ = []

