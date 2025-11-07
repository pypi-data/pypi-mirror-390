"""
Utility functions.
"""

# Inference optimization
from .inference import (
    InferenceCache,
    BatchInference,
    ModelEnsemble,
    profile_inference,
    optimize_model_for_inference
)

__all__ = [
    'InferenceCache',
    'BatchInference',
    'ModelEnsemble',
    'profile_inference',
    'optimize_model_for_inference'
]

# FAISS (optional)
try:
    from .faiss_index import FAISSIndex, create_faiss_index_from_model
    __all__.extend(['FAISSIndex', 'create_faiss_index_from_model'])
except ImportError:
    pass

