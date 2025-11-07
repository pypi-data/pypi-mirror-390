"""
SOTA Recommender Systems Library.

A modern, production-ready library for building state-of-the-art recommender systems.
"""

__version__ = '0.2.0'

# Core components
from .core import (
    BaseRecommender,
    ImplicitRecommender,
    ExplicitRecommender,
    InteractionDataset
)

# Simple but effective models
from .models.simple import EASERecommender, SLIMRecommender

# Matrix Factorization models
from .models.factorization import SVDRecommender, SVDPlusPlusRecommender, ALSRecommender

# Neural models (optional, requires PyTorch)
try:
    from .models.neural import NCFRecommender
    _NCF_AVAILABLE = True
except ImportError:
    _NCF_AVAILABLE = False

# Graph Neural Networks (optional, requires PyTorch)
try:
    from .models.graph import LightGCNRecommender
    _LIGHTGCN_AVAILABLE = True
except ImportError:
    _LIGHTGCN_AVAILABLE = False

# Sequential models (optional, requires PyTorch)
try:
    from .models.sequential import SASRecRecommender
    _SASREC_AVAILABLE = True
except ImportError:
    _SASREC_AVAILABLE = False

# Evaluation
from .evaluation import Evaluator, cross_validate

# Data processing
from .data import (
    load_movielens,
    create_synthetic_dataset,
    UniformSampler,
    PopularitySampler
)

# Utils (production features)
from .utils import (
    InferenceCache,
    BatchInference,
    ModelEnsemble,
    profile_inference
)

__all__ = [
    # Core
    'BaseRecommender',
    'ImplicitRecommender',
    'ExplicitRecommender',
    'InteractionDataset',
    # Simple models
    'EASERecommender',
    'SLIMRecommender',
    # Matrix Factorization
    'SVDRecommender',
    'SVDPlusPlusRecommender',
    'ALSRecommender',
    # Evaluation
    'Evaluator',
    'cross_validate',
    # Data
    'load_movielens',
    'create_synthetic_dataset',
    'UniformSampler',
    'PopularitySampler',
    # Utils
    'InferenceCache',
    'BatchInference',
    'ModelEnsemble',
    'profile_inference',
]

# Add optional models
if _NCF_AVAILABLE:
    __all__.append('NCFRecommender')
if _LIGHTGCN_AVAILABLE:
    __all__.append('LightGCNRecommender')
if _SASREC_AVAILABLE:
    __all__.append('SASRecRecommender')

